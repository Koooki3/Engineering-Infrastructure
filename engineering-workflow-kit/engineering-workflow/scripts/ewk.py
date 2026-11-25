#!/usr/bin/env python3
"""ewk - evidence / guard / route helper for the engineering-workflow skill.

Stdlib only, Python >= 3.9, Windows + POSIX. Subcommands:
  run    run one command with a timeout and append a bound evidence record
  check  re-validate an evidence file against the current repository state
  guard  mechanical diff checks (protected paths, mojibake, BOM, local paths, secrets)
  route  advisory Fast/Standard/Critical tier from a change set

Exit codes: 0 ok | 1 violation or failed check | 2 usage/evidence unreadable or
cannot be determined (never a pass) | 124 timeout (run only).
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time

STATUSES = {"PASS", "FAIL", "BLOCKED", "NOT_RUN", "NOT_APPLICABLE", "PENDING"}
NOTE_REQUIRED = {"BLOCKED", "NOT_RUN", "NOT_APPLICABLE", "PENDING"}
TAIL_CHARS = 800


# ----------------------------------------------------------------- git helpers
def git(repo, *args):
    try:
        return subprocess.run(["git", "-C", repo, *args], capture_output=True)
    except OSError:
        return None


def _norm(p):
    return os.path.normcase(os.path.abspath(p))


def state_id(repo, exclude=(), _depth=0):
    """HEAD, plus a content hash of uncommitted work. None if not a git repo."""
    r = git(repo, "rev-parse", "HEAD")
    if r is None or r.returncode != 0:
        return None
    head = r.stdout.decode().strip()
    top = git(repo, "rev-parse", "--show-toplevel")
    root = top.stdout.decode().strip() if top and top.returncode == 0 else repo
    skip = {_norm(p) for p in exclude}

    def skipped(rel):
        full = _norm(os.path.join(root, rel))
        return full in skip or ".ewk" in rel.replace("\\", "/").split("/")

    h = hashlib.sha256()
    dirty = False
    d = git(repo, "diff", "HEAD", "--binary", "--no-ext-diff", "--ignore-submodules=all")
    if d is not None and d.stdout:
        # tracked-file diff; evidence files are untracked by convention, but drop
        # nothing here: a tracked evidence file edit is a real change.
        h.update(d.stdout)
        dirty = True
    u = git(repo, "ls-files", "--others", "--exclude-standard", "-z")
    if u is not None:
        for raw in sorted(x for x in u.stdout.split(b"\0") if x):
            rel = raw.decode("utf-8", "replace")
            if skipped(rel):
                continue
            dirty = True
            h.update(raw)
            try:
                with open(os.path.join(root, rel), "rb") as f:
                    h.update(f.read())
            except OSError:
                h.update(b"<unreadable>")
    sm = git(repo, "submodule", "status", "--recursive")
    if sm is not None and sm.stdout.strip():
        for line in sm.stdout.decode("utf-8", "replace").splitlines():
            h.update(line.encode("utf-8"))
            parts = line.strip().split()
            if len(parts) >= 2:
                sub = os.path.join(root, parts[1])
                if os.path.isdir(sub):
                    sid = state_id(sub, exclude, _depth + 1) if _depth < 4 else None
                    h.update((sid or "-").encode())
                    dirty = dirty or bool(sid and "+" in sid)
    return head + ("+" + h.hexdigest()[:12] if dirty else "")


# ------------------------------------------------------------- evidence store
def load_evidence(path):
    if not os.path.exists(path):
        return {"version": 1, "records": []}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise ValueError("evidence file must be an object with a 'records' list")
    return data


def save_evidence(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def kill_tree(proc):
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                           capture_output=True)
        else:
            os.killpg(proc.pid, signal.SIGKILL)
    except (OSError, ProcessLookupError):
        pass
    try:
        proc.kill()
    except OSError:
        pass


def cmd_run(a):
    if not a.cmd:
        print("ewk run: command missing after --", file=sys.stderr)
        return 2
    cmd = list(a.cmd)
    repo = os.path.abspath(a.repo)
    exe = shutil.which(cmd[0])
    if exe is None and (os.sep in cmd[0] or "/" in cmd[0]):
        exe = shutil.which(os.path.join(repo, cmd[0]))
    ev_path = os.path.abspath(a.evidence)
    try:
        data = load_evidence(ev_path)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"ewk run: cannot read evidence file: {e}", file=sys.stderr)
        return 2
    if any(r.get("id") == a.id for r in data["records"]):
        print(f"ewk run: id '{a.id}' already recorded; use a new id", file=sys.stderr)
        return 2
    before = state_id(repo, [ev_path])
    started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    t0 = time.monotonic()
    note = a.note or ""
    tail = ""
    if exe is None:
        code, status = 127, "BLOCKED"
        note = (note + " " if note else "") + f"executable not found: {cmd[0]}"
    else:
        kw = {"cwd": repo, "stdout": subprocess.PIPE, "stderr": subprocess.STDOUT}
        if os.name == "nt":
            kw["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kw["start_new_session"] = True
        proc = subprocess.Popen([exe, *cmd[1:]], **kw)
        try:
            out, _ = proc.communicate(timeout=a.timeout)
            code = proc.returncode
            status = "PASS" if code == 0 else "FAIL"
        except subprocess.TimeoutExpired:
            kill_tree(proc)
            try:
                out, _ = proc.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                out = b""
            code, status = 124, "FAIL"
            note = (note + " " if note else "") + f"timeout after {a.timeout}s; process tree killed"
        tail = out.decode("utf-8", "replace")[-TAIL_CHARS:]
    after = state_id(repo, [ev_path])
    if status == "PASS" and before != after:
        status = "FAIL"
        note = (note + " " if note else "") + (
            "command changed the working tree, so this PASS does not describe the resulting state; "
            "re-run (ignore build outputs in .gitignore)")
        code = code or 1
    rec = {
        "id": a.id,
        "cmd": cmd,
        "cwd": repo,
        "exit_code": code,
        "status": status,
        "started_utc": started,
        "duration_s": round(time.monotonic() - t0, 3),
        "timeout_s": a.timeout,
        "state": after,
        "mutated_tree": before != after,
        "note": note,
        "output_tail": tail,
    }
    data["records"].append(rec)
    save_evidence(ev_path, data)
    print(f"[{status}] {a.id} exit={code} {rec['duration_s']}s state={after or 'unbound'}")
    return code if status != "BLOCKED" else 127


def cmd_check(a):
    ev_path = os.path.abspath(a.evidence)
    try:
        data = load_evidence(ev_path)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"ewk check: cannot read evidence file: {e}", file=sys.stderr)
        return 2
    if not os.path.exists(ev_path):
        print("ewk check: evidence file does not exist", file=sys.stderr)
        return 2
    repo = os.path.abspath(a.repo)
    cur = state_id(repo, [ev_path])
    problems, seen = [], {}
    for r in data["records"]:
        if not isinstance(r, dict):
            problems.append(f"malformed record: {r!r}")
            continue
        rid = r.get("id", "<no id>")
        seen[rid] = r
        st = r.get("status")
        if st not in STATUSES:
            problems.append(f"{rid}: invalid status {st!r}")
            continue
        if st in NOTE_REQUIRED and not str(r.get("note", "")).strip():
            problems.append(f"{rid}: status {st} needs a note explaining why")
        if st == "PASS":
            if r.get("exit_code") != 0 or not r.get("cmd"):
                problems.append(f"{rid}: PASS without cmd and exit_code 0 is not evidence")
            elif r.get("state") is None:
                if not a.allow_unbound:
                    problems.append(f"{rid}: PASS is not bound to a git state (--allow-unbound outside git)")
            elif cur is None:
                problems.append(f"{rid}: repo state unavailable, cannot confirm PASS is current")
            elif r["state"] != cur:
                problems.append(f"{rid}: STALE (recorded {r['state']}, current {cur}); re-run")
    for rid in [x for x in (a.require or "").split(",") if x]:
        r = seen.get(rid)
        if r is None:
            problems.append(f"{rid}: required check has no record (NOT_RUN)")
        elif r.get("status") != "PASS":
            problems.append(f"{rid}: required check is {r.get('status')}")
    if problems:
        print("ewk check: FAIL")
        for p in problems:
            print("  - " + p)
        return 1
    n = sum(1 for r in data["records"] if isinstance(r, dict) and r.get("status") == "PASS")
    print(f"ewk check: OK ({n} PASS, {len(data['records'])} records, state {cur or 'unbound'})")
    return 0


# ---------------------------------------------------------------------- guard
SECRET_RES = [
    ("private key block", re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("AWS access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("generic sk- key", re.compile(r"\bsk-[A-Za-z0-9]{32,}")),
]
TEXT_EXTS = {".md", ".txt", ".py", ".ps1", ".sh", ".cs", ".xaml", ".json", ".toml",
             ".yml", ".yaml", ".js", ".ts", ".tsx", ".css", ".html", ".csv", ".rs", ".go"}
DEFAULT_BASES = ["upstream/dev", "origin/dev", "upstream/main", "origin/main", "main", "master"]


def _lines(b):
    return b.decode("utf-8", "replace").splitlines()


def cmd_guard(a):
    repo = os.path.abspath(a.repo)
    top = git(repo, "rev-parse", "--show-toplevel")
    if top is None or top.returncode != 0:
        print("ewk guard: not a git repository; cannot determine changes (not a pass)")
        return 2
    root = top.stdout.decode().strip()
    conf = {}
    cpath = os.path.join(root, ".ewk.json")
    if os.path.exists(cpath):
        try:
            with open(cpath, "r", encoding="utf-8") as f:
                conf = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"ewk guard: bad .ewk.json: {e}")
            return 2
    protected = conf.get("protected_paths", [])
    local_re = conf.get("local_path_re", "")
    bases = conf.get("bases", []) + DEFAULT_BASES

    def ok_ref(ref):
        r = git(root, "rev-parse", "--verify", "-q", ref + "^{commit}")
        return r is not None and r.returncode == 0

    base = None
    if not a.worktree_only:
        if a.base:
            if not ok_ref(a.base):
                print(f"ewk guard: cannot resolve base '{a.base}' (not a pass; fetch it first)")
                return 2
            base = a.base
        else:
            base = next((b for b in bases if ok_ref(b)), None)
            if base is None:
                print("ewk guard: no base ref found; pass --base or --worktree-only (not a pass)")
                return 2

    files, patch = set(), []

    def collect(*args):
        r = git(root, *args)
        if r is None or r.returncode != 0:
            raise RuntimeError("git " + " ".join(args))
        return r.stdout

    try:
        if base:
            files |= {x.decode("utf-8", "replace") for x in
                      collect("diff", "--name-only", "-z", "--no-renames", f"{base}...HEAD").split(b"\0") if x}
            patch += _lines(collect("diff", "-U0", "--no-ext-diff", f"{base}...HEAD"))
        files |= {x.decode("utf-8", "replace") for x in
                  collect("diff", "--name-only", "-z", "--no-renames", "HEAD").split(b"\0") if x}
        patch += _lines(collect("diff", "-U0", "--no-ext-diff", "HEAD"))
        untracked = [x.decode("utf-8", "replace") for x in
                     collect("ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if x]
    except RuntimeError as e:
        print(f"ewk guard: could not read changes ({e}); not a pass")
        return 2
    files |= set(untracked)
    added, in_hunk = [], False
    for l in patch:
        if l.startswith("diff --git"):
            in_hunk = False
        elif l.startswith("@@"):
            in_hunk = True
        elif in_hunk and l.startswith("+"):
            added.append(l[1:])
    for rel in untracked:
        try:
            with open(os.path.join(root, rel), "rb") as f:
                blob = f.read()
        except OSError:
            continue
        if b"\0" not in blob:
            added += _lines(blob)

    fails = []

    def bad(what, fix):
        fails.append((what, fix))

    for p in protected:
        hit = sorted(f for f in files if f.replace("\\", "/").startswith(p))
        if hit:
            bad(f"change touches protected path '{p}': {hit[0]}",
                "revert these files or get explicit user authorization")
    for rel in sorted(files):
        full = os.path.join(root, rel)
        if not os.path.isfile(full):
            continue
        ext = os.path.splitext(rel)[1].lower()
        with open(full, "rb") as f:
            blob = f.read()
        if b"\0" in blob:
            continue
        try:
            text = blob.decode("utf-8")
        except UnicodeDecodeError:
            if ext in TEXT_EXTS:
                bad(f"{rel} is not valid UTF-8", "re-save as UTF-8 (with BOM for .ps1 containing non-ASCII)")
            continue
        if "�" in text:
            bad(f"{rel} contains U+FFFD replacement characters (mojibake)",
                "restore the damaged lines from the previous revision and re-edit with an encoding-safe tool")
        if ext == ".ps1" and any(ord(c) > 127 for c in text) and not blob.startswith(b"\xef\xbb\xbf"):
            bad(f"{rel} has non-ASCII text but no UTF-8 BOM (Windows PowerShell 5.1 misreads it)",
                "save as UTF-8 with BOM, or make it ASCII-only")
    for line in added:
        for name, rx in SECRET_RES:
            if rx.search(line):
                bad(f"added line looks like a secret ({name})",
                    "remove it, rotate the credential if it was real, load it from the environment instead")
                break
    if local_re:
        rx = re.compile(local_re, re.I)
        for line in added:
            if rx.search(line):
                bad("added line contains a local path/identity matching local_path_re",
                    "use a relative path or configuration; keep local paths out of the repository")
                break
    if fails:
        for what, fix in fails:
            print(f"FAIL: {what}\n  fix: {fix}")
        return 1
    print(f"ewk guard: OK ({len(files)} changed files, base {base or 'worktree-only'})")
    return 0


# ---------------------------------------------------------------------- route
CRITICAL_PATH = [
    (re.compile(r"(^|/)migrations?/", re.I), "data migration path"),
    (re.compile(r"(^|/)\.github/workflows/", re.I), "CI/release automation"),
    (re.compile(r"(^|/)(auth|security|crypto|secrets?)[^/]*", re.I), "auth/security/secret code"),
    (re.compile(r"(^|/)[^/]*(deploy|release|publish)[^/]*\.(sh|ps1|py|ya?ml)$", re.I), "deploy/release script"),
    (re.compile(r"\.sql$", re.I), "SQL / schema"),
]
STANDARD_PATH = [
    (re.compile(r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|Cargo\.lock|requirements[^/]*\.txt|[^/]+\.csproj|go\.sum)$", re.I),
     "dependency manifest (check license/audit)"),
]
DOC_EXT = {".md", ".txt", ".rst"}
FLAGS = ["irreversible", "concurrency", "data_migration", "security", "public_release", "perf_critical"]


def cmd_route(a):
    if a.files_from == "-":
        paths = [l.strip() for l in sys.stdin.read().splitlines() if l.strip()]
    elif a.files_from:
        with open(a.files_from, "r", encoding="utf-8") as f:
            paths = [l.strip() for l in f if l.strip()]
    else:
        paths = []
    norm = [p.replace("\\", "/") for p in paths]
    reasons, tier = [], "Fast"
    crit = [(p, why) for p in norm for rx, why in CRITICAL_PATH if rx.search(p)]
    for f in FLAGS:
        if getattr(a, f):
            reasons.append(f"flag --{f.replace('_', '-')}")
            tier = "Critical"
    if crit:
        tier = "Critical"
        reasons += [f"{why}: {p}" for p, why in crit[:3]]
    if tier != "Critical":
        if not norm:
            tier = "Standard"
            reasons.append("no change set provided; classify manually")
        else:
            non_doc = [p for p in norm
                       if os.path.splitext(p)[1].lower() not in DOC_EXT and not p.startswith("docs/")]
            if non_doc:
                tier = "Standard"
                reasons.append(f"code or config changed ({len(non_doc)} files)")
            std = [(p, why) for p in norm for rx, why in STANDARD_PATH if rx.search(p)]
            reasons += [f"{why}: {p}" for p, why in std[:2]]
    if tier == "Fast" and not reasons:
        reasons.append("docs-only change, no risk flags")
    out = {"tier": tier, "reasons": reasons, "advisory": True,
           "note": "escalate on new risk; downgrading needs a stated reason"}
    print(json.dumps(out, ensure_ascii=False))
    return 0


# ----------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(prog="ewk", description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="sub", required=True)
    r = sp.add_parser("run", help="run a command, record bound evidence")
    r.add_argument("--evidence", required=True)
    r.add_argument("--id", required=True)
    r.add_argument("--repo", default=".")
    r.add_argument("--timeout", type=float, default=600)
    r.add_argument("--note", default="")
    r.add_argument("cmd", nargs=argparse.REMAINDER)
    c = sp.add_parser("check", help="validate evidence against current state")
    c.add_argument("--evidence", required=True)
    c.add_argument("--repo", default=".")
    c.add_argument("--require", default="", help="comma-separated ids that must be PASS")
    c.add_argument("--allow-unbound", action="store_true", help="accept PASS records with no git state (non-git dirs)")
    g = sp.add_parser("guard", help="mechanical diff checks")
    g.add_argument("--repo", default=".")
    g.add_argument("--base", default="")
    g.add_argument("--worktree-only", action="store_true")
    t = sp.add_parser("route", help="advisory risk tier")
    t.add_argument("--files-from", default="", help="file with one changed path per line, or - for stdin")
    for f in FLAGS:
        t.add_argument("--" + f.replace("_", "-"), dest=f, action="store_true")
    a = ap.parse_args(argv)
    if a.sub == "run" and a.cmd and a.cmd[0] == "--":
        a.cmd = a.cmd[1:]
    return {"run": cmd_run, "check": cmd_check, "guard": cmd_guard, "route": cmd_route}[a.sub](a)


if __name__ == "__main__":
    sys.exit(main())
