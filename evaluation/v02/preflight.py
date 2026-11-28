"""Validate v0.2 fixtures, negative controls and the offline isolation boundary."""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time

import sandbox


ROOT = Path(__file__).resolve().parent
PYTHON = '/usr/bin/python3'
GIT = '/usr/bin/git'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write(path, content):
    path.write_bytes(content.encode() if isinstance(content, str) else content)


def runpy(workspace, name, *args):
    return sandbox.run(workspace, [PYTHON, '-I', '-B', name, *args])


def git(workspace, *args):
    result = sandbox.run(workspace, [GIT, '-c', 'core.hooksPath=/dev/null',
                                     '-c', 'core.fsmonitor=false', *args])
    if result.returncode:
        raise RuntimeError(f'Git fixture command failed: {args[0]} ({result.returncode})')
    return result.stdout


ORACLES = {
    'operation': ('solve.py', '''
import json, sys
last = {}
for name, sequence, action, *data in json.loads(sys.argv[1]):
    if action in {'set', 'delete'} and (name not in last or sequence > last[name][0]):
        last[name] = (sequence, action, data)
print(json.dumps({name: row[2][0] for name, row in last.items() if row[1] == 'set'}))
'''),
    'evidence': ('check.py', '''
import hashlib, json
from pathlib import Path
try:
    record = json.loads(Path('receipt.json').read_bytes())
    valid = hashlib.sha256(Path('source.txt').read_bytes()).hexdigest() == record['sha256']
except (ValueError, KeyError, TypeError, OSError):
    valid = False
raise SystemExit(int(not valid))
'''),
    'freshness': ('runtime.py', '''
import hashlib, json, sys
from pathlib import Path
try:
    current = json.loads(Path('installed.json').read_bytes())
    valid = current['version'] == sys.argv[1] and current['sha256'] == hashlib.sha256(Path('payload.bin').read_bytes()).hexdigest()
except (ValueError, KeyError, TypeError, OSError):
    valid = False
raise SystemExit(int(not valid))
'''),
    'rollback': ('deploy.py', '''
import hashlib
from pathlib import Path
target = Path('installed.bin')
previous = target.read_bytes()
target.write_bytes(Path('candidate.bin').read_bytes())
if hashlib.sha256(target.read_bytes()).hexdigest() != Path('expected.txt').read_text():
    target.write_bytes(previous)
    raise SystemExit(1)
'''),
    'cleanup': ('cleanup.py', '''
from pathlib import Path
for path in Path('worktrees').iterdir():
    if (path / 'complete').is_file() and (path / 'owned').is_file() and not (path / 'modified.note').exists():
        path.rename(Path('archive') / path.name)
'''),
}


def isolation_probes(base):
    work = base / 'sandbox'
    work.mkdir()
    marker = base / 'not-mounted.txt'
    write(marker, 'synthetic credentials and scoring material')
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        probe = '''
import os, pathlib, socket, sys
assert not pathlib.Path(sys.argv[1]).exists()
assert not pathlib.Path('/mnt/d').exists()
assert not pathlib.Path('/proc/self/environ').exists()
assert not pathlib.Path('/home/.codex/auth.json').exists()
assert 'EI_EVAL_TEST_SECRET' not in os.environ
with socket.socket() as receiver:
    receiver.settimeout(.3)
    assert receiver.connect_ex(('127.0.0.1', int(sys.argv[2]))) != 0
pathlib.Path('candidate-wrote.txt').write_text('isolated')
'''
        previous = os.environ.get('EI_EVAL_TEST_SECRET')
        os.environ['EI_EVAL_TEST_SECRET'] = 'synthetic host-only value'
        try:
            result = sandbox.run(work, [PYTHON, '-I', '-c', probe, str(marker), str(listener.getsockname()[1])])
        finally:
            if previous is None:
                os.environ.pop('EI_EVAL_TEST_SECRET')
            else:
                os.environ['EI_EVAL_TEST_SECRET'] = previous
    if result.returncode:
        raise RuntimeError(f'Bubblewrap isolation probe failed ({result.returncode}): ' +
                           result.stderr.decode(errors='replace')[:350])
    assert (work / 'candidate-wrote.txt').read_text() == 'isolated'
    descendant = ('import os,time,pathlib; pid=os.fork(); time.sleep(1.5); '
                  "pathlib.Path('escaped.txt').write_text('marker') if pid==0 else None")
    result = sandbox.run(work, [PYTHON, '-I', '-c', descendant], timeout=.45)
    assert result.returncode == 124
    time.sleep(1.6)
    assert not (work / 'escaped.txt').exists()
    return {'host_files_hidden': True, 'host_environment_not_inherited': True, 'no_host_loopback': True,
            'workspace_writable': True, 'timeout_terminated_descendant': True}


def seed_integration(work):
    git(work, 'init', '-q', '-b', 'main')
    git(work, 'config', 'user.name', 'Synthetic Evaluation')
    git(work, 'config', 'user.email', 'eval@example.invalid')
    write(work / 'base.txt', 'initial')
    git(work, 'add', 'base.txt')
    git(work, 'commit', '-qm', 'Base')
    for branch in ('upstream', 'feature'):
        git(work, 'switch', '-qc', branch, 'main')
        write(work / (branch + '.txt'), branch)
        git(work, 'add', branch + '.txt')
        git(work, 'commit', '-qm', branch)
    git(work, 'switch', '-q', 'main')
    write(work / 'base.txt', 'staged')
    git(work, 'add', 'base.txt')
    write(work / 'base.txt', 'unstaged')
    write(work / 'notes.txt', 'untracked')


