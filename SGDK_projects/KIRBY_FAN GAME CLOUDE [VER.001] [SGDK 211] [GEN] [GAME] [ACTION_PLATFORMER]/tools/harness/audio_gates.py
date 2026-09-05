#!/usr/bin/env python3
"""Static audio-contract gates (A1-A3, A6, A7 from doc/SOUNDMAP.md section 7.1).

These are the audio gates that can be checked WITHOUT running the ROM: they read
the source tree and res/resources.res. The runtime audio gates (A4 peak DMA per
frame, A5 driver missed_frames) are NOT here because the VLAB probe does not yet
export a DMA byte counter or the XGM2 driver metrics. That is tracked as the
`probe_nao_exporta_sh_prioridade_dma` blocker in doc/10-memory-bank.md.

Do not add a fake runtime gate here. A gate that cannot fail is worse than a
missing gate, because it reads as coverage.

Usage:
    python3 tools/harness/audio_gates.py [--project-root DIR] [--json OUT] [--quiet]

Exit code is non-zero if any hard gate fails.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# doc/SOUNDMAP.md section 4: 384 KB of PCM samples inside the 4 MB no-mapper ROM.
PCM_ROM_BUDGET_BYTES = 384 * 1024

# The single module allowed to touch FM/PSG/PCM channels
# (ARCHITECTURE.md section 6.1, SOUNDMAP.md section 2).
ROUTER_RELATIVE = Path("src/audio/xgm_router.c")

FORBIDDEN = [
    (
        "A1", "no_direct_psg_calls",
        re.compile(r"\bPSG_\w+\s*\("),
        "direct PSG_* call while XGM2 owns the PSG",
    ),
    (
        "A2", "no_direct_ym2612_writes",
        re.compile(r"\bYM2612_(write|writeReg|writeSafe)\w*\s*\("),
        "direct YM2612 register write",
    ),
    (
        "A3", "no_sfx_on_pcm_channel_1",
        re.compile(r"SOUND_PCM_CH1\b(?!_MSK)"),
        "use of SOUND_PCM_CH1, which is reserved for XGM2 music",
    ),
]


@dataclass
class Result:
    gate: str
    gate_id: str
    status: str          # pass | fail | warn
    hard: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)


class Runner:
    def __init__(self) -> None:
        self.results: list[Result] = []

    def check(self, gate_id: str, gate: str, ok: bool, hard: bool,
              message: str, **details: Any) -> None:
        self.results.append(
            Result(gate, gate_id, "pass" if ok else "fail", hard, message, details)
        )

    def warn(self, gate_id: str, gate: str, message: str, **details: Any) -> None:
        self.results.append(Result(gate, gate_id, "warn", False, message, details))

    @property
    def failed(self) -> list[Result]:
        return [r for r in self.results if r.status == "fail" and r.hard]

    @property
    def warned(self) -> list[Result]:
        return [r for r in self.results if r.status == "warn"]


def c_sources(src_root: Path) -> list[Path]:
    if not src_root.is_dir():
        return []
    return sorted(
        p for p in src_root.rglob("*")
        if p.suffix in {".c", ".h", ".s"} and p.is_file()
    )


def strip_comments(text: str) -> str:
    """Crude comment stripper so a doc comment naming PSG_ does not trip a gate."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", " ", text)
    return text


def load_baseline(project_root: Path) -> set[tuple[str, str]]:
    """Known inherited template violations, as (gate_id, relative_path) pairs.

    A baseline is not an exemption. It exists so the gate can still fail on a
    NEW violation while the pre-existing template debt stays visible in the
    report. It must reach zero when src/audio/xgm_router.c is written.
    """
    path = Path(__file__).parent / "audio_gate_baseline.json"
    if not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        (e["gate"], e["file"])
        for e in data.get("entries", [])
        if "gate" in e and "file" in e
    }


def baseline_expiry(project_root: Path) -> str:
    """Read the expiry condition from the baseline instead of restating it.

    The message used to hardcode "when xgm_router.c is written". That router now
    exists and the debt did NOT go away, because the violations live in template
    scenes that are still wired into app.c. A hardcoded condition that has been
    met while the debt persists is worse than no condition: it reads as done.
    """
    path = Path(__file__).parent / "audio_gate_baseline.json"
    if not path.is_file():
        return "(no baseline file)"
    try:
        return json.loads(path.read_text(encoding="utf-8")).get(
            "expiry_condition", "(none recorded)")
    except (json.JSONDecodeError, OSError):
        return "(baseline unreadable)"


