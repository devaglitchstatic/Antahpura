#!/usr/bin/env python3
"""
v18_runtime_engine.py

Antahpura V18 Runtime Consciousness Engine
-----------------------------------------

Connects the canonical V17.1.1 ontology with the persistent V18 runtime state.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ONTOLOGY = ROOT / "antahpura_runtime_ontology_v17_1.json"
STATE = ROOT / "registry" / "V18_RUNTIME_STATE.json"
SNAPSHOT = ROOT / "registry" / "V18_RUNTIME_SNAPSHOT.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def validate(state, ontology):
    characters = ontology["characters"]

    for cid in state["characters"]:
        if cid not in characters:
            raise ValueError(f"Runtime character not found in ontology: {cid}")

    return True


def synchronize(state, ontology):

    faction_count = 0

    if "factions" in ontology:
        faction_count = len(ontology["factions"])
    elif "graph" in ontology and "factions" in ontology["graph"]:
        faction_count = len(ontology["graph"]["factions"])

    state["runtime"] = {
        "ontology_version": ontology.get("version", "unknown"),
        "character_count": len(ontology.get("characters", {})),
        "faction_count": faction_count,
    }

    return state


def snapshot(state):
    return {
        "scene": state["scene"],
        "court": state["court"],
        "characters": state["characters"],
        "runtime": state["runtime"],
    }


def main():

    ontology = load_json(ONTOLOGY)
    state = load_json(STATE)

    validate(state, ontology)

    state = synchronize(state, ontology)

    save_json(STATE, state)
    save_json(SNAPSHOT, snapshot(state))

    print("V18 runtime synchronized.")
    print(f"Snapshot written to: {SNAPSHOT}")


if __name__ == "__main__":
    main()