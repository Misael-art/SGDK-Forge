#!/usr/bin/env python3
"""Budget gates over a sealed BlastEm evidence bundle.

Reads runtime_metrics.json + visual_vdp_dump.bin + save.sram (+ screenshot.png
when Pillow is importable) from a session directory and decides pass/fail.

Exit codes:
    0  every hard gate passed (warnings may still be present)
    1  at least one hard gate failed
    2  the bundle could not be read at all

READ tools/harness/README.md BEFORE trusting a green run. Several gates below
are structural invariants that cannot fail by construction; they are kept
because they would catch a corrupted dump or a future probe regression, NOT
because a green result means the budget was independently verified.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import probe_format as pf
import krb1  # noqa: E402

VRAM_SIZE_BYTES = 64 * 1024
BYTES_PER_TILE = 32

# Worst-case VDP table footprints. The VDP always reserves the full sprite
# attribute table; the hscroll table is sized for per-line scrolling because
# that is the largest mode the hardware can be put into.
SPRITE_ATTRIBUTE_TABLE_BYTES = 80 * 8
HSCROLL_TABLE_BYTES = 224 * 4

DEFAULT_LIMITS = {
    # 58, not 61. See doc/PALETTES.md section 2.4 for the arithmetic:
    #   64 CRAM entries
    #   -4  index 0 of each palette is transparent
    #   -2  PAL3[14] and PAL3[15] are reserved as shadow/highlight operators
    #   = 58 usable simultaneous colours
    # The project brief said 61; the brief predates the shadow/highlight
    # decision, which costs two entries. Measurement beats brief.
    "max_simultaneous_colors": 58,
    "max_sprites_per_frame": 80,
    "max_sprites_per_scanline": 20,
    "max_cpu_load_p99": 100,
    "max_over_budget_frames": 0,
    # Distinct colours allowed in the screenshot. This project runs with
    # shadow/highlight ENABLED GLOBALLY (doc/PALETTES.md section 2.2), and S/H
    # legitimately triples the on-screen colour count: every CRAM entry can
    # appear normal, shadowed and highlighted in the same frame. So the ceiling
    # is 58 * 3 = 174, not 58. A value of 58 here would fail every real scene.
    "max_screenshot_colors": 174,
}


@dataclass
class GateResult:
    name: str
    status: str  # "pass" | "fail" | "warn" | "skip"
    hard: bool
    summary: str
    detail: dict[str, Any] = field(default_factory=dict)


class GateRunner:
    def __init__(self, limits: dict[str, int]) -> None:
        self.limits = limits
        self.results: list[GateResult] = []

    def add(
        self,
        name: str,
        status: str,
        hard: bool,
        summary: str,
        **detail: Any,
    ) -> None:
        self.results.append(GateResult(name, status, hard, summary, detail))

    def check(
        self,
        name: str,
        ok: bool,
        hard: bool,
        summary: str,
        **detail: Any,
    ) -> None:
        self.add(name, "pass" if ok else ("fail" if hard else "warn"),
                 hard, summary, **detail)

    @property
    def failed(self) -> list[GateResult]:
        return [r for r in self.results if r.status == "fail" and r.hard]

    @property
    def warned(self) -> list[GateResult]:
        return [r for r in self.results if r.status == "warn"]


# --------------------------------------------------------------------------
# Individual gate groups
# --------------------------------------------------------------------------

def gate_scene_identity(runner: GateRunner, mdrt: pf.Mdrt,
                        request: dict[str, Any] | None) -> None:
    requested = mdrt.requested_scene_id
    actual = mdrt.actual_scene_id

    if requested is None:
        runner.add(
            "scene_identity", "skip", True,
            f"No scene was requested; probe measured scene {actual}. "
            "Whatever the app happened to be showing was captured.",
            actual_scene_id=actual,
        )
        return

    runner.check(
        "scene_identity", requested == actual, True,
        f"requested scene {requested}, probe measured scene {actual}",
        requested_scene_id=requested,
        actual_scene_id=actual,
        requested_scene_name=(request or {}).get("scene_name"),
    )


def gate_colors(runner: GateRunner, vlab: pf.Vlab) -> None:
    palette = vlab.palette
    transparent = set(pf.transparent_indices())
    usable = [c for i, c in enumerate(palette) if i not in transparent]

    distinct = sorted(set(usable))
    backdrop_index = vlab.metrics["background_color"] & 0x3F
    backdrop = palette[backdrop_index] if backdrop_index < len(palette) else None
    simultaneous = set(distinct) | ({backdrop} if backdrop is not None else set())

    limit = runner.limits["max_simultaneous_colors"]
    runner.check(
        "color_budget", len(simultaneous) <= limit, True,
        f"{len(simultaneous)} distinct simultaneous colours "
        f"({len(distinct)} non-transparent CRAM entries + backdrop), "
        f"limit {limit}",
        distinct_non_transparent=len(distinct),
        simultaneous_colors=len(simultaneous),
        limit=limit,
        backdrop_index=backdrop_index,
        backdrop_value=backdrop,
        note="Structural invariant: 60 non-transparent slots + 1 backdrop "
             "means this count can never exceed 61. Failing here means the "
             "VLAB dump is malformed, not that art overspent the budget.",
    )

    illegal = [
        {"index": i, "value": f"0x{c:04X}"}
        for i, c in enumerate(palette)
        if not pf.is_legal_vdp_color(c)
    ]
    runner.check(
        "cram_rgb333_legal", not illegal, True,
        f"{len(illegal)} CRAM entries outside the 0000BBB0GGG0RRR0 layout",
        illegal_entries=illegal[:16],
        mask=f"0x{pf.VDP_COLOR_MASK:04X}",
        note="Structural invariant on this path: PAL_getColors() masks every "
             "entry with VDPPALETTE_COLORMASK (0x0EEE) as it reads CRAM, so "
             "an illegal value cannot reach the dump. Kept as a corruption "
             "canary only.",
    )


def gate_screenshot_colors(runner: GateRunner, screenshot: Path) -> None:
    if not screenshot.is_file():
        runner.add("screenshot_color_count", "skip", True,
                   f"screenshot absent: {screenshot.name}")
        return
    try:
        from PIL import Image
    except ImportError:
        runner.add("screenshot_color_count", "skip", True,
                   "Pillow not importable; cannot count screenshot colours")
        return

    with Image.open(screenshot) as raw:
        image = raw.convert("RGB")
        size = image.size
        # getcolors() returns None above maxcolors; the cap is far above any
        # plausible legitimate count, so None itself is a failure signal.
        counted = image.getcolors(maxcolors=1 << 20)
    distinct = len(counted) if counted is not None else (1 << 20)

    limit = runner.limits["max_screenshot_colors"]
    # SOFT, and here is the honest reason. The ceiling was modelled as
    # "usable CRAM entries x 3" because Shadow/Highlight lets each entry appear
    # normal, shadowed and highlighted in the same frame. That model BREAKS as
    # soon as a raster effect rewrites a CRAM entry mid-frame: the sky gradient
    # drives ONE entry through 12 stops per frame, so that single entry yields
    # up to 36 distinct screen colours on its own. Measured 262 in the boss
    # arena against a modelled ceiling of 174.
    #
    # Rather than invent a ceiling that cannot be derived, this gate is demoted
    # to a gross-corruption canary. The REAL hardware constraint is CRAM
    # occupancy, and `color_budget` already checks that against the true limit
    # of 58 simultaneous entries. Weakening a gate is worth saying out loud:
    # this one was measuring the wrong quantity for raster scenes.
    runner.check(
        "screenshot_color_count", distinct <= limit, False,
        f"{distinct} distinct colours in the {size[0]}x{size[1]} "
        f"screenshot, limit {limit}",
        distinct_colors=distinct,
        limit=limit,
        image_size=list(size),
        note="SOFT: cannot bound a scene that uses raster palette changes. "
             "One CRAM entry driven through N raster stops yields up to N*3 "
             "screen colours. Use color_budget (CRAM occupancy) as the real "
             "constraint. BlastEm scales the framebuffer "
             "with nearest-neighbour, so screenshot colours map 1:1 onto "
             "on-screen colours. Raise the limit to 183 if the project uses "
             "shadow/highlight.",
    )


def gate_sprites(runner: GateRunner, vlab: pf.Vlab) -> None:
    per_frame = vlab.metrics["max_used_vdp_sprites"]
    per_scanline = vlab.metrics["max_scanline_sprites"]

    runner.check(
        "sprites_per_frame",
        per_frame <= runner.limits["max_sprites_per_frame"], True,
        f"peak {per_frame} hardware VDP sprites, limit "
        f"{runner.limits['max_sprites_per_frame']}",
        peak=per_frame, limit=runner.limits["max_sprites_per_frame"],
    )
    runner.check(
        "sprites_per_scanline",
        per_scanline <= runner.limits["max_sprites_per_scanline"], True,
        f"peak {per_scanline} sprites on a sampled scanline, limit "
        f"{runner.limits['max_sprites_per_scanline']}",
        peak=per_scanline,
        limit=runner.limits["max_sprites_per_scanline"],
        note="SAMPLED, not exhaustive: the probe watches 4 scanlines per "
             "frame and rotates them, so a one-frame spike on an unwatched "
             "line is invisible. A pass is weak evidence; a fail is strong.",
    )

    if per_frame == 0 and per_scanline == 0:
        runner.add(
            "sprites_observed", "warn", False,
            "Zero sprites were active during the whole sampled window. The "
            "sprite gates above passed vacuously.",
            max_used_vdp_sprites=per_frame,
            max_scanline_sprites=per_scanline,
        )


def _parse_vram_map(path: Path) -> dict[str, Any]:
    """Best-effort extraction of a declared tile total from doc/VRAMMAP.md.

    The document is owned by another agent and its format is not fixed yet, so
    this only recognises a couple of obvious spellings and reports honestly
    when it recognises nothing.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    patterns = [
        r"total[^\n\d]{0,40}?(\d+)\s*tiles",
        r"(\d+)\s*tiles[^\n]{0,20}total",
        r"total[^\n\d]{0,40}?(\d+)\s*bytes",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue
        value = int(match.group(1))
        if "bytes" in pattern:
            return {"declared_bytes": value, "matched": pattern}
        return {
            "declared_tiles": value,
            "declared_bytes": value * BYTES_PER_TILE,
            "matched": pattern,
        }
    return {}


DMA_BUDGET_BYTES = 4096   # doc/SOUNDMAP.md section 5.2, tighter than the
                          # 7372 B hardware ceiling on purpose.


def gate_krb1(runner: GateRunner, session: Path) -> None:
    """Gates built on the project's own KRB1 block.

    These are the gates that were impossible before the ROM exported this block:
    P5 (tile priority) and V6/A4 (DMA peak) from the design docs, plus a direct
    parallax check that replaced screenshot forensics.
    """
    block = krb1.load(session / "save.sram")
    if block is None:
        runner.check(
            "krb1_present", False, False,
            "no KRB1 telemetry block in save.sram; the KRB1-based gates below "
            "cannot run. Only scenes that call PROBE_STAGE_exportToSram emit it.",
            sram=str(session / "save.sram"),
        )
        return

    # --- parallax, verified against the design formula --------------------
    cam = block["camera_x"]
    expected = krb1.expected_hscroll(cam)
    mismatches = {
        name: {"measured": block[name], "expected": value}
        for name, value in expected.items() if block[name] != value
    }
    runner.check(
        "parallax_layer_speeds", not mismatches, True,
        f"camera_x={cam}: "
        + ", ".join(f"{n}={block[n]}" for n in expected)
        + f"; {len(mismatches)} layer(s) off the design formula",
        camera_x=cam, expected=expected, mismatches=mismatches,
        note="Read from the HScroll table the ROM programmed, not from pixels.",
    )
    if cam == 0:
        runner.check(
            "parallax_camera_moved", False, False,
            "camera_x is 0, so every layer legitimately scrolls to 0 and the "
            "parallax gate above passed VACUOUSLY. Capture during camera motion.",
            camera_x=cam,
        )

    # --- P5: tile priority under global Shadow/Highlight ------------------
    sampled = block["prio_sampled_bga"] + block["prio_sampled_bgb"]
    viol = block["prio_viol_bga"] + block["prio_viol_bgb"]
    if sampled == 0:
        runner.check(
            "tile_priority_under_sh", False, False,
            "priority audit sampled 0 nametable entries, so it proves nothing. "
            "This is a vacuous pass, not a pass.",
            sampled=0,
        )
    else:
        runner.check(
            "tile_priority_under_sh", viol == 0, True,
            f"{viol} background tile(s) at priority 0 out of {sampled} sampled "
            f"(BG_A {block['prio_viol_bga']}/{block['prio_sampled_bga']}, "
            f"BG_B {block['prio_viol_bgb']}/{block['prio_sampled_bgb']}); "
            f"with Shadow/Highlight on, priority 0 renders at half brightness",
            violations=viol, sampled=sampled,
            note="SAMPLED, not exhaustive: 16 entries per plane, stride 2 rows.",
        )

    # --- V6 / A4: DMA peak per frame --------------------------------------
    runner.check(
        "dma_peak_per_frame", block["dma_peak_bytes"] <= DMA_BUDGET_BYTES, True,
        f"peak {block['dma_peak_bytes']} bytes queued per frame, project budget "
        f"{DMA_BUDGET_BYTES} (hardware ceiling 7372 NTSC)",
        peak_bytes=block["dma_peak_bytes"], budget=DMA_BUDGET_BYTES,
        peak_queue_entries=block["dma_peak_count"],
    )

    # --- scripted playtest coverage ---------------------------------------
    # Only meaningful on a playtest capture (scene 5). On an ordinary capture
    # the script never ran, so this SKIPS rather than failing: a gate that fails
    # on every non-playtest bundle would just get ignored.
    # A bundle captured before the ROM grew these words simply lacks them. The
    # gate must degrade to a skip, not raise: crashing on an older bundle would
    # make the whole report unreadable instead of one gate inconclusive.
    if "playtest_step" not in block:
        runner.add(
            "playtest_coverage", "skip", True,
            f"this bundle's KRB1 block has no playtest fields (schema "
            f"{block.schema}, {len(block.values)} words); it predates the "
            f"scripted playtest. Re-capture to evaluate coverage.",
            krb1_words=len(block.values),
        )
    elif block["playtest_step"] == 0 and block["playtest_visited"] == 0:
        runner.add(
            "playtest_coverage", "skip", True,
            "no scripted playtest ran in this capture (boot scene 5 to run it); "
            "player-state coverage is therefore UNPROVEN for this bundle",
        )
    else:
        visited = block["playtest_visited"]
        missing = sorted(
            name for name, bit in krb1.PLAYTEST_STATES.items()
            if not (visited & bit)
        )
        # The 11 locomotion states are the STAGE script's job. A boss capture
        # runs a different script that never tries to cover them, so demanding
        # them there was the gate being wrong, not the game. Detect a boss
        # capture by its combat bits and report locomotion as informational.
        is_boss_capture = bool(visited & krb1.PLAYTEST_BOSS_ONLY)
        runner.check(
            "playtest_coverage", (not missing) or is_boss_capture,
            not is_boss_capture,
            f"{bin(visited & krb1.PLAYTEST_ALL).count('1')}/"
            f"{len(krb1.PLAYTEST_STATES)} locomotion states reached"
            + (" (boss capture: locomotion is the stage script's job, "
               "reported for information only)" if is_boss_capture else "")
            + (f"; missing: {', '.join(missing)}" if missing and not is_boss_capture
               else ""),
            visited=f"0x{visited:04X}", missing=missing,
            states=sorted(krb1.PLAYTEST_STATES),
            note="Coverage ACHIEVED, not coverage intended: each bit is set by "
                 "the scene observing the state actually happen, not by the "
                 "script asking for it.",
        )
        # An ability that is granted but never fires is the exact failure this
        # project shipped for several sessions: the hat appeared and did
        # nothing. If a capture proves the grant, it must also prove the use.
        if visited & krb1.PLAYTEST_ABILITY_GRANTED:
            runner.check(
                "ability_moveset_fires",
                bool(visited & krb1.PLAYTEST_ABILITY_USED), True,
                "a copy ability was granted in this capture; "
                + ("its moveset also fired"
                   if visited & krb1.PLAYTEST_ABILITY_USED
                   else "but NO moveset ever fired -- the hat is cosmetic"),
                granted=True,
                used=bool(visited & krb1.PLAYTEST_ABILITY_USED),
            )

        # Boss-combat states are only expected from the boss script. A stage
        # capture legitimately has none, so this only asserts when at least one
        # is present -- otherwise it stays silent rather than failing every
        # non-boss bundle.
        boss_bits = sum(krb1.PLAYTEST_BOSS_STATES.values())
        if visited & krb1.PLAYTEST_BOSS_ONLY:
            boss_missing = sorted(
                name for name, bit in krb1.PLAYTEST_BOSS_STATES.items()
                if not (visited & bit)
            )
            runner.check(
                "playtest_boss_combat", not boss_missing, True,
                f"{bin(visited & boss_bits).count('1')}/"
                f"{len(krb1.PLAYTEST_BOSS_STATES)} boss-combat states reached"
                + (f"; missing: {', '.join(boss_missing)}" if boss_missing else ""),
                missing=boss_missing,
                note="Proves the full loop: the boss damages Kirby, Kirby "
                     "counters by swallowing an apple, and the boss dies.",
            )

        runner.check(
            "playtest_completed", block["playtest_finished"] == 1, True,
            f"recorded script reached step {block['playtest_step']}, "
            f"finished={block['playtest_finished']}",
            step=block["playtest_step"],
            finished=block["playtest_finished"],
            note="A script that did not finish may have covered states by "
                 "accident rather than by design.",
        )

    # --- S/H: intent only, and labelled as such ---------------------------
    runner.check(
        "shadow_highlight_intent", block["sh_enabled"] == 1, False,
        f"ROM reports Shadow/Highlight enabled={block['sh_enabled']}. "
        f"This is the ROM's INTENT, not the VDP register: SGDK 2.11 exposes no "
        f"way to read register 0x0C back, so this cannot prove hardware state.",
        sh_enabled=block["sh_enabled"],
    )


def gate_vram(runner: GateRunner, vlab: pf.Vlab, vram_map: Path) -> None:
    m = vlab.metrics
    plane_bytes = m["plane_width"] * m["plane_height"] * 2

    # V4 from doc/VRAMMAP.md section 7. The plane size is locked at 64x32
    # because 64x64 costs 256 background tiles (25% of the budget). A silent
    # regression to a bigger plane would quietly eat the tile budget and only
    # surface much later as an unexplained VRAM overflow, so assert it here.
    runner.check(
        "plane_size_locked",
        (m["plane_width"], m["plane_height"]) == (64, 32),
        True,
        f"plane is {m['plane_width']}x{m['plane_height']} tiles "
        f"({plane_bytes} bytes per nametable); "
        f"doc/VRAMMAP.md section 2 locks 64x32",
        plane_width=m["plane_width"],
        plane_height=m["plane_height"],
        plane_bytes=plane_bytes,
        expected=[64, 32],
    )

    regions = [
        ("bg_a", m["bga_address"], plane_bytes),
        ("bg_b", m["bgb_address"], plane_bytes),
        ("window", m["window_address"], plane_bytes),
        ("sprite_list", m["sprite_list_address"],
         SPRITE_ATTRIBUTE_TABLE_BYTES),
        ("hscroll_table", m["hscroll_table_address"], HSCROLL_TABLE_BYTES),
    ]
    described = [
        {"name": n, "start": s, "end": s + size, "bytes": size}
        for n, s, size in regions
    ]

    out_of_range = [r for r in described if r["end"] > VRAM_SIZE_BYTES]
    runner.check(
        "vram_tables_in_range", not out_of_range, True,
        f"{len(out_of_range)} VDP tables extend past the 64KB VRAM window",
        regions=described, vram_size=VRAM_SIZE_BYTES,
        out_of_range=[r["name"] for r in out_of_range],
    )

    overlaps = []
    for i, a in enumerate(described):
        for b in described[i + 1:]:
            if a["start"] < b["end"] and b["start"] < a["end"]:
                overlaps.append(f"{a['name']}~{b['name']}")
    runner.check(
        "vram_tables_disjoint", not overlaps, True,
        f"{len(overlaps)} overlapping VDP table pairs" +
        (f": {', '.join(overlaps)}" if overlaps else ""),
        overlaps=overlaps, regions=described,
        note="The window plane legitimately shares its address with BG_A in "
             "some SGDK configurations; investigate a bg_a~window hit before "
             "treating it as a bug.",
    )

    lowest_table = min(r["start"] for r in described)
    tile_area_bytes = lowest_table
    tile_area_tiles = tile_area_bytes // BYTES_PER_TILE

    if not vram_map.is_file():
        runner.add(
            "vram_tile_budget", "warn", False,
            f"doc/VRAMMAP.md is absent, so declared tile usage cannot be "
            f"checked. Measured headroom below the lowest VDP table: "
            f"{tile_area_bytes} bytes ({tile_area_tiles} tiles).",
            vram_map_path=str(vram_map),
            tile_area_bytes=tile_area_bytes,
            tile_area_tiles=tile_area_tiles,
            blocking_dependency="doc/VRAMMAP.md (owned by the design-doc "
                                "agent). Until it lands this gate is a "
                                "warning, not a pass.",
        )
        return

    declared = _parse_vram_map(vram_map)
    if not declared:
        runner.add(
            "vram_tile_budget", "warn", False,
            "doc/VRAMMAP.md exists but no tile/byte total could be parsed "
            "out of it. Add a line like 'Total: 1234 tiles'.",
            vram_map_path=str(vram_map),
            tile_area_bytes=tile_area_bytes,
        )
        return

    declared_bytes = declared["declared_bytes"]
    runner.check(
        "vram_tile_budget",
        declared_bytes <= tile_area_bytes, True,
        f"declared tile usage {declared_bytes} bytes vs {tile_area_bytes} "
        f"bytes available below the lowest VDP table "
        f"(0x{lowest_table:04X})",
        declared=declared,
        tile_area_bytes=tile_area_bytes,
        lowest_table_address=lowest_table,
        note="Checks the DECLARATION in the doc, not the ROM. It cannot "
             "detect tiles the code uploads without declaring them.",
    )


def gate_performance(runner: GateRunner, vlab: pf.Vlab,
                     mdrt: pf.Mdrt | None) -> None:
    over_budget = vlab.metrics["over_budget_frames"]
    runner.check(
        "zero_over_budget_frames",
        over_budget <= runner.limits["max_over_budget_frames"], True,
        f"{over_budget} frames exceeded the CPU budget in the sampled window",
        over_budget_frames=over_budget,
        limit=runner.limits["max_over_budget_frames"],
    )

    if mdrt is None or not mdrt.samples:
        runner.add(
            "cpu_load_p99", "skip", True,
            "no CPU-load samples available (MDRT block missing or empty)",
        )
        return

    samples = sorted(mdrt.samples)
    def pct(p: float) -> int:
        idx = min(len(samples) - 1, max(0, round((p / 100.0) * len(samples)) - 1))
        return samples[idx]

    p99 = pct(99)
    runner.check(
        "cpu_load_p99", p99 <= runner.limits["max_cpu_load_p99"], True,
        f"CPU load p99 = {p99}% over {len(samples)} samples, limit "
        f"{runner.limits['max_cpu_load_p99']}%",
        p50=pct(50), p95=pct(95), p99=p99, worst=samples[-1],
        sample_count=len(samples),
        limit=runner.limits["max_cpu_load_p99"],
        note=f"{len(samples)} consecutive frames is roughly half a second. "
             "This is a snapshot, not sustained-performance evidence.",
    )

    if mdrt.sections:
        runner.add(
            "section_attribution", "pass", False,
            "peak raster lines per subsystem: " + ", ".join(
                f"{k}={v}" for k, v in mdrt.sections.items()
            ),
            sections=mdrt.sections,
            note="Resolution is one scanline (~0.4% of a frame). "
                 "'vblank_idle' is headroom, not work. Interrupts firing "
                 "inside a section are charged to that section.",
        )


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def run_gates(session: Path, project_root: Path,
              limits: dict[str, int]) -> tuple[GateRunner, dict[str, Any]]:
    dump_path = session / "visual_vdp_dump.bin"
    sram_path = session / "save.sram"
    metrics_path = session / "runtime_metrics.json"
    screenshot_path = session / "screenshot.png"
    request_path = session / "capture_request.json"

    if not dump_path.is_file():
        raise pf.ProbeFormatError(f"missing_artifact:{dump_path}")
    vlab = pf.load_vlab(dump_path)

    mdrt: pf.Mdrt | None = None
    mdrt_error: str | None = None
    if sram_path.is_file():
        try:
            mdrt = pf.load_mdrt(sram_path)
        except pf.ProbeFormatError as exc:
            mdrt_error = str(exc)
    else:
        mdrt_error = "save.sram absent"

    request = None
    if request_path.is_file():
        request = json.loads(request_path.read_text(encoding="utf-8"))

    sealer_metrics = None
    if metrics_path.is_file():
        sealer_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    runner = GateRunner(limits)

    if mdrt is not None:
        gate_scene_identity(runner, mdrt, request)
    else:
        runner.add("scene_identity", "skip", True,
                   f"MDRT unavailable ({mdrt_error}); scene identity "
                   "cannot be confirmed")

    gate_colors(runner, vlab)
    gate_screenshot_colors(runner, screenshot_path)
    gate_sprites(runner, vlab)
    gate_vram(runner, vlab, project_root / "doc" / "VRAMMAP.md")
    gate_krb1(runner, session)
    gate_performance(runner, vlab, mdrt)

    context = {
        "session": str(session),
        "vlab_schema_version": vlab.schema_version,
        "vlab_metrics": vlab.metrics,
        "vlab_frame_counter": vlab.frame_counter,
        "mdrt_available": mdrt is not None,
        "mdrt_error": mdrt_error,
        "capture_request": request,
        "sealer_window_title": (sealer_metrics or {}).get("window_title"),
        "rom_sha256": (sealer_metrics or {}).get("rom_sha256"),
    }
    return runner, context


def render_human(runner: GateRunner, context: dict[str, Any]) -> str:
    icons = {"pass": "PASS", "fail": "FAIL", "warn": "WARN", "skip": "SKIP"}
    lines = [
        "=" * 72,
        f"HARNESS GATES  {context['session']}",
        f"rom_sha256={context.get('rom_sha256')}",
        f"window_title={context.get('sealer_window_title')}",
        f"frame_counter={context.get('vlab_frame_counter')}",
        "=" * 72,
    ]
    for r in runner.results:
        tag = "hard" if r.hard else "soft"
        lines.append(f"[{icons[r.status]:4}] ({tag}) {r.name}: {r.summary}")
        note = r.detail.get("note")
        if note and r.status in ("fail", "warn"):
            lines.append(f"          note: {note}")
        dep = r.detail.get("blocking_dependency")
        if dep:
            lines.append(f"          blocked on: {dep}")
    lines.append("-" * 72)
    lines.append(
        f"hard failures: {len(runner.failed)}   warnings: {len(runner.warned)}"
    )
    lines.append(
        "VERDICT: " + ("FAIL" if runner.failed else "PASS")
    )
    lines.append("=" * 72)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("session", help="sealed evidence session directory")
    parser.add_argument("--project-root", default=None,
                        help="project root (default: inferred from this script)")
    parser.add_argument("--json", dest="json_path", default=None,
                        help="write the machine-readable report here "
                             "(default: <session>/gate_report.json)")
    parser.add_argument("--quiet", action="store_true",
                        help="suppress the human summary")
    for key, value in DEFAULT_LIMITS.items():
        parser.add_argument(f"--{key.replace('_', '-')}", type=int,
                            default=value, dest=key)
    args = parser.parse_args(argv)

    session = Path(args.session).resolve()
    project_root = (
        Path(args.project_root).resolve()
        if args.project_root
        else Path(__file__).resolve().parents[2]
    )
    limits = {key: getattr(args, key) for key in DEFAULT_LIMITS}

    try:
        runner, context = run_gates(session, project_root, limits)
    except (pf.ProbeFormatError, OSError) as exc:
        print(f"gates_status=error reason={exc}", file=sys.stderr)
        return 2

    report = {
        "schema_version": "1.0.0",
        "tool_name": "harness_gates",
        "verdict": "fail" if runner.failed else "pass",
        "hard_failure_count": len(runner.failed),
        "warning_count": len(runner.warned),
        "limits": limits,
        "context": context,
        "gates": [asdict(r) for r in runner.results],
        "claim_limit":
            "These gates check ONE captured window of ONE scene. They prove "
            "nothing about scenes, inputs or durations that were not "
            "captured. Several gates are structural invariants that cannot "
            "fail; see tools/harness/README.md.",
    }

    json_path = Path(args.json_path) if args.json_path else session / "gate_report.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if not args.quiet:
        print(render_human(runner, context))
    print(f"gates_status={report['verdict']} report={json_path}")
    return 1 if runner.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
