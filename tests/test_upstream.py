import tempfile
import unittest
from pathlib import Path

from scripts.check_upstream import next_release, update_version


def release(version, **flags):
    return {"tag_name": f"version/{version}", "draft": False, "prerelease": False, **flags}


class UpstreamReleaseTests(unittest.TestCase):
    def test_ignores_prereleases_and_unrelated_tags(self):
        candidates = [release("2026.8.6", prerelease=True), {"tag_name": "nightly"},
                      release("2026.8.7", draft=True)]
        self.assertIsNone(next_release("2026.8.5", candidates))

    def test_prefers_current_train_patches(self):
        candidates = [release("2026.11.0"), release("2027.2.0"),
                      release("2026.8.6"), release("2026.8.7")]
        self.assertEqual(next_release("2026.8.5", candidates), "2026.8.7")

    def test_does_not_skip_next_train(self):
        candidates = [release("2027.2.3"), release("2026.11.0"),
                      release("2026.11.2"), release("2027.5.0")]
        self.assertEqual(next_release("2026.8.5", candidates), "2026.11.2")

    def test_version_file_updates_are_consistent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            addon = root / "authentik"
            addon.mkdir()
            (addon / "build.yaml").write_text('args:\n  VERSION: "2026.8.5"\n')
            (addon / "config.yaml").write_text('version: "2026.8.5-1"\n')
            (addon / "README.md").write_text(
                "[release-shield]: https://img.shields.io/badge/version-v2026.8.5-blue.svg\n"
                "[release]: https://github.com/goauthentik/authentik/releases/tag/version%2F2026.8.5\n"
            )
            (addon / "CHANGELOG.md").write_text("Historical notes\n")

            self.assertTrue(update_version(root, "2026.11.2"))
            self.assertIn('VERSION: "2026.11.2"', (addon / "build.yaml").read_text())
            self.assertIn('version: "2026.11.2-0"', (addon / "config.yaml").read_text())
            self.assertIn("version-v2026.11.2-blue.svg", (addon / "README.md").read_text())
            self.assertIn("version%2F2026.11.2", (addon / "README.md").read_text())
            self.assertIn("## 2026.11.2-0", (addon / "CHANGELOG.md").read_text())
            self.assertFalse(update_version(root, "2026.11.2"))


if __name__ == "__main__":
    unittest.main()
