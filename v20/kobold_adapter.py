#!/usr/bin/env python3
"""
kobold_adapter.py — send the assembled Antahpura prompt to a local
KoboldCpp instance and capture the response.

Two modes:
  --mode chat    OpenAI-compatible /v1/chat/completions endpoint
                 (KoboldCpp 1.62+ supports this)
  --mode raw     Legacy /api/v1/generate endpoint
                 (posts a single prompt string)

Default endpoint: http://localhost:5001

Usage:
  python kobold_adapter.py
  python kobold_adapter.py --run runtime/runs/scene_run_<ts>.json
  python kobold_adapter.py --mode raw --endpoint http://localhost:5001
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS_DIR = ROOT / "runtime" / "runs"
OUTPUT_DIR = ROOT / "runtime" / "runs"


def latest_run() -> Path | None:
    runs = sorted(RUNS_DIR.glob("scene_run_*.json"), reverse=True)
    return runs[0] if runs else None


def load_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_prompt_text(report_path: Path) -> str:
    """Read the adjacent .txt prompt file."""
    txt = report_path.with_suffix(".txt")
    if not txt.exists():
        raise SystemExit(f"Prompt text not found: {txt}")
    return txt.read_text(encoding="utf-8")


# --- HTTP helpers ---------------------------------------------------------

def post_json(url: str, payload: dict, timeout: int = 300) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return {"raw_response": body}
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:500]}"}
    except urllib.error.URLError as e:
        return {"error": f"connection failed: {e}"}


# --- Chat mode (OpenAI-compatible) ---------------------------------------

def build_chat_messages(prompt_text: str, system_context: str = "") -> list:
    """
    KoboldCpp's chat endpoint expects OpenAI-style messages.
    We send a single user message containing the full assembled prompt,
    optionally preceded by a system message.
    """
    messages = []
    if system_context:
        messages.append({"role": "system", "content": system_context})
    messages.append({"role": "user", "content": prompt_text})
    return messages


def run_chat(endpoint: str, prompt_text: str, sampling: dict) -> dict:
    url = endpoint.rstrip("/") + "/v1/chat/completions"
    payload = {
        "model": "koboldcpp",
        "messages": build_chat_messages(prompt_text),
        "temperature": sampling.get("temperature", 0.75),
        "top_p": sampling.get("top_p", 0.9),
        "max_tokens": sampling.get("max_tokens", 1024),
        "frequency_penalty": sampling.get("frequency_penalty", 0.0),
        "presence_penalty": sampling.get("presence_penalty", 0.0),
        "stream": False,
    }
    return post_json(url, payload)


# --- Raw mode (legacy /api/v1/generate) ----------------------------------

def run_raw(endpoint: str, prompt_text: str, sampling: dict) -> dict:
    url = endpoint.rstrip("/") + "/api/v1/generate"
    payload = {
        "prompt": prompt_text,
        "max_length": sampling.get("max_tokens", 1024),
        "temperature": sampling.get("temperature", 0.75),
        "top_p": sampling.get("top_p", 0.9),
        "top_k": sampling.get("top_k", 0),
        "rep_pen": sampling.get("repetition_penalty", 1.1),
        "stop_sequence": [
            "\n### ",     # stop if the model starts a new section
            "</s>",
            "<|im_end|>",
        ],
    }
    return post_json(url, payload)


# --- Orchestration -------------------------------------------------------

def write_output(run_path: Path, response: dict, mode: str) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = OUTPUT_DIR / f"response_{ts}.json"
    payload = {
        "schema": "antahpura.kobold_response",
        "version": "1.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "source_run": str(run_path.relative_to(ROOT)),
        "mode": mode,
        "response": response,
    }
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                   encoding="utf-8")

    # Also write the assistant text alone for easy reading
    text = ""
    if "choices" in response and response["choices"]:
        text = response["choices"][0].get("message", {}).get("content", "")
    elif "results" in response and response["results"]:
        text = response["results"][0].get("text", "")
    if text:
        txt_out = out.with_suffix(".txt")
        txt_out.write_text(text, encoding="utf-8")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://localhost:5001")
    ap.add_argument("--mode", choices=["chat", "raw"], default="chat")
    ap.add_argument("--run", default=None,
                    help="Path to scene_run_*.json (default: latest)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print request payload without sending")
    args = ap.parse_args()

    run_path = Path(args.run) if args.run else latest_run()
    if not run_path or not run_path.exists():
        raise SystemExit("No scene_run_*.json found. Run run_scene.py first.")

    report = load_report(run_path)
    prompt_text = load_prompt_text(run_path)
    sampling = report.get("prompt", {}).get("sampling_parameters", {})

    print("=" * 60)
    print("KOBOLD ADAPTER")
    print("=" * 60)
    print(f"Source run:  {run_path.relative_to(ROOT)}")
    print(f"Endpoint:    {args.endpoint}")
    print(f"Mode:        {args.mode}")
    print(f"Prompt size: {len(prompt_text)} chars")
    print(f"Sampling:    {json.dumps(sampling, indent=2)}")
    print()

    if args.mode == "chat":
        url = args.endpoint.rstrip("/") + "/v1/chat/completions"
        payload = {
            "model": "koboldcpp",
            "messages": build_chat_messages(prompt_text),
            "temperature": sampling.get("temperature", 0.75),
            "top_p": sampling.get("top_p", 0.9),
            "max_tokens": sampling.get("max_tokens", 1024),
            "stream": False,
        }
    else:
        url = args.endpoint.rstrip("/") + "/api/v1/generate"
        payload = {
            "prompt": prompt_text,
            "max_length": sampling.get("max_tokens", 1024),
            "temperature": sampling.get("temperature", 0.75),
            "top_p": sampling.get("top_p", 0.9),
            "rep_pen": sampling.get("repetition_penalty", 1.1),
        }

    if args.dry_run:
        print("DRY RUN — request that would be sent:")
        print(f"URL: {url}")
        print(json.dumps(payload, indent=2)[:2000])
        return

    print(f"POST {url} ...")
    if args.mode == "chat":
        response = run_chat(args.endpoint, prompt_text, sampling)
    else:
        response = run_raw(args.endpoint, prompt_text, sampling)

    if "error" in response:
        print(f"ERROR: {response['error']}")
        sys.exit(1)

    out = write_output(run_path, response, args.mode)
    print(f"Response written: {out.relative_to(ROOT)}")

    # Print assistant text
    text = ""
    if "choices" in response and response["choices"]:
        text = response["choices"][0].get("message", {}).get("content", "")
    elif "results" in response and response["results"]:
        text = response["results"][0].get("text", "")
    if text:
        print()
        print("-" * 60)
        print(text)
        print("-" * 60)


if __name__ == "__main__":
    main()