#!/usr/bin/env python3
"""
fix_kama_state_keys.py — rename legacy keys in KAMA_CHARACTER_STATE.json
to canonical registry slugs.

Renames:
  kuma_ree       -> kumari_rati
  champa         -> campa
  zola           -> (removed; no canonical match)
  kamini_anisa   -> anisa

Dry-run by default. Pass --apply to write.
"""

import argparse
import json
from pathlib import Path

ROOT = Path(".").resolve()
STATE_FILE = ROOT / "characters" / "KAMA_CHARACTER_STATE.json"

KEY_RENAMES = {
    "kuma_ree":     "kumari_rati",
    "champa":       "campa",
    "kamini_anisa": "anisa",
    "kamini_reva":  "reva",
    "kamini_tarana": "tarana",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if not STATE_FILE.exists():
        raise SystemExit(f"Missing: {STATE_FILE}")

    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise SystemExit("Top-level is not a dict")

    # Some state files wrap under "characters"
    container_key = None
    for k in ("characters", "states", "character_states"):
        if isinstance(data.get(k), dict):
            container_key = k
            break

    block = data[container_key] if container_key else data

    renames = []
    for old, new in KEY_RENAMES.items():
        if old in block:
            if new in block:
                print(f"[skip] both {old!r} and {new!r} present — manual merge needed")
                continue
            renames.append((old, new))

    if not renames:
        print("No legacy keys found. State file already canonical.")
        return

    print("Renames to perform:")
    for old, new in renames:
        print(f"  {old}  ->  {new}")

    if not args.apply:
        print()
        print("Dry run only. Re-run with --apply to write.")
        return

    for old, new in renames:
        block[new] = block.pop(old)
        print(f"[renamed] {old} -> {new}")

    STATE_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print()
    print(f"[written] {STATE_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()