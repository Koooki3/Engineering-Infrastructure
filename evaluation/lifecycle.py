#!/usr/bin/env python3
"""Run a deterministic, offline acceptance evaluation of the bundled lifecycle."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE = ROOT / 'engineering-workflow-kit/engineering-workflow/scripts/lifecycle.py'
SKILLS = ROOT / 'adaptive-skills-kit/adaptive-skills/tools/skills.py'
PR_LINTER = ROOT / 'pr-authoring-kit/pr-authoring/tools/lint_pr_body.py'
FIXED_DATE = '2000-01-01T00:00:00+00:00'

ADAPTER = r'''import hashlib, json, os, subprocess, sys
from pathlib import Path

op, root = sys.argv[1], Path(sys.argv[2])
installed = root / 'installed.json'

if op == 'build':
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    Path('artifact.json').write_text(json.dumps({'sha': head, 'instance': 'fixture-service'}, sort_keys=True),
                                     encoding='utf-8')
elif op == 'test':
    data = json.loads(Path('artifact.json').read_text(encoding='utf-8'))
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    assert data == {'instance': 'fixture-service', 'sha': head}
elif op == 'install':
    installed.write_bytes(Path(os.environ['EWK_DEPLOY_ARTIFACT']).read_bytes())
    marker = root / 'fail-install-once'
    if marker.exists():
        marker.unlink()
        sys.exit(3)
elif op == 'stop':
    installed.unlink(missing_ok=True)
elif op == 'probe':
    if installed.exists():
        raw = installed.read_bytes()
        data = json.loads(raw)
        data.update(active=True, healthy=True, sha256=hashlib.sha256(raw).hexdigest(), instance='fixture-service')
        print(json.dumps(data, sort_keys=True))
    else:
        print(json.dumps({'active': False}))
'''


class EvaluationFailure(Exception):
    pass


class Scenario:
    def __init__(self, name):
        self.data = {'name': name, 'status': 'PASS', 'commands': [], 'checks': []}

    def check(self, name, actual, expected, note=None):
        passed = actual == expected
        row = {'name': name, 'status': 'PASS' if passed else 'FAIL',
               'actual': actual, 'expected': expected}
        if note:
            row['note'] = note
        self.data['checks'].append(row)
        if not passed:
            self.data['status'] = 'FAIL'
            raise EvaluationFailure(name)
        return actual

    def command(self, name, argv, cwd, expected_code=0, env=None, timeout=60):
        child_env = dict(os.environ)
        child_env.update({
            'PYTHONDONTWRITEBYTECODE': '1',
            'GIT_TERMINAL_PROMPT': '0',
            'GIT_AUTHOR_DATE': FIXED_DATE,
            'GIT_COMMITTER_DATE': FIXED_DATE,
        })
        if env:
            child_env.update(env)
        result = subprocess.run(argv, cwd=cwd, env=child_env, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
        self.data['commands'].append({'name': name, 'exit_code': result.returncode,
                                      'expected_exit_code': expected_code})
        self.check(name + ' exit code', result.returncode, expected_code)
        return result

    def json_command(self, name, argv, cwd, expected_code=0, env=None):
        result = self.command(name, argv, cwd, expected_code=expected_code, env=env)
        if expected_code != 0 and not result.stdout:
            return result, None
        try:
            return result, json.loads(result.stdout.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.check(name + ' JSON output', False, True)

    def stderr_contains(self, name, result, expected):
        message = result.stderr.decode('utf-8', errors='replace')
        self.check(name, expected in message, True, note='matched expected failure class')


class Fixture:
    def __init__(self, root):
        self.root = root
        self.repo = root / 'source'
        self.worktrees = root / 'worktrees'
        self.repo.mkdir()
        self.worktrees.mkdir()
        self.git_config = root / 'empty-gitconfig'
        self.git_config.write_text('', encoding='utf-8')
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=str(self.git_config), GIT_CONFIG_NOSYSTEM='1',
                        GIT_TERMINAL_PROMPT='0', GIT_AUTHOR_DATE=FIXED_DATE,
                        GIT_COMMITTER_DATE=FIXED_DATE, PYTHONDONTWRITEBYTECODE='1')
        self.git('init', '-b', 'main')
        self.git('config', 'user.email', 'evaluation@example.invalid')
        self.git('config', 'user.name', 'Lifecycle Evaluation')
        self.git('config', 'core.autocrlf', 'false')
        self.git('config', 'commit.gpgsign', 'false')
        self.write('.gitignore', 'artifact.json\n')
        self.write('base.txt', 'baseline\n')
        self.base = self.commit('base')
        self.git('switch', '-c', 'feature')
        self.write('feature-one.txt', 'feature one\n')
        self.feature_one = self.commit('feature one')
        self.git('switch', 'main')
        self.state = self.repo / '.git' / 'ewk-lifecycle'

    def git(self, *args, cwd=None):
        command_cwd = cwd or self.repo
        result = subprocess.run(['git', '-C', str(command_cwd), *args], cwd=command_cwd, env=self.env,
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=30, check=False)
        if result.returncode:
            raise RuntimeError('Fixture Git command failed: ' + ' '.join(args[:2]))
        return result.stdout.decode('utf-8', errors='replace').strip()

    def write(self, name, content, cwd=None):
        path = (cwd or self.repo) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def commit(self, message):
        self.git('add', '-A')
        self.git('commit', '--no-gpg-sign', '-m', message)
        return self.git('rev-parse', 'HEAD')

    def lifecycle(self, scenario, name, *args, expected_code=0):
        argv = [sys.executable, '-B', str(LIFECYCLE), '--repo', str(self.repo), *args]
        return scenario.json_command(name, argv, cwd=self.repo, expected_code=expected_code, env=self.env)

    def integrate(self, scenario, task, base, include, boundary):
        _, result = self.lifecycle(scenario, 'integrate ' + task, 'integrate', task,
                                   '--owner', 'evaluation', '--path', str(self.worktrees / task),
                                   '--base', base, '--include', include, boundary)
        return result

    def setup_contract(self):
        adapter = self.root / 'adapter.py'
        adapter.write_text(ADAPTER, encoding='utf-8')
        stages = {name: [sys.executable, str(adapter), name, str(self.root)]
                  for name in ('build', 'test', 'install', 'probe', 'stop')}
        contract = {'schema': 1, 'artifact': 'artifact.json', **stages}
        path = self.root / 'deployment-contract.json'
        path.write_text(json.dumps(contract, sort_keys=True), encoding='utf-8')
        return path


def git_version(env):
    result = subprocess.run(['git', '--version'], env=env, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=True)
    return result.stdout.decode('utf-8', errors='replace').strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lifecycle_flow(root, rows=None):
    fixture = Fixture(root)
    rows = rows if rows is not None else []

    protection = Scenario('integration_isolation_and_primary_tree_protection')
    rows.append(protection.data)
    _, inspection = fixture.lifecycle(protection, 'inspect start', 'inspect', '--event', 'start')
    protection.check('inspect identifies fixture HEAD', inspection.get('head'), fixture.base)
    protection.check('inspect identifies main branch', inspection.get('branch'), 'main')
    protection.check('inspect proposes baseline establishment', inspection.get('next'), 'establish_baseline')
    note = fixture.write('owner-note.tmp', 'preserve this local note\n')
    before_status = fixture.git('status', '--porcelain=v1')
    task_one = fixture.integrate(protection, 'release-one', 'refs/heads/main',
                                 'refs/heads/feature', fixture.base)
    protection.check('candidate phase', task_one.get('phase'), 'READY')
    protection.check('candidate includes selected feature',
                     (fixture.worktrees / 'release-one' / 'feature-one.txt').is_file(), True)
    _, ready_gate = fixture.lifecycle(protection, 'gate accepts ready integration', 'gate',
                                      '--base', 'refs/heads/main', '--task', 'release-one')
    protection.check('ready integration gate', ready_gate.get('status'), 'PASS')
    protection.check('ready integration input check', ready_gate['checks'].get('inputs'), 'PASS')
    protection.check('primary dirty status preserved', fixture.git('status', '--porcelain=v1'), before_status)
    protection.check('primary note content preserved', note.read_text(encoding='utf-8'), 'preserve this local note\n')
    note.unlink()
    protection.check('primary tree clean after fixture cleanup', fixture.git('status', '--porcelain=v1'), '')

    deployment = Scenario('verified_deployment_and_runtime_identity')
    rows.append(deployment.data)
    contract_path = fixture.setup_contract()
    _, preview = fixture.lifecycle(deployment, 'contract proposal preview', 'contract', '--task', 'release-one',
                                   '--from-json', str(contract_path))
    deployment.check('contract preview is inert', preview.get('status'), 'PREVIEW')
    _, registered = fixture.lifecycle(deployment, 'contract apply probes inactive runtime', 'contract',
                                       '--task', 'release-one', '--from-json', str(contract_path), '--apply')
    deployment.check('contract registered after probe', registered.get('status'), 'CONFIGURED')
    _, first = fixture.lifecycle(deployment, 'deploy release-one', 'deploy', 'release-one')
    deployment.check('first deployment status', first.get('status'), 'VERIFIED')
    deployment.check('runtime probe observed candidate SHA', first['observed'].get('sha'), first.get('sha'))
    deployment.check('runtime probe observed live instance', first['observed'].get('instance'), 'fixture-service')
    installed = root / 'installed.json'
    first_bytes = installed.read_bytes()
    deployment.check('installed bytes match verified artifact', sha256(installed), first.get('sha256'))

    archived = Path(first['artifact'])
    naive_exists = installed.is_file() and archived.is_file()
    deployment.check('manual artifact-exists-only baseline', naive_exists, True,
                     note='Existence alone does not establish runtime identity.')
    installed.write_bytes(b'{"sha":"wrong-version","instance":"fixture-service"}')
    proc, _ = fixture.lifecycle(deployment, 'runtime rejects installed version drift', 'runtime', expected_code=1)
    deployment.stderr_contains('runtime drift detection', proc, 'Runtime health or deployed version drift')
    installed.write_bytes(first_bytes)
    _, current = fixture.lifecycle(deployment, 'runtime restored to current', 'runtime')
    deployment.check('runtime freshness after exact restore', current.get('freshness'), 'CURRENT')

    stale = Scenario('stale_named_input_evidence_and_gate')
    rows.append(stale.data)
    fixture.git('switch', 'feature')
    fixture.write('feature-two.txt', 'feature two\n')
    feature_two = fixture.commit('feature two')
    fixture.git('switch', 'main')
    clean_status = fixture.git('status', '--porcelain=v1') == ''
    recorded_feature = first['pins']['refs/heads/feature']
    stale.check('manual clean-worktree-only baseline', clean_status, True,
                note='This manual check does not compare refs named by the deployment receipt.')
    stale.check('feature input moved from receipt pin', feature_two != recorded_feature, True)
    _, drift = fixture.lifecycle(stale, 'runtime reports stale named input', 'runtime')
    stale.check('runtime freshness', drift.get('freshness'), 'STALE_INPUTS')
    gate_proc, gate = fixture.lifecycle(stale, 'delivery gate blocks stale runtime', 'gate',
                                        '--task', 'release-one', '--runtime', expected_code=1)
    stale.check('gate status', gate.get('status'), 'BLOCKED')
    stale.check('gate input check', gate['checks'].get('inputs'), 'BLOCKED')
    stale.check('gate runtime check', gate['checks'].get('runtime'), 'BLOCKED')

    refreshed = Scenario('refreshed_candidate_deploys_after_stale_evidence')
    rows.append(refreshed.data)
    task_two = fixture.integrate(refreshed, 'release-two', 'refs/heads/main',
                                 'refs/heads/feature', fixture.base)
    refreshed.check('refreshed candidate phase', task_two.get('phase'), 'READY')
    _, second = fixture.lifecycle(refreshed, 'deploy release-two', 'deploy', 'release-two')
    refreshed.check('refreshed deployment status', second.get('status'), 'VERIFIED')
    refreshed.check('refreshed deployment SHA differs', second.get('sha') != first.get('sha'), True)
    _, fresh_runtime = fixture.lifecycle(refreshed, 'runtime after refreshed deploy', 'runtime')
    refreshed.check('fresh runtime state', fresh_runtime.get('freshness'), 'CURRENT')

    recovery = Scenario('failed_install_recovers_previous_verified_release')
    rows.append(recovery.data)
    fixture.git('switch', '-c', 'failure-candidate', 'refs/heads/feature')
    fixture.write('failure-only.txt', 'candidate that will fail installation\n')
    fixture.commit('failure candidate')
    fixture.git('switch', 'main')
    task_failed = fixture.integrate(recovery, 'release-failed', 'refs/heads/feature',
                                    'refs/heads/failure-candidate', 'refs/heads/feature')
    recovery.check('failure candidate isolated and ready', task_failed.get('phase'), 'READY')
    (root / 'fail-install-once').write_text('fail once\n', encoding='utf-8')
    failed_proc, _ = fixture.lifecycle(recovery, 'deploy install failure invokes recovery',
                                       'deploy', 'release-failed', expected_code=1)
    recovery.stderr_contains('failed install reported', failed_proc, 'project command')
    recovery.check('pending recovery journal cleared', (fixture.state / 'pending.json').exists(), False)
    stable = json.loads((fixture.state / 'stable.json').read_text(encoding='utf-8'))
    recovery.check('previous verified SHA retained', stable.get('sha'), second.get('sha'))
    recovery.check('previous verified bytes restored', sha256(installed), second.get('sha256'))
    _, recovered_runtime = fixture.lifecycle(recovery, 'runtime healthy after recovery', 'runtime')
    recovery.check('runtime healthy after recovery', recovered_runtime.get('healthy'), True)
    recovery.check('runtime current after recovery', recovered_runtime.get('freshness'), 'CURRENT')

    cleanup = Scenario('cleanup_protects_changes_then_archives_owned_worktree')
    rows.append(cleanup.data)
    one_tree = fixture.worktrees / 'release-one'
    (one_tree / 'artifact.json').unlink(missing_ok=True)
    fixture.write('review-note.tmp', 'must block destructive cleanup\n', cwd=one_tree)
    refused, _ = fixture.lifecycle(cleanup, 'cleanup refuses dirty owned worktree', 'cleanup',
                                   'release-one', '--released', '--apply', expected_code=1)
    cleanup.stderr_contains('cleanup refusal class', refused, 'no tracked, untracked or ignored files')
    (one_tree / 'review-note.tmp').unlink()
    (one_tree / 'artifact.json').unlink(missing_ok=True)
    _, archived_task = fixture.lifecycle(cleanup, 'cleanup archives clean released worktree', 'cleanup',
                                         'release-one', '--released', '--apply')
    cleanup.check('clean owned worktree removal applied', archived_task.get('applied'), True)
    cleanup.check('archived worktree absent', one_tree.exists(), False)
    cleanup.check('archive ref points to candidate',
                  fixture.git('rev-parse', 'refs/ewk/archive/release-one'), task_one['candidate_sha'])
    return rows


def adaptive_reference_flow(root):
    scenario = Scenario('adaptive_reference_discovery_stays_offline')
    home, state = root / 'adaptive-home', root / 'adaptive-state'
    home.mkdir()
    state.mkdir()
    proxy_env = {'HTTP_PROXY': 'http://127.0.0.1:1', 'HTTPS_PROXY': 'http://127.0.0.1:1',
                 'ALL_PROXY': 'http://127.0.0.1:1', 'NO_PROXY': '', 'no_proxy': ''}
    argv = [sys.executable, '-B', str(SKILLS), '--home', str(home), '--state', str(state),
            '--source', str(ROOT), 'discover', '--agent', 'codex', '--need', 'react-performance',
            '--public-query', 'review React performance in a project']
    _, result = scenario.json_command('adaptive reference discovery', argv, cwd=ROOT, env=proxy_env)
    decision = result['decisions'][0]
    scenario.check('known capability routes to reference review', decision.get('action'), 'REVIEW_REFERENCE')
    scenario.check('reference candidate identity', decision.get('id'), 'vercel-react-best-practices')
    scenario.check('no external candidate returned', result.get('candidates'), [])
    scenario.check('no public-search cache created', (state / 'search').exists(), False)
    return scenario.data


def pr_lint_flow(root):
    scenario = Scenario('pr_linter_accepts_valid_body_and_rejects_private_path')
    body = root / 'pr-body.md'
    good = ('## Summary\n\nA verified lifecycle improvement.\n\n## Validation\n\nOffline evaluation passed.\n\n'
            '## 中文摘要\n\n生命周期验证已通过。\n')
    body.write_text(good, encoding='utf-8')
    title = 'feat: evaluate lifecycle recovery and stale evidence'
    valid = scenario.command('valid PR body', [sys.executable, '-B', str(PR_LINTER), '--title', title, str(body)],
                             cwd=ROOT, expected_code=0)
    scenario.check('valid PR body has no errors', '0 error(s)' in valid.stdout.decode('utf-8'), True)
    body.write_text(good.replace('A verified lifecycle improvement.', r'Local copy at D:\private\checkout.'),
                    encoding='utf-8')
    invalid = scenario.command('private path rejected',
                               [sys.executable, '-B', str(PR_LINTER), '--title', title, str(body)],
                               cwd=ROOT, expected_code=1)
    scenario.check('private path error emitted', 'local path or host' in invalid.stdout.decode('utf-8'), True)
    return scenario.data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        help='Write the JSON receipt to this path. Without this option, write JSON to stdout only.')
    args = parser.parse_args(argv)

    out = args.output.absolute() if args.output else None
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
    git_env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_TERMINAL_PROMPT='0')
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], env=git_env,
                          stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=10, check=True).stdout.decode('ascii').strip()
    version = git_version(git_env)
    evaluation_root = ROOT / 'evaluation'
    evaluation_root.mkdir(parents=True, exist_ok=True)
    scenarios = []
    try:
        with tempfile.TemporaryDirectory(prefix='.lifecycle-eval-', dir=evaluation_root) as temp_name:
            fixture_root = Path(temp_name)
            lifecycle_rows = []
            try:
                lifecycle_flow(fixture_root, lifecycle_rows)
            except EvaluationFailure as error:
                scenarios.extend(lifecycle_rows)
                scenarios.append({'name': 'lifecycle_flow_aborted', 'status': 'FAIL',
                                  'reason': str(error)})
            else:
                scenarios.extend(lifecycle_rows)
            try:
                scenarios.append(adaptive_reference_flow(fixture_root))
            except EvaluationFailure as error:
                scenarios.append({'name': 'adaptive_reference_discovery_stays_offline', 'status': 'FAIL',
                                  'reason': str(error)})
            try:
                scenarios.append(pr_lint_flow(fixture_root))
            except EvaluationFailure as error:
                scenarios.append({'name': 'pr_linter_accepts_valid_body_and_rejects_private_path', 'status': 'FAIL',
                                  'reason': str(error)})
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        scenarios.append({'name': 'fixture_setup', 'status': 'FAIL', 'reason': type(error).__name__})

    result = {
        'schema': 1,
        'evaluation': 'specialized offline lifecycle acceptance',
        'subject': {
            'repository': 'Engineering-Infrastructure',
            'commit': head,
            'lifecycle_source_sha256': hashlib.sha256(LIFECYCLE.read_bytes()).hexdigest(),
            'evaluator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        'environment': {'python': sys.version.split()[0], 'git': version, 'platform': platform.system()},
        'method': {
            'fixture_git_commit_dates': FIXED_DATE,
            'fixture_scope': 'temporary local Git worktrees under evaluation/; removed on exit',
            'network': 'not used; adaptive discovery is forced through a closed loopback proxy',
            'model_trials': 'not run',
            'timings': 'not collected',
            'scope_limit': 'Fixture-backed CLI acceptance on this Windows host; no user deployment, GUI session, or cross-platform claim.',
            'comparison_baselines': [
                'clean git status alone versus receipt-bound named-ref freshness',
                'installed and archived artifact existence alone versus runtime identity probe',
            ],
        },
        'scenarios': scenarios,
        'summary': {
            'passed': sum(row.get('status') == 'PASS' for row in scenarios),
            'failed': sum(row.get('status') == 'FAIL' for row in scenarios),
            'checks': sum(len(row.get('checks', [])) for row in scenarios),
            'commands': sum(len(row.get('commands', [])) for row in scenarios),
            'overall': 'PASS' if scenarios and all(row.get('status') == 'PASS' for row in scenarios) else 'FAIL',
        },
    }
    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    if out:
        out.write_text(serialized, encoding='utf-8')
        display = str(out.relative_to(ROOT)) if out.is_relative_to(ROOT) else str(out)
        print(json.dumps(result['summary'], ensure_ascii=False, sort_keys=True))
        print('results: ' + display)
    else:
        sys.stdout.write(serialized)
    return 0 if result['summary']['overall'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
