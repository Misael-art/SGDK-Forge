#!/usr/bin/env python3
"""Measure semantic and mechanical defects in fixed-cell sprite sheets."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw


BLOCKING_CODES = {
    "FRAME_EMPTY",
    "FRAME_EDGE_CLIPPING",
    "SMALL_ISLAND_DEBRIS",
    "STRAY_LARGE_COMPONENT",
    "ANATOMY_REVIEW_MISSING",
    "ANATOMY_INCOMPLETE",
    "PIVOT_DRIFT",
    "FOOT_CONTACT_MISSING",
    "FRAME_DELTA_TOO_LOW",
    "FRAME_DELTA_TOO_HIGH",
    "FRAME_COUNT_MISMATCH",
    "SHEET_GRID_MISMATCH",
    "REQUIRED_ACTION_MISSING",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def foreground_mask(frame: Image.Image, transparent_index: int) -> list[list[bool]]:
    if frame.mode == "P":
        pixels = frame.load()
        return [
            [int(pixels[x, y]) != transparent_index for x in range(frame.width)]
            for y in range(frame.height)
        ]
    rgba = frame.convert("RGBA")
    pixels = rgba.load()
    return [
        [pixels[x, y][3] > 0 for x in range(frame.width)]
        for y in range(frame.height)
    ]


def components(mask: list[list[bool]]) -> list[list[tuple[int, int]]]:
    height = len(mask)
    width = len(mask[0]) if height else 0
    seen: set[tuple[int, int]] = set()
    found: list[list[tuple[int, int]]] = []
    for y in range(height):
        for x in range(width):
            if not mask[y][x] or (x, y) in seen:
                continue
            queue = deque([(x, y)])
            seen.add((x, y))
            component: list[tuple[int, int]] = []
            while queue:
                cx, cy = queue.popleft()
                component.append((cx, cy))
                for ny in range(max(0, cy - 1), min(height, cy + 2)):
                    for nx in range(max(0, cx - 1), min(width, cx + 2)):
                        if (nx, ny) not in seen and mask[ny][nx]:
                            seen.add((nx, ny))
                            queue.append((nx, ny))
            found.append(component)
    return sorted(found, key=len, reverse=True)


def bbox(points: list[tuple[int, int]]) -> list[int] | None:
    if not points:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def add_finding(
    findings: list[dict[str, Any]],
    code: str,
    action: str,
    frame_index: int,
    detail: str,
    severity: str = "error",
) -> None:
    findings.append(
        {
            "code": code,
            "severity": severity,
            "action": action,
            "frame": frame_index,
            "detail": detail,
        }
    )


def review_for_frame(action: dict[str, Any], local_index: int) -> dict[str, Any] | None:
    reviews = action.get("manual_anatomy_review", [])
    if local_index >= len(reviews):
        return None
    review = reviews[local_index]
    return review if isinstance(review, dict) else None


def make_contact_sheet(
    frames: list[tuple[str, int, Image.Image]],
    output: Path,
    scale: int = 6,
) -> None:
    margin = 8
    label_h = 16
    cell_w = frames[0][2].width * scale
    cell_h = frames[0][2].height * scale
    width = margin + len(frames) * (cell_w + margin)
    height = margin + label_h + cell_h + margin
    sheet = Image.new("RGB", (width, height), (18, 22, 30))
    draw = ImageDraw.Draw(sheet)
    for index, (action, frame_index, frame) in enumerate(frames):
        x = margin + index * (cell_w + margin)
        y = margin + label_h
        preview = frame.convert("RGBA").resize((cell_w, cell_h), Image.Resampling.NEAREST)
        checker = Image.new("RGB", (cell_w, cell_h), (35, 39, 48))
        checker.paste(preview, mask=preview.getchannel("A"))
        sheet.paste(checker, (x, y))
        draw.rectangle((x - 1, y - 1, x + cell_w, y + cell_h), outline=(70, 190, 230))
        draw.text((x, margin), f"{action}:{frame_index}", fill=(230, 235, 240))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def make_animation(frames: list[Image.Image], output: Path, hold_ms: int, scale: int = 8) -> None:
    prepared: list[Image.Image] = []
    for frame in frames:
        rgba = frame.convert("RGBA")
        canvas = Image.new("RGBA", rgba.size, (22, 26, 34, 255))
        canvas.alpha_composite(rgba)
        prepared.append(
            canvas.convert("P", palette=Image.Palette.ADAPTIVE, colors=32).resize(
                (frame.width * scale, frame.height * scale),
                Image.Resampling.NEAREST,
            )
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    prepared[0].save(
        output,
        save_all=True,
        append_images=prepared[1:],
        duration=hold_ms,
        loop=0,
        disposal=2,
    )


def analyze(spec_path: Path, output_path: Path) -> dict[str, Any]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    project_root_value = Path(spec.get("project_root", "."))
    project_root = (
        project_root_value.resolve()
        if project_root_value.is_absolute()
        else (spec_path.parent / project_root_value).resolve()
    )
    sheet_path = Path(spec["sheet"])
    if not sheet_path.is_absolute():
        sheet_path = project_root / sheet_path
    image = Image.open(sheet_path)
    cell_w = int(spec["cell"]["w"])
    cell_h = int(spec["cell"]["h"])
    transparent_index = int(spec.get("transparent_index", 0))
    pivot_x = int(spec["pivot"]["x"])
    ground_y = int(spec["pivot"]["y"])
    findings: list[dict[str, Any]] = []
    frame_reports: list[dict[str, Any]] = []
    action_frames: dict[str, list[Image.Image]] = {}
    all_preview_frames: list[tuple[str, int, Image.Image]] = []
    declared_actions = [str(action["name"]) for action in spec["actions"]]
    required_actions = [
        str(action) for action in spec.get("required_actions", declared_actions)
    ]
    missing_required_actions = [
        action for action in required_actions if action not in declared_actions
    ]
    for action in missing_required_actions:
        add_finding(
            findings,
            "REQUIRED_ACTION_MISSING",
            action,
            -1,
            "action promised by the animation state plan has no strip in this artifact",
        )

    if image.width % cell_w or image.height % cell_h:
        add_finding(
            findings,
            "SHEET_GRID_MISMATCH",
            "sheet",
            -1,
            f"{image.width}x{image.height} is not divisible by {cell_w}x{cell_h}",
        )

    for action in spec["actions"]:
        name = str(action["name"])
        row = int(action.get("row", 0))
        start = int(action.get("start", 0))
        count = int(action["count"])
        grounded = list(action.get("grounded", [True] * count))
        if len(grounded) != count:
            add_finding(
                findings,
                "FRAME_COUNT_MISMATCH",
                name,
                -1,
                "grounded array length differs from declared frame count",
            )
            grounded = (grounded + [False] * count)[:count]
        action_frames[name] = []
        previous_mask: list[list[bool]] | None = None
        for local_index in range(count):
            left = (start + local_index) * cell_w
            top = row * cell_h
            frame = image.crop((left, top, left + cell_w, top + cell_h))
            mask = foreground_mask(frame, transparent_index)
            points = [(x, y) for y, line in enumerate(mask) for x, value in enumerate(line) if value]
            parts = components(mask)
            frame_bbox = bbox(points)
            frame_findings_before = len(findings)

            if not points:
                add_finding(findings, "FRAME_EMPTY", name, local_index, "frame has no visible pixels")
            else:
                touched = []
                if any(mask[y][0] for y in range(cell_h)):
                    touched.append("left")
                if any(mask[y][cell_w - 1] for y in range(cell_h)):
                    touched.append("right")
                if any(mask[0][x] for x in range(cell_w)):
                    touched.append("top")
                if any(mask[cell_h - 1][x] for x in range(cell_w)):
                    touched.append("bottom")
                if touched:
                    add_finding(
                        findings,
                        "FRAME_EDGE_CLIPPING",
                        name,
                        local_index,
                        f"visible pixels touch {','.join(touched)} edge",
                    )

                if len(parts) > 1:
                    main_size = len(parts[0])
                    for part_index, part in enumerate(parts[1:], start=1):
                        ratio = len(part) / max(1, main_size)
                        code = "SMALL_ISLAND_DEBRIS" if len(part) <= 4 or ratio < 0.04 else "STRAY_LARGE_COMPONENT"
                        add_finding(
                            findings,
                            code,
                            name,
                            local_index,
                            f"component {part_index} has {len(part)} pixels ({ratio:.3f} of main mass)",
                        )

                bottom = frame_bbox[3] if frame_bbox else -1
                center_x = ((frame_bbox[0] + frame_bbox[2]) / 2.0) if frame_bbox else 0.0
                if grounded[local_index]:
                    contact_pixels = sum(
                        1
                        for y in range(max(0, ground_y - 1), min(cell_h, ground_y + 1))
                        for x in range(cell_w)
                        if mask[y][x]
                    )
                    if contact_pixels == 0 or abs(bottom - ground_y) > 1:
                        add_finding(
                            findings,
                            "FOOT_CONTACT_MISSING",
                            name,
                            local_index,
                            f"grounded frame bottom={bottom}, ground_y={ground_y}, contact_pixels={contact_pixels}",
                        )
                if grounded[local_index] and abs(center_x - pivot_x) > float(spec.get("pivot_tolerance_px", 3.0)):
                    add_finding(
                        findings,
                        "PIVOT_DRIFT",
                        name,
                        local_index,
                        f"bbox center {center_x:.2f}px differs from pivot_x {pivot_x}px",
                    )

            anatomy = review_for_frame(action, local_index)
            if anatomy is None:
                add_finding(
                    findings,
                    "ANATOMY_REVIEW_MISSING",
                    name,
                    local_index,
                    "manual anatomy review is mandatory",
                )
            elif anatomy.get("status") != "passed":
                add_finding(
                    findings,
                    "ANATOMY_INCOMPLETE",
                    name,
                    local_index,
                    str(anatomy.get("note", "manual anatomy review failed")),
                )

            delta = None
            if previous_mask is not None:
                changed = sum(
                    1
                    for y in range(cell_h)
                    for x in range(cell_w)
                    if mask[y][x] != previous_mask[y][x]
                )
                delta = changed / float(cell_w * cell_h)
                delta_min = float(action.get("frame_delta_min", spec.get("frame_delta_min", 0.015)))
                delta_max = float(action.get("frame_delta_max", spec.get("frame_delta_max", 0.55)))
                if delta < delta_min:
                    add_finding(
                        findings,
                        "FRAME_DELTA_TOO_LOW",
                        name,
                        local_index,
                        f"occupancy delta {delta:.4f} is below {delta_min:.4f}",
                    )
                if delta > delta_max:
                    add_finding(
                        findings,
                        "FRAME_DELTA_TOO_HIGH",
                        name,
                        local_index,
                        f"occupancy delta {delta:.4f} exceeds {delta_max:.4f}",
                    )
            previous_mask = mask
            action_frames[name].append(frame)
            all_preview_frames.append((name, local_index, frame))
            frame_reports.append(
                {
                    "action": name,
                    "frame": local_index,
                    "bbox": frame_bbox,
                    "visible_pixels": len(points),
                    "component_sizes": [len(part) for part in parts],
                    "grounded": bool(grounded[local_index]),
                    "pivot": {"x": pivot_x, "ground_y": ground_y},
                    "frame_delta_ratio": None if delta is None else round(delta, 6),
                    "anatomy_review": anatomy,
                    "status": "passed" if len(findings) == frame_findings_before else "failed",
                }
            )

    previews = spec.get("previews", {})
    contact_sheet = previews.get("contact_sheet")
    if contact_sheet:
        contact_path = Path(contact_sheet)
        if not contact_path.is_absolute():
            contact_path = project_root / contact_path
        make_contact_sheet(all_preview_frames, contact_path, int(previews.get("scale", 6)))
    animation_paths: dict[str, str] = {}
    animation_root = previews.get("animation_root")
    if animation_root:
        animation_root_path = Path(animation_root)
        if not animation_root_path.is_absolute():
            animation_root_path = project_root / animation_root_path
        for action in spec["actions"]:
            name = str(action["name"])
            animation_path = animation_root_path / f"{name}.gif"
            make_animation(
                action_frames[name],
                animation_path,
                int(action.get("hold_ms", 90)),
                int(previews.get("animation_scale", 8)),
            )
            animation_paths[name] = str(animation_path.relative_to(project_root)).replace("\\", "/")

    blocking = [finding for finding in findings if finding["code"] in BLOCKING_CODES]
    report = {
        "schema": "sprite_artifact_report.v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool": "tools/image-tools/sprite_artifact_audit.py",
        "asset_id": spec["asset_id"],
        "sheet": str(sheet_path.relative_to(project_root)).replace("\\", "/"),
        "sheet_sha256": sha256(sheet_path),
        "status": "passed" if not blocking else "technical_pass_visual_fail",
        "technical_pass": not any(
            finding["code"] in {"FRAME_EMPTY", "SHEET_GRID_MISMATCH", "FRAME_COUNT_MISMATCH"}
            for finding in findings
        ),
        "visual_pass": not blocking,
        "cell": {"w": cell_w, "h": cell_h},
        "pivot": {"x": pivot_x, "ground_y": ground_y},
        "required_checks": {
            "edge_clipping": True,
            "detached_islands": True,
            "anatomy": True,
            "pivot": True,
            "foot_contact": True,
            "frame_delta": True,
            "action_coverage": True,
        },
        "action_coverage": {
            "required_actions": required_actions,
            "declared_actions": declared_actions,
            "missing_required_actions": missing_required_actions,
            "status": "passed" if not missing_required_actions else "failed",
        },
        "summary": {
            "frames_checked": len(frame_reports),
            "findings": len(findings),
            "blocking_findings": len(blocking),
        },
        "findings": findings,
        "frames": frame_reports,
        "evidence": {
            "contact_sheet": contact_sheet,
            "animated_captures": animation_paths,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = analyze(args.spec.resolve(), args.output.resolve())
    print(json.dumps({"status": report["status"], "summary": report["summary"]}))
    return 0 if report["visual_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
