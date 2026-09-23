from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import binascii
import hashlib
import json
import struct
import zlib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EDITOR = Path(__file__).resolve().parent
DEFAULT_EXPORT_DIR = PROJECT_ROOT / "rascunho" / "taina_native_authoring_56x80_v01" / "exports"
DEFAULT_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_SPEC = {
    "schema_version": "native_editor_session.v2",
    "asset_id": "taina_idle_guard_56x80_native_authoring_v01",
    "canvas": {"width": 56, "height": 80, "pivot": [28, 74], "grid": 8},
    "export_dir": "rascunho/taina_native_authoring_56x80_v01/exports",
    "palette": [
        {"index": 0, "hex": "#000000", "role": "transparent", "visible": False},
        {"index": 1, "hex": "#220000", "role": "outline", "visible": True},
        {"index": 2, "hex": "#220022", "role": "hair_deep", "visible": True},
        {"index": 3, "hex": "#442244", "role": "hair_mid", "visible": True},
        {"index": 4, "hex": "#664422", "role": "hair_warm_highlight", "visible": True},
        {"index": 5, "hex": "#884422", "role": "skin_shadow", "visible": True},
        {"index": 6, "hex": "#AA6622", "role": "skin_base", "visible": True},
        {"index": 7, "hex": "#CC8844", "role": "skin_light", "visible": True},
        {"index": 8, "hex": "#CC4400", "role": "top_shadow", "visible": True},
        {"index": 9, "hex": "#EE6600", "role": "top_base", "visible": True},
        {"index": 10, "hex": "#EE8844", "role": "top_highlight", "visible": True},
        {"index": 11, "hex": "#004444", "role": "teal_shadow", "visible": True},
        {"index": 12, "hex": "#008888", "role": "teal_base", "visible": True},
        {"index": 13, "hex": "#00AAAA", "role": "teal_highlight", "visible": True},
        {"index": 14, "hex": "#000044", "role": "indigo_shadow", "visible": True},
        {"index": 15, "hex": "#222266", "role": "indigo_base", "visible": True},
    ],
}

SESSION = None


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def send_json(handler, status, value):
    body = json_bytes(value)
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def reject(message):
    raise ValueError(message)


def parse_hex(value):
    if not isinstance(value, str) or len(value) != 7 or value[0] != "#":
        reject("color must be #RRGGBB")
    try:
        raw = bytes.fromhex(value[1:])
    except ValueError:
        reject("invalid color")
    if any(channel % 0x22 for channel in raw):
        reject("color is outside the 9-bit VDP grid")
    return value.upper(), tuple(raw)


def validate_relative_path(value, label, allow_only_rascunho=True):
    if not isinstance(value, str) or not value or "\x00" in value:
        reject(f"{label} must be a non-empty relative path")
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        reject(f"{label} traversal/absolute path rejected")
    if allow_only_rascunho and (not candidate.parts or candidate.parts[0] != "rascunho"):
        reject(f"{label} must remain under rascunho/")
    resolved = (PROJECT_ROOT / candidate).resolve()
    if PROJECT_ROOT not in resolved.parents and resolved != PROJECT_ROOT:
        reject(f"{label} escapes project root")
    return resolved


def validate_spec(spec):
    if not isinstance(spec, dict):
        reject("spec must be an object")
    canvas = spec.get("canvas")
    if not isinstance(canvas, dict):
        reject("canvas is required")
    width, height = canvas.get("width"), canvas.get("height")
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        reject("canvas dimensions must be positive integers")
    if width % 8 or height % 8:
        reject("canvas dimensions must be multiples of 8")
    if width > 128 or height > 128:
        reject("canvas dimensions exceed editor safety limit")
    pivot = canvas.get("pivot")
    if not isinstance(pivot, list) or len(pivot) != 2 or not all(isinstance(v, int) for v in pivot):
        reject("pivot must be [x,y] integer")
    if not (0 <= pivot[0] < width and 0 <= pivot[1] < height):
        reject("pivot outside canvas")
    export_dir = validate_relative_path(spec.get("export_dir"), "export_dir")
    palette = spec.get("palette")
    if not isinstance(palette, list) or len(palette) != 16:
        reject("palette must contain exactly 16 entries")
    palette_by_hex, indices = {}, set()
    for entry in palette:
        if not isinstance(entry, dict) or not isinstance(entry.get("index"), int):
            reject("invalid palette entry")
        index = entry["index"]
        if index in indices or index < 0 or index > 15:
            reject("palette indices must be unique 0..15")
        indices.add(index)
        color, _ = parse_hex(entry.get("hex"))
        if color in palette_by_hex and index != 0:
            reject("visible palette aliases are forbidden")
        palette_by_hex[color] = index
    if 0 not in indices or not any(e.get("index") == 0 and e.get("visible") is False for e in palette):
        reject("index 0 must be the transparent entry")
    spec = json.loads(json.dumps(spec))
    spec["export_dir"] = str(export_dir.relative_to(PROJECT_ROOT))
    return spec, export_dir, palette_by_hex


