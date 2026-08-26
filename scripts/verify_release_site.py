#!/usr/bin/env python3
"""Verify a PTO specification release site without rebuilding its sources."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--redirects", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--publication-version", required=True)
    parser.add_argument("--tree", required=True)
    arguments = parser.parse_args()

    manifest = json.loads(arguments.manifest.read_text(encoding="utf-8"))
    expected = {
        "schema": "pto.site-publication.v1",
        "source_commit": arguments.commit,
        "tag": arguments.tag,
        "publication_version": arguments.publication_version,
        "publication_state": "release",
        "release_eligible": True,
        "site_tree_sha256": arguments.tree,
    }
    for field, value in expected.items():
        require(manifest.get(field) == value, f"manifest {field} is not {value!r}")

    embedded = arguments.site / "pto-site-publication.json"
    require(embedded.is_file(), "site is missing pto-site-publication.json")
    require(embedded.read_bytes() == arguments.manifest.read_bytes(), "embedded manifest differs")
    require((arguments.site / ".nojekyll").read_bytes() == b"\n", "root .nojekyll differs")
    require(
        (arguments.site / "zh-CN/.nojekyll").read_bytes() == b"\n",
        "zh-CN .nojekyll differs",
    )
    require(sha256(arguments.redirects) == manifest["redirect_manifest_sha256"], "redirect digest differs")
    require(sha256(arguments.lock) == manifest["dependency_lock_sha256"], "lock digest differs")

    files = sorted(
        path
        for path in arguments.site.rglob("*")
        if path.is_file() and path != embedded
    )
    tree = hashlib.sha256()
    for path in files:
        relative = path.relative_to(arguments.site).as_posix()
        tree.update(relative.encode("utf-8"))
        tree.update(b"\0")
        tree.update(bytes.fromhex(sha256(path)))
        tree.update(b"\n")

    require(len(files) == manifest["file_count"], "site file count differs")
    require(sum(path.stat().st_size for path in files) == manifest["content_bytes"], "site byte count differs")
    require(tree.hexdigest() == manifest["site_tree_sha256"], "site tree digest differs")
    print(
        f"verified PTO site {manifest['publication_version']} at {manifest['source_commit']}: "
        f"{len(files)} files, {tree.hexdigest()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
