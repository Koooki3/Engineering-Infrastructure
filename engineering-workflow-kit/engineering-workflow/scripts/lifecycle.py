#!/usr/bin/env python3
"""Inspect, integrate and verify a local deployment in an owned Git worktree."""

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import time
import uuid

sys.dont_write_bytecode = True
from ewk import kill_tree, state_id


KEY = re.compile(r'[a-z0-9][a-z0-9-]{0,62}\Z')
REF = re.compile(r'(?:refs/(?:heads|remotes|tags)/[^\s~^:\[\\*?]+|[0-9a-f]{40}|[0-9a-f]{64})\Z')
EVENTS = ('start', 'resume', 'integrate', 'deploy', 'deliver', 'close', 'maintenance')


def command(cwd, args, timeout=60, env=None, allowed=(0,)):
    if timeout < 1 or timeout > 3600:
        raise ValueError('Timeout must be between 1 and 3600 seconds')
    with subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                          env=env, start_new_session=os.name != 'nt',
                          creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0) as proc:
        try:
            out, err = proc.communicate(timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            kill_tree(proc)
            proc.communicate(timeout=5)
            if isinstance(exc, KeyboardInterrupt):
                raise
            raise ValueError(f'Command timed out: {Path(args[0]).name}')
        if proc.returncode not in allowed:
            # Project output may contain credentials or private data. Keep errors brief.
            action = args[1] if args[0] == 'git' else 'project command'
            raise ValueError(f'{Path(args[0]).name} exited {proc.returncode}: {action}')
        return out


def git(cwd, *args, timeout=60):
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GIT_OPTIONAL_LOCKS='0')
    return command(cwd, ['git', *args], timeout, env)


def string(data):
    return data.decode('utf-8', errors='surrogateescape').strip()


def mapping(path, default=None):
    no_links(path)
    if not path.exists():
        return default
    return json.loads(path.read_bytes())


