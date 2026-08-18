#!/usr/bin/env python3
"""
V18 Relationship Memory Engine

Maintains persistent trust, fear, devotion, rivalry, and authority memory
between canonical characters.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STATE = ROOT / "registry" / "V18_RUNTIME_STATE.json"


def load():
    return json.loads(STATE.read_text(encoding="utf-8"))


def save(data):
    STATE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def ensure_relationship(data, a, b):
    key = f"{a}->{b}"

    if key in data["relationship_memory"]:
        return key

    # Constitutional baseline: Mahā Deva ↔ Kumārī Rati
    if (a, b) == ("maha_deva", "kumari_rati"):
        data["relationship_memory"][key] = {
            "bond": "newly_wedded_sacred_union",
            "marital_status": "newly_wedded",
            "ritual_status": "consummation_pending",
            "trust": 0.88,
            "devotion": 0.82,
            "authority": 0.78,
            "intimacy": 0.64,
            "protectiveness": 0.92,
            "dynastic_obligation": 1.00,
            "history": ["marriage_consecrated", "queen_installed"]
        }
        return key

    if (a, b) == ("kumari_rati", "maha_deva"):
        data["relationship_memory"][key] = {
            "bond": "newly_wedded_sacred_union",
            "marital_status": "newly_wedded",
            "ritual_status": "consummation_pending",
            "trust": 0.86,
            "devotion": 0.89,
            "authority": 0.72,
            "intimacy": 0.61,
            "reverence": 0.84,
            "dynastic_obligation": 1.00,
            "history": ["marriage_consecrated", "queen_installed"]
        }
        return key

    # Generic default
    data["relationship_memory"][key] = {
        "trust": 0.50,
        "fear": 0.00,
        "devotion": 0.00,
        "rivalry": 0.00,
        "authority": 0.50,
        "history": []
    }

    return key


def apply_event(data, actor, target, event):

    key = ensure_relationship(data, actor, target)
    rel = data["relationship_memory"][key]

    if event == "protect":
        rel["trust"] = min(1.0, rel["trust"] + 0.10)
        rel["devotion"] = min(1.0, rel["devotion"] + 0.05)

    elif event == "betray":
        rel["trust"] = max(0.0, rel["trust"] - 0.25)
        rel["rivalry"] = min(1.0, rel["rivalry"] + 0.20)

    elif event == "ritual":
        rel["devotion"] = min(1.0, rel["devotion"] + 0.10)

    elif event == "command":
        rel["authority"] = min(1.0, rel["authority"] + 0.10)

    rel["history"].append(event)

    return rel


def main():

    data = load()

    apply_event(
        data,
        "maha_deva",
        "kumari_rati",
        "protect"
    )

    save(data)

    print("Relationship memory updated.")


if __name__ == "__main__":
    main()