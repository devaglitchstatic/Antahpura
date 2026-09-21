#!/usr/bin/env python3
"""
smoke_test.py — Antahpura repository smoke test (v4).

Fixes vs v3:
  - Registers loaded modules in sys.modules before exec_module.
    Python 3.14's @dataclass decorator requires this or it crashes.
  - KAMA_CHARACTER_STATE loader auto-detects the container key
    ("characters" / "states" / top-level) and skips non-dict values.
  - Same graceful dependency handling as v3.

Phases:
  1. Data layer integrity
  2. Emotional engine
  3. Kama engine
  4. Runtime engine

Exit code: 0 if no failures, 1 otherwise.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import traceback
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
SKIP = "\033[93mSKIP\033[0m"
INFO = "\033[94mINFO\033[0m"

_results = {"pass": 0, "fail": 0, "skip": 0}


def ok(msg): print(f"  [{PASS}] {msg}"); _results["pass"] += 1
def fail(msg): print(f"  [{FAIL}] {msg}"); _results["fail"] += 1
def skip(msg): print(f"  [{SKIP}] {msg}"); _results["skip"] += 1
def info(msg): print(f"  [{INFO}] {msg}")


def check(cond, msg_ok, msg_fail):
    ok(msg_ok) if cond else fail(msg_fail)


def section(title):
    print()
    print("=" * 66)
    print(title)
    print("=" * 66)


def load(rel):
    p = ROOT / rel
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"{rel} — parse error: {e}")
        return None


# --- search utilities -------------------------------------------------------

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__",
             ".venv", "venv", ".mypy_cache", ".pytest_cache"}


def find_file(name: str, roots: list[Path]) -> Path | None:
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            if name in filenames:
                return Path(dirpath) / name
    return None


def find_engine(candidates: list[str], roots: list[Path]) -> Path | None:
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn in candidates:
                    return Path(dirpath) / fn
    return None


@contextmanager
def chdir(path: Path):
    old = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(old)


def import_module_from_path(path: Path, module_name: str):
    """
    Import a module from an arbitrary path.

    Critical: register in sys.modules BEFORE exec_module, otherwise
    Python 3.14's @dataclass decorator crashes when it looks up
    sys.modules.get(cls.__module__).
    """
    # Clear any prior registration to avoid stale references
    if module_name in sys.modules:
        del sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # <-- the fix
    spec.loader.exec_module(module)
    return module


# --- phase 1 ----------------------------------------------------------------

def phase_1_data_layer():
    section("PHASE 1 — DATA LAYER INTEGRITY")

    print("\n[1.1] Canonical registries")
    char_reg = load("characters/V17_1_CHARACTER_REGISTRY.json")
    check(char_reg is not None and isinstance(char_reg.get("characters"), list),
          "character registry loaded", "character registry missing or malformed")
    if char_reg:
        count = len(char_reg.get("characters", []))
        check(count == 14, f"14 canonical characters ({count})",
              f"expected 14, found {count}")

    kala_sys = load("kalas/kala_system_v20.json")
    check(kala_sys is not None and isinstance(kala_sys.get("kalas"), dict),
          "kala system loaded", "kala system missing or malformed")
    if kala_sys:
        count = len(kala_sys.get("kalas", {}))
        check(count == 64, f"64 kalas ({count})",
              f"expected 64, found {count}")

    kama_reg = load("kama/MASTER_KINK_REGISTRY.json")
    check(kama_reg is not None and isinstance(kama_reg.get("KINKS"), dict),
          "kama registry loaded", "kama registry missing or malformed")
    if kama_reg:
        count = len(kama_reg.get("KINKS", {}))
        check(count >= 99, f"{count} kamas",
              f"expected >= 99, found {count}")

    print("\n[1.2] Derived Kala files")
    for name, path in [
        ("character_kala_matrix", "kalas/character_kala_matrix.json"),
        ("kala_synergies", "kalas/kala_synergies.json"),
        ("kala_mastery_ladder", "kalas/kala_mastery_ladder.json"),
        ("kala_prerequisites_graph", "kalas/kala_prerequisites_graph.json"),
        ("kala_kama_linkage", "kalas/kala_kama_linkage.json"),
    ]:
        data = load(path)
        check(data is not None, f"{name} loaded", f"{name} missing")

    print("\n[1.3] Kama-Kala bridge")
    bridge = load("kalas/KAMA_KALA_BRIDGE.json")
    check(bridge is not None, "KAMA_KALA_BRIDGE loaded", "bridge missing")

    print("\n[1.4] Relationship system")
    rel_sys = load("relationships/relationship_system_v20.json")
    check(rel_sys is not None, "relationship_system_v20 loaded",
          "relationship system missing")
    if rel_sys:
        rels = rel_sys.get("relationships", [])
        check(len(rels) == 18, f"18 canonical relationships ({len(rels)})",
              f"expected 18, found {len(rels)}")

    print("\n[1.5] World offices")
    offices = load("world/offices.json")
    check(offices is not None, "offices loaded", "offices missing")

    print("\n[1.6] Chandra Kala")
    ck = load("chandra_kala/V18_9_CHANDRA_KALA.json")
    check(ck is not None, "chandra kala loaded", "chandra kala missing")

    print("\n[1.7] Character cards")
    spec_dir = ROOT / "characters"
    specs = list(spec_dir.glob("main_*_spec_v2.json"))
    check(len(specs) == 14, f"14 character spec files ({len(specs)})",
          f"expected 14, found {len(specs)}")

    if char_reg:
        missing = []
        for c in char_reg.get("characters", []):
            cid = c.get("id")
            chub = c.get("chub_card_id")
            if not chub:
                missing.append((cid, "no chub_card_id"))
                continue
            expected = spec_dir / f"main_{chub}_spec_v2.json"
            if not expected.exists():
                missing.append((cid, f"missing {expected.name}"))
        check(not missing, "all chub_card_ids resolve to files",
              f"{len(missing)} issues: {missing[:3]}")


# --- phase 2 ----------------------------------------------------------------

def phase_2_emotional_engine():
    section("PHASE 2 — EMOTIONAL ENGINE")

    candidates = ["antapura_v31_rc2.py", "antapura_emotional_engine_v3_2.py"]
    search_roots = [ROOT, REPO, REPO / "scripts", REPO / "engines"]
    engine_path = find_engine(candidates, search_roots)

    if not engine_path:
        skip("no emotional engine found in searched paths")
        return

    info(f"engine found: {engine_path}")

    try:
        import jsonschema  # noqa: F401
    except ImportError:
        skip("jsonschema not installed — engine cannot run")
        info("run: pip install jsonschema")
        return

    try:
        module = import_module_from_path(engine_path, "antapura_emotional_engine")
    except Exception as e:
        fail(f"import failed: {type(e).__name__}: {e}")
        traceback.print_exc()
        return

    ok("module imported")

    expected = ["AntapuraEngine", "EnginePolicy", "Event"]
    missing = [n for n in expected if not hasattr(module, n)]
    present = [n for n in expected if hasattr(module, n)]
    check(not missing, f"core classes present: {present}",
          f"missing core classes: {missing}")
    if missing:
        return

    try:
        module.EnginePolicy()
        ok("EnginePolicy instantiates with defaults")
    except Exception as e:
        fail(f"EnginePolicy construction failed: {type(e).__name__}: {e}")
        return

    try:
        module.Event(
            event_type="authority_challenged",
            scene_id="smoke_test_scene_001",
            trigger_intensity=0.7,
            salience=0.8,
        )
        ok("Event constructs with standard fields")
    except TypeError as e:
        info(f"Event constructor requires different fields: {e}")
    except Exception as e:
        fail(f"Event construction failed: {type(e).__name__}: {e}")


# --- phase 3 ----------------------------------------------------------------

def _extract_states_block(state_data: dict) -> dict:
    """
    Return the dict that maps character IDs to their state blocks.

    Handles three shapes:
      A. {"characters": {cid: {...}}}
      B. {"states": {cid: {...}}}
      C. {cid: {...}} — top-level IS the container
    Metadata fields whose values are non-dicts are filtered out.
    """
    for key in ("characters", "states", "character_states"):
        block = state_data.get(key)
        if isinstance(block, dict):
            return block
    # Fallback: top level is the container; skip non-dict values
    return {k: v for k, v in state_data.items() if isinstance(v, dict)}


def phase_3_kama_engine():
    section("PHASE 3 — KAMA ENGINE")

    candidates = ["v18_9_compile_kama_engine.py"]
    search_roots = [ROOT, REPO, REPO / "V18_9_KamaEngine"]
    engine_path = find_engine(candidates, search_roots)
    if not engine_path:
        skip("kama engine not found in searched paths")
        return

    info(f"engine found: {engine_path}")
    engine_dir = engine_path.parent

    inputs = {
        "MASTER_KINK_REGISTRY.json": find_file(
            "MASTER_KINK_REGISTRY.json", [ROOT, REPO]),
        "KINK_RELATION_GRAPH.json": find_file(
            "KINK_RELATION_GRAPH.json", [ROOT, REPO]),
        "KAMA_CHARACTER_STATE.json": find_file(
            "KAMA_CHARACTER_STATE.json", [ROOT, REPO]),
    }

    for name, path in inputs.items():
        if path:
            try:
                rel = path.relative_to(REPO)
            except ValueError:
                rel = path
            info(f"{name} -> {rel}")
        else:
            info(f"{name} not found anywhere in repo")

    if not inputs["MASTER_KINK_REGISTRY.json"]:
        fail("MASTER_KINK_REGISTRY.json not found anywhere")
        return
    if not inputs["KAMA_CHARACTER_STATE.json"]:
        fail("KAMA_CHARACTER_STATE.json not found anywhere")
        return

    if not inputs["KINK_RELATION_GRAPH.json"]:
        info("KINK_RELATION_GRAPH.json missing — will use empty graph")

    staged: list[Path] = []
    try:
        for name, src in inputs.items():
            if not src:
                continue
            dst = engine_dir / name
            if not dst.exists():
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
                staged.append(dst)

        with chdir(engine_dir):
            try:
                module = import_module_from_path(engine_path, "kama_engine")
            except Exception as e:
                fail(f"import failed: {type(e).__name__}: {e}")
                traceback.print_exc()
                return

            ok("module imported")

            expected = ["KamaEngine", "KinkDefinition", "KinkRelationGraph",
                        "CharacterKamaState", "KinkState", "Preference", "Consent"]
            missing_cls = [n for n in expected if not hasattr(module, n)]
            present = [n for n in expected if hasattr(module, n)]
            check(not missing_cls, f"classes present: {len(present)}",
                  f"missing classes: {missing_cls}")
            if missing_cls:
                return

            reg_data = json.loads(
                Path("MASTER_KINK_REGISTRY.json").read_text(encoding="utf-8"))
            registry = {
                kid: module.KinkDefinition(
                    id=d["id"], name=d["name"],
                    taxonomy=d["taxonomy"], progression=d["progression"])
                for kid, d in reg_data.get("KINKS", {}).items()
            }
            ok(f"loaded {len(registry)} kink definitions")

            graph_path = Path("KINK_RELATION_GRAPH.json")
            if graph_path.exists():
                graph_data = json.loads(graph_path.read_text(encoding="utf-8"))
                info("using provided KINK_RELATION_GRAPH.json")
            else:
                graph_data = {"similar": {}, "related": {}, "secondary": {}}
                info("using empty derived graph")

            graph = module.KinkRelationGraph(
                similar=graph_data.get("similar", {}),
                related=graph_data.get("related", {}),
                secondary=graph_data.get("secondary", {}),
            )

            # --- KAMA_CHARACTER_STATE loading (shape-robust) ---
            raw_states = json.loads(
                Path("KAMA_CHARACTER_STATE.json").read_text(encoding="utf-8"))

            # Log the top-level keys for diagnostics
            if isinstance(raw_states, dict):
                top_keys = list(raw_states.keys())[:6]
                info(f"KAMA_CHARACTER_STATE top-level keys: {top_keys}")

            states_block = _extract_states_block(raw_states)
            info(f"detected {len(states_block)} character blocks")

            states = {}
            for cid, block in states_block.items():
                if not isinstance(block, dict):
                    continue
                kinks_data = block.get("kinks", {})
                if not isinstance(kinks_data, dict):
                    continue
                kinks = {}
                for kid, s in kinks_data.items():
                    if not isinstance(s, dict):
                        continue
                    try:
                        kinks[kid] = module.KinkState(
                            knowledge=s.get("knowledge", 0.0),
                            training=s.get("training", 0.0),
                            repetition=s.get("repetition", 0),
                            mastery=s.get("mastery", 0.0),
                            preference=module.Preference(
                                s.get("preference", "neutral")),
                            limits=s.get("limits", {"soft": [], "hard": []}),
                            consent=module.Consent(
                                s.get("consent", "orange")),
                            locked=s.get("locked", True),
                        )
                    except Exception as e:
                        info(f"skipping kink {kid} for {cid}: {e}")
                states[cid] = module.CharacterKamaState(
                    character_id=cid, kinks=kinks)

            ok(f"parsed states for {len(states)} characters")

            engine = module.KamaEngine(registry, graph, states)
            ok("engine instantiated")

            # Apply a probe event to a known character if available
            target = None
            for cid in ("roxana", "maha_deva", "kumari_rati", "anisa"):
                if cid in states and states[cid].kinks:
                    target = cid
                    break

            if target:
                k = next(iter(states[target].kinks.keys()))
                before = states[target].kinks[k].knowledge
                result = engine.apply_event(target, {
                    "kink_id": k,
                    "knowledge_delta": 0.1,
                    "repetition_delta": 1,
                })
                after = states[target].kinks[k].knowledge
                check("error" not in result,
                      f"event applied cleanly ({target}, kink={k})",
                      f"event error: {result.get('error')}")
                info(f"knowledge: {before:.3f} -> {after:.3f}")
            else:
                skip("no character with kink state available for event probe")
    finally:
        for p in staged:
            if p.exists():
                p.unlink()


# --- phase 4 ----------------------------------------------------------------

def phase_4_runtime_engine():
    section("PHASE 4 — RUNTIME ENGINE")

    engine_file = ROOT / "runtime" / "ANTAHPURA_RUNTIME_ENGINE_V20.json"
    if not engine_file.exists():
        skip("runtime engine JSON not found")
        return
    try:
        data = json.loads(engine_file.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"parse runtime engine: {e}")
        return
    ok("runtime engine JSON parses")
    if isinstance(data, dict):
        info(f"top-level keys: {list(data.keys())[:8]}")

    scene_file = ROOT / "runtime" / "current_scene.json"
    if scene_file.exists():
        try:
            scene = json.loads(scene_file.read_text(encoding="utf-8"))
            ok("current_scene parses")
            if isinstance(scene, dict):
                info(f"scene keys: {list(scene.keys())[:8]}")
        except Exception as e:
            fail(f"current_scene parse: {e}")


# --- main -------------------------------------------------------------------

def main():
    print()
    print("+" + "-" * 64 + "+")
    print("|" + " ANTAHPURA — SMOKE TEST v4 ".center(64) + "|")
    print("+" + "-" * 64 + "+")

    phase_1_data_layer()
    phase_2_emotional_engine()
    phase_3_kama_engine()
    phase_4_runtime_engine()

    section("SUMMARY")
    print(f"  Pass: {_results['pass']}")
    print(f"  Fail: {_results['fail']}")
    print(f"  Skip: {_results['skip']}")
    print()
    if _results["fail"] == 0:
        print("  All executed tests passed.")
        sys.exit(0)
    print(f"  {_results['fail']} test(s) failed.")
    sys.exit(1)


if __name__ == "__main__":
    main()