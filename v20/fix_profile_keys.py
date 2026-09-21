#!/usr/bin/env python3
"""
fix_profile_keys.py — rename abbreviated character keys inside
characters/character_profiles_v20.json to their canonical forms.

Only touches the top-level profile dict keys. Values are not modified.
Dry-run by default.
"""

import argparse
import json
from pathlib import Path

TARGET = Path("characters/character_profiles_v20.json")

# Key renames
KEY_RENAMES = {
    "char_maha":     "char_maha_deva",
    "char_princess": "char_kumari_rati",
    "char_sentinel": "char_altani",
    # Also handle bare forms if they appear as keys
    "maha":          "char_maha_deva",
    "princess":      "char_kumari_rati",
    "sentinel":      "char_altani",
}


def rename_keys(obj):
    """Rename dict keys at every level using KEY_RENAMES. Returns (new_obj, changes)."""
    changes = []
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            new_k = KEY_RENAMES.get(k, k) if isinstance(k, str) else k
            if new_k != k:
                changes.append((k, new_k))
            new_v, v_changes = rename_keys(v)
            new[new_k] = new_v
            changes.extend(v_changes)
        return new, changes
    if isinstance(obj, list):
        new_list = []
        for item in obj:
            new_item, i_changes = rename_keys(item)
            new_list.append(new_item)
            changes.extend(i_changes)
        return new_list, changes
    return obj, changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if not TARGET.exists():
        raise SystemExit(f"Not found: {TARGET}")

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    new_data, changes = rename_keys(data)

    if not changes:
        print("No key renames needed.")
        return

    print(f"Renames to perform in {TARGET}:")
    for old, new in changes:
        print(f"  {old}  ->  {new}")

    if args.apply:
        TARGET.write_text(
            json.dumps(new_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n[APPLIED] {TARGET}")
    else:
        print("\nDry run only. Re-run with --apply to write.")


if __name__ == "__main__":
    main()