#!/usr/bin/env python3
"""
apply_journal_event.py — Record journal entries, annotations, and
consistency tracking.
References: systems/journaling_system.json, systems/reward_registry.json,
            systems/relationship_edges.json, systems/character_states.json
"""

import argparse
from _antahpura_common import (
    SYSTEMS, load, load_or_default,
    make_event, emit, now_iso,
    get_character_state, apply_relationship_delta,
    load_character_states, load_relationship_edges,
    save_character_states, save_relationship_edges,
    cli_run
)


def load_journal_registry():
    return load_or_default(SYSTEMS / "journaling_system.json", {})


def ensure_journal_state(char_state):
    char_state.setdefault("journal_entries", [])
    char_state.setdefault("shared_journals_with", [])
    char_state.setdefault("journal_streak_current", 0)
    char_state.setdefault("journal_streak_longest", 0)
    char_state.setdefault("last_entry_at", None)
    return char_state


def write_entry(actor, target, payload):
    """
    Record a journal entry from actor.
    If target is given, the entry is shared with target.
    """
    registry = load_journal_registry()
    journal_types = registry.get("journal_types", {})
    journal_type = payload.get("journal_type", "daily_entry")
    if journal_type not in journal_types:
        raise ValueError(f"Unknown journal type: {journal_type}")

    states = load_character_states()
    edges = load_relationship_edges()
    actor_state = get_character_state(states, actor)
    ensure_journal_state(actor_state)

    entry_id = f"jrn_{now_iso()}"

    shared_with = []
    if target:
        shared_with.append(target)
        if target not in actor_state["shared_journals_with"]:
            actor_state["shared_journals_with"].append(target)

    entry = {
        "entry_id": entry_id,
        "journal_type": journal_type,
        "prompt_id": payload.get("prompt_id"),
        "written_at": now_iso(),
        "shared_with": shared_with,
        "annotation_ids": [],
        "word_count": payload.get("word_count", 0)
    }
    actor_state["journal_entries"].append(entry)

    # Streak tracking
    last = actor_state.get("last_entry_at")
    if last:
        # Simple day-based streak: increment if last entry was yesterday
        # (Actual day calculation delegated to runtime; here we simply increment if a streak exists)
        actor_state["journal_streak_current"] = actor_state.get("journal_streak_current", 0) + 1
    else:
        actor_state["journal_streak_current"] = 1

    if actor_state["journal_streak_current"] > actor_state.get("journal_streak_longest", 0):
        actor_state["journal_streak_longest"] = actor_state["journal_streak_current"]

    actor_state["last_entry_at"] = now_iso()
    actor_state["last_updated"] = now_iso()

    # Sharing affects relationship
    if target:
        apply_relationship_delta(
            edges, actor, target,
            {"trust": 2, "vulnerability": 1},
            memory_tag=f"journal_shared_{journal_type}"
        )

    # Streak rewards
    reward_triggered = None
    streak = actor_state["journal_streak_current"]
    if streak == 7:
        reward_triggered = "rw_sticker_chart"
    elif streak == 30:
        reward_triggered = "rw_pocket_token"
    elif streak == 90:
        reward_triggered = "rw_formal_title"

    save_character_states(states)
    save_relationship_edges(edges)

    event = make_event(
        "journal_entry_written", actor, target,
        {
            **payload,
            "entry_id": entry_id,
            "journal_type": journal_type,
            "word_count": entry["word_count"],
            "streak": streak,
            "reward_triggered": reward_triggered
        },
        consequence_class="micro"
    )
    return emit(event)


