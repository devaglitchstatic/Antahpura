#!/usr/bin/env python3
"""
run_scene.py - Scene runner for Antahpura V20.

Subcommands:
  start <template_id>       Initialize a scene from a template
  act                       Advance to the next act
  choice <id> <opt>         Record a choice
  end                       Finalize scene, apply consequences
  status                    Show current scene state

Options:
  --participants c1,c2      Comma-separated character IDs
  --location loc_id         Override template's default location
  --chapter N               Chapter number for events
  --auto                    Run all acts automatically in one command
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _antahpura_common import (
    RUNTIME, load, save, load_or_default,
    make_event, emit, now_iso,
    get_character_state, apply_relationship_delta,
    load_character_states, load_relationship_edges,
    save_character_states, save_relationship_edges,
)


def load_templates():
    return load_or_default(
        ROOT / "scenes" / "scene_templates.json",
        {"templates": []}
    )


def find_template(templates, template_id):
    for t in templates.get("templates", []):
        if t.get("template_id") == template_id or t.get("id") == template_id:
            return t
    return None


def load_current_scene():
    return load_or_default(RUNTIME / "current_scene.json", {})


def save_current_scene(scene):
    save(RUNTIME / "current_scene.json", scene)


def validate_participants(char_ids, states):
    missing = [c for c in char_ids if c not in states.get("states", {})]
    return missing


def start_scene(args):
    templates = load_templates()
    template = find_template(templates, args.template_id)
    if not template:
        print(f"ERROR: unknown template: {args.template_id}")
        return 1

    participants = [p.strip() for p in args.participants.split(",")] if args.participants else []
    if not participants:
        participants = template.get("typical_participants", [])
    if not participants:
        print("ERROR: no participants")
        return 1

    states = load_character_states()
    missing = validate_participants(participants, states)
    if missing:
        print(f"ERROR: unknown characters: {missing}")
        return 1

    location = args.location or template.get("default_location")
    chapter = args.chapter

    scene = {
        "schema": "antahpura.runtime.current_scene",
        "version": "20.0",
        "scene_id": f"scn_{now_iso()}",
        "template_id": args.template_id,
        "template_name": template.get("name"),
        "scene_type": template.get("scene_type"),
        "chapter": chapter,
        "location_id": location,
        "occasion_id": args.occasion or template.get("default_occasion"),
        "participants": participants,
        "pov_holder": participants[0],
        "act": 1,
        "phase": "starting",
        "act_scripts": template.get("act_scripts", {}),
        "required_kalas": template.get("required_kalas", []),
        "available_kamas": template.get("available_kamas", []),
        "choices_made": [],
        "events_emitted": [],
        "started_at": now_iso(),
        "status": "active"
    }
    save_current_scene(scene)

    event = make_event(
        "scene_started", participants[0], None,
        {
            "chapter": chapter,
            "scene_id": scene["scene_id"],
            "template_id": args.template_id,
            "location": location,
            "participants": participants
        },
        consequence_class="narrative"
    )
    emit(event)
    scene["events_emitted"].append(event["event_id"])
    save_current_scene(scene)

    print(f"Scene started: {scene['scene_id']}")
    print(f"  Template: {scene['template_name']}")
    print(f"  Type:     {scene['scene_type']}")
    print(f"  Act:      {scene['act']} (1 of 5)")
    print(f"  Location: {location}")
    print(f"  Actors:   {', '.join(participants)}")

    if args.auto:
        return auto_run(scene, chapter)

    return 0


def advance_act(scene, chapter):
    if scene.get("status") != "active":
        print("ERROR: no active scene")
        return 1

    current = scene.get("act", 1)
    if current >= 5:
        print("Already at act 5. Use 'end' to finalize.")
        return 0

    scene["act"] = current + 1
    scene["phase"] = f"act_{scene['act']}"
    save_current_scene(scene)

    act_script = scene.get("act_scripts", {}).get(f"act_{scene['act']}", "")
    participants = scene.get("participants", [])
    actor = participants[0] if participants else "system"

    event = make_event(
        "scene_act", actor, None,
        {
            "chapter": chapter,
            "scene_id": scene["scene_id"],
            "act": scene["act"],
            "act_script": act_script
        },
        consequence_class="micro"
    )
    emit(event)
    scene["events_emitted"].append(event["event_id"])
    save_current_scene(scene)

    print(f"Act advanced to {scene['act']} of 5")
    if act_script:
        print(f"  Script: {act_script}")
    return 0


def record_choice(scene, choice_id, option_id, chapter):
    if scene.get("status") != "active":
        print("ERROR: no active scene")
        return 1

    choice_entry = {
        "choice_id": choice_id,
        "option_id": option_id,
        "act": scene.get("act"),
        "timestamp": now_iso()
    }
    scene.setdefault("choices_made", []).append(choice_entry)
    save_current_scene(scene)

    participants = scene.get("participants", [])
    actor = participants[0] if participants else "system"

    event = make_event(
        "choice_made", actor, None,
        {
            "chapter": chapter,
            "scene_id": scene["scene_id"],
            "choice_id": choice_id,
            "option_id": option_id,
            "act": scene.get("act")
        },
        consequence_class="personal"
    )
    emit(event)
    scene["events_emitted"].append(event["event_id"])
    save_current_scene(scene)

    print(f"Choice recorded: {choice_id} -> {option_id}")
    return 0


def end_scene(scene, chapter):
    if scene.get("status") != "active":
        print("ERROR: no active scene")
        return 1

    participants = scene.get("participants", [])
    required_kalas = scene.get("required_kalas", [])
    available_kamas = scene.get("available_kamas", [])
    location = scene.get("location_id")

    states = load_character_states()
    edges = load_relationship_edges()

    # 1. Advance kala practice for each participant
    kala_events = []
    for cid in participants:
        cstate = get_character_state(states, cid)
        km = cstate.setdefault("kala_mastery", {})
        for kid in required_kalas:
            if kid in km:
                entry = km[kid]
                entry["practice_count"] = entry.get("practice_count", 0) + 1
                entry["confidence"] = min(1.0, entry.get("confidence", 0.5) + 0.02)
                if entry["practice_count"] % 10 == 0 and entry.get("level", 0) < 10:
                    entry["level"] = entry["level"] + 1
                    kala_events.append({"char": cid, "kala": kid, "new_level": entry["level"]})
        cstate["last_updated"] = now_iso()

    # 2. Bump kama curiosity for available kamas
    for cid in participants:
        cstate = get_character_state(states, cid)
        kl = cstate.setdefault("kama_lifecycle", {})
        for kama_id in available_kamas:
            if kama_id in kl:
                entry = kl[kama_id]
                entry["curiosity"] = min(1.0, entry.get("curiosity", 0.0) + 0.05)
                if entry.get("state") == "discoverable" and entry["curiosity"] > 0.3:
                    entry["state"] = "mentionable"
                elif entry.get("state") == "mentionable" and entry["curiosity"] > 0.6:
                    entry["state"] = "discussable"
                if not entry.get("discovered_at"):
                    entry["discovered_at"] = now_iso()

    # 3. Apply relationship deltas between participants
    for i, a in enumerate(participants):
        for b in participants[i + 1:]:
            apply_relationship_delta(edges, a, b, {"trust": 1, "familiarity": 1},
                                     memory_tag=f"scene_{scene['scene_id']}")
            apply_relationship_delta(edges, b, a, {"trust": 1, "familiarity": 1},
                                     memory_tag=f"scene_{scene['scene_id']}")

    # 4. Write memory
    memory = load_or_default(ROOT / "archive" / "memories.json", {"memories": []})
    memory.setdefault("memories", []).append({
        "memory_id": f"mem_{scene['scene_id']}",
        "scene_id": scene["scene_id"],
        "template_id": scene.get("template_id"),
        "chapter": chapter,
        "participants": participants,
        "location": location,
        "timestamp": now_iso(),
        "choices_made": scene.get("choices_made", []),
        "kala_events": kala_events,
        "salience": 0.5
    })
    save(ROOT / "archive" / "memories.json", memory)

    save_character_states(states)
    save_relationship_edges(edges)

    # 5. Emit scene_ended event
    event = make_event(
        "scene_ended", participants[0] if participants else "system", None,
        {
            "chapter": chapter,
            "scene_id": scene["scene_id"],
            "template_id": scene.get("template_id"),
            "location": location,
            "participants": participants,
            "acts_completed": scene.get("act", 5),
            "kala_events": kala_events,
            "choices_made": len(scene.get("choices_made", []))
        },
        consequence_class="personal"
    )
    emit(event)

    scene_id = scene["scene_id"]
    print(f"Scene ended: {scene_id}")
    print(f"  Acts completed: {scene.get('act')}")
    print(f"  Kala practice events: {len(kala_events)}")
    print(f"  Choices made: {len(scene.get('choices_made', []))}")
    print(f"  Participants: {', '.join(participants)}")

    # 6. Clear scene state
    save_current_scene({})

    return 0


def auto_run(scene, chapter):
    """Advance through acts 2..5 then end."""
    for act in range(2, 6):
        scene["act"] = act
        scene["phase"] = f"act_{act}"
        save_current_scene(scene)
        act_script = scene.get("act_scripts", {}).get(f"act_{act}", "")
        participants = scene.get("participants", [])
        actor = participants[0] if participants else "system"
        event = make_event(
            "scene_act", actor, None,
            {"chapter": chapter, "scene_id": scene["scene_id"],
             "act": act, "act_script": act_script},
            consequence_class="micro"
        )
        emit(event)
        scene["events_emitted"].append(event["event_id"])
        save_current_scene(scene)
        print(f"  Act {act}: {act_script}")

    return end_scene(scene, chapter)


def status():
    scene = load_current_scene()
    if not scene or not scene.get("scene_id"):
        print("No active scene.")
        return 0
    print(json.dumps({
        "scene_id": scene.get("scene_id"),
        "template": scene.get("template_name"),
        "act": scene.get("act"),
        "location": scene.get("location_id"),
        "participants": scene.get("participants"),
        "choices_made": len(scene.get("choices_made", []))
    }, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    s = sub.add_parser("start")
    s.add_argument("template_id")
    s.add_argument("--participants", default="")
    s.add_argument("--location", default=None)
    s.add_argument("--occasion", default=None)
    s.add_argument("--chapter", type=int, default=1)
    s.add_argument("--auto", action="store_true")

    a = sub.add_parser("act")
    a.add_argument("--chapter", type=int, default=1)

    c = sub.add_parser("choice")
    c.add_argument("choice_id")
    c.add_argument("option_id")
    c.add_argument("--chapter", type=int, default=1)

    e = sub.add_parser("end")
    e.add_argument("--chapter", type=int, default=1)

    sub.add_parser("status")

    args = parser.parse_args()

    if args.cmd == "start":
        return start_scene(args)
    elif args.cmd == "act":
        return advance_act(load_current_scene(), args.chapter)
    elif args.cmd == "choice":
        return record_choice(load_current_scene(), args.choice_id, args.option_id, args.chapter)
    elif args.cmd == "end":
        return end_scene(load_current_scene(), args.chapter)
    elif args.cmd == "status":
        return status()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())