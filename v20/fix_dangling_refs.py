#!/usr/bin/env python3
"""
fix_dangling_refs.py — replace known dangling references with canonical forms.

Safety rules:
  - Never touch archive/ or audit/validation_results.json
  - Prefixed forms (char_maha) are replaced everywhere
  - Bare forms (maha) are replaced only when the enclosing key is a
    reference key like 'from', 'to', 'actor', etc.

Dry-run by default. Pass --apply to write.
"""

import argparse
import json
import os
from pathlib import Path

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__",
             ".venv", "venv", ".mypy_cache", ".pytest_cache", "archive"}
SKIP_FILES = {"REPO_MANIFEST.json", "audit/validation_results.json"}

# --- Replacement tables -----------------------------------------------------

KAMA_REPLACEMENTS = {
    "INDRIVA_NIRODHA": "INDRIYA_NIRODHA",
}

CHAR_PREFIXED_REPLACEMENTS = {
    "char_maha":     "char_maha_deva",
    "char_princess": "char_kumari_rati",
    "char_sentinel": "char_altani",
}

BARE_CHAR_REPLACEMENTS = {
    "maha":     "maha_deva",
    "princess": "kumari_rati",
    "sentinel": "altani",
}

# Bare replacements only happen when the enclosing key is one of these
REFERENCE_KEYS = {
    "from", "to", "actor", "target", "source", "destination",
    "subject", "owner", "holder", "character", "characters",
    "char", "chars", "referenced_by", "depends_on", "dependents",
    "participants", "members", "candidates", "affected", "involved",
}


def walk_json(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.lower().endswith(".json"):
                continue
            full = Path(dirpath) / fn
            rel = str(full.relative_to(root)).replace("\\", "/")
            if rel in SKIP_FILES:
                continue
            yield full


def replace_value(value: str, parent_key: str | None) -> str:
    # Kama typos always apply
    if value in KAMA_REPLACEMENTS:
        return KAMA_REPLACEMENTS[value]

    # Prefixed character forms always apply
    if value in CHAR_PREFIXED_REPLACEMENTS:
        return CHAR_PREFIXED_REPLACEMENTS[value]

    # Bare forms only inside reference keys
    if parent_key and parent_key.lower() in REFERENCE_KEYS:
        if value in BARE_CHAR_REPLACEMENTS:
            return BARE_CHAR_REPLACEMENTS[value]

    return value


def fix_node(node, parent_key=None):
    changed = False

    if isinstance(node, dict):
        new = {}
        for k, v in node.items():
            # Keys themselves are not replaced — only values
            new_v, v_changed = fix_node(v, parent_key=k if isinstance(k, str) else None)
            new[k] = new_v
            changed = changed or v_changed
        return new, changed

    if isinstance(node, list):
        new_list = []
        for item in node:
            new_item, i_changed = fix_node(item, parent_key=parent_key)
            new_list.append(new_item)
            changed = changed or i_changed
        return new_list, changed

    if isinstance(node, str):
        new_s = replace_value(node, parent_key)
        return new_s, new_s != node

    return node, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()

    total = 0
    for path in sorted(walk_json(root)):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        new_data, changed = fix_node(data)
        if not changed:
            continue
        rel = path.relative_to(root)
        print(f"[{'APPLY' if args.apply else 'DRY'}] {rel}")
        if args.apply:
            path.write_text(
                json.dumps(new_data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        total += 1

    print()
    print(f"Files {'patched' if args.apply else 'to patch'}: {total}")
    if not args.apply:
        print("Dry run only. Re-run with --apply to write.")


if __name__ == "__main__":
    main()