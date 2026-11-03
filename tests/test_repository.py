import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "authentik"


class AuthentikRepositoryTest(unittest.TestCase):
    def test_one_addon_only(self):
        assert (ADDON / "config.yaml").is_file()
        other_addons = [
            p.name for p in ROOT.iterdir()
            if p.is_dir() and p.name not in {"authentik", ".github", "tests"}
        ]
        self.assertEqual(other_addons, [])

    def test_version_matches_build_and_upstream(self):
        build = (ADDON / "build.yaml").read_text()
        manifest = (ADDON / "config.yaml").read_text()
        docker = (ADDON / "Dockerfile").read_text()
        match = re.search(r'(?m)^\s+VERSION: "([0-9]{4}\.[0-9]+\.[0-9]+)"$', build)
        self.assertIsNotNone(match)
        version = match.group(1)
        self.assertRegex(manifest, r'(?m)^version: "' + re.escape(version) + r'-[0-9]+"$')
        self.assertIn("ghcr.io/goauthentik/server:${VERSION}", docker)
        self.assertIn("slug: \"authentik\"", manifest)

    def test_origin_and_scope(self):
        manifest = (ADDON / "config.yaml").read_text()
        repository = (ROOT / "repository.yaml").read_text()
        self.assertIn("https://github.com/Akm0d/ha-authentic-addon", repository)
        self.assertIn("https://github.com/Akm0d/ha-authentic-addon", manifest)
        self.assertIn("  - amd64", manifest)
        self.assertIn('boot: "manual"', manifest)
        self.assertIn("9000/tcp: 9000", manifest)
        self.assertNotIn("ingress: true", manifest)


if __name__ == "__main__":
    unittest.main()
