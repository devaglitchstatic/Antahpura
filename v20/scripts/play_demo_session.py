#!/usr/bin/env python3
"""
play_demo_session.py - Complete demo session exercising all event handlers.

Runs a canonical day: morning service → training scene → reward → punishment
→ ritual scene → journal → DBT → evening reflection.

Each event handler is called with real character IDs and real registry items.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CH = 1


def run(cmd):
    print(f"\n$ {' '.join(cmd[1:])}")
    result = subprocess.run(cmd, cwd=SCRIPTS, capture_output=False, text=True)
    return result.returncode


def main():
    python = sys.executable

    print("=" * 72)
    print("ANTAHPURA V20 - DEMO SESSION")
    print("A canonical day in the palace")
    print("=" * 72)

    # ---- MORNING: Service task + journal ----
    print("\n\n### MORNING - Service ###")
    run([python, "apply_task_event.py", "assign",
         "--actor", "char_kumari_rati",
         "--target", "char_padma",
         "--task-id", "task_service_morning",
         "--chapter", str(CH)])

    run([python, "apply_journal_event.py", "write",
         "--actor", "char_padma",
         "--target", "char_kumari_rati",
         "--journal-type", "daily_entry",
         "--prompt-id", "dp_daily_gratitude",
         "--word-count", "120",
         "--chapter", str(CH)])

    run([python, "apply_task_event.py", "complete",
         "--actor", "char_kumari_rati",
         "--target", "char_padma",
         "--task-id", "task_service_morning",
         "--chapter", str(CH)])

    # ---- MIDDAY: Training scene ----
    print("\n\n### MIDDAY - Training Scene ###")
    run([python, "run_scene.py", "start", "tpl_training_ground",
         "--participants", "char_roxana,char_altani,char_jahzara",
         "--chapter", str(CH), "--auto"])

    # ---- AFTERNOON: Reward + relationship delta ----
    print("\n\n### AFTERNOON - Reward ###")
    run([python, "apply_reward_event.py", "give_reward",
         "--actor", "char_roxana",
         "--target", "char_altani",
         "--reward-id", "rw_public_acknowledgment",
         "--chapter", str(CH)])

    # ---- Punishment + Clean Slate ----
    print("\n\n### AFTERNOON - Infraction & Clean Slate ###")
    run([python, "apply_punishment_event.py", "record_infraction",
         "--actor", "char_anisa",
         "--target", "char_padma",
         "--infraction", "forgetting_check_in",
         "--chapter", str(CH)])

    run([python, "apply_punishment_event.py", "assign",
         "--actor", "char_anisa",
         "--target", "char_padma",
         "--punishment-id", "pun_privilege_restriction",
         "--chapter", str(CH)])

    run([python, "apply_punishment_event.py", "complete",
         "--actor", "char_anisa",
         "--target", "char_padma",
         "--chapter", str(CH)])

    # ---- Consent + Traffic Light ----
    print("\n\n### CONSENT - Pre-scene negotiation ###")
    run([python, "apply_consent_event.py", "negotiate",
         "--actor", "char_shrinagar",
         "--target", "char_kumari_rati",
         "--framework", "RACK",
         "--hard-limits", "no_marks,no_breath_play",
         "--soft-limits", "light_impact,emotional_edge",
         "--chapter", str(CH)])

    run([python, "apply_traffic_light_event.py", "signal",
         "--actor", "char_kumari_rati",
         "--target", "char_shrinagar",
         "--signal", "green",
         "--cause", "scene_start",
         "--chapter", str(CH)])

    # ---- EVENING: Ritual scene ----
    print("\n\n### EVENING - Ritual Scene ###")
    run([python, "run_scene.py", "start", "tpl_dawn_ritual",
         "--participants", "char_svara,char_tarana,char_kumari_rati",
         "--chapter", str(CH), "--auto"])

    # ---- DBT if needed ----
    print("\n\n### EVENING - DBT Recovery ###")
    run([python, "apply_dbt_event.py", "apply",
         "--actor", "char_shrinagar",
         "--target", "char_kumari_rati",
         "--technique-id", "dbt_TIPP",
         "--chapter", str(CH)])

    # ---- NIGHT: Journal reflection ----
    print("\n\n### NIGHT - Reflection ###")
    run([python, "apply_journal_event.py", "write",
         "--actor", "char_kumari_rati",
         "--journal-type", "weekly_reflection",
         "--prompt-id", "wp_weekly_patterns",
         "--word-count", "450",
         "--chapter", str(CH)])

    # ---- FINAL: Status ----
    print("\n\n### FINAL STATUS ###")
    run([python, "run_scene.py", "status"])

    print("\n\n" + "=" * 72)
    print("DEMO COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()