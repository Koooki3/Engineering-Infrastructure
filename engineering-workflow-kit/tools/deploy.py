#!/usr/bin/env python3
"""Reversible deployment of the engineering-workflow skill (copy install + marked doc blocks).

  deploy.py apply    --plan PLAN.json --state STATE.json   install/update, back up, record
  deploy.py verify   --state STATE.json                    hashes still match what was installed
  deploy.py rollback --state STATE.json [--force]          remove installs, restore backups, drop blocks

PLAN.json: {"src": "<skill dir>", "skill_name": "engineering-workflow", "version": "1.0.0",
            "skills": ["<parent skills dir>", ...],
            "docs": [{"file": "<AGENTS.md/CLAUDE.md>", "block_file": "<block text file>"}]}
Run it with the native Python of each environment (Windows / WSL) using that environment's paths.
Stdlib only. Never touches a skill directory it did not install (no manifest -> refuse).
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import sys

MANIFEST = ".ewk-manifest.json"
BEGIN, END = "<!-- ewk:begin -->", "<!-- ewk:end -->"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def file_sha(p):
    with open(p, "rb") as f:
        return sha(f.read())


def tree_hashes(root, skip_manifest=True):
    out = {}
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x != "__pycache__"]
        for n in files:
            if n.endswith(".pyc") or (skip_manifest and n == MANIFEST):
                continue
            full = os.path.join(d, n)
            out[os.path.relpath(full, root).replace("\\", "/")] = file_sha(full)
    return out


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save(p, o):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(o, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ------------------------------------------------------------------ doc blocks
def split_doc(data):
    bom = data.startswith(b"\xef\xbb\xbf")
    body = data[3:] if bom else data
    return bom, (b"\r\n" if b"\r\n" in body else b"\n"), body.decode("utf-8")


def make_block(text, nl):
    t = text.replace("\r\n", "\n").strip("\n")
    return (BEGIN + "\n" + t + "\n" + END).replace("\n", nl.decode())


def _n(t):
    return t.replace("\r\n", "\n")


def find_block(s):
    i = s.find(BEGIN)
    if i < 0:
        return None
    j = s.find(END, i)
    return None if j < 0 else (i, j + len(END))


def patch_doc(entry, backups):
    path, block_text = entry["file"], open(entry["block_file"], encoding="utf-8").read()
    with open(path, "rb") as f:
        raw = f.read()
    bom, nl, s = split_doc(raw)
    block = make_block(block_text, nl)
    span = find_block(s)
    rec = {"file": path, "pre_sha256": sha(raw), "block": block}
    if span:
        if _n(s[span[0]:span[1]]) == _n(block):
            rec.update(action="unchanged", post_sha256=sha(raw))
            return rec
        new = s[:span[0]] + block + s[span[1]:]
        rec["action"] = "replaced"
    else:
        sep = "" if s.endswith(("\n", "\r\n")) or s == "" else nl.decode()
        rec["inserted"] = sep + nl.decode() + block + nl.decode()
        new = s + rec["inserted"]
        rec["action"] = "appended"
    out = (b"\xef\xbb\xbf" if bom else b"") + new.encode("utf-8")
    bk = os.path.join(backups, os.path.basename(path) + "." + sha(raw)[:12] + ".bak")
    with open(bk, "wb") as f:
        f.write(raw)
    rec["backup"] = bk
    tmp = path + ".ewk.tmp"
    with open(tmp, "wb") as f:
        f.write(out)
    os.replace(tmp, path)
    rec["post_sha256"] = sha(out)
    return rec


def unpatch_doc(rec, force):
    path = rec["file"]
    if rec["action"] == "unchanged":
        return "kept (block pre-existed, not ours to remove)"
    with open(path, "rb") as f:
        raw = f.read()
    bom, nl, s = split_doc(raw)
    span = find_block(s)
    if not span:
        return "block already absent"
    if _n(s[span[0]:span[1]]) != _n(rec["block"]) and not force:
        raise RuntimeError(f"{path}: block was edited after deployment; use --force")
    if rec["action"] == "replaced":
        raise RuntimeError(f"{path}: block pre-existed and was replaced; restore {rec.get('backup')} by hand")
    ins = rec.get("inserted", "")
    if ins and s.count(ins) == 1:
        new = s.replace(ins, "", 1)
    else:
        new = s[:span[0]] + s[span[1]:]
    out = (b"\xef\xbb\xbf" if bom else b"") + new.encode("utf-8")
    tmp = path + ".ewk.tmp"
    with open(tmp, "wb") as f:
        f.write(out)
    os.replace(tmp, path)
    return "restored" if sha(out) == rec["pre_sha256"] else "block removed (file has other later edits)"


# ---------------------------------------------------------------------- skills
def install_skill(src, parent, name, version, backups):
    dest = os.path.join(parent, name)
    if os.path.islink(dest) or getattr(os.path, "isjunction", lambda _p: False)(dest):
        raise RuntimeError(f"{dest} is a link/junction; refusing to replace it (remove the link first)")
    want = tree_hashes(src)
    rec = {"dest": dest, "version": version, "files": want, "backup": None, "action": "installed"}
    if os.path.exists(dest):
        mpath = os.path.join(dest, MANIFEST)
        if not os.path.exists(mpath):
            raise RuntimeError(f"{dest} exists and is not managed by this tool; refusing to overwrite")
        if tree_hashes(dest) == want and load(mpath).get("files") == want:
            rec["action"] = "unchanged"
            return rec
        bk = os.path.join(backups, f"{name}-{dt.datetime.now().strftime('%Y%m%d%H%M%S')}-{sha(dest.encode('utf-8'))[:8]}")
        shutil.copytree(dest, bk)
        rec["backup"] = bk
        rec["action"] = "updated"
    os.makedirs(parent, exist_ok=True)
    tmp = dest + ".ewk-new"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    save(os.path.join(tmp, MANIFEST), {"name": name, "version": version, "files": want})
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.replace(tmp, dest)
    return rec


def verify_skill(rec):
    mpath = os.path.join(rec["dest"], MANIFEST)
    if not os.path.exists(mpath):
        return [f"{rec['dest']}: missing"]
    cur = tree_hashes(rec["dest"])
    probs = []
    for k in sorted(set(cur) | set(rec["files"])):
        if cur.get(k) != rec["files"].get(k):
            probs.append(f"{rec['dest']}: {k} {'missing' if k not in cur else 'drifted' if k in rec['files'] else 'unexpected'}")
    return probs


def rollback_skill(rec, force):
    probs = verify_skill(rec)
    if probs and not force:
        raise RuntimeError("; ".join(probs) + " (use --force)")
    if rec["action"] == "unchanged":
        return "kept (pre-existing identical install)"
    if os.path.exists(rec["dest"]):
        shutil.rmtree(rec["dest"])
    if rec.get("backup") and os.path.exists(rec["backup"]):
        shutil.copytree(rec["backup"], rec["dest"])
        return "previous version restored"
    return "removed"


# ------------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="sub", required=True)
    a_ = sp.add_parser("apply")
    a_.add_argument("--plan", required=True)
    a_.add_argument("--state", required=True)
    v = sp.add_parser("verify")
    v.add_argument("--state", required=True)
    r = sp.add_parser("rollback")
    r.add_argument("--state", required=True)
    r.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.sub == "apply":
            plan = load(a.plan)
            if os.path.exists(a.state):
                print("deploy: state file exists; rollback or choose a new --state", file=sys.stderr)
                return 2
            sdir = os.path.dirname(os.path.abspath(a.state))
            backups = os.path.join(sdir, os.path.splitext(os.path.basename(a.state))[0] + ".backups")
            os.makedirs(backups, exist_ok=True)
            state = {"plan": plan, "skills": [], "docs": [],
                     "applied_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
            try:
                for parent in plan["skills"]:
                    rec = install_skill(plan["src"], parent, plan["skill_name"], plan["version"], backups)
                    state["skills"].append(rec)
                    print(f"skill {rec['action']}: {rec['dest']}")
                for d in plan.get("docs", []):
                    rec = patch_doc(d, backups)
                    state["docs"].append(rec)
                    print(f"doc {rec['action']}: {rec['file']}")
            except Exception:
                save(a.state, state)  # partial state so rollback can undo what was done
                raise
            save(a.state, state)
            return 0
        state = load(a.state)
        if a.sub == "verify":
            probs = []
            for rec in state["skills"]:
                probs += verify_skill(rec)
            for rec in state["docs"]:
                with open(rec["file"], "rb") as f:
                    _, _, s = split_doc(f.read())
                span = find_block(s)
                if not span or _n(s[span[0]:span[1]]) != _n(rec["block"]):
                    probs.append(f"{rec['file']}: block missing or changed")
            for p in probs:
                print("DRIFT: " + p)
            print("deploy verify: " + ("FAIL" if probs else "OK"))
            return 1 if probs else 0
        for rec in reversed(state["docs"]):
            print(f"doc {rec['file']}: {unpatch_doc(rec, a.force)}")
        for rec in reversed(state["skills"]):
            print(f"skill {rec['dest']}: {rollback_skill(rec, a.force)}")
        return 0
    except (RuntimeError, OSError, KeyError, json.JSONDecodeError) as e:
        print(f"deploy: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
