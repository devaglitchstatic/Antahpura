#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

VERSION = "18.7"
EVENT_TYPES = {
    "training_started", "training_progressed", "training_completed",
    "knowledge_acquired", "kala_training", "relationship_update",
    "status_set", "status_clear", "flag_set", "flag_clear",
}
IMMUTABLE = ("canonical_id", "canonical_name", "constitutional_office", "constitutional_authority")

class V187IntegrityError(RuntimeError):
    pass

def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()

def load_json(path: Path) -> Any:
    if not path.exists():
        raise V187IntegrityError(f"Required file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise V187IntegrityError(f"Invalid JSON: {path}: {exc}") from exc

def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

def find_first(repo: Path, candidates: Iterable[str]) -> Optional[Path]:
    for rel in candidates:
        p = repo / rel
        if p.exists():
            return p
    return None

def locate_inputs(repo: Path) -> Dict[str, Optional[Path]]:
    return {
        "canonical": find_first(repo, (
            "registry/V18_RUNTIME/V18_2_CANONICAL_BASELINE.json",
            "registry/V18_4_RUNTIME/V18_4_CANONICAL_INTEGRITY.json",
        )),
        "state": find_first(repo, ("registry/V18_6_RUNTIME/V18_6_RUNTIME_STATE.json",)),
        "chain": find_first(repo, ("registry/V18_6_RUNTIME/V18_6_REPLAY_CHAIN.json",)),
    }

def char_map(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    chars = data.get("characters")
    if isinstance(chars, dict):
        return chars
    if isinstance(chars, list):
        result = {}
        for char in chars:
            if isinstance(char, dict):
                cid = char.get("canonical_id") or char.get("id")
                if cid:
                    result[str(cid)] = char
        return result
    return {}

def normalize_canonical(raw: Dict[str, Any]) -> Dict[str, Any]:
    chars = char_map(raw)
    if not chars:
        raise V187IntegrityError("Canonical baseline contains no characters.")
    normalized = {
        cid: {k: copy.deepcopy(char.get(k)) for k in IMMUTABLE if k in char}
        for cid, char in sorted(chars.items())
    }
    rels = raw.get("relationships", [])
    sovereign = raw.get("sovereign_axis")
    if isinstance(rels, dict):
        sovereign = sovereign if sovereign is not None else rels.get("sovereign_axis")
        rels = rels.get("relationships", [])
    if not isinstance(rels, list):
        rels = []
    relationships = []
    for rel in rels:
        if isinstance(rel, dict):
            relationships.append({k: copy.deepcopy(rel.get(k)) for k in ("from", "to", "relation") if k in rel})
    relationships.sort(key=canonical_json)
    return {
        "schema": "V18_4_CANONICAL_CONSTITUTION",
        "characters": normalized,
        "relationships": relationships,
        "sovereign_axis": copy.deepcopy(sovereign),
    }

def relationship_set(state: Dict[str, Any]) -> set[Tuple[Any, Any, Any]]:
    return {(r.get("from"), r.get("to"), r.get("relation")) for r in state.get("relationships", []) if isinstance(r, dict)}

def initial_state(canonical: Dict[str, Any], saved: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    state = {
        "schema": "V18_7_RUNTIME_STATE",
        "version": VERSION,
        "canonical_hash": sha256_json(canonical),
        "characters": copy.deepcopy(canonical["characters"]),
        "relationships": copy.deepcopy(canonical["relationships"]),
        "sovereign_axis": copy.deepcopy(canonical["sovereign_axis"]),
        "runtime": {"skills": {}, "knowledge": {}, "kalas": {}, "training": {}, "statuses": {}, "flags": {}, "relationship_state": {}},
    }
    if isinstance(saved, dict) and isinstance(saved.get("runtime"), dict):
        for key in state["runtime"]:
            if isinstance(saved["runtime"].get(key), dict):
                state["runtime"][key] = copy.deepcopy(saved["runtime"][key])
    return state

def extract_events(raw: Any) -> List[Dict[str, Any]]:
    if isinstance(raw, list):
        return copy.deepcopy(raw)
    if isinstance(raw, dict):
        for key in ("events", "event_log", "log"):
            if isinstance(raw.get(key), list):
                return copy.deepcopy(raw[key])
    raise V187IntegrityError("Event source must be a list or contain an events list.")

def validate_event(event: Dict[str, Any], index: int, seen: set[str]) -> None:
    if not isinstance(event, dict):
        raise V187IntegrityError(f"Event {index} is not an object.")
    eid = event.get("event_id")
    if not isinstance(eid, str) or not eid.strip():
        raise V187IntegrityError(f"Event {index} has no event_id.")
    if eid in seen:
        raise V187IntegrityError(f"Duplicate event_id: {eid}")
    etype = event.get("event_type", event.get("type"))
    if etype not in EVENT_TYPES:
        raise V187IntegrityError(f"Unsupported event type: {etype!r}")
    seq = event.get("sequence")
    if seq is not None and (not isinstance(seq, int) or seq < 1):
        raise V187IntegrityError(f"Invalid sequence: {seq!r}")
    seen.add(eid)

def ensure_char(state: Dict[str, Any], cid: Optional[str]) -> None:
    if cid is not None and cid not in state["characters"]:
        raise V187IntegrityError(f"Unknown character: {cid}")

def domain(state: Dict[str, Any], name: str, cid: str) -> Dict[str, Any]:
    d = state["runtime"][name]
    d.setdefault(cid, {})
    if not isinstance(d[cid], dict):
        d[cid] = {}
    return d[cid]

def apply_event(state: Dict[str, Any], event: Dict[str, Any]) -> Dict[str, Any]:
    new = copy.deepcopy(state)
    etype = event.get("event_type", event.get("type"))
    cid = event.get("character_id") or event.get("character")
    ensure_char(new, cid)
    forbidden = ("constitutional_office", "office", "authority", "canonical_name", "provenance", "canonical_id", "sovereign_axis")
    if any(k in event for k in forbidden):
        raise V187IntegrityError("Canonical/provenance/sovereign mutation attempted.")

    if etype == "training_started":
        skill = event.get("skill")
        if not skill: raise V187IntegrityError("training_started requires skill.")
        domain(new, "training", cid)[skill] = {"status": "active", "instructor": event.get("instructor")}
    elif etype == "training_progressed":
        skill = event.get("skill")
        if not skill: raise V187IntegrityError("training_progressed requires skill.")
        domain(new, "training", cid).setdefault(skill, {}).update({"status": "active", "progress": event.get("progress")})
    elif etype == "training_completed":
        skill = event.get("skill")
        if not skill: raise V187IntegrityError("training_completed requires skill.")
        mastery = event.get("mastery", "trained")
        domain(new, "training", cid)[skill] = {"status": "completed", "mastery": mastery}
        domain(new, "skills", cid)[skill] = copy.deepcopy(event.get("skill_state", {"mastery": mastery}))
    elif etype == "knowledge_acquired":
        item = event.get("knowledge")
        if not item: raise V187IntegrityError("knowledge_acquired requires knowledge.")
        domain(new, "knowledge", cid)[item] = copy.deepcopy(event.get("value", {"source": event.get("source"), "confidence": event.get("confidence")}))
    elif etype == "kala_training":
        kala = event.get("kala")
        if not kala: raise V187IntegrityError("kala_training requires kala.")
        domain(new, "kalas", cid)[kala] = copy.deepcopy(event.get("value", {"mastery": event.get("mastery", "training")}))
    elif etype == "relationship_update":
        source, target, relation = event.get("from"), event.get("to"), event.get("relation")
        if not all(isinstance(x, str) and x for x in (source, target, relation)):
            raise V187IntegrityError("relationship_update requires from/to/relation.")
        ensure_char(new, source); ensure_char(new, target)
        key = f"{source}|{target}|{relation}"
        domain(new, "relationship_state", "_global")[key] = copy.deepcopy(event.get("state", {}))
    elif etype == "status_set":
        status = event.get("status")
        if not status: raise V187IntegrityError("status_set requires status.")
        domain(new, "statuses", cid)[status] = copy.deepcopy(event.get("value", True))
    elif etype == "status_clear":
        domain(new, "statuses", cid).pop(event.get("status"), None)
    elif etype == "flag_set":
        flag = event.get("flag")
        if not flag: raise V187IntegrityError("flag_set requires flag.")
        domain(new, "flags", cid)[flag] = copy.deepcopy(event.get("value", True))
    elif etype == "flag_clear":
        domain(new, "flags", cid).pop(event.get("flag"), None)
    return new

def assert_integrity(state: Dict[str, Any], canonical: Dict[str, Any]) -> None:
    if set(state.get("characters", {})) != set(canonical["characters"]):
        raise V187IntegrityError("Character registry changed during runtime.")
    for cid, char in canonical["characters"].items():
        for key in IMMUTABLE:
            if state["characters"][cid].get(key) != char.get(key):
                raise V187IntegrityError(f"Canonical field mutated: {cid}.{key}")
    if not relationship_set(canonical).issubset(relationship_set(state)):
        raise V187IntegrityError("Canonical relationship disappeared.")
    if state.get("sovereign_axis") != canonical.get("sovereign_axis"):
        raise V187IntegrityError("Sovereign marriage axis changed.")

def replay_prefix(canonical: Dict[str, Any], events: List[Dict[str, Any]], count: Optional[int] = None) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    selected = events if count is None else events[:count]
    state = initial_state(canonical)
    chain = []
    seen: set[str] = set()
    expected = 1
    for index, event in enumerate(selected):
        validate_event(event, index, seen)
        seq = event.get("sequence")
        if seq is not None:
            if seq != expected:
                raise V187IntegrityError(f"Non-contiguous sequence: expected {expected}, got {seq}")
            expected += 1
        before = sha256_json(state)
        state = apply_event(state, event)
        assert_integrity(state, canonical)
        after = sha256_json(state)
        chain.append({"event_id": event["event_id"], "sequence": seq if seq is not None else index + 1, "before_hash": before, "after_hash": after})
    return state, chain

def validate_event_chain(chain: List[Dict[str, Any]], events: List[Dict[str, Any]]) -> None:
    if len(chain) != len(events):
        raise V187IntegrityError("Replay chain length does not match event count.")
    previous = None
    for i, item in enumerate(chain):
        if item.get("event_id") != events[i].get("event_id"):
            raise V187IntegrityError("Replay chain event order mismatch.")
        if previous is not None and item.get("before_hash") != previous:
            raise V187IntegrityError("Replay chain hash link is broken.")
        previous = item.get("after_hash")

def make_checkpoint(branch_id: str, event_count: int, state: Dict[str, Any], chain: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "schema": "V18_7_CHECKPOINT",
        "version": VERSION,
        "branch_id": branch_id,
        "event_count": event_count,
        "state_hash": sha256_json(state),
        "chain_tip": chain[-1]["after_hash"] if chain else sha256_json(state),
    }

def build_branch(canonical: Dict[str, Any], events: List[Dict[str, Any]], branch_id: str, event_count: Optional[int] = None) -> Dict[str, Any]:
    if not branch_id or any(c in branch_id for c in "\\/:*?\"<>|"):
        raise V187IntegrityError("Invalid branch_id.")
    if event_count is None:
        event_count = len(events)
    if not isinstance(event_count, int) or event_count < 0 or event_count > len(events):
        raise V187IntegrityError("event_count is outside the available event range.")
    state, chain = replay_prefix(canonical, events, event_count)
    return {
        "schema": "V18_7_BRANCH",
        "version": VERSION,
        "branch_id": branch_id,
        "canonical_hash": sha256_json(canonical),
        "event_count": event_count,
        "state": state,
        "state_hash": sha256_json(state),
        "replay_chain": chain,
        "checkpoint": make_checkpoint(branch_id, event_count, state, chain),
    }

def recover_from_checkpoint(canonical: Dict[str, Any], events: List[Dict[str, Any]], checkpoint: Dict[str, Any]) -> Dict[str, Any]:
    branch_id = checkpoint.get("branch_id")
    count = checkpoint.get("event_count")
    branch = build_branch(canonical, events, branch_id, count)
    if branch["state_hash"] != checkpoint.get("state_hash") or branch["checkpoint"]["chain_tip"] != checkpoint.get("chain_tip"):
        raise V187IntegrityError("Checkpoint validation failed: state or chain tip mismatch.")
    return branch

def build_v18_7(repo: Path, canonical_path: Optional[Path] = None, event_log_path: Optional[Path] = None,
                state_path: Optional[Path] = None, output_dir: Optional[Path] = None):
    inputs = locate_inputs(repo)
    canonical_path = canonical_path or inputs["canonical"]
    event_log_path = event_log_path or inputs.get("chain")
    state_path = state_path or inputs["state"]
    if canonical_path is None:
        raise V187IntegrityError("V18.2/V18.4 canonical baseline not found.")
    canonical = normalize_canonical(load_json(canonical_path))
    if event_log_path is None:
        events = []
    else:
        raw = load_json(event_log_path)
        if isinstance(raw, dict) and isinstance(raw.get("events"), list):
            events = extract_events(raw)
        elif isinstance(raw, dict) and isinstance(raw.get("replay_events"), list):
            events = extract_events(raw["replay_events"])
        else:
            events = extract_events(raw)
    if state_path and state_path.exists():
        saved = load_json(state_path)
        if isinstance(saved, dict) and saved.get("canonical_hash") and saved["canonical_hash"] != sha256_json(canonical):
            raise V187IntegrityError("V18.6 state canonical hash does not match V18.7 baseline.")
    branch = build_branch(canonical, events, "main")
    report = {
        "schema": "V18_7_BRANCH_RECOVERY_REPORT",
        "version": VERSION,
        "status": "PASS",
        "characters": len(canonical["characters"]),
        "events": len(events),
        "branches": 1,
        "main_state_hash": branch["state_hash"],
        "checkpoint_support": True,
        "rollback_support": True,
        "fork_support": True,
        "merge_support": False,
        "canonical_state_locked": True,
        "authority_transfer": False,
        "provenance_mutation": False,
        "canonical_relationship_deletion": False,
        "sovereign_axis_mutation": False,
    }
    out = output_dir or repo / "registry" / "V18_7_RUNTIME"
    write_json(out / "V18_7_MAIN_BRANCH.json", branch)
    write_json(out / "V18_7_CHECKPOINT.json", branch["checkpoint"])
    write_json(out / "V18_7_BRANCH_RECOVERY_REPORT.json", report)
    return branch, report

def main() -> int:
    parser = argparse.ArgumentParser(description="Antahpura V18.7 branch, rollback and recovery compiler")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--canonical", type=Path)
    parser.add_argument("--event-log", type=Path)
    parser.add_argument("--state", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    print("Antahpura V18.7 Runtime Branch & Recovery Engine")
    try:
        branch, report = build_v18_7(args.repo, args.canonical, args.event_log, args.state, args.output_dir)
    except V187IntegrityError as exc:
        print(f"\nV18.7 branch/recovery compilation: FAIL\n{exc}")
        return 1
    print("\nV18.7 branch/recovery compilation: PASS")
    print(f"Characters: {report['characters']}")
    print(f"Events: {report['events']}")
    print("Canonical state: LOCKED")
    print("Rollback: ACTIVE")
    print("Fork support: ACTIVE")
    print("Checkpoint recovery: ACTIVE")
    print("Merge: BLOCKED")
    print(f"Main branch hash: {branch['state_hash']}")
    print(f"\nRuntime directory: {args.output_dir or args.repo / 'registry' / 'V18_7_RUNTIME'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
