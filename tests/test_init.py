import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "init_wiki.py"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True)


class InitTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.data = self.tmp / "data"

    def tearDown(self):
        self._tmp.cleanup()

    def test_new_creates_layout_and_pointer(self):
        wiki, raw = self.tmp / "my wiki", self.tmp / "rawdir"
        r = run(self.data, "new", "--wiki-dir", wiki, "--raw-dir", raw)
        self.assertEqual(r.returncode, 0, r.stderr)
        for p in ("wiki/index.md", "wiki/concepts/.gitkeep", "CONVENTIONS.md",
                  ".llm-wiki.json", ".gitignore", ".obsidian/app.json", ".git"):
            self.assertTrue((wiki / p).exists(), p)
        self.assertFalse((wiki / "raw-README.md").exists())
        self.assertTrue((raw / "README.md").exists())
        log = (wiki / "wiki" / "log.md").read_text()
        self.assertIn(f"## [{date.today().isoformat()}] bootstrap", log)
        self.assertNotIn("YYYY-MM-DD] bootstrap", log)
        conf = json.loads((wiki / ".llm-wiki.json").read_text())
        self.assertEqual(conf["raw_dir"], str(raw))
        pointer = json.loads((self.data / "config.json").read_text())
        self.assertEqual(pointer["wiki_dir"], str(wiki))
        self.assertEqual(json.loads(r.stdout)["wiki_dir"], str(wiki))

    def test_new_refuses_non_empty_dir(self):
        wiki = self.tmp / "w"
        wiki.mkdir()
        (wiki / "keep.txt").write_text("x")
        r = run(self.data, "new", "--wiki-dir", wiki, "--raw-dir", self.tmp / "r")
        self.assertEqual(r.returncode, 2)
        self.assertEqual([p.name for p in wiki.iterdir()], ["keep.txt"])
        self.assertFalse(self.data.exists())
        self.assertFalse((self.tmp / "r").exists())

    def test_existing_requires_config(self):
        wiki = self.tmp / "w"
        wiki.mkdir()
        r = run(self.data, "existing", "--wiki-dir", wiki)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(self.data.exists())

    def test_existing_with_corrupt_config_refuses(self):
        wiki = self.tmp / "w"
        wiki.mkdir()
        (wiki / ".llm-wiki.json").write_text("{not json")
        r = run(self.data, "existing", "--wiki-dir", wiki)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(self.data.exists())

    def test_existing_sets_collection_and_pointer(self):
        wiki = self.tmp / "w"
        self.assertEqual(run(self.data, "new", "--wiki-dir", wiki,
                             "--raw-dir", self.tmp / "r").returncode, 0)
        r = run(self.tmp / "d2", "existing", "--wiki-dir", wiki,
                "--qmd-collection", "mine")
        self.assertEqual(r.returncode, 0, r.stderr)
        conf = json.loads((wiki / ".llm-wiki.json").read_text())
        self.assertEqual(conf["qmd_collection"], "mine")
        self.assertTrue((self.tmp / "d2" / "config.json").exists())

    def test_snippet_mentions_wiki_path(self):
        wiki = self.tmp / "w"
        run(self.data, "new", "--wiki-dir", wiki, "--raw-dir", self.tmp / "r")
        r = run(self.data, "snippet")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(str(wiki), r.stdout)
        self.assertIn("My wiki lives at", r.stdout)
        self.assertNotIn("before exploring", r.stdout)
        self.assertNotIn("approval", r.stdout)

    def test_new_without_git_leaves_nothing(self):
        wiki = self.tmp / "w"
        env = {"PATH": str(self.tmp / "empty")}
        r = subprocess.run([sys.executable, str(SCRIPT), str(self.data), "new",
                            "--wiki-dir", str(wiki), "--raw-dir",
                            str(self.tmp / "r")],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)
        self.assertFalse(wiki.exists())
        self.assertFalse(self.data.exists())

    def test_new_raw_path_is_file(self):
        raw = self.tmp / "rawfile"
        raw.write_text("x")
        wiki = self.tmp / "w"
        r = run(self.data, "new", "--wiki-dir", wiki, "--raw-dir", raw)
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)
        self.assertFalse(wiki.exists())

    def test_new_keeps_existing_raw_readme(self):
        raw = self.tmp / "r"
        raw.mkdir()
        (raw / "README.md").write_text("mine")
        run(self.data, "new", "--wiki-dir", self.tmp / "w", "--raw-dir", raw)
        self.assertEqual((raw / "README.md").read_text(), "mine")

    def test_empty_data_dir_refuses_and_writes_nothing_in_cwd(self):
        cwd = self.tmp / "cwd"
        cwd.mkdir()
        r = subprocess.run([sys.executable, str(SCRIPT), "", "new", "--wiki-dir",
                            str(self.tmp / "w"), "--raw-dir", str(self.tmp / "r")],
                           capture_output=True, text=True, cwd=cwd)
        self.assertEqual(r.returncode, 2)
        self.assertIn("data dir", r.stderr)
        self.assertEqual(list(cwd.iterdir()), [])
        self.assertFalse((self.tmp / "w").exists())

    def test_paths_under_home_are_stored_with_tilde(self):
        home = self.tmp / "home"
        home.mkdir()
        wiki = self.tmp / "w"
        env = dict(os.environ, HOME=str(home))
        r = subprocess.run([sys.executable, str(SCRIPT), str(self.data), "new",
                            "--wiki-dir", str(wiki), "--raw-dir", str(home / "raw store"),
                            "--archive-dir", str(home / "arch")],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        conf = json.loads((wiki / ".llm-wiki.json").read_text())
        self.assertEqual(conf["raw_dir"], "~/raw store")
        self.assertEqual(conf["archive_dir"], "~/arch")
        self.assertNotIn(str(home), (wiki / ".llm-wiki.json").read_text())

    def test_snippet_ignores_env_override(self):
        wiki, other = self.tmp / "w", self.tmp / "other"
        run(self.data, "new", "--wiki-dir", wiki, "--raw-dir", self.tmp / "r")
        run(self.tmp / "d2", "new", "--wiki-dir", other, "--raw-dir",
            self.tmp / "r2")
        env = dict(os.environ, LLM_WIKI_DIR=str(other))
        r = subprocess.run([sys.executable, str(SCRIPT), str(self.data),
                            "snippet"], capture_output=True, text=True, env=env)
        self.assertIn(str(wiki), r.stdout)
        self.assertNotIn(str(other), r.stdout)


if __name__ == "__main__":
    unittest.main()
