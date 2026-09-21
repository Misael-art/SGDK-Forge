from __future__ import annotations

import importlib.util
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("measure_capture_overhead", ROOT / "tests/measure_capture_overhead.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_overhead_reader_recovers_hcad_from_session(tmp_path: Path) -> None:
    session = tmp_path / "session"
    sram = session / "userdata" / "blastem" / "rom" / "save.sram"
    sram.parent.mkdir(parents=True)
    raw = bytearray(0x640 + 40)
    fields = [100, 100, 0, 100, 0, 1, 100, 0, 60, 60, 60, 0, 1, 10, 60, 0]
    raw[0x640:0x644] = b"HCAD"
    struct.pack_into(">HH", raw, 0x644, 1, 40)
    struct.pack_into(">16H", raw, 0x648, *fields)
    sram.write_bytes(raw)
    report, source = MODULE.cadence_from_session(session)
    assert source == "save.sram"
    assert report and report["cadence_invariant"] is True
    assert report["fight_video_frames"] == 60


def test_overhead_cadence_compare_is_not_fps_claim() -> None:
    baseline = {"video_frames": 100, "logic_ticks": 100, "presentation_commits": 100,
                "zero_tick_frames": 0, "fight_video_frames": 60, "fight_logic_ticks": 60,
                "fight_presentation_commits": 60, "fight_zero_tick_frames": 0}
    captured = dict(baseline)
    result = MODULE.compare_cadence(baseline, captured)
    assert result["status"] == "equal"
    assert "not perceptual motion" in result["claim_limit"]


def test_overhead_pair_requires_persisted_fight_telemetry() -> None:
    valid = {"cadence_invariant": True, "fight_cadence_invariant": True,
             "zero_tick_frames": 0, "fight_video_frames": 1}
    no_fight = dict(valid, fight_video_frames=0)
    assert MODULE.cadence_is_comparable(valid) is True
    assert MODULE.cadence_is_comparable(no_fight) is False


def test_capture_harness_has_runtime_ready_overhead_route() -> None:
    source = (ROOT / "tests/capture_visual_ko.py").read_text(encoding="utf-8")
    assert "HDBG scene=10 is the runtime readiness contract" in source
    assert "if '--probe-short' in sys.argv" in source
    assert "Fight HUD did not appear; do not label zero yellow as KO" in source
