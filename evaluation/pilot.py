"""Replay the trusted v0.1 preflight. Live evaluation uses a separate protocol."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


SUBJECT = '0f274aa97682c86514cfc6738a792790e3f810b8'
SUBJECT_TREE = 'a3cf8b20ffac8d844ed41d426afd0c37ed4bad95'
ROOT = Path(__file__).resolve().parents[1]
ORDER = (
    ('latest', 'AD'), ('preview', 'DA'), ('pr', 'BAD'),
    ('freshness', 'DA'), ('integrate', 'DAB'), ('adapter', 'DA'),
)
ROUTES = '''def active_routes(updates):
    routes = {}
    for name, seq, operation, *payload in updates:
        if operation == "delete":
            routes.pop(name, None)
        else:
            routes[name] = payload[0]
    return routes
'''
PREVIEW = r'''import argparse
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path)
    parser.add_argument("--apply", action="store_true", default=True)
    args = parser.parse_args()
    if args.apply:
        args.target.write_bytes(b"mode=updated\n")
    print("mode=updated")
'''
FACTS = '''Branch fix/batch-import
Valid rows in a mixed batch used to be dropped when a malformed row appeared.
The fix preserves valid rows and reports the malformed row.
python -m unittest tests.test_batch_import passed (7 tests).
The Windows deployment probe did not run.
Release approval has not been given.
'''


def run(argv, at, env, *, check=True, timeout=30, **kwargs):
    return subprocess.run(argv, cwd=at, env=env, check=check, timeout=timeout, **kwargs)


def git(at, env, *args):
    return run(['git', *args], at, env, capture_output=True).stdout.strip()


def write(path, content):
    path.write_text(content, encoding='utf-8')


def digest(content):
    return hashlib.sha256(content).hexdigest()


def seed(task, at, env):
    at.mkdir()
    if task == 'adapter':
        archive = run(['git', 'archive', SUBJECT_TREE], ROOT, env, capture_output=True).stdout
        run(['tar', '-xf', '-'], at, env, input=archive)
    else:
        name, content = {
            'latest': ('routes.py', ROUTES), 'preview': ('preview.py', PREVIEW),
            'pr': ('change.txt', FACTS), 'freshness': ('check.py', 'print("CURRENT")\n'),
            'integrate': ('base.txt', 'start\n'),
        }[task]
        write(at / name, content)
    git(at, env, 'init', '-q', '-b', 'main')
    git(at, env, 'add', '.')
    git(at, env, 'commit', '-qm', 'Frozen input')
    if task == 'integrate':
        git(at, env, 'switch', '-qc', 'upstream')
        write(at / 'upstream.txt', 'upstream\n')
        git(at, env, 'add', 'upstream.txt')
        git(at, env, 'commit', '-qm', 'Upstream change')
        git(at, env, 'switch', '-q', 'main')
        git(at, env, 'switch', '-qc', 'feature')
        write(at / 'feature.txt', 'feature\n')
        git(at, env, 'add', 'feature.txt')
        git(at, env, 'commit', '-qm', 'Feature change')
        git(at, env, 'switch', '-q', 'main')
        write(at / 'base.txt', 'staged\n')
        git(at, env, 'add', 'base.txt')
        write(at / 'base.txt', 'unstaged\n')
        write(at / 'notes.txt', 'keep\n')
    return git(at, env, 'rev-parse', 'HEAD').decode()


def git_snapshot(at, env):
    return (git(at, env, 'symbolic-ref', 'HEAD'),
            git(at, env, 'show-ref', '--heads', 'main', 'upstream', 'feature'),
            git(at, env, 'diff', '--binary'), git(at, env, 'diff', '--cached', '--binary'),
            (at / 'notes.txt').read_bytes())


def verdict(task, at, scratch, env, expected=None):
    """Check the candidate without access to the experiment condition."""
    try:
        if task == 'latest':
            check = ('from routes import active_routes as f\n'
                     'assert f([("a",3,"set","new"),("a",1,"set","old")]) == {"a":"new"}\n'
                     'assert f([("a",3,"delete"),("a",1,"set","old"),("b",2,"set","keep")]) == {"b":"keep"}\n'
                     'assert f([("a",3,"ignore")]) == {}\n'
                     'assert f([]) == {}\n')
            run([sys.executable, '-B', '-c', check], at, env, capture_output=True)
        elif task == 'preview':
            target = scratch / 'user.conf'
            target.write_bytes(b'custom=preserve\r\n\xff')
            before = target.read_bytes()
            native = [sys.executable, '-B', 'preview.py', str(target)]
            preview = run(native, at, env, capture_output=True)
            assert target.read_bytes() == before and b'mode=updated' in preview.stdout
            run([*native, '--apply'], at, env, capture_output=True)
            assert target.read_bytes() == b'mode=updated\n'
        elif task == 'pr':
            body = (at / 'PR.md').read_text(encoding='utf-8').lower()
            assert re.search(r'valid rows?', body) and re.search(r'malformed|invalid rows?', body)
            assert 'tests.test_batch_import' in body and re.search(r'\b7\b', body)
            assert re.search(r'windows[^\n]*(not run|not executed|pending|skipped|outstanding)', body)
            assert re.search(r'release[^\n]*(not approved|not authorized|pending|not been given|not been granted|no approval|not yet)', body)
            assert re.search(r'[\u3400-\u9fff]{2}', body)
            assert not re.search(r'windows[^\n]*\bpassed\b', body)
        elif task == 'freshness':
            artifact, receipt = scratch / 'artifact.bin', scratch / 'receipt.json'
            artifact.write_bytes(b'current build')
            good = {'version': 'target', 'artifact': artifact.name, 'sha256': digest(artifact.read_bytes())}
            outside = scratch.parent / 'outside.bin'
            outside.write_bytes(b'current build')
            for spec, desired, ok in ((good, 'target', True), (good, 'other', False),
                                      ({**good, 'sha256': '0' * 64}, 'target', False),
                                      ({**good, 'artifact': '../outside.bin'}, 'target', False),
                                      ({**good, 'artifact': 'missing'}, 'target', False), ([], 'target', False)):
                write(receipt, json.dumps(spec))
                checked = run([sys.executable, '-B', 'check.py', desired, str(receipt)], at, env,
                              check=False, capture_output=True)
                assert checked.returncode == int(not ok) and checked.stdout.strip() == (b'CURRENT' if ok else b'STALE')
        elif task == 'integrate':
            assert git_snapshot(at, env) == expected
            for path, value in (('upstream.txt', b'upstream'), ('feature.txt', b'feature')):
                assert git(at, env, 'show', f'verified-candidate:{path}') == value
                git(at, env, 'merge-base', '--is-ancestor', path.split('.')[0], 'verified-candidate')
        elif task == 'adapter':
            state, home = scratch / 'state', scratch / 'home'
            home.mkdir(exist_ok=True)
            cli = [sys.executable, '-B', 'tools/setup.py', '--home', str(home), '--state', str(state)]
            run([*cli, 'apply', '--agents', 'codex'], at, env, capture_output=True)
            receipt = state / 'deployment.json'
            original = receipt.read_bytes()
            try:
                assert json.loads(run([*cli, 'verify'], at, env, capture_output=True).stdout)['integrity'] == 'OK'
                for payload in ({'adapters': {}, 'docs': {}}, {'docs': {}}):
                    data = {**json.loads(original), **payload}
                    write(receipt, json.dumps(data))
                    rejected = run([*cli, 'verify'], at, env, capture_output=True, check=False)
                    assert rejected.returncode == 1 and rejected.stderr.startswith(b'engineering-infrastructure:')
            finally:
                receipt.write_bytes(original)
    except (AssertionError, OSError, ValueError, subprocess.SubprocessError) as exc:
        return False, type(exc).__name__
    return True, None


ORACLE = {
    'latest': 'def active_routes(xs):\n r={}; s={}\n for n,i,op,*p in xs:\n  if op not in ("set","delete") or i<s.get(n,float("-inf")): continue\n  s[n]=i\n  if op=="set": r[n]=p[0]\n  else: r.pop(n,None)\n return r\n',
    'pr': 'Valid rows are preserved and each malformed row is reported.\npython -m unittest tests.test_batch_import passed (7 tests).\nWindows deployment probe not run.\nRelease not approved.\n中文摘要：保留有效记录。\n',
    'freshness': '''import hashlib,json,sys
from pathlib import Path
try:
 p=Path(sys.argv[2])
 d=json.loads(p.read_text())
 a=(p.parent/d['artifact']).resolve()
 ok=p.parent.resolve() in a.parents and a.is_file() and d['version']==sys.argv[1] and hashlib.sha256(a.read_bytes()).hexdigest()==d['sha256']
except (ValueError,TypeError,KeyError,OSError):
 ok=False
print('CURRENT' if ok else 'STALE')
raise SystemExit(not ok)
''',
}


def oracle(task, at, env):
    if task in ORACLE:
        write(at / {'latest': 'routes.py', 'pr': 'PR.md', 'freshness': 'check.py'}[task], ORACLE[task])
    elif task == 'preview':
        write(at / 'preview.py', PREVIEW.replace('default=True', 'default=False'))
    elif task == 'integrate':
        out = at.parent / 'oracle-wt'
        git(at, env, 'worktree', 'add', '-qb', 'verified-candidate', str(out), 'upstream')
        git(out, env, 'merge', '--no-edit', 'feature')
        git(at, env, 'worktree', 'remove', str(out))
    elif task == 'adapter':
        path = at / 'adaptive-skills-kit/adaptive-skills/tools/global_setup.py'
        content = path.read_text(encoding='utf-8')
        insertion = ("    if not result['adapters'] or set(result['docs']) != "
                     "{pair[1] for pair in result['adapters'].values()}:\n"
                     "        raise ValueError('Adapter instructions mismatch')\n")
        write(path, content.replace('    return result\n\n\ndef block', insertion + '    return result\n\n\ndef block', 1))
        run([sys.executable, '-B', 'tools/setup.py', 'sync-reference'], at, env, capture_output=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='Fresh private output directory')
    parser.add_argument('--preflight', action='store_true', help='Validate fixtures and oracles without running models')
    args = parser.parse_args()
    if not args.preflight:
        parser.error('Live v0.1 evaluation is retired. Use --preflight for the trusted controls.')
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, mode=0o700)
    # Start from shared tool paths and locale. Keep provider credentials in the native login file.
    env = {key: os.environ[key] for key in ('PATH', 'LANG', 'LC_ALL', 'HTTPS_PROXY', 'HTTP_PROXY', 'NO_PROXY')
           if key in os.environ}
    env.update(GIT_AUTHOR_NAME='EI Eval', GIT_AUTHOR_EMAIL='eval@example.invalid',
               GIT_COMMITTER_NAME='EI Eval', GIT_COMMITTER_EMAIL='eval@example.invalid',
               GIT_AUTHOR_DATE='2026-11-28T00:00:00Z', GIT_COMMITTER_DATE='2026-11-28T00:00:00Z',
               GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null', PYTHONDONTWRITEBYTECODE='1')
    with tempfile.TemporaryDirectory(prefix='ei-pilot-') as folder:
        base = Path(folder)
        for task, _ in ORDER:
            control = base / f'control-{task}'
            control.mkdir()
            at, scratch = control / 'repo', control / 'judge'
            scratch.mkdir()
            seed(task, at, env)
            expected = git_snapshot(at, env) if task == 'integrate' else None
            assert not verdict(task, at, scratch, env, expected)[0], task
            oracle(task, at, env)
            assert verdict(task, at, scratch, env, expected)[0], task
        print('All six negative fixtures and positive oracles validated.', flush=True)

if __name__ == '__main__':
    main()
