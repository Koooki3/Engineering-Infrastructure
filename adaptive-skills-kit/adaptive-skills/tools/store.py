"""Native-user store and recoverable, drift-checked file transactions."""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
import time
import uuid
from contextlib import contextmanager


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def read_json(path):
    return json.loads(path.read_bytes())


def link(path):
    attrs = path.lstat()
    return stat.S_ISLNK(attrs.st_mode) or bool(getattr(attrs, "st_file_attributes", 0) & 1024)


def check_path(path, include_leaf=True):
    for part in (*reversed(path.parents), *((path,) if include_leaf else ())):
        if os.path.lexists(part) and link(part):
            raise ValueError(f"Linked path requires an explicit migration or native real path: {part}")


def files(root, portable=False):
    check_path(root)
    if not root.is_dir():
        raise ValueError(f"Expected directory: {root}")
    result = {}
    portable_names = set()
    for path in root.iterdir():
        if link(path):
            raise ValueError(f"Unexpected link: {path}")
        if path.name == "__pycache__" or path.suffix == ".pyc":
            continue
        if portable and (path.name.startswith('.') or '\\' in path.name or ':' in path.name):
            raise ValueError(f"Unsupported distribution path: {path}")
        if portable and path.name.casefold() in portable_names:
            raise ValueError(f"Case-insensitive path collision: {path}")
        portable_names.add(path.name.casefold())
        if path.is_dir():
            result.update({f"{path.name}/{name}": content for name, content in files(path, portable).items()})
        elif stat.S_ISREG(path.stat().st_mode):
            if path.stat().st_size > 8_000_000:
                raise ValueError(f"File exceeds size limit: {path}")
            data = path.read_bytes()
            if portable and path.suffix in {'.md', '.py', '.json'}:
                data = data.replace(b'\r\n', b'\n')
            result[path.name] = data
        else:
            raise ValueError(f"Unsupported file: {path}")
    return result


def fingerprint(payload):
    return digest(encode({name: digest(content) for name, content in payload.items()}))


def signature(path):
    if not os.path.lexists(path):
        return None
    if link(path):
        return ["link", os.readlink(path)]
    if path.is_dir():
        return ["tree", fingerprint(files(path))]
    if not path.is_file():
        raise ValueError(f"Unsupported target: {path}")
    return ["file", digest(path.read_bytes())]


def replace(source, destination, *, vacant=False):
    for delay in (0.04, 0.08, 0.16, 0.32, 0.64, None):
        if vacant and os.path.lexists(destination):
            raise ValueError(f'Transaction destination appeared unexpectedly: {destination}')
        try:
            os.replace(source, destination)
            return
        except OSError as exc:
            if delay is None or getattr(exc, 'winerror', None) not in {5, 32, 33}:
                raise
            time.sleep(delay)


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".ei-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def locked(root):
    check_path(root)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = root / 'writer.lock'
    check_path(path)
    with path.open("a+b") as stream:
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def stage(path, payload):
    if isinstance(payload, bytes):
        path.write_bytes(payload)
    elif payload is not None:
        path.mkdir()
        for name, contents in payload.items():
            dest = path / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(contents)


def describe(payload):
    if isinstance(payload, bytes):
        return ['file', digest(payload)]
    if payload is not None:
        return ['tree', fingerprint(payload)]
    return None


def read_journal(journal):
    check_path(journal)
    records = read_json(journal)
    if not isinstance(records, list) or not records:
        raise ValueError('Invalid transaction journal')
    seen = set()
    transaction = None
    for index, rec in enumerate(records):
        if not isinstance(rec, dict) or not {'dest', 'scratch', 'before', 'after'} <= rec.keys():
            raise ValueError('Invalid transaction record')
        dest, scratch = Path(rec['dest']), Path(rec['scratch'])
        match = re.fullmatch(r'\.ei-([a-f0-9]{32})-' + str(index), scratch.name)
        if (not dest.is_absolute() or dest in seen
                or scratch.parent != dest.parent or not match or transaction not in (None, match[1])):
            raise ValueError('Invalid transaction paths')
        transaction = match[1]
        seen.add(dest)
        for sig in (rec['before'], rec['after']):
            if sig is not None and (not isinstance(sig, list) or len(sig) != 2
                                    or sig[0] not in ('file', 'tree', 'link') or not isinstance(sig[1], str)):
                raise ValueError('Invalid transaction signature')
    return records


