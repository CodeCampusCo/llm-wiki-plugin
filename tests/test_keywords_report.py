import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import keywords_report as kr  # noqa: E402
import wikiconf  # noqa: E402


def user(content):
    return json.dumps({"type": "user", "message": {"role": "user", "content": content}})


class Report(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "wiki" / "concepts").mkdir(parents=True)
        (self.root / "wiki" / "concepts" / "a.md").write_text(
            '---\ntitle: "A"\nkeywords: ["deploy", "never-typed"]\n---\n')
        self.wiki = wikiconf.Wiki(self.root, self.root / "raw", self.root / "archive", None, 1)

    def transcript(self, lines):
        path = self.root / "t.jsonl"
        path.write_text("\n".join(lines) + "\n")
        return [path]

    def test_report_skips_bad_lines_and_tool_results(self):
        t = self.transcript([
            "not json", "[1]", user("hello world"),
            user([{"type": "text", "text": "block prompt"}, {"type": "tool_result", "content": "secret"}]),
            user([{"type": "tool_result", "content": "only result"}]),
            json.dumps({"type": "assistant", "message": {"content": "assistant text"}}),
        ])
        self.assertEqual(kr.prompts(t), ["hello world", "block prompt"])
        self.assertEqual(kr.report(self.wiki, t)["prompts"], 2)

    def test_skips_meta_sidechain_and_wrapper_text(self):
        t = self.transcript([
            json.dumps({"type": "user", "isMeta": True, "message": {"content": "meta"}}),
            json.dumps({"type": "user", "isSidechain": True, "message": {"content": "side"}}),
            user("<command-name>/x</command-name>"),
            user([{"type": "text", "text": "<system-reminder>x</system-reminder>"},
                  {"type": "text", "text": "real prompt"}]),
        ])
        self.assertEqual(kr.prompts(t), ["real prompt"])

    def test_bad_days_prints_usage_and_exits_zero(self):
        for args in (["x", "d", "--days", "abc"], ["x", "d", "--days"], ["x", "d", "--days", "0"]):
            with self.subTest(args=args), mock.patch("sys.stdout", new_callable=io.StringIO) as out:
                self.assertEqual(kr.main(args), 0)
            self.assertIn("usage", out.getvalue())

    def test_non_utf8_page_does_not_crash_report(self):
        (self.root / "wiki" / "concepts" / "bad.md").write_bytes(b"\xff\xfe\x00 keywords")
        kr.report(self.wiki, [])

    def test_never_matched_and_frequent_unmatched(self):
        lines = [user("please deploy the kubernetes cluster") for _ in range(5)]
        lines.append(user("rare ansible"))
        lines += [user("ทำ migration ให้หน่อย")] * 5
        result = kr.report(self.wiki, self.transcript(lines))
        self.assertEqual(result["never_matched"], [("concepts/a.md", "never-typed")])
        words = dict(result["frequent_unmatched"])
        self.assertEqual(words.get("kubernetes"), 5)
        self.assertEqual(words.get("migration"), 5)
        self.assertNotIn("deploy", words)
        self.assertNotIn("the", words)
        self.assertNotIn("ansible", words)
        self.assertTrue(any("ทำ" in w for w in words))


if __name__ == "__main__":
    unittest.main()
