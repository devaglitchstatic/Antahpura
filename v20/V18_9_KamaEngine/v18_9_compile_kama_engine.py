#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Antahpura V18.9 – Kama Engine with Full Classification & Relational Graph
=======================================================================
Version: 18.9
Schema: 3.2-rc1
"""

import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum
from datetime import datetime

# ----------------------------------------------------------------------
# Enums
# ----------------------------------------------------------------------
class Preference(Enum):
    FAVORITE = "favorite"
    LIKE = "like"
    MAYBE = "maybe"
    NEUTRAL = "neutral"
    NO = "no"

class Consent(Enum):
    GREEN = "green"
    ORANGE = "orange"
    RED = "red"

class KinkState:
    __slots__ = ("knowledge", "training", "repetition", "mastery", "preference", "limits", "consent", "locked")
    def __init__(self, knowledge=0.0, training=0.0, repetition=0, mastery=0.0,
                 preference=Preference.NEUTRAL, limits=None, consent=Consent.ORANGE, locked=True):
        self.knowledge = knowledge
        self.training = training
        self.repetition = repetition
        self.mastery = mastery
        self.preference = preference
        self.limits = limits if limits else {"soft": [], "hard": []}
        self.consent = consent
        self.locked = locked

    def to_dict(self):
        return {
            "knowledge": self.knowledge,
            "training": self.training,
            "repetition": self.repetition,
            "mastery": self.mastery,
            "preference": self.preference.value,
            "limits": self.limits,
            "consent": self.consent.value,
            "locked": self.locked
        }

# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------
@dataclass
class KinkDefinition:
    id: str
    name: str
    taxonomy: Dict[str, List[str]]   # {"primary": [], "related": [], "similar": [], "secondary": []}
    progression: Dict[str, bool]     # {"knowledge": True, "training": True, ...}

@dataclass
class CharacterKamaState:
    character_id: str
    kinks: Dict[str, KinkState]   # kink_id -> KinkState

@dataclass
class KinkRelationGraph:
    similar: Dict[str, List[str]]  # kink_id -> list of similar kink IDs
    related: Dict[str, List[str]]
    secondary: Dict[str, List[str]]

class KamaEngine:
    def __init__(self, registry: Dict[str, KinkDefinition], graph: KinkRelationGraph, initial_states: Dict[str, CharacterKamaState]):
        self.registry = registry
        self.graph = graph
        self.states = initial_states
        self.event_log = []
        self.hash = self._compute_hash()

    def apply_event(self, character_id: str, event: Dict) -> Dict:
        """Process an event that modifies kink state."""
        kink_id = event.get("kink_id")
        if not kink_id or kink_id not in self.registry:
            return {"error": f"Unknown kink: {kink_id}"}

        char_state = self.states.get(character_id)
        if not char_state:
            return {"error": f"Unknown character: {character_id}"}

        kink_state = char_state.kinks.get(kink_id)
        if not kink_state:
            return {"error": f"Character {character_id} does not have kink {kink_id}"}

        # Apply deltas
        delta_knowledge = event.get("knowledge_delta", 0.0)
        delta_training = event.get("training_delta", 0.0)
        delta_repetition = event.get("repetition_delta", 0)
        delta_mastery = event.get("mastery_delta", 0.0)

        # Enforce lock
        if kink_state.locked and (delta_training > 0 or delta_repetition > 0 or delta_mastery > 0):
            return {"error": f"Kink {kink_id} is locked for {character_id}; cannot progress."}

        # Update
        kink_state.knowledge = min(1.0, max(0.0, kink_state.knowledge + delta_knowledge))
        kink_state.training = min(1.0, max(0.0, kink_state.training + delta_training))
        kink_state.repetition += delta_repetition
        kink_state.mastery = min(1.0, max(0.0, kink_state.mastery + delta_mastery))

        # Preference/consent changes can be explicitly set
        if "preference" in event:
            try:
                kink_state.preference = Preference(event["preference"])
            except ValueError:
                pass
        if "consent" in event:
            try:
                kink_state.consent = Consent(event["consent"])
            except ValueError:
                pass
        if "locked" in event:
            kink_state.locked = event["locked"]

        # Propagate knowledge to similar kinks (optional)
        if delta_knowledge > 0 and kink_id in self.graph.similar:
            for sim_id in self.graph.similar[kink_id]:
                if sim_id in char_state.kinks:
                    sim_state = char_state.kinks[sim_id]
                    sim_state.knowledge = min(1.0, sim_state.knowledge + delta_knowledge * 0.1)

        # Log event
        self.event_log.append({
            "timestamp": datetime.now().isoformat(),
            "character": character_id,
            "kink": kink_id,
            "event": event,
            "new_state": kink_state.to_dict()
        })

        self.hash = self._compute_hash()
        return {
            "character": character_id,
            "kink": kink_id,
            "new_state": kink_state.to_dict(),
            "hash": self.hash
        }

    def _compute_hash(self) -> str:
        # Deterministic hash of all states
        data = {}
        for cid, cstate in self.states.items():
            data[cid] = {k: v.to_dict() for k, v in cstate.kinks.items()}
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

# ----------------------------------------------------------------------
# Helper to build initial states from classification matrix
# ----------------------------------------------------------------------
def build_initial_states(classification_matrix: Dict[str, Dict]) -> Dict[str, CharacterKamaState]:
    """
    classification_matrix: {
        character_id: {
            "primary": [kink_ids],
            "secondary": [kink_ids],
            "similar": [kink_ids],
            "extreme": [kink_ids],
            "locked_extreme": [kink_ids]  # if locked status differs
        }
    }
    """
    states = {}
    for cid, kink_groups in classification_matrix.items():
        kinks = {}
        # Primary: unlocked, knowledge 0.5, training 0.2, repetition 10
        for kid in kink_groups.get("primary", []):
            kinks[kid] = KinkState(knowledge=0.5, training=0.2, repetition=10, mastery=0.1,
                                   preference=Preference.LIKE, consent=Consent.GREEN, locked=False)
        # Secondary: unlocked, knowledge 0.3, training 0.1, repetition 5
        for kid in kink_groups.get("secondary", []):
            kinks[kid] = KinkState(knowledge=0.3, training=0.1, repetition=5, mastery=0.05,
                                   preference=Preference.MAYBE, consent=Consent.ORANGE, locked=False)
        # Similar: unlocked, knowledge 0.1, training 0, repetition 0
        for kid in kink_groups.get("similar", []):
            kinks[kid] = KinkState(knowledge=0.1, training=0, repetition=0, mastery=0,
                                   preference=Preference.MAYBE, consent=Consent.ORANGE, locked=False)
        # Extreme: locked, knowledge 0, training 0, repetition 0
        for kid in kink_groups.get("extreme", []):
            kinks[kid] = KinkState(knowledge=0, training=0, repetition=0, mastery=0,
                                   preference=Preference.NO, consent=Consent.RED, locked=True)
        states[cid] = CharacterKamaState(character_id=cid, kinks=kinks)
    return states

# ----------------------------------------------------------------------
# Main execution – Load from JSON files and run test
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import json

    # 1. Load Master Kink Registry
    with open("MASTER_KINK_REGISTRY.json", "r", encoding="utf-8") as f:
        registry_data = json.load(f)
    registry = {}
    for kid, data in registry_data["KINKS"].items():
        registry[kid] = KinkDefinition(
            id=data["id"],
            name=data["name"],
            taxonomy=data["taxonomy"],
            progression=data["progression"]
        )

    # 2. Load Kink Relation Graph
    with open("KINK_RELATION_GRAPH.json", "r", encoding="utf-8") as f:
        graph_data = json.load(f)
    graph = KinkRelationGraph(
        similar=graph_data.get("similar", {}),
        related=graph_data.get("related", {}),
        secondary=graph_data.get("secondary", {})
    )

    # 3. Load character states from KAMA_CHARACTER_STATE.json
    with open("KAMA_CHARACTER_STATE.json", "r", encoding="utf-8") as f:
        state_dict = json.load(f)
    states = {}
    for cid, kinks in state_dict.items():
        kink_states = {}
        for kid, state in kinks["kinks"].items():
            pref = Preference(state["preference"])
            cons = Consent(state["consent"])
            ks = KinkState(
                knowledge=state["knowledge"],
                training=state["training"],
                repetition=state["repetition"],
                mastery=state["mastery"],
                preference=pref,
                limits=state["limits"],
                consent=cons,
                locked=state["locked"]
            )
            kink_states[kid] = ks
        states[cid] = CharacterKamaState(character_id=cid, kinks=kink_states)

    # 4. Create engine
    engine = KamaEngine(registry, graph, states)

    # 5. Test event: Roxana assigns a journaling task
    event = {
        "kink_id": "NIBANDHA_PRACODANA",
        "knowledge_delta": 0.2,
        "training_delta": 0.1,
        "repetition_delta": 1,
        "preference": "like",
        "consent": "green",
        "locked": False
    }
    result = engine.apply_event("roxana", event)
    print(json.dumps(result, indent=2))

    # 6. Save updated state to a new file
    with open("KAMA_CHARACTER_STATE_UPDATED.json", "w", encoding="utf-8") as f:
        output = {}
        for cid, cstate in engine.states.items():
            output[cid] = {"kinks": {kid: ks.to_dict() for kid, ks in cstate.kinks.items()}}
        json.dump(output, f, indent=2)

    print("Engine initialized, all states ready.")