def save(path, data):
    no_links(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.ewk-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, indent=2, ensure_ascii=True, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def no_links(path):
    for node in (*reversed(path.parents), path):
        if os.path.lexists(node):
            info = node.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 1024:
                raise ValueError(f'Linked path is outside managed ownership: {node}')


@contextmanager
def locked(state):
    no_links(state / 'writer.lock')
    state.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (state / 'writer.lock').open('a+b') as stream:
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def status(cwd, ignored=False):
    options = ['--ignored=matching'] if ignored else []
    return git(cwd, 'status', '--porcelain=v1', '-z', '--untracked-files=all', *options).split(b'\0')[:-1]


def worktrees(cwd):
    blocks = git(cwd, 'worktree', 'list', '--porcelain', '-z').split(b'\0\0')
    return [dict(string(field).partition(' ')[::2] for field in block.split(b'\0') if field) for block in blocks if block]


def submodule_status(cwd):
    if not any(entry.startswith(b'160000 ') for entry in git(cwd, 'ls-files', '--stage', '-z').split(b'\0')):
        return []
    return string(git(cwd, 'submodule', 'status', '--recursive')).splitlines()


def optional(cwd, *args):
    try:
        return string(git(cwd, *args))
    except ValueError:
        return None


def topology(cwd, state, event):
    head = optional(cwd, 'rev-parse', '--verify', 'HEAD')
    branch = optional(cwd, 'symbolic-ref', '--quiet', '--short', 'HEAD')
    tracking = optional(cwd, 'rev-parse', '--symbolic-full-name', '@{upstream}')
    counts = None
    if tracking:
        counts = tuple(map(int, git(cwd, 'rev-list', '--left-right', '--count', 'HEAD...' + tracking).split()))
    remotes = string(git(cwd, 'remote')).splitlines()
    snapshots = mapping(state / 'fetch.json', {})
    return {'event': event, 'head': head, 'branch': branch, 'tracking': tracking,
            'ahead_behind': counts, 'merge_base': optional(cwd, 'merge-base', 'HEAD', tracking) if tracking else None,
            'remotes': {name: {'default': optional(cwd, 'symbolic-ref', 'refs/remotes/' + name + '/HEAD'),
                               'fetched': snapshots.get(name)} for name in remotes},
            'refs': string(git(cwd, 'for-each-ref', '--format=%(objectname)%09%(refname)%09%(upstream)',
                               'refs/heads', 'refs/remotes')).splitlines(),
            'dirty_entries': len(status(cwd)), 'stash_count': len(git(cwd, 'stash', 'list', '--format=%H').splitlines()),
            'submodules': submodule_status(cwd),
            'worktrees': worktrees(cwd),
            'native_entrypoints': [name for name in ('Makefile', 'justfile', 'package.json', 'pyproject.toml',
                                                     'Cargo.toml', 'go.mod', 'CMakeLists.txt', 'tools/setup.py')
                                   if (cwd / name).is_file()],
            'native_contract': (state / 'contract.json').is_file(), 'deployment_pending': (state / 'pending.json').exists(),
            'checkpoints': sorted(item.stem for item in (state / 'checkpoints').glob('*.json'))[:10]
            if event == 'resume' else [],
            'next': {'start': 'establish_baseline', 'resume': 'restore_checkpoint',
                     'integrate': 'refresh_relevant_remotes_then_plan', 'deploy': 'verify_candidate_then_probe',
                     'deliver': 'check_upstream_and_pr_boundary', 'close': 'review_owned_cleanup_and_handoff',
                     'maintenance': 'audit_drift_and_owned_state'}[event]}


def fetch(cwd, state, remote, age):
    if remote.startswith('-') or remote not in string(git(cwd, 'remote')).splitlines():
        raise ValueError('Select an existing Git remote by name')
    if not 0 <= age <= 86400:
        raise ValueError('Fetch cache max age must be between 0 and 86400 seconds')
    path = state / 'fetch.json'
    records = mapping(path, {})
    last = records.get(remote)
    if last and 0 <= time.time() - last['utc_epoch'] < age:
        return {**last, 'cached': True}
    git(cwd, 'check-ref-format', f'refs/remotes/{remote}/HEAD')
    git(cwd, 'fetch', '--no-prune', '--no-tags', '--no-recurse-submodules', remote,
        f'+refs/heads/*:refs/remotes/{remote}/*', timeout=90)
    result = {'remote': remote, 'utc_epoch': time.time()}
    records[remote] = result
    save(path, records)
    return {**result, 'cached': False}


def commit(cwd, ref):
    if not REF.fullmatch(ref):
        raise ValueError(f'Use a full ref or exact SHA: {ref}')
    return string(git(cwd, 'rev-parse', '--verify', ref + '^{commit}'))


def compare(cwd, base, tip):
    left, right = commit(cwd, base), commit(cwd, tip)
    difference = left + '...' + right
    return {'base': left, 'tip': right, 'merge_base': optional(cwd, 'merge-base', left, right),
            'ahead_behind': list(map(int, git(cwd, 'rev-list', '--left-right', '--count', difference).split())),
            'patches': string(git(cwd, 'cherry', left, right)).splitlines()}


def fast_forward(cwd, expected, target):
    current = string(git(cwd, 'rev-parse', 'HEAD'))
    target_sha = commit(cwd, target)
    branch = optional(cwd, 'symbolic-ref', '--quiet', 'HEAD')
    if branch is None or current != expected or status(cwd):
        raise ValueError('Fast-forward requires the agreed attached HEAD and a clean worktree')
    git(cwd, 'merge-base', '--is-ancestor', current, target_sha)
    git(cwd, 'merge', '--ff-only', '--no-overwrite-ignore', target_sha)
    return {'branch': branch, 'previous': current, 'head': target_sha}


def candidate(cwd, base, includes, excludes):
    head = commit(cwd, base)
    sources = []
    pins = {base: head}
    for ref, boundary in includes:
        tip, cut = commit(cwd, ref), commit(cwd, boundary)
        pins.update({ref: tip, boundary: cut})
        git(cwd, 'merge-base', '--is-ancestor', cut, tip)
        history = cut + '..' + tip
        if git(cwd, 'rev-list', '--merges', history).strip():
            raise ValueError('Integration input contains merge commits. Select explicit linear ranges.')
        sources.append({'ref': ref, 'head': tip, 'boundary': cut,
                        'commits': string(git(cwd, 'rev-list', '--reverse', history)).splitlines()})
    if set(ref for ref, _ in excludes).intersection(ref for ref, _ in includes):
        raise ValueError('The same ref cannot be both included and excluded')
    return {'schema': 1, 'base': base, 'base_sha': head, 'pins': pins, 'sources': sources,
            'excluded': [{'ref': ref, 'reason': reason} for ref, reason in excludes]}


def validate_pins(cwd, manifest):
    for ref, sha in manifest['pins'].items():
        if commit(cwd, ref) != sha:
            raise ValueError(f'Integration input moved: {ref}. Re-plan.')


def freshness(cwd, receipt):
    tracked = {ref: sha for ref, sha in receipt.get('pins', {}).items() if ref.startswith('refs/')}
    changed = [ref for ref, sha in tracked.items() if optional(cwd, 'rev-parse', '--verify', ref + '^{commit}') != sha]
    return {'freshness': 'STALE_INPUTS' if changed else 'CURRENT' if tracked else 'UNTRACKED',
            'changed_inputs': changed}


def empty_path(path):
    no_links(path)
    if os.path.lexists(path) or not path.parent.is_dir():
        raise ValueError('Worktree destination must be absent under an existing directory')


def owned_tree(cwd, task, require_ready=True):
    tree = Path(task['path'])
    no_links(tree)
    entry = next((entry for entry in worktrees(cwd) if Path(entry['worktree']) == tree), None)
    if not entry or 'locked' in entry or 'prunable' in entry or 'detached' not in entry:
        raise ValueError('Managed detached worktree is unavailable, active in Git, or changed')
    if require_ready and (task['phase'] != 'READY' or entry['HEAD'] != task['candidate_sha']):
        raise ValueError('Worktree does not match a ready integration candidate')
    return tree, entry['HEAD']


def integrate(cwd, record, path, manifest, owner):
    if record.exists():
        raise ValueError('Task ID already has a record')
    empty_path(path)
    if any(Path(entry['worktree']) in path.parents for entry in worktrees(cwd)):
        raise ValueError('Choose a destination outside existing worktrees')
    task = {**manifest, 'path': str(path), 'owner': owner, 'phase': 'ASSEMBLING', 'applied': [], 'skipped': []}
    save(record, task)
    try:
        git(cwd, 'worktree', 'add', '--detach', '--', str(path), manifest['base_sha'])
        for source in manifest['sources']:
            for sha in source['commits']:
                current = commit(path, string(git(path, 'rev-parse', 'HEAD')))
                equivalence = string(git(path, 'cherry', current, sha, sha + '^')).splitlines()
                if not equivalence or equivalence[0].startswith('-'):
                    task['skipped'].append(sha)
                else:
                    git(path, 'cherry-pick', '-x', sha)
                    task['applied'].append({'source_sha': sha, 'candidate_sha': string(git(path, 'rev-parse', 'HEAD'))})
                save(record, task)
        validate_pins(cwd, manifest)
        task['candidate_sha'] = string(git(path, 'rev-parse', 'HEAD'))
        task['submodules'] = submodule_status(path)
        if status(path):
            raise ValueError('Candidate is dirty after integration')
        task['phase'] = 'READY'
    except (OSError, ValueError, KeyboardInterrupt):
        task['phase'] = 'BLOCKED'
        save(record, task)
        raise
    save(record, task)
    return task


def digest(path):
    no_links(path)
    if not path.is_file():
        raise ValueError(f'Missing regular artifact: {path.name}')
    with path.open('rb') as stream:
        sha = hashlib.sha256()
        for chunk in iter(lambda: stream.read(131072), b''):
            sha.update(chunk)
    return sha.hexdigest()


def project_contract(state):
    contract = mapping(state / 'contract.json')
    if contract is None:
        return None
    return validate_contract(contract)


def validate_contract(contract):
    expected = {'schema', 'build', 'test', 'install', 'probe', 'stop', 'artifact'}
    if (not isinstance(contract, dict) or
            (set(contract) - expected - {'timeout', 'verification_files', 'verification_env'}) or
            not expected.issubset(contract)):
        raise ValueError('Invalid local deployment contract')
    if contract['schema'] != 1:
        raise ValueError('Unsupported deployment contract')
    for key in ('build', 'test', 'install', 'probe', 'stop'):
        argv = contract[key]
        if not isinstance(argv, list) or not argv or any(not isinstance(value, str) or not value for value in argv):
            raise ValueError(f'Expected nonempty argv for {key}')
        if not Path(argv[0]).is_absolute() or not Path(argv[0]).is_file():
            raise ValueError(f'Expected a trusted absolute executable for {key}')
    path = Path(contract['artifact'])
    if path.is_absolute() or path.drive or not path.parts or '..' in path.parts or ':' in contract['artifact']:
        raise ValueError('Artifact path must be relative to the candidate worktree')
    for key in ('verification_files', 'verification_env'):
        values = contract.get(key, [])
        if not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError(f'Expected a list of nonempty values in {key}')
    timeout = contract.get('timeout', 120)
    if type(timeout) is not int or not 1 <= timeout <= 3600:
        raise ValueError('Invalid contract timeout')
    return contract


def discover_contract(cwd, state):
    paths = string(git(cwd, 'ls-files', '--', 'README*', 'AGENTS.md', 'pyproject.toml', 'package.json',
                       'Makefile', 'justfile', 'CMakeLists.txt', '.github/workflows', 'scripts', 'tools')).splitlines()
    evidence = [name for name in paths if
                name.startswith(('README', '.github/workflows/')) or '/' not in name
                or re.search(r'build|test|release|install|deploy|health|probe|stop', name, re.I)]
    return {'status': 'CONFIGURED' if project_contract(state) else 'DISCOVERY',
            'tracked_entrypoints': evidence[:40],
            'required': ['artifact', 'build', 'test', 'install', 'probe', 'stop'],
            'next': 'Inspect tracked entrypoints and review the actual target, native argv and rollback.'}


def register_contract(cwd, state, task, source, apply):
    contract = validate_contract(mapping(source))
    existing = project_contract(state)
    if existing and existing != contract:
        raise ValueError('An existing native deployment contract needs explicit reconciliation')
    if (state / 'pending.json').exists():
        raise ValueError('Recover the pending deployment first')
    tree, sha = owned_tree(cwd, task)
    validate_pins(cwd, task)
    if status(tree):
        raise ValueError('Review the contract against a clean integration candidate')
    inputs = verification_inputs(tree, contract, submodule_status(tree))
    if apply and not existing:
        probe(contract, tree)
        save(state / 'contract.json', contract)
    return {'status': 'CONFIGURED' if existing or apply else 'PREVIEW',
            'candidate_sha': sha, 'verification_inputs': inputs}


def execute(contract, stage, cwd, receipt=None):
    env = {key: value for key, value in os.environ.items() if not key.startswith('EWK_DEPLOY_')}
    if receipt:
        env.update(EWK_DEPLOY_SHA=receipt['sha'], EWK_DEPLOY_ARTIFACT=receipt['artifact'],
                   EWK_DEPLOY_SHA256=receipt['sha256'])
    return command(cwd, contract[stage], contract.get('timeout', 120), env)


def probe(contract, cwd, receipt=None):
    # A probe must read the running product; passing expected identifiers would permit an echo.
    observed = json.loads(execute(contract, 'probe', cwd))
    if not isinstance(observed, dict):
        raise ValueError('Invalid runtime probe report')
    if receipt is None:
        if observed.get('active') is not False:
            raise ValueError('Unmanaged runtime is active')
    elif (observed.get('active') is not True or observed.get('healthy') is not True
          or observed.get('sha') != receipt['sha'] or observed.get('sha256') != receipt['sha256']
          or not isinstance(observed.get('instance'), str) or not observed['instance'].strip()):
        raise ValueError('Runtime health or deployed version drift')
    return observed


def store_artifact(state, artifact, checksum):
    ext = artifact.suffix
    if ext and not re.fullmatch(r'\.[A-Za-z0-9_-]{1,20}', ext):
        raise ValueError('Invalid artifact extension')
    dest = state / 'artifacts' / (checksum + ext)
    no_links(dest)
    if not dest.exists():
        import shutil
        dest.parent.mkdir(exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=dest.parent, prefix='.artifact-')
        try:
            with os.fdopen(fd, 'wb') as stream, artifact.open('rb') as source:
                shutil.copyfileobj(source, stream)
            if digest(Path(tmp)) != checksum:
                raise ValueError('Artifact changed while snapshotting')
            os.replace(tmp, dest)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    if digest(dest) != checksum:
        raise ValueError('Stored artifact drift')
    return str(dest)


def revert(cwd, state, pending):
    stable = pending['stable']
    contract = pending['contract']
    if stable is None:
        execute(contract, 'stop', cwd)
    else:
        verify_stored_artifact(state, stable)
        execute(contract, 'install', cwd, stable)
    observed = probe(contract, cwd, stable)
    if stable is not None:
        save(state / 'stable.json', {**stable, 'observed': observed})
    elif (state / 'stable.json').exists():
        (state / 'stable.json').unlink()
    (state / 'pending.json').unlink()
    return observed


def contract_signature(contract):
    return hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()


def verification_inputs(cwd, contract, submodules):
    paths = {Path(item) for item in contract.get('verification_files', [])}
    for stage in ('build', 'test', 'install', 'probe', 'stop'):
        argv = contract[stage]
        paths.add(Path(argv[0]))
        for token in argv[1:]:
            path = Path(token)
            if Path(path).suffix.lower() in {'.py', '.ps1', '.sh', '.js', '.mjs', '.bat', '.cmd'}:
                if (cwd / path).is_file():
                    paths.add(path)
    facts = {'files': {str(path): digest((cwd / path).resolve(strict=True)) for path in paths},
             'env': {key: os.environ.get(key) for key in contract.get('verification_env', [])},
             'git': string(git(cwd, '--version')), 'python': sys.version, 'submodules': submodules,
             'contract': contract_signature(contract)}
    return contract_signature(facts)


def version_record(state, receipt):
    if 'record_id' in receipt:
        if not re.fullmatch(r'[a-f0-9]{32}', receipt['record_id']):
            raise ValueError('Malformed deployment record identity')
        return state / 'versions' / (receipt['record_id'] + '.json')
    if not re.fullmatch(r'(?:[a-f0-9]{40}|[a-f0-9]{64})', receipt['sha']) or not re.fullmatch(r'[a-f0-9]{64}', receipt['sha256']):
        raise ValueError('Malformed deployment version identity')
    return state / 'versions' / (receipt['sha'] + '-' + receipt['sha256'] + '.json')


def verify_stored_artifact(state, receipt):
    path = Path(receipt['artifact'])
    if path.parent != state / 'artifacts' or digest(path) != receipt['sha256']:
        raise ValueError('Verified recovery artifact drift')


def rollback(cwd, state):
    pending_path = state / 'pending.json'
    if pending_path.exists():
        raise ValueError('Recover the pending deployment first')
    current = mapping(state / 'stable.json')
    if current is None or current.get('previous') is None:
        raise ValueError('No previous verified deployment')
    contract = project_contract(state)
    previous = mapping(version_record(state, current['previous']))
    if contract is None or previous is None or any(
            receipt['contract_signature'] != contract_signature(contract) for receipt in (current, previous)):
        raise ValueError('Previous deployment contract is unavailable or changed')
    probe(contract, cwd, current)
    pending = {'schema': 1, 'stable': previous, 'candidate': current, 'contract': contract, 'cwd': str(cwd)}
    save(pending_path, pending)
    return revert(cwd, state, pending)


def deploy(cwd, state, task):
    contract = project_contract(state)
    if contract is None:
        return {'status': 'NOT_APPLICABLE', 'reason': 'No authorized local project contract'}
    tree, sha = owned_tree(cwd, task)
    validate_pins(cwd, task)
    pending_path = state / 'pending.json'
    if pending_path.exists():
        raise ValueError('Recover the pending deployment first')
    stable_path = state / 'stable.json'
    stable = mapping(stable_path)
    if stable is not None:
        if stable['contract_signature'] != contract_signature(contract):
            raise ValueError('Existing deployment contract changed; reconcile it explicitly')
        verify_stored_artifact(state, stable)
    observed = probe(contract, tree, stable)
    artifact = tree / contract['artifact']
    no_links(artifact)
    submodules = submodule_status(tree)
    before = state_id(str(tree), exclude=(str(artifact),))
    if any(line[:1] in {'-', '+', 'U'} for line in submodules) or before != sha:
        raise ValueError('Initialize the pinned submodules and use a clean candidate')
    inputs = verification_inputs(tree, contract, submodules)
    if stable and stable['sha'] == sha and stable.get('build_inputs') == inputs:
        validate_pins(cwd, task)
        action = 'REUSED'
        if stable.get('pins') != task['pins']:
            stable = {**stable, 'pins': task['pins'], 'record_id': uuid.uuid4().hex,
                      'reconciled_utc_epoch': time.time(), 'observed': observed}
            save(version_record(state, stable), stable)
            save(stable_path, stable)
            action = 'RECONCILED'
        return {'status': 'VERIFIED', 'action': action, **stable, 'observed': observed, **freshness(cwd, stable)}
    if artifact.exists():
        raise ValueError('Use a fresh artifact path or a fresh integration worktree')
    execute(contract, 'build', tree)
    checksum = digest(artifact)
    execute(contract, 'test', tree)
    if (checksum != digest(artifact) or state_id(str(tree), exclude=(str(artifact),)) != before
            or verification_inputs(tree, contract, submodule_status(tree)) != inputs):
        raise ValueError('Candidate or artifact drifted during verification')
    validate_pins(cwd, task)
    receipt = {'sha': sha, 'artifact': store_artifact(state, artifact, checksum), 'sha256': checksum, 'pins': task['pins'],
               'verified_state': before, 'submodules': submodules, 'git': string(git(tree, '--version')),
               'python': sys.version.split()[0], 'utc_epoch': time.time(), 'contract_signature': contract_signature(contract),
               'record_id': uuid.uuid4().hex, 'build_inputs': inputs,
               'previous': {key: stable[key] for key in ('sha', 'sha256', 'record_id') if key in stable}
               if stable else None}
    save(pending_path, {'schema': 1, 'stable': stable, 'candidate': receipt, 'contract': contract, 'cwd': str(tree)})
    try:
        execute(contract, 'install', tree, receipt)
        observed = probe(contract, tree, receipt)
        validate_pins(cwd, task)
        if state_id(str(tree), exclude=(str(artifact),)) != before:
            raise ValueError('Candidate changed during installation')
        if (digest(Path(receipt['artifact'])) != checksum
                or verification_inputs(tree, contract, submodule_status(tree)) != inputs):
            raise ValueError('Deployment artifact or verification inputs drifted')
        receipt['observed'] = observed
        save(version_record(state, receipt), receipt)
        save(stable_path, receipt)
    except (OSError, ValueError, KeyboardInterrupt):
        revert(tree, state, mapping(pending_path))
        raise
    pending_path.unlink()
    return {'status': 'VERIFIED', **receipt}


def cleanup(cwd, state, task, name, released, apply):
    if task['phase'] == 'ARCHIVED':
        return {'archive': task['archive'], 'sha': task['candidate_sha'], 'applied': False}
    tree, sha = owned_tree(cwd, task, require_ready=False)
    if not released or task['phase'] not in {'READY', 'CLOSED'} or status(tree, ignored=True):
        raise ValueError('Cleanup needs a ready, released worktree with no tracked, untracked or ignored files')
    if (state / 'pending.json').exists():
        raise ValueError('A pending deployment may still depend on this worktree')
    if sha != task['candidate_sha']:
        raise ValueError('Worktree advanced outside the recorded candidate')
    archive = 'refs/ewk/archive/' + name
    output = {'worktree': str(tree), 'archive': archive, 'sha': sha, 'applied': apply}
    if apply:
        previous = optional(cwd, 'rev-parse', '--verify', archive)
        if previous is None:
            git(cwd, 'update-ref', archive, sha, '0' * len(sha))
        elif previous != sha:
            raise ValueError('Archive ref has a different SHA')
        git(cwd, 'worktree', 'remove', '--', str(tree))
        save(state / 'tasks' / (name + '.json'), {**task, 'phase': 'ARCHIVED', 'archive': archive})
    return output


def checkpoint(cwd, state, name, source):
    path = state / 'checkpoints' / (name + '.json')
    if source is None:
        data = mapping(path)
        if data is None:
            raise ValueError('Checkpoint not found')
        return {**data, 'head_drift': data['head'] != optional(cwd, 'rev-parse', '--verify', 'HEAD')}
    if source.stat().st_size > 32_768:
        raise ValueError('Keep checkpoints under 32 KiB')
    data = mapping(source)
    fields = ('owner', 'goal', 'constraints', 'acceptance', 'decisions', 'evidence', 'next')
    if not isinstance(data, dict) or any(not data.get(field) for field in fields):
        raise ValueError('Checkpoint needs owner, goal, constraints, acceptance, decisions, evidence and next')
    data = {key: data[key] for key in (*fields, 'blockers', 'baseline') if key in data}
    data.update(schema=1, head=optional(cwd, 'rev-parse', '--verify', 'HEAD'), utc_epoch=time.time())
    save(path, data)
    return data


def knowledge(cwd, state, key, source, archive, evidence, require):
    path = state / 'knowledge' / (key + '.json')
    old = mapping(path)
    if source is None:
        if old is None:
            raise ValueError('Project knowledge item not found')
        if evidence is not None:
            if archive or not require or old['status'] == 'ARCHIVED':
                raise ValueError('Verification requires a current item and named evidence checks')
            command(cwd, [sys.executable, '-B', str(Path(__file__).with_name('ewk.py')), 'check',
                          '--evidence', str(evidence.absolute()), '--require', require])
            old.update(status='VERIFIED', verified_state=state_id(str(cwd)), checks=require)
            save(path, old)
        if archive and old['status'] != 'ARCHIVED':
            old['status'] = 'ARCHIVED'
            save(path, old)
        return old
    if archive or evidence is not None or source.stat().st_size > 16_384:
        raise ValueError('Provide a short knowledge record or archive an existing one')
    value = mapping(source)
    fields = ('observation', 'evidence', 'root_cause', 'invariant', 'mechanism', 'verification')
    if not isinstance(value, dict) or any(not isinstance(value.get(key), str) or not value[key].strip() for key in fields):
        raise ValueError('Knowledge records require evidence, root cause, invariant, mechanism and verification')
    data = {key: value[key].strip() for key in fields}
    token = hashlib.sha256(data['invariant'].casefold().encode()).hexdigest()
    for item in path.parent.glob('*.json'):
        if item != path and mapping(item)['fingerprint'] == token:
            raise ValueError(f'Invariant already recorded in {item.stem}; reconcile that item')
    result = {**data, 'schema': 1, 'scope': 'PROJECT', 'status': 'PROPOSED', 'fingerprint': token}
    if old and old != result:
        revision = hashlib.sha256(json.dumps(old, sort_keys=True).encode()).hexdigest()
        save(state / 'knowledge-history' / key / (revision + '.json'), old)
    save(path, result)
    return result


def delivery_gate(cwd, state, args, task):
    checks = dict.fromkeys(('baseline', 'inputs', 'runtime', 'worktree', 'lesson'), 'NOT_APPLICABLE')
    tree = None
    if args.base:
        try:
            git(cwd, 'merge-base', '--is-ancestor', commit(cwd, args.base), 'HEAD')
            checks['baseline'] = 'PASS'
        except ValueError:
            checks['baseline'] = 'BLOCKED'
    if task:
        try:
            validate_pins(cwd, task)
            accounted = set(task['skipped']) | {item['source_sha'] for item in task['applied']}
            complete = all(set(item['commits']) <= accounted for item in task['sources'])
            if task['phase'] == 'READY':
                tree, sha = owned_tree(cwd, task)
                contract = project_contract(state)
                allowed_output = (str(tree / contract['artifact']),) if contract else ()
                complete = complete and state_id(str(tree), exclude=allowed_output) == sha
            checks['inputs'] = 'PASS' if complete and task['phase'] in {'READY', 'ARCHIVED'} else 'BLOCKED'
        except (KeyError, ValueError):
            checks['inputs'] = 'BLOCKED'
        if args.close:
            checks['worktree'] = 'PASS' if task['phase'] == 'ARCHIVED' else 'PENDING'
    if args.runtime:
        try:
            stable = mapping(state / 'stable.json')
            observed = runtime_status(cwd, state)
            match = not task or (stable and stable['sha'] == task['candidate_sha'] and stable['pins'] == task['pins'])
            if match and tree:
                contract = project_contract(state)
                match = stable.get('build_inputs') == verification_inputs(tree, contract, submodule_status(tree))
            checks['runtime'] = 'PASS' if observed.get('freshness') == 'CURRENT' and match else 'BLOCKED'
        except (OSError, ValueError):
            checks['runtime'] = 'BLOCKED'
    if args.lesson:
        if not KEY.fullmatch(args.lesson):
            raise ValueError('Invalid knowledge ID')
        lesson = mapping(state / 'knowledge' / (args.lesson + '.json'))
        checks['lesson'] = ('PASS' if lesson and lesson['status'] == 'VERIFIED'
                            and lesson.get('verified_state') == state_id(str(cwd)) else 'PENDING')
    return {'status': 'BLOCKED' if {'BLOCKED', 'PENDING'}.intersection(checks.values()) else
            'PASS' if 'PASS' in checks.values() else 'NOT_APPLICABLE', 'checks': checks}


def runtime_status(cwd, state):
    contract = project_contract(state)
    stable = mapping(state / 'stable.json')
    if (state / 'pending.json').exists():
        raise ValueError('Deployment recovery pending')
    if stable:
        if not contract or stable['contract_signature'] != contract_signature(contract):
            raise ValueError('Deployment contract drift')
        verify_stored_artifact(state, stable)
    result = probe(contract, cwd, stable) if contract else {'status': 'NOT_APPLICABLE'}
    if stable:
        result.update(freshness(cwd, stable))
    return result


def promotion_plan(cwd, state, name, summary):
    lesson = mapping(state / 'knowledge' / (name + '.json'))
    if (not lesson or lesson['status'] != 'VERIFIED' or
            lesson.get('verified_state') != state_id(str(cwd))):
        raise ValueError('Knowledge must have current verification before promotion review')
    if not summary.strip() or len(summary) > 400 or '\n' in summary:
        raise ValueError('Provide one concise, sanitized rule for review')
    return {'status': 'REVIEW_REQUIRED', 'scope': 'GLOBAL_PROPOSAL', 'rule': summary.strip(),
            'fingerprint': hashlib.sha256(summary.strip().casefold().encode()).hexdigest()}


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--repo', type=Path, default=Path.cwd())
    subs = cli.add_subparsers(dest='op', required=True)
    scan = subs.add_parser('inspect')
    scan.add_argument('--event', choices=EVENTS, default='start')
    contract = subs.add_parser('contract')
    contract.add_argument('--task')
    contract.add_argument('--from-json', type=Path)
    contract.add_argument('--apply', action='store_true')
    gate = subs.add_parser('gate')
    gate.add_argument('--base')
    gate.add_argument('--task')
    gate.add_argument('--runtime', action='store_true')
    gate.add_argument('--close', action='store_true')
    gate.add_argument('--lesson')
    sync = subs.add_parser('fetch')
    sync.add_argument('remote')
    sync.add_argument('--max-age', type=int, default=900)
    comparison = subs.add_parser('compare')
    comparison.add_argument('base')
    comparison.add_argument('tip')
    ff = subs.add_parser('fast-forward')
    ff.add_argument('--expected', required=True, help='Exact currently checked out SHA')
    ff.add_argument('--target', required=True)
    for name in ('plan', 'integrate'):
        cmd = subs.add_parser(name)
        cmd.add_argument('--base', required=True)
        cmd.add_argument('--include', nargs=2, action='append', default=[], metavar=('REF', 'BOUNDARY'))
        cmd.add_argument('--exclude', nargs=2, action='append', default=[], metavar=('REF', 'REASON'))
        if name == 'integrate':
            cmd.add_argument('task')
            cmd.add_argument('--path', type=Path, required=True)
            cmd.add_argument('--owner', required=True)
    for name in ('deploy', 'cleanup', 'checkpoint', 'knowledge'):
        cmd = subs.add_parser(name)
        cmd.add_argument('task')
        if name == 'cleanup':
            cmd.add_argument('--released', action='store_true')
            cmd.add_argument('--apply', action='store_true')
        if name in ('checkpoint', 'knowledge'):
            cmd.add_argument('--from-json', type=Path)
        if name == 'knowledge':
            cmd.add_argument('--archive', action='store_true')
            cmd.add_argument('--evidence', type=Path)
            cmd.add_argument('--require')
    subs.add_parser('runtime')
    promote = subs.add_parser('promotion-plan')
    promote.add_argument('task')
    promote.add_argument('--summary', required=True)
    subs.add_parser('recover')
    subs.add_parser('rollback')
    return cli


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        cwd = Path(string(git(args.repo, 'rev-parse', '--show-toplevel')))
        state = Path(string(git(cwd, 'rev-parse', '--path-format=absolute', '--git-common-dir'))) / 'ewk-lifecycle'
        no_links(state)
        if args.op == 'inspect':
            result = topology(cwd, state, args.event)
        elif args.op == 'contract' and args.from_json is None and not args.apply:
            result = discover_contract(cwd, state)
        elif args.op == 'plan':
            result = candidate(cwd, args.base, args.include, args.exclude)
        elif args.op == 'compare':
            result = compare(cwd, args.base, args.tip)
        else:
            name = getattr(args, 'task', '') or ''
            if name and not KEY.fullmatch(name):
                raise ValueError('Invalid task or knowledge ID')
            if args.op == 'promotion-plan':
                print(json.dumps(promotion_plan(cwd, state, name, args.summary), indent=2, ensure_ascii=True))
                return 0
            if args.op == 'gate':
                task = mapping(state / 'tasks' / (name + '.json')) if name else None
                if (name or args.close) and not task:
                    raise ValueError('Gate needs an existing integration task')
                result = delivery_gate(cwd, state, args, task)
                print(json.dumps(result, indent=2, ensure_ascii=True))
                return 1 if result['status'] == 'BLOCKED' else 0
            with locked(state):
                record = state / 'tasks' / (name + '.json')
                if args.op == 'fetch':
                    result = fetch(cwd, state, args.remote, args.max_age)
                elif args.op == 'fast-forward':
                    result = fast_forward(cwd, args.expected, args.target)
                elif args.op == 'integrate':
                    manifest = candidate(cwd, args.base, args.include, args.exclude)
                    result = integrate(cwd, record, args.path.absolute(), manifest, args.owner)
                elif args.op == 'checkpoint':
                    result = checkpoint(cwd, state, name, args.from_json)
                elif args.op == 'knowledge':
                    result = knowledge(cwd, state, name, args.from_json, args.archive, args.evidence, args.require)
                elif args.op == 'contract':
                    task = mapping(record) if name else None
                    if not task or not args.from_json:
                        raise ValueError('Contract registration needs --task and --from-json')
                    result = register_contract(cwd, state, task, args.from_json, args.apply)
                elif args.op in ('deploy', 'cleanup'):
                    task = mapping(record)
                    if not task:
                        raise ValueError('Integration task not found')
                    result = (deploy(cwd, state, task) if args.op == 'deploy'
                              else cleanup(cwd, state, task, name, args.released, args.apply))
                elif args.op == 'recover':
                    pending = mapping(state / 'pending.json')
                    result = revert(Path(pending['cwd']), state, pending) if pending else {'pending': False}
                elif args.op == 'rollback':
                    result = rollback(cwd, state)
                else:
                    result = runtime_status(cwd, state)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'ewk lifecycle: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
