"""Publish allowlisted pilot evidence, summarize outcomes, or render the result figure."""

import argparse
import json
from pathlib import Path
import random
import re
import statistics


METADATA = {'protocol', 'subject', 'runner_sha256', 'lock_sha256', 'core', 'agent', 'model', 'effort',
            'timeout_s', 'platform', 'python', 'git', 'order'}
ROWS = {'id', 'task', 'condition', 'initial_sha', 'distribution', 'started_utc', 'ended_utc',
        'seconds', 'setup_s', 'verify_s', 'exit_code', 'status', 'oracle_pass', 'verifier_error',
        'tokens', 'core_invoked', 'human_interventions', 'git_diff_sha256', 'artifacts'}
LABELS = {'latest': 'Out-of-order updates', 'preview': 'Preview preserves data', 'pr': 'PR draft accuracy',
          'freshness': 'Deployment freshness', 'integrate': 'Dirty-checkout integration',
          'adapter': 'Deployment receipt integrity'}


def collect(folder):
    metadata = json.loads((folder / 'metadata.json').read_text(encoding='utf-8'))
    runs = [json.loads(line) for line in (folder / 'runs.jsonl').read_text(encoding='utf-8').splitlines()]
    return {'metadata': metadata, 'runs': runs}


def validate(data):
    assert set(data['metadata']) == METADATA, 'Unexpected metadata fields'
    runs = data['runs']
    expected = [f'{task}-{condition}' for task, options in data['metadata']['order'] for condition in options]
    assert [row['id'] for row in runs] == expected[:len(runs)], 'Unexpected attempt order'
    for row in runs:
        assert set(row) == ROWS, 'Unexpected receipt fields'
        assert row['id'] == f"{row['task']}-{row['condition']}"
        assert row['seconds'] > 0 and row['setup_s'] >= 0 and row['verify_s'] >= 0
        assert row['status'] in {'PASS', 'FAIL', 'TIMEOUT', 'CLI_FAILURE'}
        assert row['status'] != 'PASS' or (row['oracle_pass'] and row['exit_code'] == 0)
        assert row['artifacts'].keys() <= {'candidate_tree', 'PR.md', 'check.py'}
        assert all(re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', value) for value in row['artifacts'].values())
        if row['tokens'] is not None:
            assert {'input_tokens', 'cached_input_tokens', 'output_tokens'} <= row['tokens'].keys()
            assert row['tokens'].keys() <= {'input_tokens', 'cached_input_tokens', 'output_tokens',
                                            'cache_write_input_tokens', 'reasoning_output_tokens'}
            assert all(isinstance(value, int) and value >= 0 for value in row['tokens'].values())
    by_task = {}
    for row in runs:
        by_task.setdefault(row['task'], []).append(row)
    assert all(len({row['initial_sha'] for row in block}) == 1 for block in by_task.values())
    distributions = {row['distribution'] for row in runs if row['condition'] == 'D'}
    assert len(distributions) <= 1 and None not in distributions


def summary(data):
    validate(data)
    runs = data['runs']
    by_id = {row['id']: row for row in runs}
    groups = {}
    for condition in 'ABD':
        rows = [row for row in runs if row['condition'] == condition]
        if not rows:
            continue
        usage = [row['tokens'] for row in rows if row['tokens'] is not None]
        groups[condition] = {
            'attempts': len(rows), 'passes': sum(row['status'] == 'PASS' for row in rows),
            'total_seconds': round(sum(row['seconds'] for row in rows), 3),
            'setup_seconds': round(sum(row['setup_s'] for row in rows), 3),
            'verification_seconds': round(sum(row['verify_s'] for row in rows), 3),
            'median_seconds': statistics.median(row['seconds'] for row in rows),
            'token_records': len(usage),
            'tokens': {key: sum(record[key] for record in usage) for key in
                       ('input_tokens', 'cached_input_tokens', 'output_tokens')} if usage else None,
        }
    pairs = {}
    for left, right in ('DA', 'DB', 'BA'):
        pair_rows = [(by_id[f'{task}-{left}'], by_id[f'{task}-{right}']) for task in LABELS
                     if f'{task}-{left}' in by_id and f'{task}-{right}' in by_id]
        if not pair_rows:
            continue
        differences = [int(a['status'] == 'PASS') - int(b['status'] == 'PASS') for a, b in pair_rows]
        contrasts = {'pairs': len(differences), 'wins': differences.count(1), 'losses': differences.count(-1),
                     'ties': differences.count(0), 'success_difference': statistics.mean(differences),
                     'median_seconds_difference': statistics.median(a['seconds'] - b['seconds'] for a, b in pair_rows)}
        if len(differences) >= 5 and len(set(differences)) > 1:
            rng = random.Random(20261128)
            values = sorted(statistics.mean(rng.choices(differences, k=len(differences))) for _ in range(10000))
            contrasts['task_bootstrap_95'] = [values[250], values[9749]]
        pairs[left + '-' + right] = contrasts
    return {'groups': groups, 'paired': pairs}


def chart(data, destination):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    validate(data)
    colors = {'A': '#274d81', 'B': '#926112', 'D': '#087966'}
    names = {'A': 'Native', 'B': 'Prompt only', 'D': 'Full infrastructure'}
    fg, dim, bg = '#172941', '#465771', '#f7f9fc'
    fig, (left, right) = plt.subplots(1, 2, width_ratios=(1, 1.42), figsize=(11, 4.9), facecolor=bg)
    fig.subplots_adjust(left=.245, right=.955, bottom=.20, top=.74, wspace=.28)
    fig.text(.032, .91, 'What changed with the harness?', fontsize=22, weight='bold', color=fg)
    fig.text(.033, .84, 'EI-Eval v0.1  /  Matched Codex trials in fresh WSL workspaces', fontsize=11, color=dim)
    offsets = {'A': -.19, 'B': 0, 'D': .19}
    for axis in (left, right):
        axis.set_facecolor(bg)
        axis.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
        axis.set_ylim(len(LABELS) - .48, -.53)
        axis.tick_params(colors=dim, length=0, pad=10)
        for i in range(len(LABELS)):
            if i % 2 == 0:
                axis.axhspan(i - .48, i + .48, color='#eaf0f7', zorder=0)
    for row in data['runs']:
        condition = row['condition']
        y = list(LABELS).index(row['task']) + offsets[condition]
        success = row['status'] == 'PASS'
        marker = 'o' if success else '^' if row['status'] == 'CLI_FAILURE' else 'x'
        style = {'color': colors[condition], 'marker': marker, 's': 39, 'zorder': 3}
        left.scatter('Pass' if success else 'Unsuccessful', y, **style)
        right.scatter(row['seconds'], y, **style)
    handles = [Line2D([], [], color=color, marker='o', linestyle='', label=names[key])
               for key, color in colors.items()]
    left.set_title('Artifact acceptance', loc='left', weight='bold', color=fg, fontsize=11)
    left.set_yticks(range(len(LABELS)), LABELS.values())
    left.set_xticks(['Unsuccessful', 'Pass'])
    left.set_xlim(-.5, 1.5)
    right.set_title('Session time (seconds)', loc='left', weight='bold', color=fg, fontsize=11)
    right.set_yticks([])
    right.set_xlim(0, max(10, max(row['seconds'] for row in data['runs']) * 1.08))
    right.grid(axis='x', linewidth=.6, color='#cbd5e3')
    fig.legend(handles=handles, loc='lower left', bbox_to_anchor=(.025, .077), ncol=3, frameon=False)
    fig.text(.033, .037, 'One mark per attempt. Prompt only covers two tasks. × unsuccessful, ▲ CLI startup failure.',
             color=dim, fontsize=9)
    fig.savefig(destination, dpi=160, facecolor=bg)


def markdown(data, result):
    ids = {row['id']: row for row in data['runs']}
    lines = ['# EI-Eval v0.1 results', '',
             'Generated from [pilot-results.json](pilot-results.json) with [analyze.py](analyze.py).', '',
             '| Task | Native A | Prompt only B | Full D |',
             '| --- | --- | --- | --- |']
    for name, label in LABELS.items():
        cells = []
        for condition in 'ABD':
            row = ids.get(f'{name}-{condition}')
            cells.append(f"{row['status']} · {row['seconds']:.1f} s" if row else 'Not scheduled or not reached')
        lines.append(f"| {label} | {' | '.join(cells)} |")
    lines += ['', '## Usage across all attempts', '',
              '| Condition | Passed / attempts | Session time (s) | Setup (s) | Verifier (s) | Median session (s) | Input tokens | Cached input | Output tokens |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for condition, group in result['groups'].items():
        usage = group['tokens']
        counts = ' / '.join(str(group[key]) for key in ('passes', 'attempts'))
        times = ' | '.join(f"{group[key]:.1f}" for key in
                           ('total_seconds', 'setup_seconds', 'verification_seconds', 'median_seconds'))
        tokens = ' | '.join(f'{value:,}' for value in usage.values()) if usage else 'Unavailable | Unavailable | Unavailable'
        lines.append(f'| {condition} | {counts} | {times} | {tokens} |')
    lines += ['', 'Cached input is a subset of input. Provider billing is unavailable.', '',
              '## Matched contrasts', '',
              '| Contrast | Matched tasks | First condition wins / ties / loses | Pass difference | Median paired session difference |',
              '| --- | ---: | ---: | ---: | ---: |']
    for contrast, pair in result['paired'].items():
        lines.append(f"| {contrast} | {pair['pairs']} | {pair['wins']} / {pair['ties']} / {pair['losses']} | "
                     f"{pair['success_difference'] * 100:+.1f} pp | {pair['median_seconds_difference']:+.1f} s |")
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--publish', type=Path, help='Write allowlisted run evidence from a private run folder')
    parser.add_argument('--chart', type=Path)
    parser.add_argument('--table', type=Path)
    args = parser.parse_args()
    data = collect(args.input) if args.input.is_dir() else json.loads(args.input.read_text(encoding='utf-8'))
    result = summary(data)
    if args.publish:
        args.publish.write_bytes((json.dumps(data, indent=2, sort_keys=True) + '\n').encode('utf-8'))
    if args.chart:
        chart(data, args.chart)
    if args.table:
        args.table.write_bytes(markdown(data, result).encode('utf-8'))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
