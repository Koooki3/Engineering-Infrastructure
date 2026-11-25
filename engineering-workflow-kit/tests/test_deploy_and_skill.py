"""Deploy tool behaviour + skill hygiene (size budget, portability, links, frontmatter)."""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, ".."))
SKILL = os.path.join(KIT, "engineering-workflow")
DEPLOY = os.path.join(KIT, "tools", "deploy.py")
PY = sys.executable


def run(*a):
    return subprocess.run([PY, DEPLOY, *a], capture_output=True, text=True, encoding="utf-8")


def wr(p, data):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data if isinstance(data, bytes) else data.encode("utf-8"))


def rd(p):
    with open(p, "rb") as f:
        return f.read()


class TestDeploy(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory(prefix="ewk dep 部署 ")
        r = self.t.name
        self.src = os.path.join(r, "src", "engineering-workflow")
        wr(os.path.join(self.src, "SKILL.md"), "---\nname: x\n---\nhi\n")
        wr(os.path.join(self.src, "scripts", "a.py"), "print(1)\n")
        self.parents = [os.path.join(r, "p1", "skills"), os.path.join(r, "p 2", "skills")]
        self.block = os.path.join(r, "block.md")
        wr(self.block, "## 工程工作流\n- 路由一行\n")
        self.doc_lf = os.path.join(r, "AGENTS.md")
        self.doc_crlf = os.path.join(r, "CLAUDE.md")
        wr(self.doc_lf, "# A\n\ntext\n")
        wr(self.doc_crlf, b"\xef\xbb\xbf# C\r\n\r\ntext\r\n")
        self.orig = {p: rd(p) for p in (self.doc_lf, self.doc_crlf)}
        self.plan = os.path.join(r, "plan.json")
        self.state = os.path.join(r, "out", "state.json")
        self.write_plan()

    def write_plan(self, **kw):
        plan = {"src": self.src, "skill_name": "engineering-workflow", "version": "t",
                "skills": self.parents,
                "docs": [{"file": self.doc_lf, "block_file": self.block},
                         {"file": self.doc_crlf, "block_file": self.block}]}
        plan.update(kw)
        wr(self.plan, json.dumps(plan))

    def tearDown(self):
        self.t.cleanup()

    def apply(self):
        return run("apply", "--plan", self.plan, "--state", self.state)

    def test_apply_verify_rollback_byte_exact(self):
        r = self.apply()
        self.assertEqual(r.returncode, 0, r.stderr)
        for p in self.parents:
            self.assertTrue(os.path.exists(os.path.join(p, "engineering-workflow", "SKILL.md")))
        self.assertEqual(run("verify", "--state", self.state).returncode, 0)
        crlf = rd(self.doc_crlf)
        self.assertTrue(crlf.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\n", crlf.replace(b"\r\n", b""))  # CRLF preserved, no bare LF
        rb = run("rollback", "--state", self.state)
        self.assertEqual(rb.returncode, 0, rb.stderr)
        for p, data in self.orig.items():
            self.assertEqual(rd(p), data, p)
        for p in self.parents:
            self.assertFalse(os.path.exists(os.path.join(p, "engineering-workflow")))

    def test_reapply_requires_new_state_and_is_idempotent_on_content(self):
        self.apply()
        self.assertEqual(self.apply().returncode, 2)  # state exists
        state2 = self.state + "2.json"
        r = run("apply", "--plan", self.plan, "--state", state2)
        self.assertEqual(r.returncode, 0)
        self.assertIn("unchanged", r.stdout)
        docs = rd(self.doc_lf)
        self.assertEqual(docs.count(b"<!-- ewk:begin -->"), 1)
        # rolling back the no-op second state must not remove the first install
        self.assertEqual(run("rollback", "--state", state2).returncode, 0)
        self.assertTrue(os.path.exists(os.path.join(self.parents[0], "engineering-workflow")))
        self.assertEqual(run("verify", "--state", self.state).returncode, 0)

    def test_refuses_foreign_directory(self):
        wr(os.path.join(self.parents[0], "engineering-workflow", "mine.md"), "user's own")
        r = self.apply()
        self.assertEqual(r.returncode, 1)
        self.assertIn("not managed", r.stderr)
        self.assertEqual(rd(os.path.join(self.parents[0], "engineering-workflow", "mine.md")), b"user's own")

    def test_drift_detected_and_rollback_refuses_without_force(self):
        self.apply()
        wr(os.path.join(self.parents[0], "engineering-workflow", "SKILL.md"), "tampered")
        self.assertEqual(run("verify", "--state", self.state).returncode, 1)
        self.assertEqual(run("rollback", "--state", self.state).returncode, 1)
        self.assertTrue(os.path.exists(os.path.join(self.parents[0], "engineering-workflow")))
        self.assertEqual(run("rollback", "--state", self.state, "--force").returncode, 0)

    def test_update_backs_up_and_rollback_restores_previous(self):
        self.apply()
        wr(os.path.join(self.src, "SKILL.md"), "---\nname: x\n---\nv2\n")
        state2 = self.state + "2.json"
        r = run("apply", "--plan", self.plan, "--state", state2)
        self.assertIn("updated", r.stdout)
        self.assertIn(b"v2", rd(os.path.join(self.parents[0], "engineering-workflow", "SKILL.md")))
        self.assertEqual(run("rollback", "--state", state2).returncode, 0)
        self.assertIn(b"hi", rd(os.path.join(self.parents[0], "engineering-workflow", "SKILL.md")))

    def test_update_of_several_targets_in_same_second_does_not_collide(self):
        self.write_plan(skills=self.parents + [os.path.join(self.t.name, "p3", "skills"), os.path.join(self.t.name, "p4", "skills")])
        self.assertEqual(self.apply().returncode, 0)
        wr(os.path.join(self.src, "SKILL.md"), "---\nname: x\n---\nv3\n")
        r = run("apply", "--plan", self.plan, "--state", self.state + "3.json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count("updated"), 4)

    def test_later_unrelated_doc_edit_survives_rollback(self):
        self.apply()
        wr(self.doc_lf, rd(self.doc_lf) + b"\n## added later\n")
        self.assertEqual(run("rollback", "--state", self.state).returncode, 0)
        out = rd(self.doc_lf)
        self.assertIn(b"added later", out)
        self.assertNotIn(b"ewk:begin", out)

    def test_edited_block_blocks_rollback_without_force(self):
        self.apply()
        wr(self.doc_lf, rd(self.doc_lf).replace("路由一行".encode(), "改过".encode()))
        self.assertEqual(run("rollback", "--state", self.state).returncode, 1)

    def test_missing_doc_aborts_but_partial_state_allows_rollback(self):
        self.write_plan(docs=[{"file": os.path.join(self.t.name, "nope.md"), "block_file": self.block}])
        self.assertEqual(self.apply().returncode, 1)
        self.assertEqual(run("rollback", "--state", self.state).returncode, 0)
        for p in self.parents:
            self.assertFalse(os.path.exists(os.path.join(p, "engineering-workflow")))


class TestSkillHygiene(unittest.TestCase):
    def text(self, rel):
        with open(os.path.join(SKILL, rel), encoding="utf-8") as f:
            return f.read()

    def files(self):
        for d, _, fs in os.walk(SKILL):
            for n in fs:
                if not n.endswith(".pyc") and "__pycache__" not in d:
                    yield os.path.join(d, n)

    def test_frontmatter_and_name(self):
        t = self.text("SKILL.md")
        m = re.match(r"---\nname: ([a-z0-9-]+)\ndescription: (.+)\n---\n", t)
        self.assertTrue(m, "frontmatter must be exactly name + one-line description")
        self.assertEqual(m.group(1), "engineering-workflow")
        self.assertLess(len(m.group(2)), 400)

    def test_entry_context_budget(self):
        b = len(self.text("SKILL.md").encode("utf-8"))
        self.assertLess(b, 6500, f"SKILL.md is {b} bytes; keep the always-loaded entry small")

    def test_core_is_portable(self):
        bad = [r"[A-Za-z]:[\\/]", r"/home/\w+", r"/mnt/[a-z]/", r"BrimDeck", r"kooki", r"14983",
               r"@[\w.-]+\.(com|edu|sg)\b"]
        for p in self.files():
            if p.endswith(".py"):
                pass
            with open(p, encoding="utf-8") as f:
                t = f.read()
            for rx in bad:
                m = re.search(rx, t)
                self.assertIsNone(m, f"{os.path.relpath(p, SKILL)} contains local/project-specific text: {m and m.group(0)}")

    def test_referenced_files_exist(self):
        t = self.text("SKILL.md")
        for rel in set(re.findall(r"`((?:references|templates|scripts)/[\w./-]+)`", t)):
            self.assertTrue(os.path.exists(os.path.join(SKILL, rel)), rel)

    def test_no_empty_shells(self):
        for p in self.files():
            self.assertGreater(os.path.getsize(p), 200, os.path.relpath(p, SKILL))

    def test_status_vocabulary_matches_script(self):
        t = self.text("SKILL.md")
        sys.path.insert(0, os.path.join(SKILL, "scripts"))
        try:
            import ewk
        finally:
            sys.path.pop(0)
        for s in ewk.STATUSES:
            self.assertIn(s, t)

    def test_pr_interface_delegates_not_copies(self):
        t = self.text("SKILL.md")
        self.assertIn("pr-authoring", t)
        for phrase in ("中文摘要", "Conventional Commits", "--attach"):
            self.assertNotIn(phrase, t, "PR rules must stay in pr-authoring, not be copied here")


if __name__ == "__main__":
    unittest.main()