def snapshot(work):
    return [git(work, *args) for args in [('symbolic-ref', 'HEAD'),
                                          ('show-ref', '--heads', 'main', 'upstream', 'feature'),
                                          ('diff', '--binary'), ('diff', '--cached', '--binary')]]


def integration(work, positive):
    seed_integration(work)
    before = snapshot(work)
    if positive:
        script = ('set -eu; git worktree add -q -b candidate /tmp/candidate upstream; '
                  'git -C /tmp/candidate merge -q --no-edit feature; git worktree remove /tmp/candidate')
        result = sandbox.run(work, ['/usr/bin/bash', '-c', script])
        assert result.returncode == 0, result.stderr.decode(errors='replace')
    return (snapshot(work) == before and (work / 'notes.txt').read_bytes() == b'untracked'
            and (work / '.git/refs/heads/candidate').is_file()
            and all(git(work, 'show', 'candidate:' + ref + '.txt') == ref.encode()
                    for ref in ('upstream', 'feature'))
            and all(not git(work, 'merge-base', '--is-ancestor', ref, 'candidate')
                    for ref in ('main', 'upstream', 'feature')))


def verify(task, work, positive):
    if task == 'integration':
        return integration(work, positive)
    name, oracle = ORACLES[task]
    write(work / name, oracle if positive else 'print("{}")\n')
    if task == 'operation':
        data = '[["east",2,"delete"],["east",1,"set","old"],["west",4,"set","live"],["west",5,"ignore"]]'
        result = runpy(work, name, data)
        return result.returncode == 0 and json.loads(result.stdout) == {'west': 'live'}
    if task in ('evidence', 'freshness'):
        content, receipt = (('source.txt', 'receipt.json') if task == 'evidence'
                            else ('payload.bin', 'installed.json'))
        expected = b'verified artifact'
        record = json.dumps({'sha256': digest(expected), 'version': 'new'})
        write(work / content, expected)
        write(work / receipt, record)
        args = ('new',) if task == 'freshness' else ()
        first = runpy(work, name, *args)
        assert (work / content).read_bytes() == expected and (work / receipt).read_text() == record
        write(work / content, b'drift')
        second = runpy(work, name, *args)
        assert (work / content).read_bytes() == b'drift' and (work / receipt).read_text() == record
        write(work / receipt, 'null')
        malformed = runpy(work, name, *args)
        return first.returncode == 0 and second.returncode == malformed.returncode == 1
    if task == 'rollback':
        write(work / 'installed.bin', b'stable')
        write(work / 'candidate.bin', b'replacement')
        write(work / 'expected.txt', digest(b'different'))
        write(work / 'unrelated.txt', b'keep')
        first = runpy(work, name)
        preserved = (work / 'installed.bin').read_bytes() == b'stable'
        write(work / 'expected.txt', digest(b'replacement'))
        second = runpy(work, name)
        return (first.returncode == 1 and preserved and second.returncode == 0
                and (work / 'installed.bin').read_bytes() == b'replacement'
                and (work / 'unrelated.txt').read_bytes() == b'keep')
    (work / 'worktrees').mkdir()
    (work / 'archive').mkdir()
    layout = {'ready': ['complete', 'owned'], 'dirty': ['complete', 'owned', 'modified.note'],
              'unowned': ['complete'], 'pending': ['owned']}
    for folder, files in layout.items():
        root = work / 'worktrees' / folder
        root.mkdir()
        for file in files:
            write(root / file, folder)
    result = runpy(work, name)
    return (result.returncode == 0 and set(p.name for p in (work / 'archive').iterdir()) == {'ready'}
            and not (work / 'worktrees/ready').exists()
            and all((work / 'worktrees' / folder / file).read_text() == folder
                    for folder, files in layout.items() if folder != 'ready' for file in files))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='New JSON file for this preflight')
    args = parser.parse_args()
    raw = (ROOT / 'tasks.json').read_bytes()
    manifest = json.loads(raw)
    assert Counter(sequence for _, sequence in manifest['order']) == {'AD': 3, 'DA': 3}
    assert set(task for task, _ in manifest['order']) == manifest['tasks'].keys()
    result = {'version': manifest['version'], 'manifest_sha256': digest(raw), 'model_trials': 0,
              'preflight_sha256': digest(Path(__file__).read_bytes()),
              'sandbox_sha256': digest((ROOT / 'sandbox.py').read_bytes()),
              'kernel': os.uname().release,
              'bubblewrap': subprocess.check_output(['/usr/bin/bwrap', '--version'], timeout=5).decode().strip()}
    with tempfile.TemporaryDirectory(prefix='ei-v02-') as folder:
        base = Path(folder)
        result['isolation'] = isolation_probes(base)
        result['tasks'] = {}
        for task, _ in manifest['order']:
            controls = []
            for positive in (False, True):
                work = base / f'{task}-{positive}'
                work.mkdir()
                write(work / 'TASK.txt', manifest['tasks'][task])
                controls.append(verify(task, work, positive))
            assert controls == [False, True], task
            result['tasks'][task] = {'negative_rejected': True, 'oracle_accepted': True}
    result['status'] = 'PASS'
    encoded = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.out:
        with args.out.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(encoded)
    print(encoded, end='')


if __name__ == '__main__':
    main()
