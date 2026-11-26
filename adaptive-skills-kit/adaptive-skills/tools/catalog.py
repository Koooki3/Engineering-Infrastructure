"""Portable catalog, bounded inventory, and local-first capability resolution."""

from datetime import date
import os
from pathlib import Path
import re

from store import files, fingerprint, read_json


ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
TIERS = {'CORE', 'RECOMMENDED', 'DOMAIN', 'EXPERIMENTAL', 'DEPRECATED', 'QUARANTINED'}


def metadata(data, name):
    content = data.decode('utf-8').splitlines()
    if not content or content[0] != '---' or '---' not in content[1:]:
        raise ValueError('Missing SKILL.md frontmatter')
    header = content[1:content.index('---', 1)]
    fields = {}
    for line in header:
        key, sep, value = line.partition(':')
        if not sep or key in fields or key not in {'name', 'description'}:
            raise ValueError('Expected unique name and description fields')
        fields[key] = value.strip().strip('"\'')
    if len(name) > 64 or not ID.fullmatch(name) or fields.get('name') != name:
        raise ValueError('Invalid Skill name or directory mismatch')
    if not 0 < len(fields.get('description', '')) <= 1024:
        raise ValueError('Missing or oversized Skill description')
    return fields['description']


def catalog(root):
    registry = read_json(root / 'skills-registry.json')
    if registry.get('schema') != 1 or not isinstance(registry.get('skills'), list):
        raise ValueError('Unsupported catalog schema')
    entries = {}
    for entry in registry['skills']:
        name = entry['id']
        if not ID.fullmatch(name) or name in entries or entry['tier'] not in TIERS:
            raise ValueError(f'Invalid/duplicate catalog entry: {name}')
        for field in ('name', 'category', 'triggers', 'non_goals', 'source', 'source_path',
                      'license', 'installation', 'evidence', 'trust', 'status', 'verified'):
            if not isinstance(entry[field], str) or not entry[field].strip():
                raise ValueError(f'Missing catalog field {name}.{field}')
        if entry['name'] != name or not (entry['source'].startswith('https://') or entry['source'] == 'Local-only'):
            raise ValueError(f'Invalid name/source for {name}')
        if any(part in {'', '.', '..'} or ':' in part or '\\' in part for part in entry['source_path'].split('/')):
            raise ValueError(f'Invalid source subdirectory for {name}')
        for field in ('capabilities', 'agents', 'os', 'dependencies', 'conflicts'):
            if not isinstance(entry[field], list) or any(not isinstance(item, str) for item in entry[field]):
                raise ValueError(f'Invalid list for {name}.{field}')
        date.fromisoformat(entry['verified'])
        entries[name] = entry
    return entries


def core_lock(root, registry_dir):
    lock = {}
    for name, entry in catalog(registry_dir).items():
        if entry['tier'] != 'CORE':
            continue
        path = root / entry['source_path']
        payload = files(path, portable=True)
        metadata(payload['SKILL.md'], name)
        lock[name] = fingerprint(payload)
    return {'schema': 1, 'sha256': lock}


def reference(entries, lock):
    lines = ['# Skills reference', '', 'Generated from `skills-registry.json` and `skills-lock.json`.',
             'The CORE tree hashes pin bundled content. Local references require their own reviewed source and pin.', '']
    for name, row in sorted(entries.items(), key=lambda item: (item[1]['category'], item[0])):
        lines.extend((f'## {name}', ''))
        for field in ('category', 'tier', 'capabilities', 'triggers', 'non_goals', 'source', 'source_path',
                      'license', 'installation', 'agents', 'os', 'evidence', 'dependencies', 'conflicts',
                      'trust', 'status', 'verified'):
            value = row[field]
            if isinstance(value, list):
                value = ', '.join(value) or 'None recorded'
            lines.append(f"- **{field.replace('_', ' ').capitalize()}** {value}")
        version = lock['sha256'].get(name, row.get('version', 'Pin during local review'))
        lines.extend((f'- **Version** `{version}`', ''))
    return ('\n'.join(lines).rstrip() + '\n').encode()


