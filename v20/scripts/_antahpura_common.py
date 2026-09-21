#!/usr/bin/env python3
"""
Shared helpers for Antahpura V20 event scripts.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
ARCHIVE = ROOT / "archive"
SYSTEMS = ROOT / "systems"
WORLD = ROOT / "world"
CHARACTER = ROOT / "character"


def load(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_or_default(path, default):
    try:
        return load(path)
    except FileNotFoundError:
        return default


def append_event(event):
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    with open(ARCHIVE / "events.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def make_event(event_type, actor, target, payload, **extras):
    base = {
        "event_id": f"evt_{uuid.uuid4().hex[:12]}",
        "timestamp": now_iso(),
        "chapter": payload.get("chapter", 0),
        "scene_id": payload.get("scene_id"),
        "event_type": event_type,
        "actor": actor,
        "target": target,
        "location": payload.get("location"),
        "visibility": payload.get("visibility", 2),
        "audience": payload.get("audience", "private"),
        "consequence_class": payload.get("consequence_class", "personal"),
        "payload": payload,
    }
    base.update(extras)
    return base


def get_character_state(states_root, char_id, default=None):
    states = states_root.setdefault("states", {})
    if char_id not in states:
        states[char_id] = default or {"last_updated": now_iso()}
    return states[char_id]


def apply_relationship_delta(edges_root, from_char, to_char, deltas, memory_tag=None):
    edge_id = f"rel_{from_char}_{to_char}"
    edges = edges_root.setdefault("edges", {})
    if edge_id not in edges:
        edges[edge_id] = {
            "edge_id": edge_id,
            "from": from_char,
            "to": to_char,
            "runtime_deltas": [],
            "current": {},
            "status": "runtime_modified",
        }
    edge = edges[edge_id]
    entry = {"timestamp": now_iso(), "dimension_changes": deltas}
    if memory_tag:
        entry["memory_tag"] = memory_tag
    edge["runtime_deltas"].append(entry)
    for dim, delta in deltas.items():
        edge["current"][dim] = edge["current"].get(dim, 0) + delta
    edge["last_updated"] = now_iso()
    return edge


def load_character_states():
    return load_or_default(RUNTIME / "character_states.json", {"states": {}})


def load_relationship_edges():
    return load_or_default(RUNTIME / "relationship_edges.json", {"edges": {}})


def save_character_states(data):
    save(RUNTIME / "character_states.json", data)


def save_relationship_edges(data):
    save(RUNTIME / "relationship_edges.json", data)


def emit(event):
    append_event(event)
    return event


def cli_run(parser, dispatch_fn, action_choices):
    """
    Common CLI runner. Merges all parsed args into a payload dict, then
    hands off to the dispatch function. Subcommand-specific flags
    (--journal-type, --framework, --word-count, etc.) are automatically
    available to handlers via payload.
    """
    parser.add_argument("action", choices=action_choices)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--target", default=None)
    parser.add_argument("--chapter", type=int, default=0)
    parser.add_argument("--scene-id", default=None)
    parser.add_argument("--visibility", type=int, default=2)
    parser.add_argument("--audience", default="private")
    args = parser.parse_args()

    # Build payload from ALL parsed args. Dashes -> underscores.
    payload = {}
    for k, v in vars(args).items():
        key = k.replace("-", "_")
        payload[key] = v

    # Ensure canonical keys present
    payload.setdefault("chapter", 0)
    payload.setdefault("scene_id", None)
    payload.setdefault("visibility", 2)
    payload.setdefault("audience", "private")

    # Drop keys that already exist at the top level of the emitted event.
    for redundant in ("action", "actor", "target"):
        payload.pop(redundant, None)

    result = dispatch_fn(args, payload)
    print(json.dumps(result, indent=2, ensure_ascii=False))