"""Global deployment across native agent discovery directories."""

import os
from pathlib import Path

from catalog import catalog, core_lock, reference
from store import check_path, describe, encode, files, fingerprint, link, read_json, signature


START, END = '<!-- engineering-infrastructure:begin -->', '<!-- engineering-infrastructure:end -->'
LEGACY_START, LEGACY_END = '<!-- ewk:begin -->', '<!-- ewk:end -->'
CORE = {'engineering-workflow', 'adaptive-skills', 'pr-authoring'}


def env_path(home, name, fallback):
    return Path(os.environ.get(name) or home / fallback).absolute()


def adapters(home):
    codex = env_path(home, 'CODEX_HOME', '.codex')
    claude = env_path(home, 'CLAUDE_CONFIG_DIR', '.claude')
    xdg = env_path(home, 'XDG_CONFIG_HOME', '.config')
    opencode = xdg / 'opencode'
    gemini = home / '.gemini'
    return {'codex': (home / '.agents/skills', codex / 'AGENTS.md'),
            'claude': (claude / 'skills', claude / 'CLAUDE.md'),
            'opencode': (opencode / 'skills', opencode / 'AGENTS.md'),
            'antigravity': (gemini / 'config/skills', gemini / 'GEMINI.md')}


def selected_adapters(home, agents):
    available = adapters(home)
    return {agent: available[agent] for agent in agents}


def state_at(root):
    path = root / 'deployment.json'
    check_path(path)
    if not path.exists():
        return None
    result = read_json(path)
    if result['schema'] != 1 or not CORE.issubset(result['managed']):
        raise ValueError('Unsupported deployment state')
    return result


def block(runtime):
    cli = runtime / 'tools/setup.py'
    return ('For substantive engineering work, load `engineering-workflow` and use its risk and evidence rules. '
            'Run its repository lifecycle inspection when starting or resuming substantive Git work. '
            'Use `adaptive-skills` when a required capability is missing or an existing one needs evaluation. '
            'For pull request work, load `pr-authoring` and follow upstream policy. Keep project-specific rules in the project.\n\n'
            f'Global maintenance entry point: `{cli}`. Use native Python and consult its `--help`, '
            '`BOOTSTRAP.md` or `OPTIMIZE.md` when maintaining the global environment.')


def patch_rules(raw, runtime, prior=None, migrate=False, obsolete_line=None):
    text = raw.decode('utf-8-sig')
    nl = '\r\n' if '\r\n' in text else '\n'
    current = extract_block(text)
    if prior is not None and (current is None or current.replace('\r\n', '\n') != prior):
        raise ValueError('Managed instruction block is missing or edited')
    if prior is None and current is not None:
        raise ValueError('Managed instruction block already exists outside this deployment')
    target = f'{START}\n{block(runtime)}\n{END}'
    legacy = extract_block(text, LEGACY_START, LEGACY_END)
    if current is not None:
        if legacy is not None:
            raise ValueError('Unexpected legacy EWK block beside the managed block')
        result = text.replace(current, target.replace('\n', nl), 1)
    elif legacy is not None:
        if not migrate:
            raise ValueError('Existing EWK block requires explicit migration')
        result = text.replace(legacy, target.replace('\n', nl), 1)
    else:
        sep = '' if not text else nl if text.endswith(nl) else nl * 2
        result = text + sep + target.replace('\n', nl) + nl
    if obsolete_line is not None:
        if not migrate or not obsolete_line or '\n' in obsolete_line or '\r' in obsolete_line:
            raise ValueError('Expected one exact legacy instruction line during migration')
        lines = result.splitlines(keepends=True)
        matches = [line for line in lines if line.rstrip('\r\n') == obsolete_line]
        if len(matches) != 1:
            raise ValueError('Exact migration line missing or repeated')
        lines.remove(matches[0])
        result = ''.join(lines)
    bom = b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b''
    return bom + result.encode(), target


def extract_block(text, start=START, end=END):
    if start not in text and end not in text:
        return None
    if text.count(start) != 1 or text.count(end) != 1 or text.index(start) >= text.index(end):
        raise ValueError('Invalid or duplicate managed instruction markers')
    return text[text.index(start):text.index(end) + len(end)]


def bundle(source):
    registry_dir = source / 'adaptive-skills-kit'
    entries = catalog(registry_dir)
    lock = core_lock(source, registry_dir)
    if set(lock['sha256']) != CORE:
        raise ValueError('Unexpected protected CORE set')
    reference_bytes = reference(entries, lock)
    if (read_json(registry_dir / 'skills-lock.json') != lock or
            (registry_dir / 'skills reference.md').read_bytes().replace(b'\r\n', b'\n') != reference_bytes):
        raise ValueError('Catalog lock or reference drift. Run sync-reference and review the diff.')
    skills = {name: files(source / entries[name]['source_path'], portable=True) for name in sorted(CORE)}
    shared = {}
    for name, payload in skills.items():
        shared.update({f"{entries[name]['source_path']}/{path}": data for path, data in payload.items()})
    for rel in ['BOOTSTRAP.md', 'OPTIMIZE.md', 'LICENSE', 'README.md', 'README.zh-CN.md',
                'CONTRIBUTING.md', 'AGENTS.md', 'CHANGELOG.md', 'tools/setup.py',
                'adaptive-skills-kit/README.md', 'engineering-workflow-kit/README.md',
                'engineering-workflow-kit/deploy/plan.example.json', 'engineering-workflow-kit/deploy/block-claude.md',
                'engineering-workflow-kit/deploy/block-codex.md', 'engineering-workflow-kit/tools/deploy.py',
                'engineering-workflow-kit/CHANGELOG.md', 'engineering-workflow-kit/reports/vnext.md',
                'engineering-workflow-kit/reports/evidence-and-decisions.md',
                'engineering-workflow-kit/reports/recovery.md',
                'engineering-workflow-kit/reports/validation-and-deployment.md',
                'pr-authoring-kit/README.md', 'adaptive-skills-kit/skills-registry.json',
                'adaptive-skills-kit/skills-lock.json', 'adaptive-skills-kit/skills reference.md']:
        check_path(source / rel)
        shared[rel] = (source / rel).read_bytes().replace(b'\r\n', b'\n')
    for rel in ('docs/diagrams', 'engineering-workflow-kit/tests', 'adaptive-skills-kit/tests'):
        for path, data in files(source / rel, portable=True).items():
            shared[f'{rel}/{path}'] = data
    return shared, skills


