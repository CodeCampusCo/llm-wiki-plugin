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

import post_wiki_edit as pwe  # noqa: E402
import session_start as ss  # noqa: E402
import wikiconf  # noqa: E402


def make_wiki(root, collection="notes"):
    root.mkdir(parents=True, exist_ok=True)
    conf = {"schema_version": 1}
    if collection:
        conf["qmd_collection"] = collection
    (root / ".llm-wiki.json").write_text(json.dumps(conf))
    (root / "wiki").mkdir(exist_ok=True)
    return wikiconf.resolve(None, {"LLM_WIKI_DIR": str(root)})


class ReindexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()

    def test_edit_in_other_projects_wiki_folder_is_ignored(self):
        wiki = make_wiki(self.tmp / "mine")
        self.assertFalse(pwe.should_reindex("/tmp/x/wiki/a.md", wiki))

    def test_edit_inside_wiki_with_collection(self):
        wiki = make_wiki(self.tmp / "mine")
        self.assertTrue(pwe.should_reindex(str(wiki.pages_dir / "concepts" / "a.md"), wiki))

    def test_no_collection_means_no_reindex(self):
        wiki = make_wiki(self.tmp / "mine", collection=None)
        self.assertFalse(pwe.should_reindex(str(wiki.pages_dir / "a.md"), wiki))

    def test_no_wiki_or_empty_path(self):
        self.assertFalse(pwe.should_reindex("/x/wiki/a.md", None))
        wiki = make_wiki(self.tmp / "mine")
        self.assertFalse(pwe.should_reindex("", wiki))

    def test_dotdot_escape_is_ignored(self):
        wiki = make_wiki(self.tmp / "mine")
        self.assertFalse(pwe.should_reindex(str(wiki.pages_dir / ".." / "raw" / "a.md"), wiki))

    def test_main_runs_qmd_update_with_timeout(self):
        wiki = make_wiki(self.tmp / "mine")
        payload = json.dumps({"tool_input": {"file_path": str(wiki.pages_dir / "a.md")}})
        with mock.patch.dict(os.environ, {"LLM_WIKI_DIR": str(wiki.root)}), \
                mock.patch("sys.stdin", __import__("io").StringIO(payload)), \
                mock.patch("shutil.which", return_value="/bin/qmd"), \
                mock.patch("subprocess.run") as run:
            pwe.main(["x", str(self.tmp / "data")])
        args, kwargs = run.call_args
        self.assertEqual(args[0], ["qmd", "update"])
        self.assertEqual(kwargs["timeout"], 10)

    def test_main_skips_without_qmd(self):
        wiki = make_wiki(self.tmp / "mine")
        payload = json.dumps({"tool_input": {"file_path": str(wiki.pages_dir / "a.md")}})
        with mock.patch.dict(os.environ, {"LLM_WIKI_DIR": str(wiki.root)}), \
                mock.patch("sys.stdin", __import__("io").StringIO(payload)), \
                mock.patch("shutil.which", return_value=None), \
                mock.patch("subprocess.run") as run:
            pwe.main(["x", str(self.tmp / "data")])
        run.assert_not_called()


class SessionStartTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()

    def test_session_start_unconfigured_points_to_init_with_labels(self):
        text = ss.context(None, Path("/plug"), Path("/data"))
        self.assertIn("Run /llm-wiki:init", text)
        self.assertIn("Plugin root: /plug", text.splitlines())
        self.assertIn("Plugin data dir: /data", text.splitlines())

    def test_session_start_configured_has_same_labels(self):
        text = ss.context(make_wiki(self.tmp / "mine"), Path("/plug"), Path("/data"))
        self.assertIn("Plugin root: /plug", text.splitlines())
        self.assertIn("Plugin data dir: /data", text.splitlines())

    def test_session_start_empty_or_missing_data_dir(self):
        for argv in (["x", ""], ["x"]):
            with self.subTest(argv=argv), mock.patch("sys.stdout", new_callable=__import__("io").StringIO) as out:
                ss.main(argv)
            self.assertEqual(out.getvalue().strip(),
                             "llm-wiki: plugin data dir unavailable; update Claude Code")

    def test_session_start_lists_last_five_log_entries(self):
        wiki = make_wiki(self.tmp / "mine")
        entries = [f"## [2026-01-0{i}] ingest | item {i}" for i in range(1, 8)]
        (wiki.pages_dir / "log.md").write_text("# Log\n\n" + "\n\nbody\n".join(entries) + "\n")
        text = ss.context(wiki, Path("/plug"), Path("/data"))
        self.assertNotIn("item 2", text)
        for i in range(3, 8):
            self.assertIn(f"item {i}", text)
        self.assertIn('python3 "/plug/scripts/wikiconf.py" show "/data"', text)
        self.assertIn("/plug/schema/schema.md", text)
        self.assertIn("/plug/scripts", text)
        self.assertIn(str(wiki.root), text)

    def test_missing_log_is_fine(self):
        wiki = make_wiki(self.tmp / "mine")
        self.assertIn(str(wiki.root), ss.context(wiki, Path("/plug"), Path("/data")))


class ExitZeroTests(unittest.TestCase):
    def test_hooks_exit_zero_on_garbage_stdin(self):
        for name in ("post_wiki_edit.py", "session_start.py"):
            with self.subTest(script=name):
                r = subprocess.run([sys.executable, str(SCRIPTS / name), "/nonexistent"],
                                   input="not json {{{", capture_output=True, text=True)
                self.assertEqual(r.returncode, 0)
                self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
