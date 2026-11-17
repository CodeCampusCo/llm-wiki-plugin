import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import wikiconf  # noqa: E402


def tracked_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    return [ROOT / p for p in out if (ROOT / p).is_file()]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def digests(text: str) -> set[str]:
    """sha256 of every lowercase word, hyphen-joined compound and hyphen part in text."""
    out = set()
    for word in re.findall(r"[a-z0-9_-]+", text.lower()):
        for token in {word, word.strip("-"), *word.split("-")}:
            if token:
                out.add(hashlib.sha256(token.encode()).hexdigest())
        parts = [p for p in word.split("-") if p]
        for i in range(len(parts)):  # compounds such as "a-b" inside longer hyphenated words
            for j in range(i + 2, len(parts) + 1):
                out.add(hashlib.sha256("-".join(parts[i:j]).encode()).hexdigest())
    return out


class SchemaTests(unittest.TestCase):
    def test_no_slack_outside_superpowers_docs(self):
        needle = "sla" + "ck"
        bad = []
        for path in tracked_files():
            rel = path.relative_to(ROOT).as_posix()
            if rel.startswith("docs/superpowers/") or rel == "tests/test_schema.py":
                continue
            if needle in rel.lower() or needle in read_text(path).lower():
                bad.append(rel)
        self.assertEqual(bad, [])

    def test_no_personal_names(self):
        # Only sha256 digests of the forbidden lowercase tokens are stored, so this file does not leak them.
        forbidden = {
            "c77e3c070c3c1df247632a7e283f062548e75b3a1d224ff23bd1819d558e360b",
            "890137a2716d7a81cc09a94d75a22dba1767b522244ccccd3f9b0074d6f938dc",
            "a3b5e35e725d7c781631966050dd41877c82fc788b83b72e12a946bf30b1d386",
            "3582bcb898935077ec528b9ba8b31faaae068903333c3f4e8999ecb9e2961769",
        }
        bad = []
        for path in tracked_files():
            rel = path.relative_to(ROOT).as_posix()
            if rel == ".github/CODEOWNERS":
                continue
            if forbidden & digests(rel + "\n" + read_text(path)):
                bad.append(rel)
        self.assertEqual(bad, [])

    def test_schema_links_resolve(self):
        files = list((ROOT / "schema").glob("*.md"))
        files += list((ROOT / "schema" / "operations").glob("*.md"))
        files += list((ROOT / "skills").glob("*/SKILL.md"))
        self.assertTrue(files)
        pattern = re.compile(r"schema/[A-Za-z0-9_./-]+\.(?:md|json)")
        missing = []
        for f in files:
            for ref in pattern.findall(read_text(f)):
                if not (ROOT / ref).exists():
                    missing.append(f"{f.relative_to(ROOT)} -> {ref}")
        self.assertEqual(missing, [])

    def test_skeleton_config_matches_schema_version(self):
        cfg = json.loads((ROOT / "skeleton" / ".llm-wiki.json").read_text())
        self.assertEqual(cfg["schema_version"], wikiconf.SCHEMA_VERSION)

    def test_schema_has_keywords_and_backfill_rules(self):
        text = (ROOT / "schema" / "schema.md").read_text(encoding="utf-8")
        self.assertIn("keywords:", text)
        self.assertIn("Bootstrap backfill", text)

    def test_every_skill_has_description_and_reads_schema(self):
        names = {"init", "lint", "ingest", "query", "prune", "act"}
        skills = {p.parent.name: p for p in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertTrue(names <= set(skills), names - set(skills))
        for name, path in skills.items():
            text = read_text(path)
            self.assertRegex(text, r"(?m)^description:", name)
            if name != "init":  # init only creates the wiki; it reads no schema
                self.assertIn("schema/schema.md", text, name)


if __name__ == "__main__":
    unittest.main()
