import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import lint_wiki  # noqa: E402
import wikiconf  # noqa: E402

GOOD = ('---\ntitle: "T"\ntype: concept\ntags: []\ncreated: 2026-01-01\nupdated: 2026-01-01\n'
        'sources: []\n---\n> TL;DR: x\n')


class Lint(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for d in ("concepts", "sources", "entities"):
            (self.root / "wiki" / d).mkdir(parents=True)

    def wiki(self, version=1):
        return wikiconf.Wiki(self.root, self.root / "raw", self.root / "archive", None, version)

    def put(self, rel, text):
        (self.root / "wiki" / rel).write_text(text)

    def kinds(self, version=1):
        return {(k, p) for k, p, _ in lint_wiki.check(self.wiki(version))}

    def test_flags_missing_frontmatter_broken_link_orphan(self):
        self.put("index.md", "[[concepts/a]] [[concepts/missing|Gone]]\n")
        self.put("concepts/a.md", GOOD.replace("tags: []\n", ""))
        self.put("concepts/lonely.md", GOOD)
        found = self.kinds()
        self.assertIn(("frontmatter", "concepts/a.md"), found)
        self.assertIn(("broken-link", "index.md"), found)
        self.assertIn(("orphan", "concepts/lonely.md"), found)
        self.assertNotIn(("orphan", "concepts/a.md"), found)
        self.assertNotIn(("frontmatter", "index.md"), found)

    def test_flags_bad_keywords_line(self):
        self.put("index.md", "[[concepts/a]]\n")
        self.put("concepts/a.md", GOOD.replace("---\n>", "keywords: [oops\n---\n>"))
        self.assertIn(("keywords", "concepts/a.md"), self.kinds())

    def test_flags_secret_patterns_and_email(self):
        bodies = ["AKIA" + "A" * 16, "-----BEGIN RSA PRIVATE KEY-----", "xoxb-123",
                  "ghp_" + "a" * 36, "sk-" + "a" * 20, "me@example.com"]
        self.put("index.md", "[[concepts/s]]\n")
        self.put("concepts/s.md", GOOD + "\n".join(bodies) + "\n")
        details = [d for k, _, d in lint_wiki.check(self.wiki()) if k == "secret"]
        self.assertEqual(len(details), 6)
        self.assertFalse(any("AKIAAAAA" in d for d in details))

    def test_older_schema_version_points_to_changelog(self):
        found = lint_wiki.check(self.wiki(version=0))
        self.assertEqual([k for k, _, _ in found], ["schema"])
        self.assertIn("schema/CHANGELOG.md", found[0][2])

    def test_newer_schema_version_says_update_plugin(self):
        found = lint_wiki.check(self.wiki(version=99))
        self.assertEqual([k for k, _, _ in found], ["schema"])
        self.assertIn("update the plugin", found[0][2])

    def test_non_utf8_page_does_not_crash_check_or_main(self):
        self.put("index.md", "[[concepts/b]]\n")
        (self.root / "wiki" / "concepts" / "b.md").write_bytes(
            b'---\ntitle: "B"\nkeywords: ["x"]\n---\n\xff\xfe\n')
        lint_wiki.check(self.wiki())
        (self.root / ".llm-wiki.json").write_text('{"schema_version": 1}')
        with mock.patch("sys.stdout", new_callable=io.StringIO), \
                mock.patch.dict("os.environ", {"LLM_WIKI_DIR": str(self.root)}):
            self.assertEqual(lint_wiki.main(["x", ""]), 0)

    def test_clean_skeleton_has_no_findings(self):
        shutil.copytree(ROOT / "skeleton", self.root / "sk")
        wiki = wikiconf.resolve(None, {"LLM_WIKI_DIR": str(self.root / "sk")})
        self.assertEqual(lint_wiki.check(wiki), [])


if __name__ == "__main__":
    unittest.main()
