#!/usr/bin/env python3
"""Track stable upstream Authentik releases without skipping release trains.

The workflow opens a PR; this script only changes source files in the checkout.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.github.com/repos/goauthentik/authentik/releases"
TAG = re.compile(r"^version/(\d{4})\.(\d+)\.(\d+)$")
VERSION = re.compile(r"^([0-9]{4})\.([0-9]+)\.([0-9]+)$")


def parse_version(value: str) -> tuple[int, int, int]:
    match = VERSION.fullmatch(value)
    if not match:
        raise ValueError(f"unsupported Authentik version: {value}")
    return tuple(map(int, match.groups()))


def next_release(current: str, releases: list[dict]) -> str | None:
    """Prefer patches on the current train, then the earliest newer train.

    Using the highest release globally could skip required intermediate trains.
    """
    installed = parse_version(current)
    candidates: set[tuple[int, int, int]] = set()
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue
        match = TAG.fullmatch(release.get("tag_name", ""))
        if match:
            candidate = tuple(map(int, match.groups()))
            if candidate > installed:
                candidates.add(candidate)
    if not candidates:
        return None
    current_train = [v for v in candidates if v[:2] == installed[:2]]
    if current_train:
        selected = max(current_train)
    else:
        first_train = min(v[:2] for v in candidates)
        selected = max(v for v in candidates if v[:2] == first_train)
    return ".".join(map(str, selected))


def fetch_releases() -> list[dict]:
    releases: list[dict] = []
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ha-authentic-addon-updater"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for page in range(1, 11):
        req = Request(f"{API}?per_page=100&page={page}", headers=headers)
        with urlopen(req, timeout=20) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise ValueError("Unexpected upstream GitHub releases payload")
        releases.extend(batch)
        if len(batch) < 100:
            return releases
    raise RuntimeError("More than 1000 releases: refusing to choose an incomplete upgrade path")


def exactly_one(source: str, pattern: str, replacement: str) -> str:
    updated, count = re.subn(pattern, lambda _: replacement, source, flags=re.M)
    if count != 1:
        raise ValueError(f"Expected exactly one match for {pattern!r}, got {count}")
    return updated


def current_version(root: Path = ROOT) -> str:
    build = (root / "authentik/build.yaml").read_text(encoding="utf-8")
    match = re.search(r'^  VERSION: "([0-9]{4}\.[0-9]+\.[0-9]+)"$', build, re.M)
    if not match:
        raise ValueError("Expected exactly one pinned Authentik version in build.yaml")
    return match.group(1)


def update_version(root: Path, target: str) -> bool:
    current = current_version(root)
    if parse_version(target) <= parse_version(current):
        return False

    paths = {name: root / name for name in (
        "authentik/build.yaml", "authentik/config.yaml",
        "authentik/README.md", "authentik/CHANGELOG.md",
    )}
    original = {key: path.read_text(encoding="utf-8") for key, path in paths.items()}
    build = exactly_one(original["authentik/build.yaml"],
                        r'^  VERSION: "[0-9]{4}\.[0-9]+\.[0-9]+"$',
                        f'  VERSION: "{target}"')
    manifest = exactly_one(original["authentik/config.yaml"],
                           r'^version: "[0-9]{4}\.[0-9]+\.[0-9]+-[0-9]+"$',
                           f'version: "{target}-0"')
    readme = exactly_one(original["authentik/README.md"],
                         r'^\[release-shield\]: https://img\.shields\.io/badge/version-v[0-9.]+-blue\.svg$',
                         f'[release-shield]: https://img.shields.io/badge/version-v{target}-blue.svg')
    readme = exactly_one(readme,
                         r'^\[release\]: https://github\.com/goauthentik/authentik/releases/tag/version%2F[0-9.]+$',
                         f'[release]: https://github.com/goauthentik/authentik/releases/tag/version%2F{target}')
    changelog = (f"## {target}-0 — upstream Authentik release\n\n"
                 f"- Update upstream Authentik from {current} to {target}.\n"
                 f"- Review upstream release notes and database upgrade sequence before deployment:\n"
                 f"  https://github.com/goauthentik/authentik/releases/tag/version%2F{target}\n\n"
                 + original["authentik/CHANGELOG.md"])

    changes = {
        "authentik/build.yaml": build,
        "authentik/config.yaml": manifest,
        "authentik/README.md": readme,
        "authentik/CHANGELOG.md": changelog,
    }
    for name, value in changes.items():
        paths[name].write_text(value, encoding="utf-8")
    return True


def main() -> None:
    current = current_version()
    target = next_release(current, fetch_releases())
    print(f"Current upstream: {current}; next release: {target or 'none'}")
    if target and update_version(ROOT, target):
        print(f"Prepared upgrade PR source changes: {current} -> {target}")
        output = os.environ.get("GITHUB_OUTPUT")
        if output:
            with open(output, "a", encoding="utf-8") as f:
                f.write(f"version={target}\n")


if __name__ == "__main__":
    main()
