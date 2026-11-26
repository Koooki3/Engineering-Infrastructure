import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).resolve().parents[1] / 'engineering-workflow/scripts/lifecycle.py'

ADAPTER = """import hashlib, json, os, subprocess, sys
from pathlib import Path
op, root = sys.argv[1], Path(sys.argv[2])
installed = root / 'installed.json'
if op == 'build':
    if (root / 'fail-build').exists():
        sys.exit(2)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    Path('artifact.json').write_text(json.dumps({'sha': head, 'instance': 'fixture-cli'}))
elif op == 'test':
    assert not (root / 'fail-test').exists()
    assert json.loads(Path('artifact.json').read_text())['instance'] == 'fixture-cli'
elif op == 'install':
    installed.write_bytes(Path(os.environ['EWK_DEPLOY_ARTIFACT']).read_bytes())
    if (root / 'fail-install-once').exists():
        (root / 'fail-install-once').unlink()
        sys.exit(3)
elif op == 'stop':
    installed.unlink(missing_ok=True)
elif op == 'probe':
    if installed.exists():
        output = json.loads(installed.read_bytes())
        output.update(active=True, healthy=True, sha256=hashlib.sha256(installed.read_bytes()).hexdigest())
        print(json.dumps(output))
    else:
        print(json.dumps({'active': False}))
"""


