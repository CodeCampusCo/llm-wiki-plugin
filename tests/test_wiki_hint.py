import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import wiki_hint as wh  # noqa: E402
import wikiconf  # noqa: E402


class Matches(unittest.TestCase):
    def test_latin_is_a_whole_word_or_identifier(self):
        self.assertTrue(wh.matches("pr", "push แล้วเปิด pr ให้เลย"))
        self.assertTrue(wh.matches("pr", "(pr)"))
        self.assertFalse(wh.matches("pr", "prompt"))
        self.assertFalse(wh.matches("api", "api-gateway-x"))
        self.assertFalse(wh.matches("core", "my-core-x"))
        self.assertTrue(wh.matches("db-migrate", "run db-migrate first"))

    def test_identifier_prefixes_and_paths(self):
        self.assertTrue(wh.matches("tk_", "update tk_abc123"))
        self.assertTrue(wh.matches("/status", "check /status endpoint"))
        self.assertFalse(wh.matches("status", "check /status endpoint"))

    def test_thai_is_a_substring_and_case_is_ignored(self):
        self.assertTrue(wh.matches("เปิด pr", "แล้วเปิด pr"))
        self.assertTrue(wh.matches("เสียบ key", "เสียบ key แล้ว"))
        self.assertTrue(wh.matches("CMS", "cms user"))
        self.assertFalse(wh.matches("", "anything"))


class Fixture(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.pages = self.root / "wiki"
        (self.pages / "concepts").mkdir(parents=True)
        c = self.pages / "concepts"
        (c / "sign.md").write_text(
            '---\ntitle: "Signing"\nkeywords: ["commit", "เสียบ key", "vpn"]\n---\n> TL;DR: Sign it.\n')
        (c / "pr.md").write_text('---\ntitle: "PR"\nkeywords: ["pr", "commit"]\n---\n> TL;DR: PRs.\n')
        (c / "none.md").write_text('---\ntitle: "None"\n---\ncommit in the body only\n')
        (c / "bad.md").write_text('---\ntitle: "Bad"\nkeywords: [not json\n---\n')
        self.wiki = wikiconf.Wiki(self.root, self.root / "raw", self.root / "archive", "my-wiki", 1)

    def test_ranks_by_matched_keywords_and_ignores_body_and_bad_frontmatter(self):
        p = self.pages
        self.assertEqual(wh.rank("เสียบ key แล้ว commit", p),
                         [("concepts/sign.md", "Signing"), ("concepts/pr.md", "PR")])
        self.assertEqual(wh.rank("commit then open a pr", p),
                         [("concepts/pr.md", "PR"), ("concepts/sign.md", "Signing")])
        self.assertEqual(wh.rank("ทำวิดีโอให้หน่อย", p), [])

    def test_hint_carries_the_tldr_and_skips_pages_already_shown(self):
        text, found = wh.hint("commit", {"concepts/pr.md"}, self.wiki)
        self.assertEqual(found, ["concepts/sign.md"])
        self.assertIn("concepts/sign.md: Signing. Sign it.", text)
        self.assertEqual(wh.hint("commit", {"concepts/pr.md", "concepts/sign.md"}, self.wiki), ("", []))

    def test_a_shown_top_page_is_not_replaced_by_a_weaker_one(self):
        with mock.patch.object(wh, "MAX_HITS", 1):
            self.assertEqual(wh.hint("pr commit", {"concepts/pr.md"}, self.wiki), ("", []))

    def test_tldr_is_truncated(self):
        (self.pages / "long.md").write_text("> TL;DR: " + "word " * 100 + "\n")
        self.assertLessEqual(len(wh.tldr(self.pages, "long.md")), wh.TLDR_CHARS + 4)
        self.assertEqual(wh.tldr(self.pages, "missing.md"), "")

    def test_header_uses_qmd_collection_or_read_path(self):
        text, _ = wh.hint("commit", set(), self.wiki)
        self.assertIn("qmd get qmd://my-wiki/<path>", text.splitlines()[0])
        plain = wikiconf.Wiki(self.root, self.root / "raw", self.root / "archive", None, 1)
        text, _ = wh.hint("commit", set(), plain)
        self.assertIn(f"Read {self.root}/wiki/<path>", text.splitlines()[0])
        self.assertNotIn("qmd", text.splitlines()[0])


class BadPage(unittest.TestCase):
    def test_non_utf8_page_does_not_break_hints(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "concepts"
            d.mkdir()
            (d / "bad.md").write_bytes(b'---\ntitle: "B"\nkeywords: ["zzz"]\n---\n\xff\xfe\n')
            (d / "good.md").write_text('---\ntitle: "G"\nkeywords: ["deploy"]\n---\n')
            self.assertEqual(wh.rank("please deploy", tmp), [("concepts/good.md", "G")])
            self.assertEqual(wh.rank("zzz", tmp), [("concepts/bad.md", "B")])


class EndToEnd(unittest.TestCase):
    def run_hook(self, payload, tmp, data, wiki_dir=None):
        env = {**os.environ, "TMPDIR": tmp}
        env.pop("LLM_WIKI_DIR", None)
        if wiki_dir:
            env["LLM_WIKI_DIR"] = str(wiki_dir)
        return subprocess.run([sys.executable, str(SCRIPTS / "wiki_hint.py"), str(data)],
                              input=payload, capture_output=True, text=True, env=env)

    def make_root(self, tmp):
        root = Path(tmp) / "wikiroot"
        (root / "wiki" / "concepts").mkdir(parents=True)
        (root / ".llm-wiki.json").write_text("{}")
        (root / "wiki" / "concepts" / "sign.md").write_text(
            '---\ntitle: "Signing"\nkeywords: ["commit", "เสียบ key"]\n---\n> TL;DR: Sign it.\n')
        return root

    def test_hints_once_per_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_root(tmp)
            payload = json.dumps({"session_id": "t1", "prompt": "เสียบ key แล้ว commit ให้เลย"})
            out = self.run_hook(payload, tmp, Path(tmp) / "data", root).stdout
            ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("concepts/sign.md", ctx)
            self.assertLess(len(ctx), 1200)
            self.assertEqual(self.run_hook(payload, tmp, Path(tmp) / "data", root).stdout, "")
            self.assertTrue((Path(tmp) / "llm-wiki-hint" / "t1").exists())

    def test_bad_input_prints_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self.run_hook("not json", tmp, Path(tmp) / "data", self.make_root(tmp))
            self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_no_wiki_configured_prints_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            data.mkdir()
            payload = json.dumps({"session_id": "t2", "prompt": "commit"})
            r = self.run_hook(payload, tmp, data)
            self.assertEqual((r.returncode, r.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