def new_session(spec):
    validated, export_dir, palette_by_hex = validate_spec(spec)
    return {"spec": validated, "export_dir": export_dir, "palette_by_hex": palette_by_hex,
            "pixels": [0] * (validated["canvas"]["width"] * validated["canvas"]["height"]), "actions": []}


def require_session():
    if SESSION is None:
        reject("no active session; POST /api/session first")
    return SESSION


def check_xy(session, x, y):
    width, height = session["spec"]["canvas"]["width"], session["spec"]["canvas"]["height"]
    if not isinstance(x, int) or not isinstance(y, int) or x < 0 or y < 0 or x >= width or y >= height:
        reject("pixel coordinate outside canvas")
    return y * width + x


def action_color(session, action):
    normalized, _ = parse_hex(action.get("color"))
    if normalized not in session["palette_by_hex"]:
        reject("action color is not in session palette")
    return session["palette_by_hex"][normalized], normalized


def apply_one(session, action, record=True):
    if not isinstance(action, dict) or action.get("kind") not in {"pencil", "eraser", "fill"}:
        reject("action kind must be pencil, eraser or fill")
    kind, x, y = action["kind"], action.get("x"), action.get("y")
    start = check_xy(session, x, y)
    if kind == "eraser":
        target, normalized = 0, "#000000"
    else:
        target, normalized = action_color(session, action)
        if target == 0:
            reject("pencil/fill cannot paint transparent; use eraser")
    before = list(session["pixels"]) if kind == "fill" else session["pixels"][start]
    if kind in {"pencil", "eraser"}:
        session["pixels"][start] = target
    else:
        source = session["pixels"][start]
        if source != target:
            width, height = session["spec"]["canvas"]["width"], session["spec"]["canvas"]["height"]
            stack, seen = [(x, y)], set()
            while stack:
                cx, cy = stack.pop()
                if (cx, cy) in seen or cx < 0 or cy < 0 or cx >= width or cy >= height:
                    continue
                seen.add((cx, cy)); pos = cy * width + cx
                if session["pixels"][pos] != source:
                    continue
                session["pixels"][pos] = target
                stack.extend(((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)))
    if record:
        entry = {"n": len(session["actions"]) + 1, "kind": kind, "x": x, "y": y, "color": normalized,
                 "before": before, "after": list(session["pixels"]) if kind == "fill" else target}
        session["actions"].append(entry)


def action_log(session):
    spec = session["spec"]
    return {
        "schema_version": "native_editor_action_log.v2",
        "asset_id": spec["asset_id"], "canvas": spec["canvas"], "palette": spec["palette"],
        "provenance": "ai_generated/agent_operated_native_editor_draft",
        "tool": "taina_native_authoring_editor",
        "source_of_identity": {"path": "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png",
                                "sha256": "324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a",
                                "role": "identity_only_not_pixel_source"},
        "visual_direction_reference": {"path": "data/source_art/visual_producer_outputs/taina_idle_guard_scale_shootout_v01/taina_idle_guard_56x80_visual_source_v01.png",
                                         "sha256": "32c5a8089c52251c0276eb0c28406b44e7797455a767b4a498c1da74be094d4f",
                                         "role": "proportion_direction_only_not_pixel_source"},
        "actions": session["actions"],
    }


def png_chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)


def write_indexed_png(path, session):
    spec, width, height = session["spec"], session["spec"]["canvas"]["width"], session["spec"]["canvas"]["height"]
    palette = sorted(spec["palette"], key=lambda item: item["index"])
    rgb = b"".join(bytes.fromhex(item["hex"][1:]) for item in palette)
    rows = bytearray()
    for y in range(height):
        rows.append(0); row = session["pixels"][y * width:(y + 1) * width]
        for x in range(0, width, 2):
            rows.append((row[x] << 4) | (row[x + 1] if x + 1 < width else 0))
    payload = b"\x89PNG\r\n\x1a\n"
    payload += png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 4, 3, 0, 0, 0))
    payload += png_chunk(b"PLTE", rgb) + png_chunk(b"tRNS", bytes([0] + [255] * 15))
    payload += png_chunk(b"tEXt", b"provenance\x00ai_generated/agent_operated_native_editor_draft")
    payload += png_chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + png_chunk(b"IEND", b"")
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest(), len(payload)


