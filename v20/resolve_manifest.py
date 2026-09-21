#!/usr/bin/env python3
"""
resolve_manifest.py — reconcile REPO_MANIFEST.json with disk state.

Actions:
  1. Remove manifest entries whose files do not exist on disk
  2. Add entries for files on disk that are not declared
  3. Report the changes

Safe to run multiple times. Idempotent.
"""

import json
from pathlib import Path

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__",
             ".venv", "venv", ".mypy_cache", ".pytest_cache", "archive"}

ROOT = Path(".").resolve()
MANIFEST = ROOT / "REPO_MANIFEST.json"


def walk_json(root: Path):
    import os
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.lower().endswith(".json"):
                yield Path(dirpath) / fn


def infer_role(path_str: str) -> str:
    if "/runtime/" in path_str or path_str.endswith("current_scene.json"):
        return "runtime_state"
    if path_str.startswith("audit/"):
        return "canonical"
    if path_str.startswith("archive/"):
        return "archive"
    return "stub"


def infer_domain(path_str: str) -> str:
    parts = path_str.split("/")
    return parts[0] if len(parts) > 1 else "root"


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # 1. Remove stale entries
    kept, removed = [], []
    for f in manifest.get("files", []):
        p = f["path"]
        if (ROOT / p).exists():
            kept.append(f)
        else:
            removed.append(p)

    # 2. Add undeclared files
    declared = {f["path"] for f in kept}
    added = []
    for path in sorted(walk_json(ROOT)):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if rel in declared or rel == "REPO_MANIFEST.json":
            continue
        kept.append({
            "path": rel,
            "role": infer_role(rel),
            "domain": infer_domain(rel),
            "schema": None,
            "version": None,
            "depends_on": [],
            "referenced_by": [],
            "reference_types": [],
            "note": "Auto-declared by resolve_manifest.py."
        })
        added.append(rel)

    kept.sort(key=lambda f: f["path"])
    manifest["files"] = kept
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                        encoding="utf-8")

    print("=" * 60)
    print("MANIFEST RECONCILIATION")
    print("=" * 60)
    print(f"Removed stale entries: {len(removed)}")
    for r in removed:
        print(f"  - {r}")
    print(f"Added undeclared files: {len(added)}")
    for a in added:
        print(f"  + {a}")
    print(f"Total manifest entries: {len(kept)}")


if __name__ == "__main__":
    main()