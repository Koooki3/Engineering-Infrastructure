"""Run trusted controls for one pinned Terminal-Bench task in WSL."""

import argparse
from collections import Counter
import csv
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import tempfile
from urllib.request import urlopen

import pilot
from v02 import sandbox


REVISION = '12b7565679ce5006230b820666353673a133db93'
TASK = 'log-summary-date-ranges'
SOURCE = f'https://raw.githubusercontent.com/harbor-framework/terminal-bench-2-1/{REVISION}/tasks/{TASK}'


def download(name):
    with urlopen(f'{SOURCE}/{name}', timeout=20) as response:
        return response.read(100_000).decode('utf-8')


def reference_control(workspace, grader):
    """Exercise unchanged acceptance assertions against an independent tally."""
    command = ['/usr/bin/python3', '-I', '-B', '-c', grader]
    failed_empty = sandbox.run(workspace, command)
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
    verified = sandbox.run(workspace, command)
    task_prompt_sha256 = pilot.digest(result_path.read_bytes())
    tally(totals + inclusive_lower_bound)
    alternative = sandbox.run(workspace, command)
    return {'missing_artifact_rejected': failed_empty.returncode != 0,
            'reference_tally_accepted': verified.returncode == 0,
            'reference_csv_sha256': task_prompt_sha256,
            'inclusive_lookback_lower_bound_accepted': alternative.returncode == 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--publish', type=Path)
    parser.add_argument('--preflight', action='store_true', help='Exercise the upstream assertions without model calls')
    args = parser.parse_args()
    if not args.preflight:
        parser.error('Live v0.1 evaluation is retired. Use --preflight for the trusted controls.')
    args.out.mkdir(parents=True, mode=0o700)
    names = ('instruction.md', 'environment/log_generator_deterministic.py', 'tests/test_outputs.py')
    instruction, generator, verifier = originals = [download(name) for name in names]
    result = {'benchmark': 'Terminal-Bench 2.1', 'classification': 'adapted verifier preflight',
              'task': TASK, 'revision': REVISION, 'subject': pilot.SUBJECT, 'runs': [],
              'source_hashes': {name: hashlib.sha256(content.encode()).hexdigest()
                                for name, content in zip(names, originals)}}
    with tempfile.TemporaryDirectory(prefix='ei-terminal-subset-') as folder:
        base = Path(folder)
        initial = base / 'input'
        initial.mkdir()
        generated = sandbox.run(initial, ['/usr/bin/python3', '-I', '-B', '-c',
                                          generator.replace('/app/logs', 'logs')])
        if generated.returncode:
            raise RuntimeError(f'Pinned generator failed in the sandbox ({generated.returncode})')
        inputs = {p.name: pilot.digest(p.read_bytes()) for p in (initial / 'logs').glob('*.log')}
        if not inputs:
            raise ValueError('The pinned log generator produced no input files')
        result['input_count'] = len(inputs)
        result['input_manifest_sha256'] = pilot.digest(json.dumps(inputs, sort_keys=True).encode())
        # Keep the original verifier and all expected counts. Adapt only the /app output path.
        grader = verifier.replace('/app/summary.csv', 'summary.csv')
        grader += '\n\ntest_summary_file_exists()\ntest_summary_structure_and_counts()\n'
        result['reference_control'] = reference_control(initial, grader)
        encoded = json.dumps(result, indent=2) + '\n'
        pilot.write(args.out / 'result.json', encoded)
        if args.publish:
            pilot.write(args.publish, encoded)
        print(json.dumps(result['reference_control']))
        if not all(result['reference_control'][key] for key in
                   ('missing_artifact_rejected', 'reference_tally_accepted')):
            raise SystemExit(1)


if __name__ == '__main__':
    main()
