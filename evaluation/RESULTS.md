# EI-Eval v0.1 results

Generated from [pilot-results.json](pilot-results.json) with [analyze.py](analyze.py).

| Task | Native A | Prompt only B | Full D |
| --- | --- | --- | --- |
| Out-of-order updates | FAIL · 44.8 s | Not scheduled or not reached | FAIL · 74.0 s |
| Preview preserves data | PASS · 37.3 s | Not scheduled or not reached | PASS · 40.7 s |
| PR draft accuracy | PASS · 21.2 s | PASS · 23.0 s | PASS · 37.1 s |
| Deployment freshness | PASS · 70.2 s | Not scheduled or not reached | PASS · 58.2 s |
| Dirty-checkout integration | FAIL · 62.4 s | FAIL · 41.1 s | FAIL · 51.1 s |
| Deployment receipt integrity | CLI_FAILURE · 3.9 s | Not scheduled or not reached | FAIL · 31.1 s |

## Usage across all attempts

| Condition | Passed / attempts | Session time (s) | Setup (s) | Verifier (s) | Median session (s) | Input tokens | Cached input | Output tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 3 / 6 | 239.9 | 2.4 | 0.9 | 41.1 | 415,409 | 381,696 | 7,255 |
| B | 1 / 2 | 64.1 | 0.1 | 0.0 | 32.0 | 172,315 | 145,408 | 1,407 |
| D | 3 / 6 | 292.2 | 2.5 | 0.7 | 45.9 | 611,007 | 549,888 | 7,394 |

Cached input is a subset of input. Provider billing is unavailable.

## Matched contrasts

| Contrast | Matched tasks | First condition wins / ties / loses | Pass difference | Median paired session difference |
| --- | ---: | ---: | ---: | ---: |
| D-A | 6 | 0 / 6 / 0 | +0.0 pp | +9.7 s |
| D-B | 2 | 0 / 2 / 0 | +0.0 pp | +12.0 s |
| B-A | 2 | 0 / 2 / 0 | +0.0 pp | -9.7 s |
