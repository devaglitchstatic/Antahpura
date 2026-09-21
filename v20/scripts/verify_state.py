#!/usr/bin/env python3
"""verify_state.py - Report current runtime state after a session."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)


events_file = ROOT / "archive" / "events.jsonl"
events = sum(1 for _ in open(events_file, encoding="utf-8")) if events_file.exists() else 0
print(f"Total events: {events}")

mem = load(ROOT / "archive" / "memories.json")
print(f"Memories: {len(mem.get('memories', []))}")

d = load(ROOT / "runtime" / "character_states.json")

for cid in ("char_padma", "char_kumari_rati", "char_shrinagar"):
    if cid not in d.get("states", {}):
        print(f"{cid}: MISSING")
        continue
    s = d["states"][cid]
    print(f"\n{cid}:")
    print(f"  tasks_completed_total:   {s.get('tasks_completed_total', 0)}")
    print(f"  punishment_history:      {len(s.get('punishment_history', []))}")
    print(f"  journal_entries:         {len(s.get('journal_entries', []))}")
    print(f"  dbt_skills_known:        {len(s.get('dbt_skills_known', []))}")
    print(f"  consent_records:         {len(s.get('consent_records', []))}")
    print(f"  reward_history_summary:  {s.get('reward_history_summary', {})}")
    print(f"  emotional_pressure:      {s.get('emotional_pressure', 0)}")