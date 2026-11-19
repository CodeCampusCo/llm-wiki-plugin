import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import wikiconf  # noqa: E402


def make_wiki(root: Path, marker: str = "{}") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / ".llm-wiki.json").write_text(marker, encoding="utf-8")
    return root


class ResolveTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.data = self.tmp / "data"
        self.data.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_env_beats_pointer(self):
        env_wiki = make_wiki(self.tmp / "env-wiki")
        ptr_wiki = make_wiki(self.tmp / "ptr-wiki")
        wikiconf.write_pointer(self.data, ptr_wiki)
        wiki = wikiconf.resolve(self.data, {"LLM_WIKI_DIR": str(env_wiki)})
        self.assertEqual(wiki.root, env_wiki)
        wiki = wikiconf.resolve(self.data, {})
        self.assertEqual(wiki.root, ptr_wiki)

    def test_pointer_with_tilde_and_spaces(self):
        home = self.tmp / "home"
        make_wiki(home / "my wiki")
        (self.data / "config.json").write_text(
            json.dumps({"wiki_dir": "~/my wiki"}), encoding="utf-8")
        old = os.environ.get("HOME")
        os.environ["HOME"] = str(home)
        try:
            wiki = wikiconf.resolve(self.data, {"HOME": str(home)})
        finally:
            if old is None:
                del os.environ["HOME"]
            else:
                os.environ["HOME"] = old
        self.assertEqual(wiki.root, home / "my wiki")
        self.assertEqual(wiki.pages_dir, home / "my wiki" / "wiki")

    def test_relative_raw_dir_is_under_root(self):
        root = make_wiki(self.tmp / "w", json.dumps({
            "raw_dir": "raw", "archive_dir": str(self.tmp / "abs-archive"),
            "qmd_collection": "w", "schema_version": 1}))
        wiki = wikiconf.resolve(None, {"LLM_WIKI_DIR": str(root)})
        self.assertEqual(wiki.raw_dir, root / "raw")
        self.assertEqual(wiki.archive_dir, self.tmp / "abs-archive")
        self.assertEqual(wiki.qmd_collection, "w")
        self.assertEqual(wiki.schema_version, 1)

    def test_session_rules_default_on_and_only_false_turns_off(self):
        cases = [(None, True), (False, False), (True, True), ("no", True), (0, True)]
        for value, expected in cases:
            conf = {"schema_version": 1} if value is None else {"schema_version": 1, "session_rules": value}
            root = make_wiki(self.tmp / f"w-{value}", json.dumps(conf))
            with self.subTest(value=value):
                wiki = wikiconf.resolve(None, {"LLM_WIKI_DIR": str(root)})
                self.assertIs(wiki.session_rules, expected)

    def test_missing_or_corrupt_config_returns_none(self):
        self.assertIsNone(wikiconf.resolve(self.data, {}))
        self.assertIsNone(wikiconf.resolve(None, {}))
        empty = self.tmp / "empty"
        empty.mkdir()
        wikiconf.write_pointer(self.data, empty)
        self.assertIsNone(wikiconf.resolve(self.data, {}))
        make_wiki(empty, "{")
        self.assertIsNone(wikiconf.resolve(self.data, {}))
        (self.data / "config.json").write_text("{", encoding="utf-8")
        self.assertIsNone(wikiconf.resolve(self.data, {}))

    def test_show_cli_unconfigured(self):
        env = {k: v for k, v in os.environ.items() if k != "LLM_WIKI_DIR"}
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "wikiconf.py"), "show", str(self.data)],
            capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)
        self.assertIs(out["configured"], False)
        self.assertIn("plugin_root", out)


if __name__ == "__main__":
    unittest.main()