def annotate_entry(actor, target, payload):
    """
    Dominant annotates a submissive's journal entry.
    actor = Dominant, target = submissive
    """
    registry = load_journal_registry()
    annotation_types = registry.get("journal_annotation_types", {})
    annotation_type = payload.get("annotation_type", "acknowledgment")
    if annotation_type not in annotation_types:
        raise ValueError(f"Unknown annotation type: {annotation_type}")

    states = load_character_states()
    edges = load_relationship_edges()
    target_state = get_character_state(states, target)
    ensure_journal_state(target_state)

    entry_id = payload.get("entry_id")
    if entry_id:
        for entry in target_state["journal_entries"]:
            if entry["entry_id"] == entry_id:
                annotation_id = f"ann_{now_iso()}"
                entry["annotation_ids"].append(annotation_id)
                break

    annotation_effect = annotation_types[annotation_type].get("relationship_effect", {})
    if annotation_effect:
        apply_relationship_delta(
            edges, target, actor, annotation_effect,
            memory_tag=f"journal_annotation_{annotation_type}"
        )

    target_state["last_updated"] = now_iso()
    save_character_states(states)
    save_relationship_edges(edges)

    event = make_event(
        "journal_entry_annotated", actor, target,
        {
            **payload,
            "entry_id": entry_id,
            "annotation_type": annotation_type,
            "effects": annotation_effect
        },
        consequence_class="micro"
    )
    return emit(event)


def share_journal(actor, target, payload):
    """
    Grant or revoke journal sharing to a target.
    """
    states = load_character_states()
    edges = load_relationship_edges()
    actor_state = get_character_state(states, actor)
    ensure_journal_state(actor_state)

    action = payload.get("share_action", "grant")

    if action == "grant":
        if target not in actor_state["shared_journals_with"]:
            actor_state["shared_journals_with"].append(target)
            apply_relationship_delta(
                edges, actor, target, {"trust": 3},
                memory_tag="journal_sharing_granted"
            )
    elif action == "revoke":
        if target in actor_state["shared_journals_with"]:
            actor_state["shared_journals_with"].remove(target)
            apply_relationship_delta(
                edges, actor, target, {"trust": -2},
                memory_tag="journal_sharing_revoked"
            )

    actor_state["last_updated"] = now_iso()
    save_character_states(states)
    save_relationship_edges(edges)

    event = make_event(
        "journal_sharing_changed", actor, target,
        {**payload, "share_action": action},
        consequence_class="personal"
    )
    return emit(event)


def record_neglect(actor, target, payload):
    """
    Record journal neglect — a signal, not a punishment.
    """
    days_missed = payload.get("days_missed", 3)
    registry = load_journal_registry()
    signals = registry.get("journal_neglect_signals", {})

    signal_key = None
    for key in ("missed_3_days", "missed_7_days", "missed_14_days"):
        if days_missed >= int(key.split("_")[1]):
            signal_key = key

    signal = signals.get(signal_key, {}) if signal_key else {}

    event = make_event(
        "journal_neglect_recorded", actor, target,
        {
            **payload,
            "days_missed": days_missed,
            "signal": signal.get("signal"),
            "action": signal.get("action")
        },
        consequence_class="micro"
    )
    return emit(event)


def dispatch(args, payload):
    if args.action == "write":
        return write_entry(args.actor, args.target, payload)
    elif args.action == "annotate":
        return annotate_entry(args.actor, args.target, payload)
    elif args.action == "share":
        return share_journal(args.actor, args.target, payload)
    elif args.action == "neglect":
        return record_neglect(args.actor, args.target, payload)
    raise ValueError(f"Unknown journal action: {args.action}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--journal-type", default="daily_entry",
                        choices=["daily_entry", "weekly_reflection", "monthly_review",
                                 "scene_debrief", "free_write", "prompt_response"])
    parser.add_argument("--prompt-id", default=None)
    parser.add_argument("--entry-id", default=None)
    parser.add_argument("--annotation-type", default="acknowledgment",
                        choices=["acknowledgment", "reflection", "question",
                                 "assignment", "praise", "concern"])
    parser.add_argument("--share-action", default="grant", choices=["grant", "revoke"])
    parser.add_argument("--days-missed", type=int, default=3)
    parser.add_argument("--word-count", type=int, default=0)
    cli_run(parser, dispatch, ["write", "annotate", "share", "neglect"])