def inventory(roots):
    assets = {}
    problems = []
    for scope, root in roots:
        if not root.is_dir():
            continue
        try:
            children = sorted(root.iterdir())
        except OSError as exc:
            problems.append({'root': str(root), 'issue': str(exc)})
            continue
        for entry in children:
            if entry.name.startswith('.') or entry.name in {'node_modules', '__pycache__'}:
                continue
            skill = entry / 'SKILL.md' if entry.is_dir() else entry
            if not skill.is_file() or (skill == entry and skill.suffix != '.md'):
                if entry.is_symlink() and not entry.exists():
                    problems.append({'entry': str(entry), 'issue': 'broken link'})
                continue
            try:
                canonical = entry.resolve(strict=True)
                key = os.path.normcase(str(canonical))
                name = skill.stem if skill == entry else entry.name
                data = skill.read_bytes() if skill.stat().st_size <= 256_000 else b''
                if key not in assets:
                    header = re.search(rb'^description:[ \t]*(.*)$', data, flags=re.MULTILINE)
                    portable_hash = None
                    issue = None
                    try:
                        payload = ({entry.name: data} if skill == entry else files(canonical, portable=True))
                        portable_hash = fingerprint(payload)
                    except (OSError, ValueError) as exc:
                        issue = str(exc)
                    assets[key] = {'id': name, 'source': str(canonical), 'entries': [],
                                   'metadata_bytes': len(header[1].rstrip()) if header else None,
                                   'state': 'INSTALLED', 'sha256': portable_hash, 'issue': issue}
                assets[key]['entries'].append({'scope': scope, 'path': str(entry)})
            except (OSError, ValueError) as exc:
                problems.append({'entry': str(entry), 'issue': str(exc)})
    names, contents = {}, {}
    for asset in assets.values():
        names.setdefault(asset['id'].casefold(), []).append(asset['source'])
        if asset['sha256']:
            contents.setdefault(asset['sha256'], []).append(asset['source'])
    return {'assets': list(assets.values()), 'problems': problems,
            'same_name': {key: value for key, value in names.items() if len(value) > 1},
            'same_content': {key: value for key, value in contents.items() if len(value) > 1}}


def installed_names(directories):
    found = set()
    for path in directories:
        if not path.is_dir():
            continue
        for entry in path.iterdir():
            if ID.fullmatch(entry.name) and (entry / 'SKILL.md').is_file():
                found.add(entry.name)
    return found


def resolve(needs, entries, installed, native, agent, platform):
    decisions = []
    for need in dict.fromkeys(needs):
        if need in native:
            decisions.append({'capability': need, 'action': 'USE_NATIVE'})
            continue
        matches = [item for item in entries.values() if need in item['capabilities'] and
                   item['tier'] not in {'DEPRECATED', 'QUARANTINED'} and
                   agent in item['agents'] and platform in item['os'] and
                   (item['source'] != 'Local-only' or item['id'] in installed)]
        matches.sort(key=lambda item: (item['id'] not in installed,
                                       ('CORE', 'RECOMMENDED', 'DOMAIN', 'EXPERIMENTAL').index(item['tier']), item['id']))
        if matches:
            candidate = matches[0]
            decisions.append({'capability': need, 'action': 'USE_INSTALLED' if candidate['id'] in installed
                              else 'REVIEW_REFERENCE', 'id': candidate['id'], 'candidates': [item['id'] for item in matches],
                              'dependencies': candidate['dependencies'], 'conflicts': candidate['conflicts']})
        else:
            decisions.append({'capability': need, 'action': 'DISCOVER_OR_FALL_BACK',
                              'reason': 'No compatible installed or catalog capability'})
    return decisions
