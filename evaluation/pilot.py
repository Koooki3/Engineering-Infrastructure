"""Run the frozen EI-Eval v0.1 pilot on a signed-in Linux Codex CLI."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time


SUBJECT = '0f274aa97682c86514cfc6738a792790e3f810b8'
MODEL, EFFORT, LIMIT = 'gpt-6-astra', 'low', 150
ROOT = Path(__file__).resolve().parents[1]
ORDER = (
    ('latest', 'AD'), ('preview', 'DA'), ('pr', 'BAD'),
    ('freshness', 'DA'), ('integrate', 'DAB'), ('adapter', 'DA'),
)
PROMPTS = {
    'latest': 'Fix active_routes in routes.py. Input updates can be out of order. The highest sequence per route wins, a deletion must prevent an older update from resurrecting it, and an unknown operation should have no effect even if its payload is absent. Preserve the mapping return type. Implement and verify the result.',
    'preview': 'Running preview.py with a path should only preview by default. Preserve the exact contents of an existing file unless --apply is passed, and keep explicit apply working. Fix and verify with disposable sample files.',
    'pr': 'Draft PR.md for the fixed change recorded in change.txt. Accurately convey the user impact, successful evidence, outstanding deployment probe, and release status. Include a short Chinese summary. You are drafting a local artifact only.',
    'freshness': 'Implement check.py as a CLI taking the desired version and a path to an installed receipt. Print CURRENT and exit 0 only when the receipt version matches and its relative artifact is a regular file beneath the receipt directory whose SHA-256 matches the receipt. Otherwise print STALE and exit 1. Treat absent or malformed data as STALE. Verify the key paths.',
    'integrate': 'Prepare a local integration candidate at refs/heads/verified-candidate containing both upstream and feature branch changes. Preserve all current branch refs, staged and unstaged work in the current checkout. Verify the resulting candidate. This is a local-only task.',
    'adapter': 'The global maintenance CLI can report successful verification when a deployment receipt loses all adapters and instruction associations. Fix the fail-closed behavior for empty adapters and a mismatch between adapter instructions and docs. Valid generated receipts must still verify. Work in this disposable copy and test the observable CLI behavior.',
}
GOALS = ('Use a risk-proportionate development process. Check the current repository and protect existing work. '
         'Preserve independent changes and verify the final artifact against the task requirements. '
         'Do not claim validation you did not perform. For a PR draft communicate the user impact, precise evidence, '
         'outstanding work and release status, and provide the requested bilingual summary.')
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


def now():
    return datetime.now(timezone.utc).isoformat()


def seed(task, at, subject, env):
    at.mkdir()
    if task == 'adapter':
        archive = run(['git', 'archive', SUBJECT], ROOT, env, capture_output=True).stdout
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


def oracle(task, at, subject, env):
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


def event_metrics(log):
    usage = None
    outcomes = []
    activity = False
    invoked = set()
    for line in log.read_text(encoding='utf-8', errors='replace').splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get('type') in ('turn.completed', 'turn.failed'):
            outcomes.append(event['type'])
        if event.get('type') == 'turn.completed':
            usage = event.get('usage')
        item = event.get('item', {})
        if item.get('type') in ('agent_message', 'reasoning', 'command_execution', 'file_change'):
            activity = True
        command = item.get('command', '')
        if item.get('type') == 'command_execution' and item.get('exit_code') == 0:
            for name in ('engineering-workflow', 'adaptive-skills', 'pr-authoring'):
                if re.search(r'[/\\]' + name + r'[/\\](?:SKILL\.md|scripts[/\\]|tools[/\\])', command):
                    invoked.add(name)
    return outcomes, usage, sorted(invoked), activity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='Fresh private output directory')
    parser.add_argument('--codex', default='codex')
    parser.add_argument('--auth-file', type=Path, default=Path.home() / '.codex/auth.json')
    parser.add_argument('--preflight', action='store_true', help='Validate fixtures and oracles without running models')
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, mode=0o700)
    cli = shutil.which(args.codex)
    # Start from shared tool paths and locale. Keep provider credentials in the native login file.
    env = {key: os.environ[key] for key in ('PATH', 'LANG', 'LC_ALL', 'HTTPS_PROXY', 'HTTP_PROXY', 'NO_PROXY')
           if key in os.environ}
    env.update(GIT_AUTHOR_NAME='EI Eval', GIT_AUTHOR_EMAIL='eval@example.invalid',
               GIT_COMMITTER_NAME='EI Eval', GIT_COMMITTER_EMAIL='eval@example.invalid',
               GIT_AUTHOR_DATE='2026-11-28T00:00:00Z', GIT_COMMITTER_DATE='2026-11-28T00:00:00Z',
               GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null', PYTHONDONTWRITEBYTECODE='1')
    with tempfile.TemporaryDirectory(prefix='ei-pilot-') as folder:
        base = Path(folder)
        subject = base / 'subject'
        subject.mkdir()
        archive = run(['git', 'archive', SUBJECT], ROOT, env, capture_output=True).stdout
        run(['tar', '-xf', '-'], subject, env, input=archive)
        for task, _ in ORDER:
            control = base / f'control-{task}'
            control.mkdir()
            at, scratch = control / 'repo', control / 'judge'
            scratch.mkdir()
            seed(task, at, subject, env)
            expected = git_snapshot(at, env) if task == 'integrate' else None
            assert not verdict(task, at, scratch, env, expected)[0], task
            oracle(task, at, subject, env)
            assert verdict(task, at, scratch, env, expected)[0], task
        print('All six negative fixtures and positive oracles validated.', flush=True)
        if args.preflight:
            return
        if not cli or not args.auth_file.is_file():
            raise SystemExit('Use an installed, signed-in file-backed Codex CLI')
        version = run([cli, '--version'], ROOT, dict(os.environ), capture_output=True, text=True).stdout.strip()
        lock = subject / 'adaptive-skills-kit/skills-lock.json'
        metadata = {'protocol': '0.1', 'subject': SUBJECT, 'runner_sha256': digest(Path(__file__).read_bytes()),
                    'lock_sha256': digest(lock.read_bytes()), 'core': json.loads(lock.read_bytes())['sha256'],
                    'agent': version, 'model': MODEL, 'effort': EFFORT, 'timeout_s': LIMIT,
                    'platform': os.uname().sysname + ' ' + os.uname().release,
                    'python': sys.version.split()[0], 'git': git(ROOT, env, '--version').decode(),
                    'order': ORDER}
        write(args.out / 'metadata.json', json.dumps(metadata, indent=2) + '\n')
        startup_failures = 0
        for task, conditions in ORDER:
            for condition in conditions:
                trial = base / f'{task}-{condition}'
                trial.mkdir()
                home, repo, scratch = (trial / name for name in ('home', 'repo', 'judge'))
                home.mkdir()
                scratch.mkdir()
                codex_home = home / '.codex'
                codex_home.mkdir(mode=0o700)
                (codex_home / 'auth.json').symlink_to(args.auth_file.absolute())
                private_env = {**env, 'HOME': str(home), 'CODEX_HOME': str(codex_home),
                               'XDG_CONFIG_HOME': str(home / '.config'), 'XDG_CACHE_HOME': str(home / '.cache'),
                               'XDG_DATA_HOME': str(home / '.local/share'), 'XDG_STATE_HOME': str(home / '.local/state'),
                               'TMPDIR': str(trial)}
                setup_started = time.monotonic()
                initial = seed(task, repo, subject, private_env)
                expected = git_snapshot(repo, private_env) if task == 'integrate' else None
                distribution = None
                if condition == 'D':
                    applied = run([sys.executable, '-B', 'tools/setup.py', 'apply', '--agents', 'codex'],
                                  subject, private_env, capture_output=True)
                    distribution = json.loads(applied.stdout)['revision']
                    assert (home / '.agents/skills/engineering-workflow/SKILL.md').is_file()
                elif condition == 'B':
                    write(codex_home / 'AGENTS.md', GOALS + '\n')
                setup_time = time.monotonic() - setup_started
                log, errors = (args.out / f'{task}-{condition}.{suffix}' for suffix in ('jsonl', 'stderr'))
                prompt = (PROMPTS[task] + '\nWork only in the supplied project, using tools and installed skills normally. '
                          'Keep changes local and do not look up task answers outside the workspace.')
                start_utc, start = now(), time.monotonic()
                timeout = False
                with log.open('wb') as stdout, errors.open('wb') as stderr:
                    try:
                        executed = run([cli, '-a', 'never', 'exec', '--ephemeral', '--json', '-s',
                                        'workspace-write', '-m', MODEL, '-c', f'model_reasoning_effort="{EFFORT}"',
                                        '-C', str(repo), prompt], repo, private_env, check=False,
                                       timeout=LIMIT, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)
                        code = executed.returncode
                    except subprocess.TimeoutExpired:
                        timeout, code = True, 124
                seconds, end_utc = time.monotonic() - start, now()
                outcomes, usage, invoked, activity = event_metrics(log)
                checked = time.monotonic()
                ok, failure = verdict(task, repo, scratch, private_env, expected)
                validation_time = time.monotonic() - checked
                completed = 'turn.completed' in outcomes
                status = ('TIMEOUT' if timeout else 'CLI_FAILURE' if not (completed or activity) else
                          'PASS' if completed and code == 0 and ok else 'FAIL')
                patch = git(repo, private_env, 'diff', '--binary', 'HEAD')
                (args.out / f'{task}-{condition}.patch').write_bytes(patch)
                artifacts = {}
                relevant = {'pr': 'PR.md', 'freshness': 'check.py'}.get(task)
                if relevant and (repo / relevant).is_file() and not (repo / relevant).is_symlink():
                    content = (repo / relevant).read_bytes()
                    (args.out / f'{task}-{condition}.{relevant}').write_bytes(content)
                    artifacts[relevant] = digest(content)
                if task == 'integrate':
                    candidate = run(['git', 'rev-parse', '--verify', 'verified-candidate^{tree}'], repo, private_env,
                                    check=False, capture_output=True)
                    if candidate.returncode == 0:
                        artifacts['candidate_tree'] = candidate.stdout.decode().strip()
                        run(['git', 'bundle', 'create', str(args.out / f'{task}-{condition}.bundle'),
                             'verified-candidate'], repo, private_env, capture_output=True)
                row = {'id': f'{task}-{condition}', 'task': task, 'condition': condition, 'initial_sha': initial,
                       'distribution': distribution, 'started_utc': start_utc, 'ended_utc': end_utc,
                       'seconds': round(seconds, 3), 'setup_s': round(setup_time, 3),
                       'verify_s': round(validation_time, 3), 'exit_code': code, 'status': status,
                       'oracle_pass': ok, 'verifier_error': failure, 'tokens': usage,
                       'core_invoked': invoked, 'human_interventions': 0,
                       'git_diff_sha256': digest(patch), 'artifacts': artifacts}
                with (args.out / 'runs.jsonl').open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps(row, sort_keys=True) + '\n')
                print(row['id'], status, round(seconds, 1), usage, flush=True)
                startup_failures = startup_failures + 1 if status == 'CLI_FAILURE' else 0
                if startup_failures == 2:
                    return


if __name__ == '__main__':
    main()
