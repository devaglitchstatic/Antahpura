#!/usr/bin/env python3
"""
fix_kama_typos.py — fix known kama ID typos.

- INDRIVA_NIRODHA → INDRIYA_NIRODHA (typo)

Also reports every occurrence of MAITHUNA so the user can decide whether to
add it to MASTER_KINK_REGISTRY.json.

Dry-run by default. Pass --apply to write changes.
"""

import argparse
import json
from pathlib import Path

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__",
             ".venv", "venv", ".mypy_cache", ".pytest_cache"}

REPLACEMENTS = {
    "INDRIVA_NIRODHA": "INDRIYA_NIRODHA",
}

REPORT_ONLY = {"MAITHUNA"}


def walk_json(root: Path):
    import os
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.lower().endswith(".json"):
                yield Path(dirpath) / fn


def fix_object(node):
    changed = False
    if isinstance(node, dict):
        new = {}
        for k, v in node.items():
            new_v, v_changed = fix_object(v)
            new[k] = new_v
            changed = changed or v_changed
        return new, changed
    elif isinstance(node, list):
        return [fix_object(i)[0] for i in node], any(fix_object(i)[1] for i in node)
    elif isinstance(node, str):
        if node in REPLACEMENTS:
            return REPLACEMENTS[node], True
        return node, False
    return node, False


def report_only_hits(node, path="$"):
    hits = []
    if isinstance(node, dict):
        for k, v in node.items():
            hits.extend(report_only_hits(v, f"{path}.{k}"))
    elif isinstance(node, list):
        for i, item in enumerate(node):
            hits.extend(report_only_hits(item, f"{path}[{i}]"))
    elif isinstance(node, str):
        if node in REPORT_ONLY:
            hits.append((node, path))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    files = sorted(walk_json(root))

    total_changed = 0
    report_hits = []

    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        # report-only scanning
        for value, at in report_only_hits(data):
            report_hits.append((str(path.relative_to(root)), value, at))

        new_data, changed = fix_object(data)
        if not changed:
            continue

        rel = path.relative_to(root)
        total_changed += 1
        print(f"[{'APPLY' if args.apply else 'DRY'}] {rel}")

        if args.apply:
            path.write_text(
                json.dumps(new_data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    print()
    print(f"Files changed (typo fixes): {total_changed}")
    if not args.apply:
        print("Dry run only. Re-run with --apply to write.")

    if report_hits:
        print()
        print(f"Report-only hits for {sorted(REPORT_ONLY)}:")
        for rel, value, at in report_hits:
            print(f"  {rel} :: {at} = {value}")


if __name__ == "__main__":
    main()