def export_session(session, name=None, target_dir=None):
    name = name or f"{session['spec']['asset_id']}.png"
    if not isinstance(name, str) or Path(name).name != name or Path(name).suffix.lower() != ".png":
        reject("export name must be a plain .png filename")
    export_dir = session["export_dir"] if target_dir is None else validate_relative_path(target_dir, "target_dir")
    if PROJECT_ROOT / "res" in export_dir.parents or export_dir == PROJECT_ROOT / "res":
        reject("res/ is forbidden for this route")
    export_dir.mkdir(parents=True, exist_ok=True); png_path = (export_dir / name).resolve()
    if export_dir not in png_path.parents:
        reject("export path escapes target directory")
    log_path = png_path.with_suffix(".actions.json"); png_sha, png_bytes = write_indexed_png(png_path, session)
    log_data = json_bytes(action_log(session)); log_path.write_bytes(log_data)
    return {"png": {"path": str(png_path.relative_to(PROJECT_ROOT)), "sha256": png_sha, "bytes": png_bytes},
            "action_log": {"path": str(log_path.relative_to(PROJECT_ROOT)), "sha256": hashlib.sha256(log_data).hexdigest(), "bytes": len(log_data)},
            "canvas": session["spec"]["canvas"], "visible_colors": len({value for value in session["pixels"] if value != 0}),
            "index0_transparent": True}


def bbox(session):
    width = session["spec"]["canvas"]["width"]
    points = [(i % width, i // width) for i, value in enumerate(session["pixels"]) if value != 0]
    if not points:
        return None
    xs, ys = zip(*points)
    return [min(xs), min(ys), max(xs), max(ys)]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global SESSION
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path.endswith("index.html"):
            body = (EDITOR / "index.html").read_bytes(); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        elif parsed.path == "/api/health":
            send_json(self, 200, {"status": "ok", "editor": "native_editor_session.v2"}); return
        elif parsed.path == "/api/session":
            if SESSION is None: SESSION = new_session(DEFAULT_SPEC)
            send_json(self, 200, {"spec": SESSION["spec"], "actions": len(SESSION["actions"]), "pixels": SESSION["pixels"]}); return
        else:
            try: candidate = validate_relative_path(parsed.path.lstrip("/"), "asset_path", False)
            except ValueError: self.send_error(400, "invalid path"); return
            if not candidate.is_file(): self.send_error(404); return
            body = candidate.read_bytes(); self.send_response(200); self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_POST(self):
        global SESSION
        parsed = urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 8_000_000: reject("invalid payload length")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if parsed.path == "/api/session": SESSION = new_session(payload.get("spec", payload)); send_json(self, 200, {"status": "session_open", "spec": SESSION["spec"]}); return
            session = require_session()
            if parsed.path == "/api/apply":
                actions = payload.get("actions")
                if not isinstance(actions, list) or not actions or len(actions) > 12000: reject("actions must be a non-empty list of at most 12000 entries")
                for action in actions: apply_one(session, action)
                send_json(self, 200, {"status": "actions_applied", "actions": len(session["actions"])}); return
            if parsed.path == "/api/restore":
                log = payload.get("action_log")
                if not isinstance(log, dict) or log.get("canvas") != session["spec"]["canvas"]: reject("action log canvas differs from active session")
                actions = log.get("actions")
                if not isinstance(actions, list) or len(actions) > 12000: reject("invalid action log")
                session["pixels"] = [0] * len(session["pixels"]); session["actions"] = []
                for action in actions: apply_one(session, action)
                send_json(self, 200, {"status": "session_restored", "actions": len(session["actions"])}); return
            if parsed.path == "/api/export": send_json(self, 200, export_session(session, payload.get("name"), payload.get("target_dir"))); return
            if parsed.path == "/api/export-log":
                target_dir = session["export_dir"] if payload.get("target_dir") is None else validate_relative_path(payload["target_dir"], "target_dir")
                name = payload.get("name", f"{session['spec']['asset_id']}.actions.json")
                if not isinstance(name, str) or Path(name).name != name or not name.endswith(".actions.json"): reject("log name must be a plain .actions.json filename")
                target_dir.mkdir(parents=True, exist_ok=True); path = (target_dir / name).resolve()
                if target_dir not in path.parents: reject("log path escapes target directory")
                data = json_bytes(action_log(session)); path.write_bytes(data)
                send_json(self, 200, {"path": str(path.relative_to(PROJECT_ROOT)), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}); return
            if parsed.path == "/api/validate":
                visible = sorted({value for value in session["pixels"] if value != 0})
                send_json(self, 200, {"canvas": session["spec"]["canvas"], "dimensions_valid": True, "visible_indices": visible,
                                      "visible_color_count": len(visible), "index0_transparent": True, "grid_8x8": True,
                                      "action_count": len(session["actions"]), "bbox": bbox(session)}); return
            reject("unknown API endpoint")
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc: send_json(self, 400, {"status": "rejected", "error": str(exc)})
        except Exception as exc: send_json(self, 500, {"status": "error", "error": str(exc)})

    def log_message(self, *_): pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
