#!/usr/bin/env python3
"""Contrato barato do runner P11; a reprodução real é executada separadamente."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    runner = ROOT / "tests" / "reproduce_p11_isolated.py"
    docs = [
        ROOT / "doc" / "engine_quickstart.md",
        ROOT / "doc" / "engine_extension_guide.md",
        ROOT / "doc" / "controls_and_options.md",
        ROOT / "doc" / "engine" / "release_inventory.json",
    ]
    failures = []
    if not runner.exists():
        failures.append("runner P11 ausente")
    for doc in docs:
        if not doc.exists():
            failures.append(f"manual ausente: {doc.name}")
    text = runner.read_text(encoding="utf-8", errors="replace") if runner.exists() else ""
    for token in ("StageDefinition", "stage_probe", "claim_limit", "build_sgdk_wine_bridge.sh", "release_inventory.json"):
        if token not in text:
            failures.append(f"runner P11 sem token {token}")
    if failures:
        print("FAIL:")
        for item in failures:
            print("  -", item)
        return 1
    print("PASS: manuais P11 e reprodução isolada possuem contrato mínimo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