def gate_channel_ownership(runner: Runner, project_root: Path) -> None:
    src_root = project_root / "src"
    sources = c_sources(src_root)
    router = project_root / ROUTER_RELATIVE

    if not sources:
        for gate_id, gate, _, _ in FORBIDDEN:
            runner.warn(
                gate_id, gate,
                "No C sources found under src/, so this gate passed vacuously.",
                src_root=str(src_root),
            )
        return

    router_exists = router.is_file()

    baseline = load_baseline(project_root)

    for gate_id, gate, pattern, what in FORBIDDEN:
        hits: list[dict[str, Any]] = []
        baselined: list[dict[str, Any]] = []
        for path in sources:
            # The router is the designated owner and is exempt by design.
            if router_exists and path.resolve() == router.resolve():
                continue
            rel = str(path.relative_to(project_root))
            body = strip_comments(
                path.read_text(encoding="utf-8", errors="replace")
            )
            for match in pattern.finditer(body):
                line = body.count("\n", 0, match.start()) + 1
                hit = {"file": rel, "line": line, "match": match.group(0)}
                # Inherited template debt is tracked, not hidden: it is reported
                # separately so a NEW violation in game code still fails.
                if (gate_id, rel) in baseline:
                    baselined.append(hit)
                else:
                    hits.append(hit)

        msg = (
            f"{len(hits)} NEW occurrence(s) of {what} outside "
            f"{ROUTER_RELATIVE.as_posix()}"
        )
        if baselined:
            msg += f"; {len(baselined)} baselined template occurrence(s) still owed"
        runner.check(
            gate_id, gate, not hits, True, msg,
            hits=hits[:40], hit_count=len(hits),
            baselined=baselined[:40], baselined_count=len(baselined),
            router_present=router_exists,
        )
        if baselined:
            runner.warn(
                gate_id + "-debt", gate + "_template_debt",
                f"{len(baselined)} inherited template violation(s) remain in "
                f"{sorted({h['file'] for h in baselined})}. Expiry condition "
                f"(read from the baseline file, not hardcoded here): "
                f"{baseline_expiry(project_root)}",
                files=sorted({h["file"] for h in baselined}),
                count=len(baselined),
            )

    if not router_exists:
        runner.warn(
            "A0", "audio_router_present",
            f"{ROUTER_RELATIVE.as_posix()} does not exist yet, so the "
            f"single-owner rule has no owner to exempt. The gates above are "
            f"checking a codebase with no audio code in it.",
            expected_path=str(router),
        )


def gate_res_declarations(runner: Runner, project_root: Path) -> None:
    res = project_root / "res" / "resources.res"
    if not res.is_file():
        runner.warn(
            "A7", "music_declared_as_xgm2",
            "res/resources.res is absent; nothing to parse.",
            path=str(res),
        )
        return

    text = res.read_text(encoding="utf-8", errors="replace")
    music_lines: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(("#", "//")):
            continue
        head = line.split()[0].upper()
        if head in {"XGM", "XGM2", "VGM", "WAV", "PCM"}:
            entry = {"line": n, "kind": head, "text": line}
            music_lines.append(entry)
            # doc/SOUNDMAP.md section 1.1 locks the driver to XGM2. A stray
            # XGM (v1) or raw VGM declaration would silently change drivers.
            if head in {"XGM", "VGM"}:
                bad.append(entry)

    if not music_lines:
        runner.warn(
            "A7", "music_declared_as_xgm2",
            "No audio resources declared in res/resources.res yet.",
            path=str(res),
        )
        return

    runner.check(
        "A7", "music_declared_as_xgm2", not bad, True,
        f"{len(bad)} audio resource(s) declared with a driver other than XGM2; "
        f"doc/SOUNDMAP.md section 1.1 locks the project to XGM2",
        offending=bad, audio_resources=music_lines,
    )


def gate_pcm_rom_budget(runner: Runner, project_root: Path) -> None:
    sfx_dirs = [project_root / "res" / "sfx", project_root / "res" / "audio"]
    samples: list[dict[str, Any]] = []
    for d in sfx_dirs:
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*")):
            if p.suffix.lower() in {".wav", ".pcm"} and p.is_file():
                samples.append({
                    "file": str(p.relative_to(project_root)),
                    "bytes": p.stat().st_size,
                })
    total = sum(s["bytes"] for s in samples)

    if not samples:
        runner.warn(
            "A6", "pcm_rom_budget",
            "No PCM samples on disk yet, so the 384 KB budget passed vacuously.",
            budget_bytes=PCM_ROM_BUDGET_BYTES,
        )
        return

    runner.check(
        "A6", "pcm_rom_budget", total <= PCM_ROM_BUDGET_BYTES, True,
        f"PCM samples total {total} bytes "
        f"({total / 1024:.1f} KB), budget {PCM_ROM_BUDGET_BYTES // 1024} KB",
        total_bytes=total, budget_bytes=PCM_ROM_BUDGET_BYTES,
        sample_count=len(samples), samples=samples[:60],
    )


