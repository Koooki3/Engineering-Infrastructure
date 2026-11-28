#!/usr/bin/env python3
"""Plan and maintain global engineering infrastructure and reviewed Skills."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import time

import candidate
import catalog
import global_setup as setup
from store import atomic, check_path, describe, digest, encode, files, locked, read_json, recover, rollback, signature, transact


SOURCE = Path(__file__).resolve().parents[3]
AGENTS = ('codex', 'claude', 'opencode', 'antigravity')
PLATFORM = {'win32': 'windows', 'darwin': 'macos'}.get(sys.platform, 'linux')


def output(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


ENTRY = re.compile(r'Global maintenance entry point: `([^`\r\n]+)`')


def _same(path):
    return os.path.normcase(os.path.abspath(path))


def deployed_state(home):
    """The one state directory that the managed instruction blocks in this home belong to.

    None when no adapter carries a block (first install). Raises when blocks are malformed,
    point outside a state layout, are not owned by the state they name, or name more than
    one state: the caller must then pass --state. Integrity is not required, so a state that
    needs recover or rollback can still be located.
    """
    found = {}
    for agent, (_skills, rules) in setup.adapters(home).items():
        try:
            text = rules.read_bytes().decode('utf-8-sig')
        except FileNotFoundError:
            continue
        block = setup.extract_block(text)  # raises on duplicate or unbalanced markers
        if block is None:
            continue
        match = ENTRY.findall(block)
        if len(match) != 1:
            raise ValueError(f'Managed instruction block in {rules} has no single entry point; pass --state')
        cli = Path(match[0])
        if [part.lower() for part in cli.parts[-3:]] != ['runtime', 'tools', 'setup.py']:
            raise ValueError(f'Managed instruction block in {rules} does not name <state>/runtime/tools/setup.py; '
                             'pass --state')
        root = cli.parent.parent.parent
        path = root / 'deployment.json'
        if path.is_file():
            try:
                docs = read_json(path).get('docs', {})
            except ValueError as exc:
                raise ValueError(f'{path} is unreadable ({exc}); pass --state') from exc
            if _same(rules) not in {_same(doc) for doc in docs}:
                raise ValueError(f'{rules} is not owned by {root}; pass --state')
        elif not (root / 'history').is_dir():
            raise ValueError(f'Managed instruction block in {rules} names {root}, which holds no deployment; '
                             'pass --state')
        found.setdefault(_same(root), (root, []))[1].append(agent)
    if len(found) > 1:
        detail = '; '.join(f"{root} ({', '.join(agents)})" for root, agents in found.values())
        raise ValueError(f'Agents point to different deployments: {detail}. Pass --state to choose one.')
    return next(iter(found.values()))[0] if found else None


def default_state(home):
    if os.environ.get('ENGINEERING_INFRA_HOME'):
        return Path(os.environ['ENGINEERING_INFRA_HOME']).absolute()
    if SOURCE.name == 'runtime' and (SOURCE.parent / 'deployment.json').is_file():
        return SOURCE.parent.absolute()
    # From a checkout, follow the deployment the agents actually use; a leftover default state
    # must not shadow it. No managed block at all means a first install at the default location.
    return (deployed_state(home) or home / '.engineering-infrastructure').absolute()


def roots(args, home):
    adapter_roots = [(agent, pair[0]) for agent, pair in setup.adapters(home).items()]
    result = adapter_roots + [('codex-compatibility', setup.env_path(home, 'CODEX_HOME', '.codex') / 'skills'),
                              ('codex-bundled', setup.env_path(home, 'CODEX_HOME', '.codex') / 'skills/.system'),
                              ('antigravity-compatibility', home / '.gemini/antigravity/skills'),
                              ('gemini-cli', home / '.gemini/skills')]
    for project in args.project:
        result.extend(('project:' + path, project / path) for path in
                      ('.agents/skills', '.claude/skills', '.opencode/skills', '.gemini/skills'))
    result.extend(('explicit', root) for root in args.root)
    return result


def args_for_cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, help='Native machine-local state directory')
    parser.add_argument('--home', type=Path, default=Path.home(), help='Native user home or isolated fixture')
    parser.add_argument('--source', type=Path, default=SOURCE, help='Trusted distribution root')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('plan', 'apply'):
        command = commands.add_parser(name)
        command.add_argument('--agents', nargs='+', choices=AGENTS, required=True)
        command.add_argument('--migrate', action='store_true', help='Adopt matching copies/links and migrate EWK blocks')
        command.add_argument('--retire-alias', action='append', default=[])
        command.add_argument('--obsolete-rules', type=Path, help='Local JSON mapping adapter to exact obsolete rule line')
        command.add_argument('--adopt-fingerprints', type=Path, help='Local JSON mapping exact legacy paths to reviewed SHA-256')
    for name in ('inventory', 'doctor'):
        command = commands.add_parser(name)
        command.add_argument('--root', type=Path, action='append', default=[])
        command.add_argument('--project', type=Path, action='append', default=[])
    for name in ('resolve', 'discover'):
        command = commands.add_parser(name)
        command.add_argument('--agent', choices=AGENTS, required=True)
        command.add_argument('--need', action='append', required=True)
        command.add_argument('--native', action='append', default=[])
        command.add_argument('--available', action='append', default=[], help='IDs independently verified in this session')
        command.add_argument('--exclude', action='append', default=[], help='IDs ruled out after project constraint review')
        if name == 'discover':
            command.add_argument('--public-query', required=True, help='Public generic phrase suitable to send to GitHub')
    for name in ('verify', 'recover'):
        commands.add_parser(name)
    command = commands.add_parser('rollback')
    command.add_argument('transaction')
    command = commands.add_parser('sync-reference')
    command.add_argument('--check', action='store_true')
    command = commands.add_parser('stage')
    command.add_argument('id')
    command.add_argument('--repo', required=True)
    command.add_argument('--commit', required=True)
    command.add_argument('--skill-path', required=True)
    command.add_argument('--license-path', default='LICENSE')
    command.add_argument('--local', type=Path, help='An inert local copy of the same reviewed source')
    command = commands.add_parser('stage-reference')
    command.add_argument('id')
    command.add_argument('--activate', action='store_true', help='Apply only an exact pre-existing Markdown approval')
    command = commands.add_parser('activate', aliases=['update'])
    command.add_argument('id')
    command.add_argument('sha256')
    command = commands.add_parser('archive', aliases=['disable'])
    command.add_argument('id')
    command.add_argument('--reason', required=True, choices=('duplicate', 'replacement', 'regression', 'risk', 'obsolete'))
    command.add_argument('--dependents-cleared', action='store_true', help='Confirm no reverse dependencies or active tasks')
    command = commands.add_parser('feedback')
    command.add_argument('id')
    command.add_argument('result', choices=('DISCOVERABLE', 'INVOKED', 'VERIFIED', 'REGRESSION', 'GAP'))
    command.add_argument('--agent', choices=AGENTS, required=True)
    command.add_argument('--seconds', type=int)
    command.add_argument('--tokens', type=int)
    return parser


def exact_id(name):
    if not catalog.ID.fullmatch(name) or len(name) > 64:
        raise ValueError('Invalid Skill ID')
    return name


def pin_source(args):
    if not candidate.REPO.fullmatch(args.repo) or not candidate.SHA.fullmatch(args.commit) or any(
            part in {'.', '..'} for part in args.repo.split('/')):
        raise ValueError('Use owner/repository and an exact lowercase Git commit')
    source = f'https://github.com/{args.repo}/tree/{args.commit}/{candidate.source_path(args.skill_path)}'
    return source, candidate.source_path(args.license_path)


def stage_candidate(args, root):
    name = exact_id(args.id)
    if name in setup.CORE:
        raise ValueError('CORE Skills update only through a reviewed distribution')
    source, license_path = pin_source(args)
    if args.local:
        payload = files(args.local.absolute())
    else:
        payload = candidate.acquire(args.repo, args.commit, args.skill_path, args.license_path)
    sha = candidate.review_payload(name, payload)
    receipt = {'id': name, 'sha256': sha, 'source': source, 'license_path': license_path,
               'transport': 'local' if args.local else 'github', 'state': 'STAGED'}
    return save_stage(root, payload, receipt)


def save_stage(root, payload, receipt):
    path = root / 'staged' / receipt['id'] / receipt['sha256']
    check_path(path / 'receipt.json')
    if path.exists():
        existing = read_json(path / 'receipt.json')
        if existing != receipt or files(path / 'payload') != payload:
            raise ValueError('Staging conflict or drift')
        return receipt
    staged = {f'payload/{p}': value for p, value in payload.items()}
    staged['receipt.json'] = encode(receipt)
    transact(root, [(path, None, staged)])
    return receipt


def stage_reference(args, root, source, state, settings):
    row = catalog.catalog(source / 'adaptive-skills-kit').get(exact_id(args.id), {})
    pin = row.get('pin')
    if not pin or row['tier'] in {'CORE', 'DEPRECATED', 'QUARANTINED'}:
        raise ValueError('No eligible portable bundle pin for this reference')
    if args.activate and (pin['lane'] != 'markdown' or settings['mode'] != 'TRUSTED_AUTO'):
        raise ValueError('Reference activation requires a Markdown pin and TRUSTED_AUTO')
    source_url = f"{row['source']}/tree/{pin['commit']}"
    if row['source_path'] != '.':
        source_url += '/' + row['source_path']
    sha = digest(encode({name: item['sha256'] for name, item in pin['files'].items()}))
    receipt = {'id': args.id, 'sha256': sha, 'source': source_url, 'state': 'STAGED',
               'transport': 'pinned-reference', 'lane': pin['lane'],
               'license_path': pin['files'][pin['license_file']]['path']}
    if args.activate:
        if state is None:
            raise ValueError('Global bootstrap required before activation')
        candidate.require_approval(settings, receipt, state['adapters'], PLATFORM)
    cached = root / 'staged' / args.id / sha / 'payload'
    check_path(cached)
    payload = files(cached) if cached.is_dir() else candidate.acquire_pinned(pin)
    if {name: digest(data) for name, data in payload.items()} != {name: item['sha256'] for name, item in pin['files'].items()}:
        raise ValueError('Staged reference differs from the exact lock')
    if pin['lane'] == 'markdown':
        candidate.review_payload(args.id, payload)
    save_stage(root, payload, receipt)
    if args.activate:
        update = argparse.Namespace(command='activate', id=args.id, sha256=sha)
        return skill_change(update, root, state, settings)
    return receipt


def skill_change(args, root, state, settings):
    name = exact_id(args.id)
    if name in setup.CORE:
        raise ValueError('Protected CORE Skills cannot be replaced or archived here')
    issues = setup.verify(root, state)
    if issues:
        raise ValueError('Resolve deployment drift before modifying Skills: ' + ', '.join(issues))
    managed = state['managed']
    promoted = state.setdefault('promoted', {})
    current = managed.get(name)
    archive = args.command in ('archive', 'disable')
    if archive:
        if settings['mode'] != 'TRUSTED_AUTO' or not args.dependents_cleared or current is None:
            raise ValueError('Archiving needs a managed skill, TRUSTED_AUTO and a dependency/task review')
        managed.pop(name)
        promoted.pop(name, None)
        payload = None
    else:
        if not re.fullmatch('[a-f0-9]{64}', args.sha256):
            raise ValueError('Expected exact staged SHA-256')
        path = root / 'staged' / name / args.sha256
        check_path(path / 'receipt.json')
        receipt = read_json(path / 'receipt.json')
        if receipt.get('lane') == 'review-only':
            raise ValueError('Reference bundle is limited to isolated review')
        payload = files(path / 'payload')
        if receipt.get('id') != name or receipt.get('sha256') != args.sha256 or candidate.review_payload(name, payload) != args.sha256:
            raise ValueError('Candidate identity or staged content drift')
        approval = candidate.require_approval(settings, receipt, state['adapters'], PLATFORM)
        managed[name] = describe(payload)
        promoted[name] = {'id': name, 'tier': 'RECOMMENDED', 'capabilities': approval.get('capabilities', [name]),
                          'agents': approval['agents'], 'os': approval['os'], 'source': receipt['source'],
                          'dependencies': [], 'conflicts': []}
    targets = {root / 'active' / name}
    targets.update(Path(pair[0]) / name for pair in state['adapters'].values())
    changes = [(target, current, payload) for target in sorted(targets)]
    deployment = root / 'deployment.json'
    changes.append((deployment, signature(deployment), encode(state)))
    if archive:
        record = root / 'archive' / name / (current[1] + '.json')
        check_path(record)
        changes.append((record, signature(record), encode({'id': name, 'sha256': current[1], 'reason': args.reason,
                                                            'utc': datetime.now(timezone.utc).isoformat()})))
    txn = transact(root, changes)
    result = {'transaction': txn, 'id': name, 'state': 'ARCHIVED' if archive else 'ACTIVE'}
    if archive:
        result['reason'] = args.reason
    return result


def resolve(args, source, home, root):
    entries = {name: row for name, row in catalog.catalog(source / 'adaptive-skills-kit').items()
               if name not in args.exclude}
    state = setup.state_at(root)
    if state:
        entries.update({name: row for name, row in state.get('promoted', {}).items() if name not in args.exclude})
    directories = [setup.adapters(home)[args.agent][0]]
    if args.agent == 'opencode':
        directories.extend((home / '.agents/skills', home / '.claude/skills'))
    found = set(args.available)
    found.update(catalog.installed_names(directories))
    return catalog.resolve(args.need, entries, found, args.native, args.agent, PLATFORM)


def plan(args, source, root, home):
    return setup.deployment_plan(source, root, home, args.agents, args.migrate, args.retire_alias,
                                 read_json(args.obsolete_rules) if args.obsolete_rules else None,
                                 read_json(args.adopt_fingerprints) if args.adopt_fingerprints else None)


def run(args):
    home, source = args.home.absolute(), args.source.resolve()
    if args.command == 'sync-reference':
        path = source / 'adaptive-skills-kit'
        entries = catalog.catalog(path)
        lock = catalog.core_lock(source, path)
        generated = {path / 'skills-lock.json': encode(lock), path / 'skills reference.md': catalog.reference(entries, lock)}
        for dest, data in generated.items():
            if args.check:
                if dest.read_bytes().replace(b'\r\n', b'\n') != data:
                    raise ValueError(f'Generated catalog drift: {dest}')
            else:
                atomic(dest, data)
        output({'catalog': 'OK', 'entries': len(entries)})
        return 0
    root = args.state.absolute() if args.state else default_state(home)
    if args.command == 'plan':
        state, changes = plan(args, source, root, home)
        output({'revision': state['revision'], 'changes': [str(path) for path, before, after in changes if before != describe(after)]})
        return 0
    if args.command == 'inventory':
        output(catalog.inventory(roots(args, home)))
        return 0
    if args.command == 'resolve':
        output(resolve(args, source, home, root))
        return 0
    with locked(root):
        pending = root / 'pending.json'
        if pending.exists():
            if args.command != 'recover':
                raise ValueError('Interrupted transaction present. Run recover first.')
            recover(pending)
            output({'recovered': True})
        elif args.command == 'recover':
            output({'recovered': False})
        elif args.command == 'rollback':
            if not re.fullmatch('[a-f0-9]{32}', args.transaction):
                raise ValueError('Invalid transaction ID')
            journal = root / 'history' / (args.transaction + '.json')
            rollback(root, journal)
            output({'rolled_back': args.transaction})
        elif args.command == 'apply':
            state, changes = plan(args, source, root, home)
            issues = setup.verify(root, setup.state_at(root)) if (root / 'deployment.json').exists() else []
            if issues:
                raise ValueError('Resolve deployment drift: ' + ', '.join(issues))
            txn = transact(root, changes)
            output({'transaction': txn, 'revision': state['revision'], 'agents': list(state['adapters'])})
        else:
            return lifecycle(args, root, home, source)
    return 0


def lifecycle(args, root, home, source):
    state = setup.state_at(root)
    policy_path = root / 'policy.json'
    check_path(policy_path)
    settings = candidate.policy(policy_path)
    if args.command in ('verify', 'doctor'):
        issues = setup.verify(root, state)
        if state:
            for name, expected in state['managed'].items():
                if name not in setup.CORE and signature(root / 'active' / name) != expected:
                    issues.append(str(root / 'active' / name))
        result = {'integrity': 'DRIFT' if issues else 'OK', 'issues': issues, 'revision': state['revision'],
                  'agents': list(state['adapters']), 'mode': settings['mode'], 'discovery': 'Use platform runtime to verify'}
        if args.command == 'doctor':
            result['inventory'] = catalog.inventory(roots(args, home))
            result['history'] = [p.stem for p in sorted((root / 'history').glob('*.json'), key=lambda p: p.stat().st_mtime)]
        output(result)
        return bool(issues)
    if args.command == 'discover':
        decisions = resolve(args, source, home, root)
        missing = any(row['action'] == 'DISCOVER_OR_FALL_BACK' for row in decisions)
        found = []
        if missing and settings['mode'] != 'OFF':
            cache = root / 'search' / (digest(args.public_query.encode()) + '.json')
            check_path(cache)
            if cache.is_file() and time.time() - cache.stat().st_mtime < 3600:
                found = read_json(cache)
            else:
                found = candidate.public_search(args.public_query)
                atomic(cache, encode(found))
        output({'decisions': decisions, 'candidates': found, 'mode': settings['mode']})
    elif args.command == 'stage':
        if settings['mode'] == 'OFF':
            raise ValueError('Acquisition disabled by policy')
        output(stage_candidate(args, root))
    elif args.command == 'stage-reference':
        if settings['mode'] == 'OFF':
            raise ValueError('Acquisition disabled by policy')
        output(stage_reference(args, root, source, state, settings))
    elif args.command in ('activate', 'update', 'archive', 'disable'):
        output(skill_change(args, root, state, settings))
    elif args.command == 'feedback':
        name = exact_id(args.id)
        record = {key: getattr(args, key) for key in ('result', 'agent', 'seconds', 'tokens')}
        if any(record[key] is not None and record[key] < 0 for key in ('seconds', 'tokens')):
            raise ValueError('Feedback measurements must be nonnegative')
        record.update(id=name, utc=datetime.now(timezone.utc).isoformat(),
                      revision=state['revision'] if state else None,
                      version=state['managed'].get(name) if state else None)
        log = root / 'feedback.json'
        check_path(log)
        records = read_json(log) if log.exists() else []
        atomic(log, encode(records[-199:] + [record]))
        output(record)
    return 0


def main(argv=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        return run(args_for_cli().parse_args(argv))
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        print(f'engineering-infrastructure: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