def migratable(path, name, desired, pin=None):
    canonical = path.resolve(strict=True)
    if not canonical.is_dir():
        return False
    legacy = canonical / '.ewk-manifest.json'
    if name == 'engineering-workflow' and legacy.is_file() and not link(legacy):
        from store import digest
        recorded = read_json(legacy)
        current = {p: digest(data) for p, data in files(canonical).items() if p != legacy.name}
        return recorded.get('name') == name and recorded.get('files') == current
    actual = fingerprint(files(canonical, portable=True))
    return actual == fingerprint(desired) or actual == pin


def deployment_plan(source, root, home, agent_names, migrate=False, retire=(), obsolete_rules=None, adoption=None):
    runtime = root / 'runtime'
    shared, skills = bundle(source)
    previous = state_at(root)
    revision = fingerprint(shared)
    targets = selected_adapters(home, agent_names)
    for parent, doc in targets.values():
        if root == parent or parent in root.parents or root in parent.parents or root in doc.parents:
            raise ValueError('State must be separate from discovery and instruction paths')
    paths = {name: [str(p) for p in pair] for name, pair in targets.items()}
    if previous and previous['adapters'] != paths:
        raise ValueError('Adapter set changed. Roll back the previous deployment before changing scope.')
    current_runtime = signature(runtime)
    expected_runtime = ['tree', previous['revision']] if previous else None
    if current_runtime != expected_runtime:
        raise ValueError('Shared runtime is unowned or has drifted')
    changes = [(runtime, current_runtime, shared)]
    managed = dict(previous['managed']) if previous else {}
    roots = list(dict.fromkeys(pair[0] for pair in targets.values()))
    adoption = adoption or {}
    if set(adoption).difference(str(parent / name) for parent in roots for name in CORE):
        raise ValueError('Adoption fingerprints must name exact selected CORE paths')
    for name, payload in skills.items():
        desired = describe(payload)
        for parent in roots:
            dest = parent / name
            existing = signature(dest)
            expected = managed.get(name)
            if existing != expected:
                if not (expected is None and existing is not None and migrate and
                        migratable(dest, name, payload, adoption.get(str(dest)))):
                    raise ValueError(f'Unowned or drifted skill: {dest}')
            changes.append((dest, existing, payload))
        managed[name] = desired
    if retire:
        if not migrate:
            raise ValueError('Retiring a compatibility alias requires --migrate')
        legacy_roots = {env_path(home, 'CODEX_HOME', '.codex') / 'skills', home / '.gemini/antigravity/skills'}
        for dest in map(Path, dict.fromkeys(retire)):
            dest = dest.absolute()
            if dest.parent not in legacy_roots or dest.name not in CORE or dest.parent in roots:
                raise ValueError(f'Not a supported legacy CORE alias: {dest}')
            if not os.path.lexists(dest):
                continue
            if not migratable(dest, dest.name, skills[dest.name]):
                raise ValueError(f'Refusing to retire an unverified alias: {dest}')
            changes.append((dest, signature(dest), None))
    docs = {}
    obsolete_rules = obsolete_rules or {}
    if set(obsolete_rules).difference(targets):
        raise ValueError('Rule migration must name a selected adapter')
    for path in dict.fromkeys(pair[1] for pair in targets.values()):
        check_path(path)
        if path.name == 'AGENTS.md' and path.with_name('AGENTS.override.md').exists():
            raise ValueError(f'Global Codex override must be reconciled explicitly: {path.parent}')
        old = signature(path)
        raw = path.read_bytes() if old else b''
        obsolete_line = next((obsolete_rules[agent] for agent in obsolete_rules if targets[agent][1] == path), None)
        requested, docs[str(path)] = patch_rules(raw, runtime, previous['docs'][str(path)] if previous else None,
                                                migrate, obsolete_line)
        changes.append((path, old, requested))
    state = {'schema': 1, 'revision': revision, 'adapters': paths, 'managed': managed,
             'promoted': previous.get('promoted', {}) if previous else {}, 'docs': docs}
    state_path = root / 'deployment.json'
    changes.append((state_path, signature(state_path), encode(state)))
    return state, changes


def verify(root, state):
    if state is None:
        raise ValueError('No global deployment found')
    issues = []
    expected = {root / 'runtime': ['tree', state['revision']]}
    for name, digest in state['managed'].items():
        expected.update({Path(pair[0]) / name: digest for pair in state['adapters'].values()})
    for path, sig in expected.items():
        check_path(path, include_leaf=False)
        if signature(path) != sig:
            issues.append(str(path))
    for name, value in state['docs'].items():
        path = Path(name)
        check_path(path)
        if not path.is_file() or extract_block(path.read_text(encoding='utf-8-sig')) != value:
            issues.append(name)
    return issues
