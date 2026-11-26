"""Bounded, inert acquisition and review of exact Markdown-only candidates."""

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
import time
from urllib.parse import quote, urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from catalog import ID, metadata
from store import digest, fingerprint, read_json


GATES = {'provenance', 'license', 'instructions', 'permissions', 'compatibility', 'functional', 'rollback'}
LICENSES = {'MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', '0BSD', 'CC0-1.0'}
REPO = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z')
SHA = re.compile(r'[0-9a-f]{40}\Z')


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url, limit=256_000):
    request = Request(url, headers={'User-Agent': 'Engineering-Infrastructure', 'Accept': 'application/json, text/plain'})
    deadline = time.monotonic() + 10
    out = io.BytesIO()
    with build_opener(NoRedirect()).open(request, timeout=5) as response:
        while time.monotonic() < deadline:
            data = response.read1(8192)
            if not data:
                return out.getvalue()
            out.write(data)
            if out.tell() > limit:
                raise ValueError('Remote file exceeds acquisition budget')
    raise TimeoutError('Acquisition exceeded time budget')


def public_search(query):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 -]{2,79}', query) or len(query.split()) > 8:
        raise ValueError('Use a short public capability phrase without private values or search operators')
    params = urlencode({'q': query + ' agent skills in:name,description,topics', 'per_page': 4})
    response = json.loads(fetch('https://api.github.com/search/repositories?' + params))
    return [{'repo': row['full_name'], 'url': 'https://github.com/' + row['full_name']}
            for row in response['items'][:4] if REPO.fullmatch(row['full_name'])]


def source_path(value):
    if not value or any(not re.fullmatch(r'[A-Za-z0-9_.-]+', part) or part.endswith('.')
                        or re.fullmatch(r'(?:con|prn|aux|nul|com[1-9]|lpt[1-9])', part.split('.')[0], re.I)
                        for part in value.split('/')):
        raise ValueError('Source must be a repository-relative path')
    return quote(value, safe='/')


def acquire(repo, commit, skill_path, license_path):
    if not REPO.fullmatch(repo) or any(part in {'.', '..'} for part in repo.split('/')) or not SHA.fullmatch(commit):
        raise ValueError('Expected owner/repository and a full lowercase Git commit SHA')
    base = f'https://raw.githubusercontent.com/{repo}/{commit}/'
    return {'SKILL.md': fetch(base + source_path(skill_path.rstrip('/') + '/SKILL.md')),
            'LICENSE': fetch(base + source_path(license_path))}


def acquire_pinned(pin):
    base = f"https://raw.githubusercontent.com/{pin['repo']}/{pin['commit']}/"
    payload = {}
    jobs = iter(pin['files'].items())
    deadline = time.monotonic() + 45
    total = 0
    with ThreadPoolExecutor(max_workers=5) as pool:
        def start():
            entry = next(jobs, None)
            if entry is None:
                return None
            name, item = entry
            return pool.submit(fetch, base + source_path(item['path'])), (name, item['sha256'])

        pending = dict(item for item in (start() for _ in range(5)) if item)
        while pending:
            completed, _ = wait(pending, timeout=max(0, deadline - time.monotonic()), return_when=FIRST_COMPLETED)
            if not completed:
                raise TimeoutError('Pinned bundle acquisition exceeded its deadline')
            for future in completed:
                name, wanted = pending.pop(future)
                data = future.result()
                if digest(data) != wanted:
                    raise ValueError(f'Pinned source digest mismatch: {name}')
                total += len(data)
                if total > 4_000_000:
                    raise ValueError('Pinned bundle exceeds total size budget')
                payload[name] = data
                item = start()
                if item:
                    pending[item[0]] = item[1]
    return payload


def review_payload(name, payload):
    if not ID.fullmatch(name) or set(payload) not in ({'SKILL.md', 'LICENSE'}, {'SKILL.md', 'LICENSE.txt'}):
        raise ValueError('Automatic activation supports only SKILL.md and LICENSE')
    metadata(payload['SKILL.md'], name)
    body = payload['SKILL.md'].decode('utf-8')
    license_text = payload['LICENSE' if 'LICENSE' in payload else 'LICENSE.txt'].decode('utf-8')
    if len(body) > 64_000 or not license_text.strip() or len(license_text) > 32_000:
        raise ValueError('Candidate content or license exceeds bounds')
    if re.search(r'\b(ignore (all |any |the )?(previous|prior) instructions|disable (the )?sandbox|'
                 r'curl\b[^\n]{0,200}\|\s*(ba)?sh|\.mcp\.json|\bpretooluse\b)\b', body, re.I):
        raise ValueError('Candidate contains a prohibited instruction pattern')
    if re.search(r'\]\(\s*(?!https://|#)[^)]*\)|<\s*/?\s*(script|iframe|object)\b', body, re.I):
        raise ValueError('Candidate has an unsupported file reference or embedded element')
    return fingerprint(payload)


def policy(path):
    value = read_json(path) if path.is_file() else {'schema': 1, 'mode': 'REPORT_ONLY', 'approvals': []}
    if value.get('schema') != 1 or value.get('mode') not in {'OFF', 'REPORT_ONLY', 'TRUSTED_AUTO'}:
        raise ValueError('Invalid lifecycle policy')
    if not isinstance(value.get('approvals'), list):
        raise ValueError('Invalid policy approvals')
    for row in value['approvals']:
        if not ID.fullmatch(row['id']) or not re.fullmatch('[a-f0-9]{64}', row['sha256']):
            raise ValueError('Invalid approval identity')
        if row['license'] not in LICENSES or set(row['gates']) != GATES or any(
                not isinstance(reason, str) or not reason.strip() for reason in row['gates'].values()):
            raise ValueError('Approval requires license and evidence for every hard gate')
        if not isinstance(row['agents'], list) or not row['agents'] or not isinstance(row['os'], list) or not row['os']:
            raise ValueError('Approval requires agent and OS scope')
        tags = row.get('capabilities', [row['id']])
        if not isinstance(tags, list) or not 0 < len(tags) <= 12 or any(not ID.fullmatch(tag) for tag in tags):
            raise ValueError('Approval capability tags must be short, stable IDs')
        expiry = datetime.fromisoformat(row['expires_utc'].replace('Z', '+00:00'))
        if expiry.tzinfo is None:
            raise ValueError('Approval expiry must include a timezone')
    return value


def require_approval(settings, receipt, active_agents, platform):
    if settings['mode'] != 'TRUSTED_AUTO':
        raise ValueError('Activation requires TRUSTED_AUTO and an exact user-reviewed approval')
    for row in settings['approvals']:
        if all(row[key] == receipt[key] for key in ('id', 'sha256', 'source')) and platform in row['os'] \
                and set(active_agents).issubset(row['agents']) and datetime.fromisoformat(
                    row['expires_utc'].replace('Z', '+00:00')) > datetime.now(timezone.utc):
            return row
    raise ValueError('No exact, current, scope-compatible approval for candidate')
