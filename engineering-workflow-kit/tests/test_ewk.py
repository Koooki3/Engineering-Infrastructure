"""Tests for scripts/ewk.py. Real git repos in temp dirs; no network; no writes outside temp."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EWK = os.path.join(HERE, "..", "engineering-workflow", "scripts", "ewk.py")
PY = sys.executable


def ewk(*args, cwd=None, stdin=None):
    return subprocess.run([PY, EWK, *args], cwd=cwd, input=stdin, capture_output=True,
                          text=True, encoding="utf-8")


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def jdump(path, obj, raw=None):
    with open(path, "w", encoding="utf-8") as f:
        f.write(raw if raw is not None else json.dumps(obj))


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t",
                        "-c", "commit.gpgsign=false", *args], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ewk test 项目 ")  # spaces + CJK on purpose
        self.repo = os.path.join(self.tmp.name, "repo")
        os.mkdir(self.repo)
        git(self.repo, "init", "-q", "-b", "main")
        self.write("a.txt", "one\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "init")
        self.ev = os.path.join(self.tmp.name, "evidence.json")  # outside repo

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, content, mode="w", **kw):
        p = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if mode == "wb":
            with open(p, "wb") as f:
                f.write(content)
        else:
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
        return p

    def run_ok(self, id_, code="pass", timeout="20"):
        return ewk("run", "--evidence", self.ev, "--id", id_, "--repo", self.repo,
                   "--timeout", timeout, "--", PY, "-c",
                   "import sys; sys.exit(0 if %r=='pass' else 3)" % code)


class TestRunCheck(Repo):
    def test_pass_then_check_ok(self):
        self.assertEqual(self.run_ok("t1").returncode, 0)
        self.assertEqual(ewk("check", "--evidence", self.ev, "--repo", self.repo).returncode, 0)

    def test_failure_is_fail_and_never_passes_check(self):
        r = self.run_ok("t1", code="fail")
        self.assertEqual(r.returncode, 3)
        rec = jload(self.ev)["records"][0]
        self.assertEqual(rec["status"], "FAIL")
        c = ewk("check", "--evidence", self.ev, "--repo", self.repo, "--require", "t1")
        self.assertEqual(c.returncode, 1)

    def test_stale_after_new_commit(self):
        self.run_ok("t1")
        self.write("a.txt", "two\n")
        git(self.repo, "commit", "-qam", "next")
        c = ewk("check", "--evidence", self.ev, "--repo", self.repo)
        self.assertEqual(c.returncode, 1)
        self.assertIn("STALE", c.stdout)

    def test_stale_after_uncommitted_edit_and_untracked(self):
        self.run_ok("t1")
        self.write("a.txt", "dirty\n")
        self.assertEqual(ewk("check", "--evidence", self.ev, "--repo", self.repo).returncode, 1)
        git(self.repo, "checkout", "--", "a.txt")
        self.assertEqual(ewk("check", "--evidence", self.ev, "--repo", self.repo).returncode, 0)
        self.write("new.txt", "x\n")
        self.assertEqual(ewk("check", "--evidence", self.ev, "--repo", self.repo).returncode, 1)

    def test_evidence_file_inside_repo_does_not_self_invalidate(self):
        ev = os.path.join(self.repo, "ev.json")
        subprocess.run([PY, EWK, "run", "--evidence", ev, "--id", "t", "--repo", self.repo,
                        "--", PY, "-c", "pass"], capture_output=True)
        self.assertEqual(ewk("check", "--evidence", ev, "--repo", self.repo).returncode, 0)

    def test_forged_pass_without_exit_code_rejected(self):
        jdump(self.ev, {"records": [{"id": "x", "status": "PASS", "cmd": ["true"], "state": None}]})
        self.assertEqual(ewk("check", "--evidence", self.ev, "--repo", self.repo).returncode, 1)

    def test_not_run_needs_note_and_required_missing_fails(self):
        jdump(self.ev, {"records": [{"id": "x", "status": "NOT_RUN"}]})
        self.assertEqual(ewk("check", "--evidence", self.ev, "--repo", self.repo).returncode, 1)
        jdump(self.ev, {"records": []})
        r = ewk("check", "--evidence", self.ev, "--repo", self.repo, "--require", "unit")
        self.assertEqual(r.returncode, 1)

    def test_missing_or_corrupt_evidence_is_exit_2(self):
        self.assertEqual(ewk("check", "--evidence", self.ev, "--repo", self.repo).returncode, 2)
        jdump(self.ev, None, raw="{not json")
        self.assertEqual(ewk("check", "--evidence", self.ev, "--repo", self.repo).returncode, 2)

    def test_timeout_kills_process_tree_and_does_not_hang(self):
        marker = os.path.join(self.tmp.name, "child-alive")
        child = os.path.join(self.tmp.name, "child.py")
        parent = os.path.join(self.tmp.name, "parent.py")
        with open(child, "w", encoding="utf-8") as f:
            f.write("import sys, time, pathlib\ntime.sleep(3)\npathlib.Path(sys.argv[1]).write_text('x')\n")
        with open(parent, "w", encoding="utf-8") as f:
            f.write("import subprocess, sys, time\n"
                    "subprocess.Popen([sys.executable, sys.argv[1], sys.argv[2]])\ntime.sleep(60)\n")
        t0 = time.time()
        r = subprocess.run([PY, EWK, "run", "--evidence", self.ev, "--id", "slow", "--repo", self.repo,
                            "--timeout", "1", "--", PY, parent, child, marker], capture_output=True, text=True)
        self.assertLess(time.time() - t0, 20)
        self.assertEqual(r.returncode, 124)
        self.assertEqual(jload(self.ev)["records"][0]["status"], "FAIL")
        time.sleep(4)
        self.assertFalse(os.path.exists(marker), "grandchild survived the timeout")

    def test_missing_executable_is_blocked_not_pass(self):
        r = ewk("run", "--evidence", self.ev, "--id", "n", "--repo", self.repo, "--", "no-such-tool-xyz")
        self.assertEqual(r.returncode, 127)
        rec = jload(self.ev)["records"][0]
        self.assertEqual(rec["status"], "BLOCKED")

    def test_duplicate_id_refused(self):
        self.run_ok("t1")
        self.assertEqual(self.run_ok("t1").returncode, 2)

    def test_non_git_dir_is_unbound_and_strict_rejects(self):
        d = os.path.join(self.tmp.name, "plain")
        os.mkdir(d)
        ev = os.path.join(self.tmp.name, "e2.json")
        subprocess.run([PY, EWK, "run", "--evidence", ev, "--id", "t", "--repo", d, "--", PY, "-c", "pass"],
                       capture_output=True)
        self.assertEqual(ewk("check", "--evidence", ev, "--repo", d).returncode, 1)
        self.assertEqual(ewk("check", "--evidence", ev, "--repo", d, "--allow-unbound").returncode, 0)


class TestReviewRegressions(Repo):
    def test_command_that_mutates_tree_is_not_a_pass(self):
        r = ewk("run", "--evidence", self.ev, "--id", "m", "--repo", self.repo, "--", PY, "-c",
                "open('made.txt','w').write('x')")
        self.assertNotEqual(r.returncode, 0)
        rec = jload(self.ev)["records"][0]
        self.assertEqual(rec["status"], "FAIL")
        self.assertTrue(rec["mutated_tree"])

    def test_forged_unbound_pass_rejected_by_default(self):
        jdump(self.ev, {"records": [{"id": "x", "status": "PASS", "cmd": ["t"], "exit_code": 0, "state": None}]})
        self.assertEqual(ewk("check", "--evidence", self.ev, "--repo", self.repo).returncode, 1)

    def test_malformed_record_is_reported_not_crash(self):
        jdump(self.ev, {"records": [1]})
        r = ewk("check", "--evidence", self.ev, "--repo", self.repo)
        self.assertEqual(r.returncode, 1)
        self.assertNotIn("Traceback", r.stderr)

    def test_dirty_submodule_changes_state(self):
        sub = os.path.join(self.tmp.name, "subsrc")
        os.mkdir(sub)
        git(sub, "init", "-q", "-b", "main")
        with open(os.path.join(sub, "f.txt"), "w") as f:
            f.write("1\n")
        git(sub, "add", "-A"); git(sub, "commit", "-qm", "s")
        git(self.repo, "-c", "protocol.file.allow=always", "submodule", "add", sub, "m")
        git(self.repo, "commit", "-qm", "add sub")
        self.run_ok("t")
        self.assertEqual(ewk("check", "--evidence", self.ev, "--repo", self.repo).returncode, 0)
        with open(os.path.join(self.repo, "m", "f.txt"), "w") as f:
            f.write("2\n")
        self.assertEqual(ewk("check", "--evidence", self.ev, "--repo", self.repo).returncode, 1)
        with open(os.path.join(self.repo, "m", "f.txt"), "w") as f:
            f.write("3\n")
        with open(os.path.join(self.repo, "m", "new.txt"), "w") as f:
            f.write("n\n")
        self.run_ok("t2")
        with open(os.path.join(self.repo, "m", "new.txt"), "w") as f:
            f.write("changed\n")
        self.assertEqual(ewk("check", "--evidence", self.ev, "--repo", self.repo, "--require", "t2").returncode, 1)

    def test_guard_sees_deleted_and_renamed_protected_files(self):
        self.write(".ewk.json", json.dumps({"protected_paths": ["src/"]}))
        self.write("src/a.txt", "a\n"); self.write("src/b.txt", "b\n")
        git(self.repo, "add", "-A"); git(self.repo, "commit", "-qm", "src")
        git(self.repo, "rm", "-q", "src/a.txt")
        self.assertEqual(ewk("guard", "--repo", self.repo, "--worktree-only").returncode, 1)
        git(self.repo, "reset", "-q", "--hard")
        git(self.repo, "mv", "src/b.txt", "moved.txt")
        self.assertEqual(ewk("guard", "--repo", self.repo, "--worktree-only").returncode, 1)

    def test_guard_secret_on_line_starting_with_plus_plus(self):
        key = "AK" + "IA" + "ABCDEFGHIJKLMNOP"
        self.write("p.txt", "++ " + key + "\n")
        git(self.repo, "add", "-A")
        self.assertEqual(ewk("guard", "--repo", self.repo, "--worktree-only").returncode, 1)

    def test_relative_executable_resolves_against_repo(self):
        self.write("tool.cmd" if os.name == "nt" else "tool.sh", "echo ok\n" if os.name == "nt" else "#!/bin/sh\necho ok\n")
        if os.name != "nt":
            os.chmod(os.path.join(self.repo, "tool.sh"), 0o755)
        git(self.repo, "add", "-A"); git(self.repo, "commit", "-qm", "tool")
        name = "./tool.cmd" if os.name == "nt" else "./tool.sh"
        r = subprocess.run([PY, EWK, "run", "--evidence", self.ev, "--id", "rel", "--repo", self.repo, "--", name],
                           cwd=self.tmp.name, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class TestGuard(Repo):
    def branch(self):
        git(self.repo, "branch", "base")  # base == current main commit

    def test_clean_ok_and_read_only(self):
        self.branch()
        before = git(self.repo, "status", "--porcelain")
        r = ewk("guard", "--repo", self.repo, "--base", "base")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(before, git(self.repo, "status", "--porcelain"))

    def test_unresolvable_base_is_exit_2(self):
        self.assertEqual(ewk("guard", "--repo", self.repo, "--base", "nope").returncode, 2)

    def test_no_base_found_needs_flag(self):
        git(self.repo, "branch", "-m", "trunk")
        self.assertEqual(ewk("guard", "--repo", self.repo).returncode, 2)
        self.assertEqual(ewk("guard", "--repo", self.repo, "--worktree-only").returncode, 0)

    def test_not_a_repo_is_exit_2(self):
        self.assertEqual(ewk("guard", "--repo", self.tmp.name, "--worktree-only").returncode, 2)

    def test_protected_path(self):
        self.branch()
        self.write(".ewk.json", json.dumps({"protected_paths": ["releases/"]}))
        git(self.repo, "add", "-A"); git(self.repo, "commit", "-qm", "conf")
        self.write("releases/x.md", "x\n")
        r = ewk("guard", "--repo", self.repo, "--worktree-only")
        self.assertEqual(r.returncode, 1)
        self.assertIn("releases/", r.stdout)
        self.assertIn("fix:", r.stdout)

    def test_mojibake_and_bom(self):
        self.write("m.md", "bad \ufffd char\n")
        self.write("zh.ps1", "Write-Host '中文'\n")
        r = ewk("guard", "--repo", self.repo, "--worktree-only")
        self.assertEqual(r.returncode, 1)
        self.assertIn("U+FFFD", r.stdout)
        self.assertIn("BOM", r.stdout)

    def test_bom_present_and_ascii_ps1_pass(self):
        self.write("ok.ps1", b"\xef\xbb\xbfWrite-Host '\xe4\xb8\xad'\n", mode="wb")
        self.write("ascii.ps1", "Write-Host 'x'\n")
        self.assertEqual(ewk("guard", "--repo", self.repo, "--worktree-only").returncode, 0)

    def test_invalid_utf8_text_file(self):
        self.write("bad.md", b"\xff\xfe\xfa", mode="wb")
        self.assertEqual(ewk("guard", "--repo", self.repo, "--worktree-only").returncode, 1)

    def test_binary_ignored(self):
        self.write("img.bin", b"\x00\xff\xfe\x00", mode="wb")
        self.assertEqual(ewk("guard", "--repo", self.repo, "--worktree-only").returncode, 0)

    def test_secret_in_added_line_untracked_and_committed(self):
        key = "AK" + "IA" + "ABCDEFGHIJKLMNOP"  # built at runtime so this file never matches itself
        self.write("cfg.py", f'KEY = "{key}"\n')
        r = ewk("guard", "--repo", self.repo, "--worktree-only")
        self.assertEqual(r.returncode, 1)
        self.assertIn("secret", r.stdout)

    def test_secret_in_old_line_not_flagged(self):
        key = "gh" + "p_" + "a" * 36
        self.write("old.txt", key + "\n")
        git(self.repo, "add", "-A"); git(self.repo, "commit", "-qm", "old")
        self.branch()
        self.write("a.txt", "two\n")
        self.assertEqual(ewk("guard", "--repo", self.repo, "--base", "base").returncode, 0)

    def test_local_path_regex(self):
        self.write(".ewk.json", json.dumps({"local_path_re": r"C:[/\\]Users[/\\]someone"}))
        self.write("n.md", "see C:\\Users\\someone\\x\n")
        r = ewk("guard", "--repo", self.repo, "--worktree-only")
        self.assertEqual(r.returncode, 1)
        self.assertIn("local path", r.stdout)

    def test_bad_conf_is_exit_2(self):
        self.write(".ewk.json", "{oops")
        self.assertEqual(ewk("guard", "--repo", self.repo, "--worktree-only").returncode, 2)

    def test_committed_change_vs_base(self):
        self.branch()
        self.write("m.md", "bad \ufffd\n")
        git(self.repo, "add", "-A"); git(self.repo, "commit", "-qm", "oops")
        self.assertEqual(ewk("guard", "--repo", self.repo, "--base", "base").returncode, 1)


class TestRoute(unittest.TestCase):
    def route(self, files, *flags):
        r = ewk("route", "--files-from", "-", *flags, stdin="\n".join(files))
        self.assertEqual(r.returncode, 0)
        return json.loads(r.stdout)

    def test_docs_only_is_fast(self):
        self.assertEqual(self.route(["README.md", "docs/guide.md", "docs/a.png"])["tier"], "Fast")
        self.assertEqual(self.route(["README.md", "src/a.png"])["tier"], "Standard")

    def test_code_is_standard(self):
        self.assertEqual(self.route(["src/app.py"])["tier"], "Standard")

    def test_sensitive_paths_are_critical(self):
        for p in ["db/migrations/001.sql", ".github/workflows/ci.yml", "src/auth/login.py", "tools/deploy.ps1"]:
            self.assertEqual(self.route([p])["tier"], "Critical", p)

    def test_flag_escalates_docs(self):
        self.assertEqual(self.route(["README.md"], "--irreversible")["tier"], "Critical")

    def test_empty_input_not_fast(self):
        self.assertEqual(self.route([])["tier"], "Standard")

    def test_windows_separators(self):
        self.assertEqual(self.route([".github\\workflows\\ci.yml"])["tier"], "Critical")

    def test_dependency_manifest_noted(self):
        out = self.route(["package-lock.json"])
        self.assertEqual(out["tier"], "Standard")
        self.assertTrue(any("dependency" in r for r in out["reasons"]))


if __name__ == "__main__":
    unittest.main()
