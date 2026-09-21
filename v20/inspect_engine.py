#!/usr/bin/env python3
"""
inspect_engine.py — introspect the emotional engine's public API.

Prints every public class and function with signatures and dataclass fields.
"""

import importlib.util
import inspect
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__",
             ".venv", "venv", ".mypy_cache", ".pytest_cache", "runs",
             "archive"}


def find_engine():
    candidates = ["antapura_v31_rc2.py", "antapura_emotional_engine_v3_2.py"]
    for root in (ROOT, REPO, REPO / "scripts"):
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn in candidates:
                    return Path(dirpath) / fn
    return None


def import_module(path, name):
    if name in sys.modules:
        del sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    print("=" * 66)
    print("EMOTIONAL ENGINE — API INSPECTION")
    print("=" * 66)

    engine_path = find_engine()
    if not engine_path:
        print("No emotional engine found.")
        sys.exit(1)

    print(f"Engine: {engine_path}")
    print()

    try:
        module = import_module(engine_path, "antapura_emotional_engine")
    except Exception as e:
        print(f"Import failed: {type(e).__name__}: {e}")
        sys.exit(2)

    public = [n for n in dir(module) if not n.startswith("_")]
    classes = [n for n in public if inspect.isclass(getattr(module, n))]
    functions = [n for n in public if inspect.isfunction(getattr(module, n))]

    print(f"--- Classes ({len(classes)}) ---")
    for name in sorted(classes):
        cls = getattr(module, name)
        print(f"  {name}")
        if hasattr(cls, "__dataclass_fields__"):
            print("    @dataclass, fields:")
            for fname, ffield in cls.__dataclass_fields__.items():
                tn = getattr(ffield.type, "__name__", str(ffield.type))
                print(f"      {fname}: {tn}")
        try:
            sig = inspect.signature(cls.__init__)
            print(f"    __init__{sig}")
        except (ValueError, TypeError):
            pass
        methods = [m for m in dir(cls) if not m.startswith("_")]
        if methods:
            print(f"    methods: {', '.join(sorted(methods)[:10])}")
        print()

    print(f"--- Functions ({len(functions)}) ---")
    for name in sorted(functions):
        try:
            sig = inspect.signature(getattr(module, name))
            print(f"  {name}{sig}")
        except (ValueError, TypeError):
            print(f"  {name}(?)")

    print()
    print("=" * 66)


if __name__ == "__main__":
    main()