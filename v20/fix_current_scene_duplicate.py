#!/usr/bin/env python3
"""
fix_current_scene_duplicate.py — resolve the current_scene duplicate.

Actions:
  1. If runtime/current_scene.json has rich content and scenes/current_scene.json
     is a stub, merge the rich content into the canonical file.
  2. Move runtime/current_scene.json to archive/duplicates/.
  3. Update REPO_MANIFEST.json: mark the original as archived, declare the
     archived copy.

Safe to run multiple times.
"""

import json
import shutil
from pathlib import Path

ROOT = Path(".").resolve()
MANIFEST = ROOT / "REPO_MANIFEST.json"
CANONICAL = ROOT / "scenes" / "current_scene.json"
DUPLICATE = ROOT / "runtime" / "current_scene.json"
ARCHIVE = ROOT / "archive" / "duplicates" / "runtime" / "current_scene.json"

RICH_KEYS = {"scene_id", "pov", "participants", "user_message", "event_type"}


def is_rich(data: dict) -> bool:
    return bool(RICH_KEYS & set(data.keys()))


def main():
    if not CANONICAL.exists():
        raise SystemExit(f"Canonical file missing: {CANONICAL}")

    # 1. Merge rich content into canonical, if beneficial
    if DUPLICATE.exists():
        try:
            dup = json.loads(DUPLICATE.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Duplicate unreadable: {e}")
            dup = {}

        try:
            can = json.loads(CANONICAL.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Canonical unreadable: {e}")
            can = {}

        if is_rich(dup) and not is_rich(can):
            merged = dict(can)
            merged.update(dup)
            merged["schema"] = "antahpura.current_scene"
            merged["version"] = "20.0"
            CANONICAL.write_text(
                json.dumps(merged, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"[merge] rich content → {CANONICAL.relative_to(ROOT)}")
        elif is_rich(can):
            print(f"[merge] canonical already rich; not overwriting")
        else:
            print(f"[merge] neither file is rich; leaving canonical as-is")

        # 2. Archive the duplicate
        ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
        if not ARCHIVE.exists():
            shutil.move(str(DUPLICATE), str(ARCHIVE))
            print(f"[archive] {DUPLICATE.relative_to(ROOT)} → {ARCHIVE.relative_to(ROOT)}")
        else:
            DUPLICATE.unlink()
            print(f"[archive] archive exists; removed {DUPLICATE.relative_to(ROOT)}")
    else:
        print("[archive] duplicate already absent")

    # 3. Update manifest
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for f in manifest.get("files", []):
        if f["path"] == "runtime/current_scene.json":
            f["role"] = "archive"
            f["note"] = (
                "Duplicate of scenes/current_scene.json. "
                "Moved to archive/duplicates/runtime/."
            )

    paths = {f["path"] for f in manifest["files"]}
    arc_rel = "archive/duplicates/runtime/current_scene.json"
    if arc_rel not in paths:
        manifest["files"].append({
            "path": arc_rel,
            "role": "archive",
            "domain": "archive",
            "schema": "antahpura.current_scene",
            "version": "20.0",
            "depends_on": [],
            "referenced_by": [],
            "reference_types": [],
            "note": "Archived duplicate of scenes/current_scene.json.",
        })

    manifest["files"].sort(key=lambda f: f["path"])
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[manifest] updated ({len(manifest['files'])} entries)")


if __name__ == "__main__":
    main()