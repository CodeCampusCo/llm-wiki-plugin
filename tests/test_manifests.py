import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class ManifestTests(unittest.TestCase):
    def test_all_json_parses(self):
        for path in ROOT.rglob("*.json"):
            if ".git" in path.relative_to(ROOT).parts:
                continue
            with self.subTest(path=str(path.relative_to(ROOT))):
                json.loads(path.read_text(encoding="utf-8"))

    def test_hook_scripts_exist(self):
        hooks = ROOT / "hooks" / "hooks.json"
        if not hooks.exists():
            self.skipTest("hooks/hooks.json not present yet")
        names = re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/scripts/([\w.-]+\.py)",
                           hooks.read_text(encoding="utf-8"))
        for name in names:
            with self.subTest(script=name):
                self.assertTrue((ROOT / "scripts" / name).is_file())

    def test_names_agree(self):
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
        self.assertEqual(plugin["name"], market["plugins"][0]["name"])
        self.assertEqual(plugin["name"], "llm-wiki")


if __name__ == "__main__":
    unittest.main()