AUDIO_RAW_FLOAT32 = True     # BlastEm writes 32-bit float @48k stereo.
                             # Verified in blastem.log: "Initialized audio at
                             # frequency 48000 ... 32-bit float format".
                             # Reading it as int16 produced garbage dB figures
                             # once already -- do not assume, check the log.
AUDIO_SILENCE_FLOOR_RMS = 0.015   # measured with music disabled: RMS 0.0113
AUDIO_MAX_PEAK = 0.85             # leave headroom so PCM cannot clip the mix


def gate_audio_output(runner: Runner, session: Path | None) -> None:
    """Prove the music is actually AUDIBLE, not merely that it compiled.

    Requires a capture taken with --audio-driver disk. Without one this SKIPS,
    because silence and 'no recording' are different claims.
    """
    if session is None:
        return
    raw_path = session / "audio.raw"
    if not raw_path.is_file():
        runner.warn(
            "A8", "music_audible",
            "no audio.raw in this bundle; capture with --audio-driver disk to "
            "prove the music is audible. Compiling is not playing.",
            session=str(session),
        )
        return

    import struct
    import math

    raw = raw_path.read_bytes()
    count = len(raw) // 4
    values = struct.unpack(f"<{count}f", raw[:count * 4])
    left = values[0::2]
    if not left:
        runner.check("A8", "music_audible", False, True,
                     "audio.raw is empty", bytes=len(raw))
        return

    peak = max(abs(x) for x in left)
    rms = math.sqrt(sum(x * x for x in left) / len(left))

    runner.check(
        "A8", "music_audible", rms > AUDIO_SILENCE_FLOOR_RMS, True,
        f"RMS {rms:.4f} vs measured silence floor {AUDIO_SILENCE_FLOOR_RMS} "
        f"(peak {peak:.4f}); seconds={len(left)/48000:.1f}",
        rms=round(rms, 5), peak=round(peak, 5),
        seconds=round(len(left) / 48000.0, 1),
        note="Proves sound is COMING OUT. Says nothing about whether it is "
             "good music -- that is a human checklist, doc/SOUNDMAP.md 7.2.",
    )
    runner.check(
        "A9", "dac_headroom", peak < AUDIO_MAX_PEAK, True,
        f"peak {peak:.4f}, ceiling {AUDIO_MAX_PEAK} so simultaneous PCM "
        f"cannot clip the mix",
        peak=round(peak, 5), ceiling=AUDIO_MAX_PEAK,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root", type=Path, default=None)
    ap.add_argument("--json", dest="json_path", type=Path, default=None)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--session", type=Path, default=None,
                    help="evidence session dir; enables the audio-output gates")
    args = ap.parse_args()

    project_root = (args.project_root or Path(__file__).resolve().parents[2]).resolve()

    runner = Runner()
    gate_channel_ownership(runner, project_root)
    gate_res_declarations(runner, project_root)
    gate_pcm_rom_budget(runner, project_root)
    gate_audio_output(runner, args.session)

    if not args.quiet:
        print("=" * 72)
        print(f"AUDIO CONTRACT GATES  {project_root}")
        print("=" * 72)
        for r in runner.results:
            tag = {"pass": "PASS", "fail": "FAIL", "warn": "WARN"}[r.status]
            kind = "hard" if r.hard else "soft"
            print(f"[{tag}] ({kind}) {r.gate_id} {r.gate}: {r.message}")
        print("-" * 72)
        print(f"hard failures: {len(runner.failed)}   warnings: {len(runner.warned)}")
        print(f"VERDICT: {'FAIL' if runner.failed else 'PASS'}")
        print("=" * 72)
        print("NOTE: runtime audio gates A4 (peak DMA/frame) and A5 (driver")
        print("missed_frames) are absent by design; the probe does not export")
        print("them yet. See doc/SOUNDMAP.md section 7.1.")

    report = {
        "schema_version": "1.0.0",
        "tool_name": "audio_gates",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_root),
        "status": "fail" if runner.failed else "pass",
        "hard_failures": len(runner.failed),
        "warnings": len(runner.warned),
        "absent_runtime_gates": {
            "A4_peak_dma_per_frame": "probe does not export a DMA byte counter",
            "A5_driver_missed_frames": "probe does not export XGM2 driver metrics",
        },
        "gates": [
            {
                "id": r.gate_id, "gate": r.gate, "status": r.status,
                "hard": r.hard, "message": r.message, "details": r.details,
            }
            for r in runner.results
        ],
    }
    out = args.json_path or (project_root / "out" / "logs" / "audio_gate_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"audio_gates_status={report['status']} report={out}")

    return 1 if runner.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
