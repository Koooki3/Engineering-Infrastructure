"""Run one pinned Terminal-Bench task with relative workspace paths in WSL."""

import argparse
from collections import Counter
import csv
from datetime import date
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
from urllib.request import urlopen

import pilot


REVISION = '12b7565679ce5006230b820666353673a133db93'
TASK = 'log-summary-date-ranges'
SOURCE = f'https://raw.githubusercontent.com/harbor-framework/terminal-bench-2-1/{REVISION}/tasks/{TASK}'


def download(name):
    with urlopen(f'{SOURCE}/{name}', timeout=20) as response:
        return response.read(100_000).decode('utf-8')


def reference_control(workspace, grader):
    """Exercise unchanged acceptance assertions against an independent tally."""
    env = dict(os.environ)
    command = [sys.executable, '-B', '-c', grader]
    failed_empty = pilot.run(command, workspace, env, check=False, capture_output=True)
    reference = date(2025, 8, 12)
    month_start = reference.replace(day=1)
    totals = Counter()
    severities = ('ERROR', 'WARNING', 'INFO')
    periods = ('today', 'last_7_days', 'last_30_days', 'month_to_date', 'total')
    inclusive_lower_bound = Counter()
    for path in (workspace / 'logs').glob('*.log'):
        day = date.fromisoformat(path.name.split('_', 1)[0])
        age = (reference - day).days
        counts = Counter(re.findall(r'^[^\[\]\r\n]+ \[(ERROR|WARNING|INFO)\]', path.read_text(encoding='utf-8'), re.M))
        applies = (age == 0, 0 <= age < 7, 0 <= age < 30, month_start <= day <= reference, True)
        for period, included in zip(periods, applies):
            if included:
                totals.update({(period, severity): count for severity, count in counts.items()})
        if age in (7, 30):
            period = 'last_7_days' if age == 7 else 'last_30_days'
            inclusive_lower_bound.update({(period, severity): count for severity, count in counts.items()})
    result_path = workspace / 'summary.csv'

    def tally(values):
        with result_path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.writer(handle)
            writer.writerow(('period', 'severity', 'count'))
            writer.writerows((period, severity, values[period, severity])
                             for period in periods for severity in severities)

    tally(totals)
    verified = pilot.run(command, workspace, env, check=False, capture_output=True)
    task_prompt_sha256 = pilot.digest(result_path.read_bytes())
    tally(totals + inclusive_lower_bound)
    alternative = pilot.run(command, workspace, env, check=False, capture_output=True)
    return {'missing_artifact_rejected': failed_empty.returncode != 0,
            'reference_tally_accepted': verified.returncode == 0,
            'reference_csv_sha256': task_prompt_sha256,
            'inclusive_lookback_lower_bound_accepted': alternative.returncode == 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--publish', type=Path)
    parser.add_argument('--codex', default='codex')
    parser.add_argument('--auth-file', type=Path, default=Path.home() / '.codex/auth.json')
    parser.add_argument('--preflight', action='store_true', help='Exercise the upstream assertions without model calls')
    args = parser.parse_args()
    cli = shutil.which(args.codex)
    if not args.preflight and (not cli or not args.auth_file.is_file()):
        parser.error('Use an installed, signed-in file-backed Codex CLI')
    args.out.mkdir(parents=True, mode=0o700)
    names = ('instruction.md', 'environment/log_generator_deterministic.py', 'tests/test_outputs.py')
    instruction, generator, verifier = originals = [download(name) for name in names]
    version = None if args.preflight else pilot.run(
        [cli, '--version'], pilot.ROOT, dict(os.environ), text=True, capture_output=True).stdout.strip()
    result = {'benchmark': 'Terminal-Bench 2.1', 'classification': 'adapted task', 'task': TASK,
              'revision': REVISION, 'subject': pilot.SUBJECT, 'cli': version, 'model': pilot.MODEL,
              'effort': pilot.EFFORT, 'timeout_s': 180, 'order': ['D', 'A'],
              'source_hashes': {name: hashlib.sha256(content.encode()).hexdigest()
                                for name, content in zip(names, originals)}, 'runs': []}
    with tempfile.TemporaryDirectory(prefix='ei-terminal-subset-') as folder:
        base = Path(folder)
        distribution, initial = base / 'subject', base / 'input'
        distribution.mkdir()
        initial.mkdir()
        pilot.run(['tar', '-xf', '-'], distribution, dict(os.environ), input=pilot.run(
            ['git', 'archive', pilot.SUBJECT], pilot.ROOT, dict(os.environ), capture_output=True).stdout)
        pilot.run([sys.executable, '-B', '-c', generator.replace('/app/logs', 'logs')], initial,
                  dict(os.environ), capture_output=True)
        inputs = {p.name: pilot.digest(p.read_bytes()) for p in (initial / 'logs').glob('*.log')}
        if not inputs:
            raise ValueError('The pinned log generator produced no input files')
        result['input_count'] = len(inputs)
        result['input_manifest_sha256'] = pilot.digest(json.dumps(inputs, sort_keys=True).encode())
        # Keep the original verifier and all expected counts. Adapt only the /app output path.
        grader = verifier.replace('/app/summary.csv', 'summary.csv')
        grader += '\n\ntest_summary_file_exists()\ntest_summary_structure_and_counts()\n'
        if args.preflight:
            result['classification'] = 'adapted verifier preflight'
            result['order'] = []
            result['reference_control'] = reference_control(initial, grader)
            encoded = json.dumps(result, indent=2) + '\n'
            pilot.write(args.out / 'result.json', encoded)
            if args.publish:
                pilot.write(args.publish, encoded)
            print(json.dumps(result['reference_control']))
            if not all(result['reference_control'][key] for key in
                       ('missing_artifact_rejected', 'reference_tally_accepted')):
                raise SystemExit(1)
            return
        for condition in result['order']:
            trial = base / condition
            repo, home = trial / 'workspace', trial / 'home'
            trial.mkdir()
            shutil.copytree(initial, repo)
            codex_home = home / '.codex'
            codex_home.mkdir(parents=True, mode=0o700)
            (codex_home / 'auth.json').symlink_to(args.auth_file.absolute())
            env = {key: os.environ[key] for key in ('PATH', 'LANG', 'LC_ALL', 'HTTPS_PROXY', 'HTTP_PROXY', 'NO_PROXY')
                   if key in os.environ}
            env.update(HOME=str(home), CODEX_HOME=str(codex_home), XDG_CONFIG_HOME=str(home / '.config'),
                       XDG_CACHE_HOME=str(home / '.cache'), XDG_DATA_HOME=str(home / '.local/share'),
                       XDG_STATE_HOME=str(home / '.local/state'), TMPDIR=str(trial))
            deployed = None
            if condition == 'D':
                deployed = json.loads(pilot.run([sys.executable, '-B', 'tools/setup.py', 'apply', '--agents', 'codex'],
                                                distribution, env, capture_output=True).stdout)['revision']
            prompt = (instruction.replace('/app/logs', './logs').replace('/app/summary.csv', './summary.csv')
                      + '\nUse the local workspace only. Do not look up the answer or verifier.')
            log = args.out / f'{condition}.jsonl'
            start_utc, start = pilot.now(), time.monotonic()
            with log.open('wb') as stdout, (args.out / f'{condition}.stderr').open('wb') as stderr:
                try:
                    process = pilot.run([cli, '-a', 'never', 'exec', '--ephemeral', '--json', '-s', 'workspace-write',
                                         '--skip-git-repo-check', '-C', str(repo), '-m', pilot.MODEL,
                                         '-c', f'model_reasoning_effort="{pilot.EFFORT}"', prompt], repo, env,
                                        check=False, timeout=180, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)
                    code = process.returncode
                except subprocess.TimeoutExpired:
                    code = 124
            elapsed, ended = time.monotonic() - start, pilot.now()
            outcomes, tokens, invoked, activity = pilot.event_metrics(log)
            artifact = repo / 'summary.csv'
            safe = not artifact.is_symlink() and artifact.is_file()
            checked = pilot.run([sys.executable, '-B', '-c', grader], repo, env, check=False, capture_output=True) if safe else None
            unchanged = inputs == {p.name: pilot.digest(p.read_bytes()) for p in (repo / 'logs').glob('*.log')}
            accepted = bool(checked and not checked.returncode and unchanged)
            status = ('TIMEOUT' if code == 124 else 'CLI_FAILURE' if not activity and 'turn.completed' not in outcomes else
                      'PASS' if code == 0 and 'turn.completed' in outcomes and accepted else 'FAIL')
            row = {'condition': condition, 'started_utc': start_utc, 'ended_utc': ended,
                   'distribution': deployed, 'exit_code': code, 'seconds': round(elapsed, 3),
                   'tokens': tokens, 'core_invoked': invoked, 'status': status,
                   'inputs_unchanged': unchanged, 'original_assertions_passed': bool(checked and not checked.returncode),
                   'csv_sha256': pilot.digest(artifact.read_bytes()) if safe else None}
            result['runs'].append(row)
            print(condition, status, round(elapsed, 1), flush=True)
            pilot.write(args.out / 'result.json', json.dumps(result, indent=2) + '\n')
    if args.publish:
        pilot.write(args.publish, json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
