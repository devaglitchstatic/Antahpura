#!/usr/bin/env python3
"""
apply_task_event.py - Assign, complete, or fail tasks.

References:
  systems/task_system.json
  systems/reward_registry.json
  systems/punishment_system.json
"""

import json
import argparse
from _antahpura_common import (
    SYSTEMS, load, save, load_or_default,
    make_event, emit, now_iso,
    get_character_state, apply_relationship_delta,
    load_character_states, load_relationship_edges,
    save_character_states, save_relationship_edges,
    cli_run
)


def load_task_registry():
    return load_or_default(SYSTEMS / "task_system.json", {"task_registry": {"tasks": []}})


def find_task(registry, task_id):
    for task in registry.get("task_registry", {}).get("tasks", []):
        if task.get("task_id") == task_id:
            return task
    return None


def ensure_task_state(char_state):
    char_state.setdefault("tasks_active", [])
    char_state.setdefault("tasks_completed_total", 0)
    char_state.setdefault("tasks_missed_total", 0)
    char_state.setdefault("current_streak", 0)
    char_state.setdefault("longest_streak", 0)
    return char_state


def assign_task(actor, target, task_id, payload):
    registry = load_task_registry()
    task = find_task(registry, task_id)
    if not task:
        raise ValueError(f"Unknown task_id: {task_id}")

    states = load_character_states()
    target_state = get_character_state(states, target)
    ensure_task_state(target_state)

    target_state["tasks_active"] = [
        t for t in target_state["tasks_active"] if t["task_id"] != task_id
    ]

    entry = {
        "task_id": task_id,
        "name": task.get("name"),
        "category": task.get("category"),
        "assigned_by": actor,
        "assigned_at": now_iso(),
        "deadline": task.get("deadline", "as_specified"),
        "completion_count": 0,
        "miss_count": 0,
        "streak": 0,
        "verification_status": "pending",
        "last_completed_at": None
    }
    target_state["tasks_active"].append(entry)
    target_state["last_updated"] = now_iso()
    save_character_states(states)

    return emit(make_event(
        "task_assigned", actor, target,
        {**payload, "task_id": task_id, "category": task.get("category")},
        consequence_class="micro"
    ))


def complete_task(actor, target, task_id, payload):
    registry = load_task_registry()
    task = find_task(registry, task_id)
    states = load_character_states()
    edges = load_relationship_edges()
    target_state = get_character_state(states, target)
    ensure_task_state(target_state)

    found = None
    for t in target_state["tasks_active"]:
        if t["task_id"] == task_id:
            found = t
            break
    if not found:
        raise ValueError(f"Task {task_id} not active for {target}")

    found["completion_count"] += 1
    found["streak"] = found.get("streak", 0) + 1
    found["last_completed_at"] = now_iso()
    found["verification_status"] = "verified"

    target_state["tasks_completed_total"] = target_state.get("tasks_completed_total", 0) + 1
    target_state["current_streak"] = target_state.get("current_streak", 0) + 1
    if target_state["current_streak"] > target_state.get("longest_streak", 0):
        target_state["longest_streak"] = target_state["current_streak"]
    target_state["last_updated"] = now_iso()

    apply_relationship_delta(
        edges, target, actor,
        {"trust": 1, "respect": 1},
        memory_tag=f"task_complete_{task_id}"
    )

    save_character_states(states)
    save_relationship_edges(edges)

    reward_hint = task.get("reward_on_completion") if task else None

    return emit(make_event(
        "task_completed", actor, target,
        {
            **payload,
            "task_id": task_id,
            "streak": found["streak"],
            "reward_hint": reward_hint
        },
        consequence_class="micro"
    ))


def fail_task(actor, target, task_id, payload):
    registry = load_task_registry()
    task = find_task(registry, task_id)
    states = load_character_states()
    edges = load_relationship_edges()
    target_state = get_character_state(states, target)
    ensure_task_state(target_state)

    found = None
    for t in target_state["tasks_active"]:
        if t["task_id"] == task_id:
            found = t
            break
    if not found:
        raise ValueError(f"Task {task_id} not active for {target}")

    found["miss_count"] += 1
    found["streak"] = 0
    found["verification_status"] = "rejected"
    target_state["tasks_missed_total"] = target_state.get("tasks_missed_total", 0) + 1
    target_state["current_streak"] = 0
    target_state["last_updated"] = now_iso()

    apply_relationship_delta(
        edges, target, actor,
        {"trust": -1},
        memory_tag=f"task_miss_{task_id}"
    )

    save_character_states(states)
    save_relationship_edges(edges)

    punishment_hint = task.get("punishment_on_miss") if task else None

    return emit(make_event(
        "task_failed", actor, target,
        {
            **payload,
            "task_id": task_id,
            "miss_count": found["miss_count"],
            "punishment_hint": punishment_hint
        },
        consequence_class="micro"
    ))


def dispatch(args, payload):
    if args.action == "assign":
        return assign_task(args.actor, args.target, args.task_id, payload)
    elif args.action == "complete":
        return complete_task(args.actor, args.target, args.task_id, payload)
    elif args.action == "fail":
        return fail_task(args.actor, args.target, args.task_id, payload)
    raise ValueError(f"Unknown task action: {args.action}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    cli_run(parser, dispatch, ["assign", "complete", "fail"])