def validate_recovery(journal, check_all=False):
    records = read_journal(journal)
    for rec in reversed(records):
        dest, scratch = Path(rec['dest']), Path(rec['scratch'])
        check_path(dest, include_leaf=False)
        check_path(scratch)
        before, after = rec['before'], rec['after']
        current, backup = signature(dest), signature(scratch / 'old')
        if backup is not None and backup != before:
            raise ValueError(f"Rollback backup drift: {dest}")
        if current != before and (current not in (after, None) or backup != before):
            raise ValueError(f"Rollback refused because target drifted: {dest}")
        if check_all and current != after:
            raise ValueError(f"Rollback refused because target drifted: {dest}")
    return records


def recover(journal):
    records = validate_recovery(journal)
    for rec in reversed(records):
        dest, scratch = Path(rec['dest']), Path(rec['scratch'])
        old, discarded = scratch / 'old', scratch / 'discarded'
        if signature(dest) == rec['before']:
            continue
        if os.path.lexists(dest):
            scratch.mkdir(mode=0o700, exist_ok=True)
            replace(dest, discarded, vacant=True)
        if os.path.lexists(old):
            replace(old, dest, vacant=True)
    for rec in records:
        scratch = Path(rec['scratch'])
        if scratch.exists():
            shutil.rmtree(scratch)
    journal.unlink()


def rollback(root, journal):
    validate_recovery(journal, check_all=True)
    pending = root / 'pending.json'
    replace(journal, pending, vacant=True)
    recover(pending)


def transact(root, changes):
    """changes contains (absolute Path, expected signature, replacement bytes/tree/None)."""
    txn = uuid.uuid4().hex
    journal = root / 'pending.json'
    if journal.exists():
        raise ValueError('An interrupted transaction needs recover first')
    records = []
    payloads = []
    for dest, before, payload in changes:
        check_path(dest, include_leaf=False)
        if signature(dest) != before:
            raise ValueError(f"Target changed since planning: {dest}")
        after = describe(payload)
        if before != after:
            records.append({'dest': str(dest), 'scratch': str(dest.parent / f'.ei-{txn}-{len(records)}'),
                            'before': before, 'after': after})
            payloads.append(payload)
    if not records:
        return None
    atomic(journal, encode(records))
    try:
        for rec, payload in zip(records, payloads):
            dest, scratch = Path(rec['dest']), Path(rec['scratch'])
            scratch.mkdir(mode=0o700, parents=True)
            stage(scratch / 'new', payload)
            if isinstance(payload, bytes) and os.name != 'nt':
                mode = stat.S_IMODE(dest.stat().st_mode) if rec['before'] and rec['before'][0] == 'file' else 0o600
                (scratch / 'new').chmod(mode)
            if signature(scratch / 'new') != rec['after'] or signature(dest) != rec['before']:
                raise ValueError(f"Pre-activation integrity check failed: {dest}")
            if rec['before'] is not None:
                replace(dest, scratch / 'old', vacant=True)
            if payload is not None:
                replace(scratch / 'new', dest, vacant=True)
        for rec in records:
            if signature(Path(rec['dest'])) != rec['after']:
                raise ValueError(f"Post-activation integrity check failed: {rec['dest']}")
        history = root / 'history' / f'{txn}.json'
        history.parent.mkdir(exist_ok=True)
        replace(journal, history, vacant=True)
    except BaseException:
        recover(journal)
        raise
    for rec in records:
        if rec['before'] is None:
            try:
                Path(rec['scratch']).rmdir()
            except OSError:
                pass  # Retained scratch is still covered by the history journal.
    return txn
