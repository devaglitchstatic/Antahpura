#!/usr/bin/env python3
"""
extract_canon.py - Produce canon/kalas.json and canon/locations.json
from the composite source files. Reformats into canonical shape.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "canon"


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save(p, data):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"WROTE: {p.relative_to(ROOT)}  ({p.stat().st_size} bytes)")


# ---- kalas.json ----
src = ROOT / "canon" / "kala_system_v20.json"
if src.exists():
    data = load(src)
    out = {
        "schema": "antahpura.canon.kalas",
        "version": "20.1",
        "source": "extracted from canon/kala_system_v20.json",
        "total_kalas": len(data.get("kalas", {})),
        "total_domains": len(data.get("domains", {})),
        "domains": data.get("domains", {}),
        "mastery_ladder": data.get("mastery_ladder", {}),
        "kala_synergies": data.get("kala_synergies", []),
        "kalas": data.get("kalas", {})
    }
    save(CANON / "kalas.json", out)
else:
    print(f"MISSING: {src}")


# ---- locations.json ----
candidates = [
    ROOT / "location" / "location_system_v20.json",
    ROOT / "location" / "Location System V20 - Complete Registry.json",
    ROOT / "registries" / "location_system_v20.json",
]
src = next((p for p in candidates if p.exists()), None)
if src:
    data = load(src)
    out = {
        "schema": "antahpura.canon.locations",
        "version": "20.1",
        "source": f"extracted from {src.relative_to(ROOT)}",
        "institutions": data.get("institutions", {}),
        "zones": data.get("zones", {}),
        "locations": data.get("locations", {}),
        "occasion_location_map": data.get("occasion_location_map", {})
    }
    save(CANON / "locations.json", out)
else:
    print("MISSING: no location_system_v20.json found in location/ or registries/")