#!/usr/bin/env python3
"""
verify_cards.py — verify that every character has a Chub card file
at characters/main_<chub_card_id>_spec_v2.json.

Reads the character registry, checks each entry.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC_DIR = ROOT / "characters"
REGISTRY = SPEC_DIR / "V17_1_CHARACTER_REGISTRY.json"

if not REGISTRY.exists():
    print(f"ERROR: registry not found: {REGISTRY}")
    sys.exit(2)

reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
characters = reg.get("characters", [])

print("=" * 60)
print("CHARACTER CARD VERIFICATION")
print("=" * 60)
print(f"Registry:  {REGISTRY.relative_to(ROOT)}")
print(f"Cards dir: {SPEC_DIR.relative_to(ROOT)}")
print(f"Entries:   {len(characters)}")
print("-" * 60)

missing = 0
present = 0
for c in characters:
    cid = c.get("id")
    chub = c.get("chub_card_id")
    display = c.get("display_name", cid)
    if not chub:
        print(f"  MISSING  {cid:14s}  no chub_card_id")
        missing += 1
        continue
    expected = SPEC_DIR / f"main_{chub}_spec_v2.json"
    if expected.exists():
        print(f"  OK       {cid:14s}  {expected.name}")
        present += 1
    else:
        print(f"  MISSING  {cid:14s}  expected {expected.name}")
        missing += 1

print("-" * 60)
print(f"Present: {present}  Missing: {missing}")
print("=" * 60)

if missing:
    sys.exit(1)
sys.exit(0)