class ProjectLifecycle(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.repo = self.root / 'source'
        self.repo.mkdir()
        self.git('init', '-b', 'main')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'user.name', 'Lifecycle Fixture')
        self.write('.gitignore', 'artifact.json\n')
        self.write('base', 'starting content\n')
        self.base = self.add('base')
        self.state = self.repo / '.git/ewk-lifecycle'

    def git(self, *args, cwd=None):
        out = subprocess.run(['git', '-C', str(cwd or self.repo), *args], capture_output=True,
                             check=True, timeout=40)
        return out.stdout.decode().strip()

    def cli(self, *args, blocked=False):
        out = subprocess.run([sys.executable, '-B', str(CLI), '--repo', str(self.repo), *args],
                             capture_output=True, timeout=100)
        if blocked:
            self.assertEqual(out.returncode, 1, out.stderr.decode())
            return out.stderr.decode()
        self.assertEqual(out.returncode, 0, out.stderr.decode())
        return json.loads(out.stdout)

    def write(self, name, body):
        (self.repo / name).write_text(body, encoding='utf-8')

    def add(self, message):
        self.git('add', '.')
        self.git('commit', '-m', message)
        return self.git('rev-parse', 'HEAD')

    def branch(self, name, base, path, body):
        self.git('switch', '-c', name, base)
        self.write(path, body)
        tip = self.add(name)
        self.git('switch', 'main')
        return tip

    def prepare(self, name, *args, base='refs/heads/main'):
        return self.cli('integrate', name, '--path', str(self.root / name), '--owner', 'fixture',
                        '--base', base, *args)

    def setup_contract(self):
        self.state.mkdir(parents=True, exist_ok=True)
        script = self.root / 'adapter.py'
        script.write_text(ADAPTER, encoding='utf-8')
        stages = {op: [sys.executable, str(script), op, str(self.root)]
                  for op in ('build', 'test', 'install', 'probe', 'stop')}
        (self.state / 'contract.json').write_text(json.dumps({'schema': 1, 'artifact': 'artifact.json', **stages}),
                                                encoding='utf-8')

    def test_fork_fetch_status_cache_and_failure_preserve_refs(self):
        self.assertEqual(self.cli('inspect')['remotes'], {})
        upstream = self.root / 'upstream'
        self.git('clone', str(self.repo), str(upstream))
        self.git('config', 'user.email', 'fixture@example.invalid', cwd=upstream)
        self.git('config', 'user.name', 'Upstream Fixture', cwd=upstream)
        (upstream / 'new').write_text('upstream')
        self.git('add', 'new', cwd=upstream)
        self.git('commit', '-m', 'change upstream', cwd=upstream)
        self.git('remote', 'add', 'upstream', str(upstream))
        self.assertFalse(self.cli('fetch', 'upstream')['cached'])
        self.git('branch', '--set-upstream-to', 'upstream/main')
        self.assertEqual(self.cli('inspect')['ahead_behind'], [0, 1])
        self.assertTrue(self.cli('fetch', 'upstream')['cached'])
        self.assertEqual(self.cli('compare', 'refs/heads/main', 'refs/remotes/upstream/main')['ahead_behind'], [0, 1])
        self.git('switch', '-c', 'sync-view', self.base)
        advanced = self.cli('fast-forward', '--expected', self.base, '--target', 'refs/remotes/upstream/main')
        self.assertNotEqual(advanced['head'], self.base)
        self.git('switch', 'main')
        self.write('local', 'downstream')
        local = self.add('diverge')
        self.assertEqual(self.cli('inspect')['ahead_behind'], [1, 1])
        self.cli('fast-forward', '--expected', local, '--target', 'refs/remotes/upstream/main', blocked=True)
        self.git('remote', 'set-url', 'upstream', str(self.root / 'missing'))
        self.cli('fetch', 'upstream', '--max-age', '0', blocked=True)
        self.assertEqual(self.git('rev-parse', 'HEAD'), local)
        self.assertEqual(self.cli('inspect')['ahead_behind'], [1, 1])

    def test_equivalence_dependency_exclusion_and_dirty_source_protection(self):
        first = self.branch('feature', self.base, 'feature', 'feature content\n')
        second = self.branch('dependent', first, 'dependent', 'depends on feature\n')
        self.branch('experiment', self.base, 'experimental', 'not ready\n')
        self.write('feature', 'feature content\n')
        self.add('equivalent upstream feature')
        self.write('uncommitted', 'preserve this\n')
        before = self.git('status', '--porcelain')
        task = self.prepare('candidate', '--include', 'refs/heads/feature', self.base,
                            '--include', 'refs/heads/dependent', first,
                            '--exclude', 'refs/heads/experiment', 'unvalidated')
        self.assertEqual(task['skipped'], [first])
        self.assertEqual([row['source_sha'] for row in task['applied']], [second])
        self.assertTrue((self.root / 'candidate/dependent').is_file())
        self.assertFalse((self.root / 'candidate/experimental').exists())
        self.assertEqual(self.git('status', '--porcelain'), before)
        self.assertEqual(self.git('rev-parse', 'dependent'), second)

    def test_conflict_never_mutates_primary_and_is_blocked(self):
        other = self.branch('feature', self.base, 'base', 'feature\n')
        self.write('base', 'upstream\n')
        before = self.add('different upstream')
        self.cli('integrate', 'conflict', '--path', str(self.root / 'conflict'), '--owner', 'fixture',
                 '--base', 'refs/heads/main', '--include', other, self.base, blocked=True)
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)
        task = json.loads((self.state / 'tasks/conflict.json').read_bytes())
        self.assertEqual(task['phase'], 'BLOCKED')
        self.cli('cleanup', 'conflict', '--released', '--apply', blocked=True)

    def test_runtime_binding_gates_and_recovery(self):
        self.setup_contract()
        first = self.prepare('first')
        good = self.cli('deploy', 'first')
        self.assertEqual(good['observed']['sha'], first['candidate_sha'])
        self.assertEqual(good['sha256'], hashlib.sha256((self.root / 'installed.json').read_bytes()).hexdigest())
        self.assertEqual(self.cli('deploy', 'first')['sha256'], good['sha256'])
        self.assertEqual(self.cli('runtime')['freshness'], 'CURRENT')
        self.write('next', 'next version')
        self.add('next')
        self.assertEqual(self.cli('runtime')['freshness'], 'STALE_INPUTS')
        self.prepare('bad-build')
        (self.root / 'fail-build').touch()
        self.cli('deploy', 'bad-build', blocked=True)
        (self.root / 'fail-build').unlink()
        self.prepare('bad-test')
        (self.root / 'fail-test').touch()
        self.cli('deploy', 'bad-test', blocked=True)
        (self.root / 'fail-test').unlink()
        self.prepare('bad-install')
        (self.root / 'fail-install-once').touch()
        self.cli('deploy', 'bad-install', blocked=True)
        self.assertFalse((self.state / 'pending.json').exists())
        self.assertEqual(self.cli('runtime')['sha'], good['sha'])
        self.prepare('second')
        new = self.cli('deploy', 'second')
        self.assertNotEqual(new['sha'], good['sha'])
        self.assertIn('Integration input moved', self.cli('deploy', 'first', blocked=True))
        self.assertEqual(self.cli('rollback')['sha'], good['sha'])
        (self.root / 'installed.json').write_text('{}')
        self.cli('runtime', blocked=True)

    def test_same_commit_reconciles_pins_and_revalidates_changed_adapter(self):
        self.setup_contract()
        self.prepare('original')
        first = self.cli('deploy', 'original')
        self.git('branch', 'alternate', self.base)
        self.prepare('renamed-input', base='refs/heads/alternate')
        self.assertEqual(self.cli('deploy', 'renamed-input')['pins'], {'refs/heads/alternate': self.base})
        with (self.root / 'adapter.py').open('a') as script:
            script.write('\n# reviewed adapter revision\n')
        self.prepare('changed-input', base='refs/heads/alternate')
        (self.root / 'fail-test').touch()
        self.cli('deploy', 'changed-input', blocked=True)
        self.assertEqual(json.loads((self.state / 'stable.json').read_bytes())['sha256'], first['sha256'])
        (self.root / 'fail-test').unlink()
        self.prepare('retry-input', base='refs/heads/alternate')
        refreshed = self.cli('deploy', 'retry-input')
        self.assertEqual(first['sha256'], refreshed['sha256'])
        self.assertNotEqual(first['build_inputs'], refreshed['build_inputs'])
        self.assertNotEqual(refreshed['previous']['record_id'], refreshed['record_id'])

    def test_git_mutations_preserve_project_hooks(self):
        self.git('switch', '-c', 'target')
        self.write('next', 'advance')
        target = self.add('advance')
        self.git('switch', 'main')
        hooks = self.repo / '.git/hooks'
        hook = hooks / 'reference-transaction'
        hook.write_bytes(b'#!/bin/sh\nif [ "$1" = prepared ]; then exit 1; fi\n')
        hook.chmod(0o755)
        self.cli('fast-forward', '--expected', self.base, '--target', target, blocked=True)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.base)

    def test_contract_preview_and_delivery_gate(self):
        self.write('pyproject.toml', '# tracked build entry')
        base = self.add('native tool metadata')
        self.prepare('reviewed')
        self.setup_contract()
        proposed = self.root / 'proposal.json'
        (self.state / 'contract.json').replace(proposed)
        self.assertIn('pyproject.toml', self.cli('contract')['tracked_entrypoints'])
        args = ('contract', '--task', 'reviewed', '--from-json', str(proposed))
        self.assertEqual(self.cli(*args)['status'], 'PREVIEW')
        self.assertFalse((self.state / 'contract.json').exists())
        self.assertEqual(self.cli(*args, '--apply')['status'], 'CONFIGURED')
        self.cli('gate', '--task', 'reviewed', '--runtime', blocked=True)
        self.cli('deploy', 'reviewed')
        self.assertEqual(self.cli('gate', '--base', base, '--task', 'reviewed', '--runtime')['status'], 'PASS')
        self.cli('gate', '--task', 'reviewed', '--close', blocked=True)
        (self.root / 'reviewed/artifact.json').unlink()
        self.cli('cleanup', 'reviewed', '--released', '--apply')
        self.assertEqual(self.cli('gate', '--task', 'reviewed', '--close')['checks']['worktree'], 'PASS')

    def test_released_owned_cleanup_archives_and_leaves_stash(self):
        self.prepare('clean')
        tree = self.root / 'clean'
        self.write('scratch', 'stash stays')
        self.git('stash', 'push', '--include-untracked')
        self.cli('cleanup', 'clean', '--apply', blocked=True)
        (tree / 'user.txt').touch()
        self.cli('cleanup', 'clean', '--released', '--apply', blocked=True)
        (tree / 'user.txt').unlink()
        (tree / 'artifact.json').touch()
        self.cli('cleanup', 'clean', '--released', '--apply', blocked=True)
        (tree / 'artifact.json').unlink()
        self.assertFalse(self.cli('cleanup', 'clean', '--released')['applied'])
        result = self.cli('cleanup', 'clean', '--released', '--apply')
        self.assertFalse(tree.exists())
        self.assertEqual(self.git('rev-parse', result['archive']), self.base)
        self.assertEqual(self.cli('inspect')['stash_count'], 1)
        self.assertFalse(self.cli('cleanup', 'clean', '--released', '--apply')['applied'])

    def test_checkpoint_and_knowledge_stay_local(self):
        source = self.root / 'context.json'
        data = {key: 'required fact' for key in ('owner','goal','constraints','acceptance','decisions','evidence','next')}
        source.write_text(json.dumps(data))
        self.cli('checkpoint', 'task', '--from-json', str(source))
        self.assertFalse(self.cli('checkpoint', 'task')['head_drift'])
        self.write('changed', 'new commit')
        self.add('new commit')
        self.assertTrue(self.cli('checkpoint', 'task')['head_drift'])
        data = {key: 'observed fact' for key in ('observation','evidence','root_cause','invariant','mechanism','verification')}
        source.write_text(json.dumps(data))
        self.assertEqual(self.cli('knowledge', 'lesson', '--from-json', str(source))['status'], 'PROPOSED')
        self.cli('knowledge', 'duplicate', '--from-json', str(source), blocked=True)
        evidence = self.root / 'checks.json'
        subprocess.run([sys.executable, '-B', str(CLI.with_name('ewk.py')), 'run', '--evidence', str(evidence),
                        '--id', 'verified', '--', sys.executable, '-c', 'print("green")'],
                       check=True, capture_output=True, cwd=self.repo, timeout=30)
        self.assertEqual(self.cli('knowledge', 'lesson', '--evidence', str(evidence),
                                  '--require', 'verified')['status'], 'VERIFIED')
        proposal = self.cli('promotion-plan', 'lesson', '--summary', 'Verify inputs before reuse.')
        self.assertEqual(proposal['status'], 'REVIEW_REQUIRED')
        self.assertNotIn('evidence', proposal)
        self.assertEqual(self.cli('knowledge', 'lesson', '--archive')['status'], 'ARCHIVED')
        self.assertEqual(self.git('status', '--porcelain'), '')
