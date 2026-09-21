#!/usr/bin/env python3
"""Remove manifest entries whose files no longer exist on disk."""
import json
from pathlib import Path

root = Path(".").resolve()
mf = root / "REPO_MANIFEST.json"
manifest = json.loads(mf.read_text(encoding="utf-8"))

kept, removed = [], []
for f in manifest["files"]:
    p = f["path"]
    if not (root / p).exists():
        removed.append(p)
        continue
    kept.append(f)

by_path = {f["path"]: f for f in kept}
manifest["files"] = sorted(by_path.values(), key=lambda f: f["path"])
mf.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"Removed {len(removed)} stale entries:")
for r in removed:
    print(f"  {r}")
print(f"Manifest now: {len(manifest['files'])} entries.")