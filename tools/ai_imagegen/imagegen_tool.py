#!/usr/bin/env python3
"""
imagegen_tool.py
CLI principal para a camada oficial de geracao visual do ecossistema MegaDrive_DEV.
Comandos: status, install, route, generate, convert, healthcheck

Regra canonica: a geracao nativa (callable/inline) tem prioridade. O toolchain
local (ComfyUI) so e usado como fallback. raw_ai nunca promove direto para res/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

# --- Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR / "config"
REPORTS_DIR = SCRIPT_DIR / "reports"
WORKFLOWS_DIR = SCRIPT_DIR / "workflows" / "comfyui"
CACHE_DIR = SCRIPT_DIR / "cache"
RUNTIME_DIR = SCRIPT_DIR / "runtime"
COMFY_DIR = RUNTIME_DIR / "ComfyUI"
VENV_DIR = RUNTIME_DIR / "venv"
MODELS_DIR = SCRIPT_DIR / "models"
CHECKPOINTS_DIR = MODELS_DIR / "checkpoints"

PROFILE_PATH = CONFIG_DIR / "imagegen_profiles.json"
MANIFEST_PATH = MODELS_DIR / "manifest.json"

# Repo root: tools/ai_imagegen/ -> tools/ -> repo
REPO_ROOT = SCRIPT_DIR.parent.parent
DATA_RAW_AI = REPO_ROOT / "data" / "raw_ai"
DATA_SOURCE_ART = REPO_ROOT / "data" / "source_art"

COMFY_HOST = "127.0.0.1"
COMFY_PORT = 8188
COMFY_BASE = f"http://{COMFY_HOST}:{COMFY_PORT}"
COMFY_REPO = "https://github.com/comfyanonymous/ComfyUI.git"


# --- Utils ---


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_bool_auto(value):
    """Argparse helper: accepts true/false/auto for native channel flags."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in ("auto", ""):
        return None
    if normalized in ("true", "1", "yes", "y", "on"):
        return True
    if normalized in ("false", "0", "no", "n", "off"):
        return False
    raise argparse.ArgumentTypeError("expected true, false, or auto")


def _env_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in ("true", "1", "yes", "y", "on")


def _detect_native_channel_default() -> tuple[bool, bool, str]:
    """Best-effort default for agent surfaces.

    Shell tools cannot introspect the model's callable tool list directly. The
    safest practical default is:
    - explicit env override wins;
    - Codex Desktop/Codex agent sessions default to callable native imagegen;
    - plain CLI/human shells default to no native channel.
    """
    override = (
        os.environ.get("SGDK_NATIVE_IMAGEGEN_CHANNEL")
        or os.environ.get("AI_IMAGEGEN_NATIVE_CHANNEL")
        or ""
    ).strip().lower()
    if override in ("callable", "native_callable", "native-chat-callable"):
        return True, False, "env_override_callable"
    if override in ("inline", "native_inline", "native-chat-inline"):
        return False, True, "env_override_inline"
    if override in ("none", "false", "off", "local", "blocked"):
        return False, False, "env_override_no_native"

    if _env_truthy(os.environ.get("SGDK_NATIVE_IMAGEGEN_AVAILABLE")):
        return True, False, "env_sgdk_native_imagegen_available"

    codex_markers = (
        "CODEX_THREAD_ID",
        "CODEX_INTERNAL_ORIGINATOR_OVERRIDE",
        "CODEX_DESKTOP_LAUNCH_ACTION_SOCKET",
    )
    if any(os.environ.get(k) for k in codex_markers):
        return True, False, "auto_codex_agent_surface"

    return False, False, "auto_no_native_channel_detected"


def resolve_native_channel_flags(native_callable, native_inline) -> tuple[bool, bool, str]:
    """Resolve explicit/auto native image generation channel flags."""
    explicit_callable = parse_bool_auto(native_callable)
    explicit_inline = parse_bool_auto(native_inline)

    if explicit_callable is not None or explicit_inline is not None:
        return (
            bool(explicit_callable),
            bool(explicit_inline) if explicit_callable is not True else False,
            "explicit_cli_flags",
        )

    return _detect_native_channel_default()


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def run_cmd(cmd, cwd=None, timeout=30):
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def resolve_profile_alias(name: str, profiles_doc: dict) -> str:
    """Normalize aliases like 'deck-safe' -> 'deck_safe_sd15'."""
    if name in profiles_doc.get("profiles", {}):
        return name
    aliases = profiles_doc.get("aliases", {}) or {}
    if name in aliases:
        return aliases[name]
    # tolerate dash/underscore swap
    swapped = name.replace("-", "_")
    if swapped in profiles_doc.get("profiles", {}):
        return swapped
    if swapped in aliases:
        return aliases[swapped]
    return name


def http_get(url: str, timeout: float = 2.0):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status, resp.read()
    except Exception:
        return None, None


def http_post_json(url: str, payload: dict, timeout: float = 10.0):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return None, {"error": str(e)}


# --- Detection ---


def detect_os_info() -> dict:
    system = platform.system()
    release = platform.release().lower()
    os_name = system
    platform_tag = "unknown"
    if system == "Windows":
        platform_tag = "windows"
    elif system == "Darwin":
        platform_tag = "macos"
    elif system == "Linux":
        is_steam = False
        if "steamdeck" in release or "steamos" in release:
            is_steam = True
        if os.path.exists("/etc/os-release"):
            try:
                with open("/etc/os-release") as f:
                    content = f.read().lower()
                    if "steam" in content:
                        is_steam = True
            except Exception:
                pass
        if is_steam:
            os_name = "SteamOS"
            platform_tag = "steamos_linux"
        else:
            platform_tag = "linux_desktop"
    return {"os": os_name, "platform_tag": platform_tag}


def detect_python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def detect_ram_free_gb() -> float:
    """RAM free in GB with portable fallbacks; no psutil hard dependency."""
    try:
        import psutil  # type: ignore

        return round(psutil.virtual_memory().available / (1024 ** 3), 1)
    except Exception:
        pass
    # Linux: /proc/meminfo
    if sys.platform.startswith("linux"):
        try:
            with open("/proc/meminfo") as f:
                meminfo = {}
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        k = parts[0].strip()
                        v = parts[1].strip().split()
                        if v:
                            try:
                                meminfo[k] = int(v[0])  # kB
                            except ValueError:
                                pass
            avail_kb = meminfo.get("MemAvailable") or meminfo.get("MemFree", 0)
            return round(avail_kb / (1024 * 1024), 1)
        except Exception:
            return 0.0
    # Windows: GlobalMemoryStatusEx via ctypes
    if sys.platform.startswith("win"):
        try:
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            if ok:
                return round(stat.ullAvailPhys / (1024 ** 3), 1)
        except Exception:
            return 0.0
    return 0.0


def detect_disk_free_gb(path: Path = SCRIPT_DIR) -> float:
    try:
        return round(shutil.disk_usage(str(path)).free / (1024 ** 3), 1)
    except Exception:
        return 0.0


def detect_comfyui() -> dict:
    """Detects ComfyUI install + online status. Does not depend on /dev/null."""
    comfy_home = None
    if COMFY_DIR.exists() and (COMFY_DIR / "main.py").exists():
        comfy_home = str(COMFY_DIR)
    elif COMFY_DIR.exists():
        comfy_home = str(COMFY_DIR)

    status, _ = http_get(f"{COMFY_BASE}/system_stats", timeout=1.5)
    comfy_online = status == 200
    return {"comfyui_home": comfy_home, "comfyui_online": comfy_online}


def detect_gpu() -> dict:
    vendor = "Unknown"
    model = ""
    vram_gb = 0.0
    ok, out, _ = run_cmd(
        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"]
    )
    if ok and out.strip():
        vendor = "NVIDIA"
        lines = out.strip().splitlines()
        if lines:
            parts = lines[0].split(",")
            model = parts[0].strip() if parts else ""
            vraw = parts[1].strip() if len(parts) > 1 else ""
            try:
                vram_mb = int(vraw.replace("MiB", "").strip())
                vram_gb = round(vram_mb / 1024, 1)
            except Exception:
                vram_gb = 0.0
    else:
        if sys.platform.startswith("linux"):
            ok2, out2, _ = run_cmd(["lspci", "-nnk"])
            if ok2 and out2:
                for line in out2.splitlines():
                    if ("AMD" in line or "Radeon" in line) and "VGA" in line:
                        vendor = "AMD"
                        model = line.strip()
                        break
                    if "Intel" in line and "VGA" in line:
                        vendor = vendor if vendor != "Unknown" else "Intel"
                        if not model:
                            model = line.strip()
        elif sys.platform.startswith("win"):
            ok2, out2, _ = run_cmd(
                ["wmic", "path", "win32_VideoController", "get", "name"]
            )
            if ok2 and out2:
                lines = [
                    l.strip()
                    for l in out2.splitlines()
                    if l.strip() and "Name" not in l
                ]
                if lines:
                    head = lines[0]
                    if "AMD" in head or "Radeon" in head:
                        vendor = "AMD"
                    elif "Intel" in head:
                        vendor = "Intel"
                    elif "NVIDIA" in head:
                        vendor = "NVIDIA"
                    model = head
    return {"vendor": vendor, "model": model, "vram_gb": vram_gb}


def models_present() -> list:
    present = []
    if CHECKPOINTS_DIR.exists():
        for f in CHECKPOINTS_DIR.iterdir():
            if f.is_file() and f.stat().st_size > 0:
                present.append(
                    {
                        "id": f.stem,
                        "path": str(f),
                        "size_mb": round(f.stat().st_size / (1024 ** 2), 1),
                        "checksum_ok": None,
                    }
                )
    return present


def _resolve_model_url(install: dict) -> str:
    ckpt = install.get("checkpoint_url")
    if ckpt and ckpt != "not_used":
        return ckpt
    return install.get("gguf_url") or ""


def profile_model_present(profile_cfg: dict) -> bool:
    install = profile_cfg.get("install", {}) or {}
    url = _resolve_model_url(install)
    if not url:
        return False
    fname = url.rsplit("/", 1)[-1]
    candidate = CHECKPOINTS_DIR / fname
    return candidate.exists() and candidate.stat().st_size > 0


# --- Profile recommendation ---


def recommend_profile(os_info: dict, ram_gb: float, gpu: dict) -> str:
    pt = os_info.get("platform_tag", "")
    vram = gpu.get("vram_gb", 0) or 0
    if pt == "steamos_linux":
        return "deck_safe_sd15"
    if vram >= 12:
        return "sdxl_lowvram"
    if vram >= 6:
        return "sdxl_lowvram"
    if vram >= 4:
        return "deck_safe_sd15"
    if ram_gb >= 12:
        return "deck_safe_sd15"
    return "cpu_fallback"


# --- Commands ---


def cmd_self_check(args):
    """Secao 34/38: a ferramenta prova a integridade dos proprios artefatos
    antes de ser usada como fonte de medicao/roteamento."""
    checks = []

    def add(name, ok, detail):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    def try_json(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh), None
        except Exception as exc:
            return None, str(exc)

    manifest, err = try_json(MODELS_DIR / "manifest.json")
    if err:
        add("models_manifest_parses", False, err)
    else:
        ids = [m.get("id") for m in manifest.get("models", [])]
        add(
            "models_manifest_parses",
            bool(ids) and all(ids),
            f"{len(ids)} model ids: {ids[:4]}{'...' if len(ids) > 4 else ''}",
        )

    profiles, err = try_json(PROFILE_PATH)
    if err:
        add("profiles_config_parses", False, err)
    else:
        names = sorted((profiles.get("profiles") or {}).keys())
        add("profiles_config_parses", bool(names), f"profiles: {names}")

    canonical_schemas = [
        "capability_report.schema.json",
        "generation_channel_decision.schema.json",
        "asset_lineage_record.schema.json",
    ]
    for name in canonical_schemas:
        _, err = try_json(REPORTS_DIR / "schema" / name)
        add(f"schema_{name}", err is None, err or "ok")

    successor_schema = (
        SCRIPT_DIR.parent
        / "sgdk_wrapper"
        / "schemas"
        / "successor_asset_directive.schema.json"
    )
    _, err = try_json(successor_schema)
    add("schema_successor_asset_directive", err is None, err or "ok")

    skill_path = (
        SCRIPT_DIR.parent
        / "sgdk_wrapper"
        / ".agent"
        / "skills"
        / "art"
        / "image-generation-routing"
        / "SKILL.md"
    )
    add("routing_skill_present", skill_path.exists(), str(skill_path))

    passed = all(c["ok"] for c in checks)
    report = {
        "tool": "imagegen_tool",
        "self_check": "pass" if passed else "fail",
        "timestamp": now_iso(),
        "checks": checks,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for c in checks:
            mark = "PASS" if c["ok"] else "FAIL"
            print(f"[{mark}] {c['check']}: {c['detail']}")
        print(f"SELF-CHECK: {report['self_check'].upper()}")
    return report


def cmd_status(args):
    os_info = detect_os_info()
    disk_free_gb = detect_disk_free_gb()
    ram_free_gb = detect_ram_free_gb()
    gpu = detect_gpu()
    comfy = detect_comfyui()
    models = models_present()
    profile = recommend_profile(os_info, ram_free_gb, gpu)
    report = {
        "timestamp": now_iso(),
        "os": os_info["os"],
        "platform_tag": os_info["platform_tag"],
        "python_version": detect_python_version(),
        "git_present": run_cmd(["git", "--version"])[0],
        "disk_free_gb": disk_free_gb,
        "ram_free_gb": ram_free_gb,
        "gpu_info": gpu,
        "comfyui_detected": comfy["comfyui_home"] is not None,
        "comfyui_online": comfy["comfyui_online"],
        "models_present": models,
        "profile_recommended": profile,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"OS: {report['os']} ({report['platform_tag']})")
        print(f"Python: {report['python_version']}  Git: {report['git_present']}")
        print(
            f"Disk free: {report['disk_free_gb']} GB  RAM free: {report['ram_free_gb']} GB"
        )
        print(f"GPU: {gpu['vendor']} {gpu['model']} VRAM: {gpu['vram_gb']} GB")
        print(
            f"ComfyUI detected: {report['comfyui_detected']}  online: {report['comfyui_online']}"
        )
        print(
            f"Models: {len(models)} present  Recommended profile: {report['profile_recommended']}"
        )
    return report


def _profile_healthcheck(profile_key: str, profile_cfg: dict) -> dict:
    """Returns a per-profile readiness summary used by route/healthcheck."""
    comfy = detect_comfyui()
    ckpt_present = profile_model_present(profile_cfg)
    disk_ok = detect_disk_free_gb() >= 8
    ram_ok = detect_ram_free_gb() >= 4
    return {
        "profile": profile_key,
        "comfyui_installed": comfy["comfyui_home"] is not None,
        "comfyui_online": comfy["comfyui_online"],
        "model_present": ckpt_present,
        "disk_ok": disk_ok,
        "ram_ok": ram_ok,
        "ready": all(
            [
                comfy["comfyui_home"] is not None,
                ckpt_present,
                disk_ok,
                ram_ok,
            ]
        ),
    }


def cmd_route(args):
    native_callable, native_inline, native_detection = resolve_native_channel_flags(
        args.native_callable,
        args.native_inline,
    )
    os_info = detect_os_info()
    gpu = detect_gpu()
    ram_free_gb = detect_ram_free_gb()
    profile = recommend_profile(os_info, ram_free_gb, gpu)

    profiles_doc = load_json(PROFILE_PATH)
    profile_cfg = profiles_doc["profiles"].get(profile, {})
    hc = _profile_healthcheck(profile, profile_cfg) if profile_cfg else None

    run_id = uuid.uuid4().hex[:12]
    dec = {
        "run_id": run_id,
        "timestamp": now_iso(),
        "native_preflight": {
            "callable": native_callable,
            "inline": native_inline,
            "fallback_only": not native_callable and not native_inline,
            "detection": native_detection,
        },
        "selected_source": None,
        "profile_used": None,
        "rationale": "",
    }

    if native_callable:
        dec["selected_source"] = "native_chat_image_generation_callable"
        dec["profile_used"] = "native_chat_image_generation_callable"
        dec["rationale"] = "Native callable generation available; local toolchain not needed."
    elif native_inline:
        dec["selected_source"] = "native_chat_inline_generation"
        dec["profile_used"] = "native_chat_inline_generation"
        dec["rationale"] = "No callable interface, inline generation available."
    elif not hc:
        dec["selected_source"] = "blocked"
        dec["profile_used"] = "none"
        dec["rationale"] = f"No profile config for {profile}."
    elif not hc["ready"]:
        # Distinguish install-required vs hard block
        missing = [k for k, v in hc.items() if k not in ("profile", "ready") and not v]
        if not hc["disk_ok"] or not hc["ram_ok"]:
            dec["selected_source"] = "blocked"
            dec["profile_used"] = "none"
            dec["rationale"] = (
                f"Host insufficient for {profile}: {', '.join(missing)}."
            )
        else:
            dec["selected_source"] = "local_install_required"
            dec["profile_used"] = profile
            dec["rationale"] = (
                f"Profile {profile} recommended but not ready. Missing: {', '.join(missing)}. "
                f"Run: python tools/ai_imagegen/imagegen_tool.py install --profile {profile}"
            )
    else:
        dec["selected_source"] = profile
        dec["profile_used"] = profile
        dec["rationale"] = (
            f"Local profile {profile} ready (ComfyUI online={hc['comfyui_online']}, model present)."
        )

    if args.json:
        print(json.dumps(dec, indent=2))
    else:
        print(f"Run ID: {run_id}")
        print(f"Selected source: {dec['selected_source']}")
        print(f"Profile used: {dec['profile_used']}")
        print(f"Native detection: {native_detection}")
        print(f"Rationale: {dec['rationale']}")
    return dec


# --- Install pipeline ---


def _git_clone_or_update(repo_url: str, dest: Path) -> tuple[bool, str]:
    if dest.exists() and (dest / ".git").exists():
        ok, out, err = run_cmd(["git", "-C", str(dest), "pull", "--ff-only"], timeout=120)
        return ok, out + err
    dest.parent.mkdir(parents=True, exist_ok=True)
    ok, out, err = run_cmd(
        ["git", "clone", "--depth", "1", repo_url, str(dest)], timeout=300
    )
    return ok, out + err


def _python_executable_for_venv() -> Path:
    if sys.platform.startswith("win"):
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _ensure_venv() -> tuple[bool, str]:
    py = _python_executable_for_venv()
    if py.exists():
        return True, f"venv exists: {VENV_DIR}"
    VENV_DIR.parent.mkdir(parents=True, exist_ok=True)
    ok, out, err = run_cmd(
        [sys.executable, "-m", "venv", str(VENV_DIR)], timeout=120
    )
    return ok, out + err


def _pip_install(packages: list, extra_index: str | None = None) -> tuple[bool, str]:
    py = _python_executable_for_venv()
    cmd = [str(py), "-m", "pip", "install", "--upgrade"] + list(packages)
    if extra_index:
        cmd += ["--extra-index-url", extra_index]
    ok, out, err = run_cmd(cmd, timeout=900)
    return ok, out + err


def _download_file(url: str, dest: Path, expected_size_mb: float | None = None) -> tuple[bool, str]:
    if dest.exists() and dest.stat().st_size > 0:
        return True, f"already present: {dest}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        with urllib.request.urlopen(url, timeout=60) as resp, open(tmp, "wb") as out:
            shutil.copyfileobj(resp, out)
        tmp.rename(dest)
        return True, f"downloaded {dest}"
    except Exception as e:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass
        return False, f"download failed: {e}"


def cmd_install(args):
    profiles_doc = load_json(PROFILE_PATH)
    profile_key = resolve_profile_alias(args.profile, profiles_doc)
    profiles = profiles_doc.get("profiles", {})
    if profile_key not in profiles:
        print(
            f"ERROR: Profile '{args.profile}' (resolved '{profile_key}') not in {PROFILE_PATH}",
            file=sys.stderr,
        )
        sys.exit(1)
    cfg = profiles[profile_key]
    install = cfg.get("install", {}) or {}

    print(f"Install profile: {profile_key}")
    print(f"Name: {cfg.get('name', profile_key)}")
    print(f"Model: {cfg.get('model', '<none>')}")

    # Host check (advisory, not fatal in dry-run)
    os_info = detect_os_info()
    gpu = detect_gpu()
    ram_free_gb = detect_ram_free_gb()
    disk_free_gb = detect_disk_free_gb()
    required_disk = max(12.0, (install.get("checkpoint_size_mb", 4200) / 1024.0) + 6.0)
    advisory = []
    if disk_free_gb < required_disk:
        advisory.append(
            f"low disk: {disk_free_gb} GB free, ~{required_disk:.1f} GB recommended"
        )
    if ram_free_gb < 6:
        advisory.append(f"low RAM: {ram_free_gb} GB free")
    if (
        profile_key in ("sdxl_lowvram", "flux_schnell_gguf")
        and os_info["platform_tag"] == "steamos_linux"
    ):
        advisory.append(
            f"{profile_key} is not recommended on Steam Deck; prefer deck_safe_sd15"
        )

    plan = {
        "profile": profile_key,
        "venv": str(VENV_DIR),
        "comfyui": {"repo": COMFY_REPO, "dest": str(COMFY_DIR)},
        "model": {
            "url": _resolve_model_url(install),
            "dest_dir": str(CHECKPOINTS_DIR),
            "expected_size_mb": install.get("checkpoint_size_mb"),
        },
        "host_advisory": advisory,
    }

    if args.dry_run:
        print("[dry-run] Plan:")
        print(json.dumps(plan, indent=2))
        return plan

    # Idempotent execution
    steps = []

    ok_venv, msg_venv = _ensure_venv()
    steps.append({"step": "venv", "ok": ok_venv, "message": msg_venv.strip()})
    if not ok_venv:
        print(json.dumps({"steps": steps, "ok": False}, indent=2))
        sys.exit(2)

    ok_clone, msg_clone = _git_clone_or_update(COMFY_REPO, COMFY_DIR)
    steps.append({"step": "comfyui_clone", "ok": ok_clone, "message": msg_clone.strip()[:500]})
    if not ok_clone:
        print(json.dumps({"steps": steps, "ok": False}, indent=2))
        sys.exit(3)

    # Torch flavor: keep conservative defaults; user can swap manually.
    torch_pkgs = ["torch", "torchvision", "torchaudio"]
    ok_torch, msg_torch = _pip_install(torch_pkgs)
    steps.append({"step": "pip_torch", "ok": ok_torch, "message": msg_torch.strip()[-400:]})

    req_file = COMFY_DIR / "requirements.txt"
    if req_file.exists():
        py = _python_executable_for_venv()
        ok_req, out, err = run_cmd(
            [str(py), "-m", "pip", "install", "-r", str(req_file)], timeout=1800
        )
        steps.append(
            {
                "step": "pip_requirements",
                "ok": ok_req,
                "message": (out + err).strip()[-400:],
            }
        )

    # Model download
    model_url = _resolve_model_url(install)
    if model_url:
        fname = model_url.rsplit("/", 1)[-1]
        dest = CHECKPOINTS_DIR / fname
        ok_dl, msg_dl = _download_file(model_url, dest)
        steps.append({"step": "model_download", "ok": ok_dl, "message": msg_dl})

    summary = {
        "profile": profile_key,
        "ok": all(s["ok"] for s in steps),
        "steps": steps,
        "host_advisory": advisory,
    }
    print(json.dumps(summary, indent=2))
    if not summary["ok"]:
        sys.exit(4)
    return summary


# --- Generate ---


def _load_workflow_for_profile(profile_key: str) -> dict | None:
    mapping = {
        "deck_safe_sd15": "sd15_pixelart_low.json",
        "sdxl_lowvram": "sdxl_lowvram_pixel.json",
        "flux_schnell_gguf": "flux_schnell_gguf.json",
        "cpu_fallback": "sd15_pixelart_low.json",
    }
    wf_name = mapping.get(profile_key)
    if not wf_name:
        return None
    wf_path = WORKFLOWS_DIR / wf_name
    if not wf_path.exists():
        return None
    return load_json(wf_path)


def _patch_workflow(workflow: dict, prompt: str, negative: str, seed: int, steps: int, cfg: float, w: int, h: int) -> dict:
    nodes = workflow.get("nodes", {})
    # naive patch: assume node "2" is positive CLIPTextEncode, "3" negative,
    # "4" KSampler, "5" EmptyLatentImage. Matches our bundled workflows.
    if "2" in nodes and prompt:
        nodes["2"].setdefault("inputs", {})["text"] = prompt
    if "3" in nodes and negative:
        nodes["3"].setdefault("inputs", {})["text"] = negative
    if "4" in nodes:
        inp = nodes["4"].setdefault("inputs", {})
        inp["seed"] = seed
        inp["steps"] = steps
        inp["cfg"] = cfg
    if "5" in nodes:
        inp = nodes["5"].setdefault("inputs", {})
        inp["width"] = w
        inp["height"] = h
    return workflow


def _comfy_submit_prompt(workflow_nodes: dict, client_id: str) -> dict:
    status, body = http_post_json(
        f"{COMFY_BASE}/prompt",
        {"prompt": workflow_nodes, "client_id": client_id},
        timeout=15,
    )
    if status != 200:
        return {"ok": False, "error": body}
    return {"ok": True, **body}


def _comfy_wait_history(prompt_id: str, timeout_s: float = 600.0, poll_s: float = 2.0) -> dict | None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        status, body = http_get(f"{COMFY_BASE}/history/{prompt_id}", timeout=5)
        if status == 200 and body:
            try:
                data = json.loads(body.decode("utf-8"))
            except Exception:
                data = None
            if data and prompt_id in data:
                return data[prompt_id]
        time.sleep(poll_s)
    return None


def _comfy_fetch_image(filename: str, subfolder: str, type_: str, dest: Path) -> bool:
    qs = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": type_})
    status, body = http_get(f"{COMFY_BASE}/view?{qs}", timeout=30)
    if status != 200 or not body:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(body)
    return True


def cmd_generate(args):
    profiles_doc = load_json(PROFILE_PATH)
    profile_key = resolve_profile_alias(args.profile or "deck_safe_sd15", profiles_doc)
    profiles = profiles_doc.get("profiles", {})
    if profile_key not in profiles:
        print(f"ERROR: Unknown profile {profile_key}", file=sys.stderr)
        sys.exit(1)
    cfg = profiles[profile_key]
    gen_cfg = cfg.get("generation", {})

    run_id = uuid.uuid4().hex[:12]
    dims = gen_cfg.get("dimensions", [512, 512])
    w = int(args.width) if args.width else int(dims[0])
    h = int(args.height) if args.height else int(dims[1])
    steps = int(args.steps) if args.steps else int(gen_cfg.get("steps", 20))
    cfg_scale = float(gen_cfg.get("cfg", 7.0))
    seed = int(args.seed) if args.seed is not None else 42
    prompt = args.prompt or ""
    negative = args.negative or "blurry, photo, 3d render, text, watermark"

    out_dir = DATA_RAW_AI / run_id
    output_path = out_dir / "output.png"

    report = {
        "run_id": run_id,
        "timestamp": now_iso(),
        "source": "local",
        "profile": profile_key,
        "prompt": prompt,
        "negative_prompt": negative,
        "output_path": str(output_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "dimensions": f"{w}x{h}",
        "seed": seed,
        "steps": steps,
        "cfg": cfg_scale,
    }

    if args.dry_run:
        print("[dry-run] Generation plan:")
        print(json.dumps(report, indent=2))
        return report

    workflow = _load_workflow_for_profile(profile_key)
    if not workflow:
        print(f"ERROR: no workflow bundled for profile {profile_key}", file=sys.stderr)
        sys.exit(2)
    workflow = _patch_workflow(workflow, prompt, negative, seed, steps, cfg_scale, w, h)
    nodes = workflow.get("nodes") or workflow.get("prompt") or {}

    comfy = detect_comfyui()
    if not comfy["comfyui_online"]:
        print(
            "ERROR: ComfyUI is not online at "
            f"{COMFY_BASE}. Start it under runtime/ComfyUI before generate, "
            "or run with --dry-run.",
            file=sys.stderr,
        )
        sys.exit(3)

    client_id = uuid.uuid4().hex
    sub = _comfy_submit_prompt(nodes, client_id)
    if not sub.get("ok") or "prompt_id" not in sub:
        print(f"ERROR: submit failed: {sub.get('error')}", file=sys.stderr)
        sys.exit(4)
    prompt_id = sub["prompt_id"]
    report["prompt_id"] = prompt_id

    history = _comfy_wait_history(prompt_id, timeout_s=args.timeout)
    if not history:
        print("ERROR: timed out waiting for ComfyUI history", file=sys.stderr)
        sys.exit(5)

    outputs = history.get("outputs", {})
    saved = False
    for _node_id, node_out in outputs.items():
        for img in node_out.get("images", []) or []:
            ok = _comfy_fetch_image(
                img.get("filename", ""),
                img.get("subfolder", ""),
                img.get("type", "output"),
                output_path,
            )
            if ok:
                saved = True
                break
        if saved:
            break

    report["persisted_to_filesystem"] = saved
    report_path = out_dir / "generation_report.json"
    save_json(report_path, report)

    if not saved:
        print("ERROR: generation finished but no image could be fetched", file=sys.stderr)
        sys.exit(6)

    print(json.dumps(report, indent=2))
    return report


# --- Convert ---


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_convert(args):
    source = Path(args.source).resolve()
    spec = Path(args.spec).resolve() if args.spec else None
    if not source.exists():
        print(f"ERROR: source not found: {source}", file=sys.stderr)
        sys.exit(1)

    # Block direct raw_ai promotions: the source MUST live under data/source_art/
    try:
        source.relative_to(DATA_SOURCE_ART.resolve())
    except ValueError:
        print(
            "ERROR: convert requires source under data/source_art/. "
            "Move the asset there first (raw_ai -> source_art) before conversion.",
            file=sys.stderr,
        )
        sys.exit(2)

    if not spec or not spec.exists():
        print(
            "ERROR: --spec is required and must point to a tools/image-tools spec JSON.",
            file=sys.stderr,
        )
        sys.exit(3)

    spec_data = load_json(spec)

    run_id = uuid.uuid4().hex[:12]
    lineage_id = f"lineage_{run_id}"
    lineage = {
        "lineage_id": lineage_id,
        "run_id": run_id,
        "timestamp": now_iso(),
        "raw_path": "",
        "source_art_path": str(source.relative_to(REPO_ROOT)).replace("\\", "/"),
        "res_paths": [],
        "conversion_log": "",
        "source_sha256": _hash_file(source),
        "spec": str(spec.relative_to(REPO_ROOT)).replace("\\", "/"),
    }

    if args.raw_path:
        lineage["raw_path"] = args.raw_path

    if args.dry_run:
        print("[dry-run] Convert plan:")
        print(json.dumps(lineage, indent=2))
        return lineage

    # A conversao automatica foi REMOVIDA daqui, e nao substituida.
    #
    # Este bloco chamava tools/image-tools/batch_resize_index.py, que fazia
    # downscale Lanczos e emitia RGBA — destruindo o index 0 e criando pixel
    # intermediario. Aquele script hoje falha fechado de proposito.
    #
    # O substituto canonico (`python3 -m forge_art convert`) AINDA NAO EXISTE.
    # Chamar o script morto daqui so produziria um erro confuso a jusante, e
    # improvisar outro resize aqui recriaria exatamente o defeito. Entao este
    # comando registra a linhagem, declara o bloqueio e para.
    lineage["conversion_log"] = ""
    lineage["status"] = "blocked_no_canonical_converter"
    lineage["blocked_since"] = "2026-08-30"
    lineage["why"] = (
        "batch_resize_index.py foi aposentado (downscale Lanczos + saida RGBA, "
        "destruia o index 0). `forge-art convert` ainda nao foi implementado."
    )
    lineage["next_action"] = (
        "converta manualmente respeitando o contrato (PNG modo P, PLTE <= 16, "
        "<= 15 cores visiveis, index 0 conforme o papel declarado, nearest "
        "apenas) e MECA com "
        "`python3 tools/sgdk_wrapper/forge_art/pixel_contract.py --validate "
        "<png> --index0-role <papel>`; se a fonte for high-res de identidade, "
        "a rota e assisted_native_translation e a producao vai para um "
        "produtor capaz — registre com `python3 -m forge_art translate`"
    )
    lineage_path = DATA_SOURCE_ART / f"{lineage_id}.json"
    save_json(lineage_path, lineage)

    print(json.dumps({"ok": False, "status": lineage["status"],
                      "lineage": str(lineage_path),
                      "next_action": lineage["next_action"]}, indent=2))
    print(f"[BLOCKED] {lineage['why']}", file=sys.stderr)
    sys.exit(4)
    if not ok:
        sys.exit(5)
    return lineage


# --- Healthcheck ---


def cmd_healthcheck(args):
    os_info = detect_os_info()
    disk_free_gb = detect_disk_free_gb()
    ram_free_gb = detect_ram_free_gb()
    gpu = detect_gpu()
    profiles_doc = load_json(PROFILE_PATH)

    profile_key = (
        resolve_profile_alias(args.profile, profiles_doc)
        if args.profile
        else recommend_profile(os_info, ram_free_gb, gpu)
    )
    profile_cfg = profiles_doc.get("profiles", {}).get(profile_key, {})
    hc = _profile_healthcheck(profile_key, profile_cfg) if profile_cfg else None

    results = {
        "timestamp": now_iso(),
        "profile": profile_key,
        "checks": {
            "os_supported": os_info["platform_tag"]
            in ("windows", "steamos_linux", "linux_desktop", "macos"),
            "disk_ok": disk_free_gb >= 8,
            "ram_ok": ram_free_gb >= 4,
            "gpu_detected": gpu["vendor"] != "Unknown",
            "profile_known": profile_cfg is not None and bool(profile_cfg),
            "comfyui_installed": bool(hc and hc["comfyui_installed"]),
            "comfyui_online": bool(hc and hc["comfyui_online"]),
            "model_present": bool(hc and hc["model_present"]),
        },
    }
    results["pass"] = all(results["checks"].values())
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for k, v in results["checks"].items():
            print(f"[{'PASS' if v else 'FAIL'}] {k}")
        print(
            f"Overall: {'PASS' if results['pass'] else 'FAIL'}  Profile: {profile_key}"
        )
    return results


# --- Bonsai / License / Preflight (v2 integration) ---


BONSAI_DIR = RUNTIME_DIR / "bonsai"
BONSAI_LICENSE_ACK = BONSAI_DIR / "bonsai_license_ack.json"
BONSAI_VENDOR_MANIFEST = BONSAI_DIR / "vendor_manifest.json"
BONSAI_SESSION_JSON = BONSAI_DIR / "bonsai_session.json"
BONSAI_LOG_DIR = BONSAI_DIR / "logs"
BONSAI_PORT = 8000
BONSAI_REPO_URL = "https://github.com/PrismML-Eng/Bonsai-Image-Demo.git"
BONSAI_REPO_FILES = [
    "setup.ps1",
    "setup.sh",
    "scripts/common.ps1",
    "scripts/common.sh",
    "scripts/serve.ps1",
    "scripts/serve.sh",
    "scripts/send_request.ps1",
    "scripts/send_request.sh",
    "scripts/generate.ps1",
    "scripts/generate.sh",
    "scripts/generate.py",
    "scripts/download_model.ps1",
    "scripts/download_model.sh",
]
BONSAI_REPO_EXCLUDED = [
    "vendor/image-studio",
    "frontend",
    "node_modules",
]

BONSAI_ALLOWED_SCOPES = [
    "concept_art",
    "tileset_concept",
    "dither_mask",
    "contrast_study",
]
BONSAI_FORBIDDEN_SCOPES = [
    "animated_sprite_final",
    "hud_final",
    "res_direct",
    "aaa_final_asset",
]


def _is_windows() -> bool:
    return sys.platform.startswith("win")


def _bonsai_script_ext() -> str:
    return "ps1" if _is_windows() else "sh"


def _bonsai_backend_label() -> str:
    if _is_windows():
        return "bonsai_serve_windows"
    if sys.platform == "darwin":
        return "bonsai_serve_macos"
    return "bonsai_serve_linux"


def _bonsai_compatibility(gpu: dict) -> bool:
    """Bonsai supports NVIDIA (gemlite+HQQ/triton-windows) or Apple Silicon (mflux).
    AMD and Intel are not supported by Bonsai's official backends.
    """
    vendor = (gpu.get("vendor") or "").lower()
    if "nvidia" in vendor:
        return True
    if sys.platform == "darwin" and vendor in ("apple", ""):
        return True
    return False


def _load_license_ack() -> tuple[bool, dict, str]:
    """Returns (passed, ack_dict, sha256_or_empty)."""
    if not BONSAI_LICENSE_ACK.exists():
        return False, {}, ""
    try:
        data = load_json(BONSAI_LICENSE_ACK)
    except Exception as e:
        return False, {"_error": str(e)}, ""
    required = [
        "model_license",
        "output_license",
        "usage_policy",
        "allowed_scopes",
        "approver",
        "approval_date",
        "evidence_url",
    ]
    missing = [k for k in required if k not in data]
    if missing:
        return False, {"_missing": missing, **data}, ""
    import re as _re
    if not _re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", str(data.get("approval_date", ""))):
        return False, {"_error": "approval_date must match YYYY-MM-DD"}, ""
    scopes = data.get("allowed_scopes", [])
    if not isinstance(scopes, list) or any(
        s not in BONSAI_ALLOWED_SCOPES + BONSAI_FORBIDDEN_SCOPES for s in scopes
    ):
        return False, {"_error": "allowed_scopes contains unknown values"}, ""
    if any(s in BONSAI_FORBIDDEN_SCOPES for s in scopes):
        return False, {"_error": "allowed_scopes must not include forbidden scopes"}, ""
    sha = _hash_file(BONSAI_LICENSE_ACK)
    return True, data, sha


def _validate_asset_scope(asset_role: str | None) -> tuple[bool, list[str], list[str]]:
    """Returns (passed, allowed_list, block_reasons)."""
    if not asset_role:
        return False, BONSAI_ALLOWED_SCOPES, ["asset_role is required for Bonsai"]
    if asset_role in BONSAI_FORBIDDEN_SCOPES:
        return (
            False,
            BONSAI_ALLOWED_SCOPES,
            [f"asset_role '{asset_role}' is in forbidden_scopes"],
        )
    if asset_role not in BONSAI_ALLOWED_SCOPES:
        return (
            False,
            BONSAI_ALLOWED_SCOPES,
            [
                f"asset_role '{asset_role}' not in allowed_scopes "
                f"{BONSAI_ALLOWED_SCOPES}"
            ],
        )
    return True, BONSAI_ALLOWED_SCOPES, []


def _resolve_master_style_manifest(
    project_root: Path | None,
    asset_role: str | None,
    override: str | None,
) -> dict:
    """Multi-path lookup: override -> doc/art -> data/source_art/<role> -> out/logs."""
    paths_tried: list[str] = []
    candidates: list[tuple[str, Path]] = []
    if override:
        candidates.append(("override", Path(override)))
    if project_root:
        candidates.append(("doc_art", project_root / "doc" / "art" / "master_style_manifest.json"))
        if asset_role:
            candidates.append(
                (
                    "source_art_role",
                    project_root
                    / "data"
                    / "source_art"
                    / asset_role
                    / "master_style_manifest.json",
                )
            )
        candidates.append(
            ("out_logs", project_root / "out" / "logs" / "master_style_manifest.json")
        )

    for source, p in candidates:
        try:
            paths_tried.append(str(p))
        except Exception:
            continue
        if p.exists() and p.is_file():
            try:
                sha = _hash_file(p)
                return {
                    "paths_tried": paths_tried,
                    "resolved": True,
                    "resolved_path": str(p),
                    "sha256": sha,
                    "source": source,
                    "block_reasons": [],
                }
            except Exception as e:
                return {
                    "paths_tried": paths_tried,
                    "resolved": False,
                    "resolved_path": str(p),
                    "sha256": "",
                    "source": source,
                    "block_reasons": [f"read_error: {e}"],
                }

    return {
        "paths_tried": paths_tried,
        "resolved": False,
        "resolved_path": "",
        "sha256": "",
        "source": "not_found",
        "block_reasons": ["master_style_manifest.json not found in any candidate path"],
    }


def _write_prompt_pack_manifest(
    out_dir: Path,
    run_id: str,
    prompt: str,
    negative: str,
    seed: int,
    model_id: str,
    model_variant: str,
    sampler: str,
    steps: int,
    cfg: float,
    width: int,
    height: int,
    profile: str,
    channel: str,
    output_sha256: str,
    asset_role: str | None,
    license_ack_sha: str,
    style_manifest_sha: str,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    pack = {
        "run_id": run_id,
        "timestamp": now_iso(),
        "prompt": prompt,
        "negative_prompt": negative,
        "seed": seed,
        "model_id": model_id,
        "model_variant": model_variant,
        "sampler": sampler,
        "steps": steps,
        "cfg": cfg,
        "width": width,
        "height": height,
        "profile": profile,
        "channel": channel,
        "output_sha256": output_sha256,
        "license_ack_sha256": license_ack_sha,
        "style_manifest_sha256": style_manifest_sha,
        "asset_role": asset_role or "",
    }
    path = out_dir / "prompt_pack_manifest.json"
    save_json(path, pack)
    return path


def _write_vendor_manifest(
    bonsai_dir: Path, repo_url: str, commit_sha: str, cloned_at: str
) -> tuple[bool, Path, list[str]]:
    files_block: list[dict] = []
    missing: list[str] = []
    for rel in BONSAI_REPO_FILES:
        p = bonsai_dir / rel
        if not p.exists():
            missing.append(rel)
            continue
        try:
            sha = _hash_file(p)
            files_block.append({"path": rel, "sha256": sha, "size_bytes": p.stat().st_size})
        except Exception as e:
            missing.append(f"{rel} (read_error: {e})")
    manifest = {
        "schema_version": "1.0.0",
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "cloned_at": cloned_at,
        "files": files_block,
        "excluded": BONSAI_REPO_EXCLUDED,
        "missing_files": missing,
    }
    out = bonsai_dir / "vendor_manifest.json"
    save_json(out, manifest)
    return (len(missing) == 0), out, missing


def _bonsai_serve_url() -> str:
    return f"http://127.0.0.1:{BONSAI_PORT}"


def _bonsai_serve_online() -> bool:
    status, _ = http_get(f"{_bonsai_serve_url()}/system_stats", timeout=1.0)
    if status == 200:
        return True
    status, _ = http_get(f"{_bonsai_serve_url()}/", timeout=1.0)
    return status == 200


def _host_gate_status() -> dict:
    gpu = detect_gpu()
    ram = detect_ram_free_gb()
    comfy = detect_comfyui()
    block_reasons: list[str] = []
    if not _bonsai_compatibility(gpu):
        block_reasons.append(
            f"gpu_vendor={gpu.get('vendor')} (Bonsai requires NVIDIA or Apple Silicon)"
        )
    if (gpu.get("vram_gb") or 0) < 4:
        block_reasons.append(
            f"vram_gb={gpu.get('vram_gb')} (Bonsai recommends >=6, hard floor 4)"
        )
    if ram < 6:
        block_reasons.append(f"ram_free_gb={ram} (Bonsai hard floor 6)")
    return {
        "passed": len(block_reasons) == 0,
        "gpu_vendor": gpu.get("vendor", "Unknown"),
        "gpu_model": gpu.get("model", ""),
        "vram_gb": gpu.get("vram_gb", 0.0),
        "ram_free_gb": ram,
        "nvidia_smi": gpu.get("vendor") == "NVIDIA",
        "bonsai_compatible": _bonsai_compatibility(gpu),
        "comfyui_online": comfy["comfyui_online"],
        "block_reasons": block_reasons,
    }


def _license_gate_status() -> dict:
    passed, ack, sha = _load_license_ack()
    block_reasons: list[str] = []
    if not BONSAI_LICENSE_ACK.exists():
        block_reasons.append("bonsai_license_ack.json not found")
    elif not passed:
        if "_missing" in ack:
            block_reasons.append(f"ack missing required fields: {ack['_missing']}")
        elif "_error" in ack:
            block_reasons.append(f"ack parse error: {ack['_error']}")
        else:
            block_reasons.append("ack validation failed")
    return {
        "passed": passed,
        "ack_path": str(BONSAI_LICENSE_ACK.relative_to(REPO_ROOT)).replace("\\", "/")
        if BONSAI_LICENSE_ACK.exists()
        else "",
        "ack_sha256": sha,
        "ack_data": {k: v for k, v in ack.items() if not k.startswith("_")} if passed else {},
        "block_reasons": block_reasons,
    }


def _scope_gate_status(asset_role: str | None) -> dict:
    passed, allowed, reasons = _validate_asset_scope(asset_role)
    return {
        "passed": passed,
        "asset_role": asset_role or "",
        "allowed_scopes": allowed,
        "forbidden_scopes": BONSAI_FORBIDDEN_SCOPES,
        "block_reasons": reasons,
    }


def _build_preflight_report(
    project_root: Path | None,
    asset_role: str | None,
    style_manifest_override: str | None,
    native_callable: bool,
    native_inline: bool,
    asset_role_required: bool = True,
) -> dict:
    """Combines status + route + license + host + scope into a single report.

    asset_role_required=False makes the scope gate a soft advisory (used by
    'just show me the host capability' dry-runs).
    """
    native_callable, native_inline, native_detection = resolve_native_channel_flags(
        native_callable,
        native_inline,
    )
    license_gate = _license_gate_status()
    host_gate = _host_gate_status()

    scope_gate: dict
    if asset_role_required:
        scope_gate = _scope_gate_status(asset_role)
    else:
        scope_gate = {
            "passed": True,
            "asset_role": asset_role or "",
            "allowed_scopes": BONSAI_ALLOWED_SCOPES,
            "forbidden_scopes": BONSAI_FORBIDDEN_SCOPES,
            "block_reasons": [],
        }

    style_lookup = _resolve_master_style_manifest(
        project_root, asset_role, style_manifest_override
    )

    run_id = uuid.uuid4().hex[:12]
    fallback_chain: list[str] = [
        "native_chat_image_generation_callable",
        "native_chat_inline_generation",
    ]

    selected_source = "blocked"
    profile_used = "none"
    rationale = ""

    if native_callable:
        selected_source = "native_chat_image_generation_callable"
        profile_used = "native_chat_image_generation_callable"
        rationale = "Native callable generation available; local toolchain not needed."
    elif native_inline:
        selected_source = "native_chat_inline_generation"
        profile_used = "native_chat_inline_generation"
        rationale = "No callable interface, inline generation available."
    else:
        if not license_gate["passed"]:
            selected_source = "license_blocked"
            rationale = (
                "Bonsai license ack missing or invalid: "
                + "; ".join(license_gate["block_reasons"])
            )
        elif asset_role_required and not scope_gate["passed"]:
            selected_source = "scope_blocked"
            rationale = (
                "asset_role blocked: " + "; ".join(scope_gate["block_reasons"])
            )
        elif not host_gate["passed"]:
            selected_source = "blocked_host_capability"
            rationale = (
                "Host insufficient for Bonsai: "
                + "; ".join(host_gate["block_reasons"])
            )
        else:
            selected_source = "bonsai_4b_ternary"
            profile_used = "bonsai_4b_ternary"
            rationale = "All gates passed; Bonsai 4B ternary selected as opt-in profile."

        fallback_chain.append(selected_source)

    return {
        "run_id": run_id,
        "timestamp": now_iso(),
        "native_preflight": {
            "callable": native_callable,
            "inline": native_inline,
            "fallback_only": not native_callable and not native_inline,
            "detection": native_detection,
        },
        "selected_source": selected_source,
        "profile_used": profile_used,
        "rationale": rationale,
        "gates": {
            "license": {
                "passed": license_gate["passed"],
                "ack_path": license_gate["ack_path"],
                "ack_sha256": license_gate["ack_sha256"],
                "block_reasons": license_gate["block_reasons"],
            },
            "host": {
                "passed": host_gate["passed"],
                "gpu_vendor": host_gate["gpu_vendor"],
                "gpu_model": host_gate["gpu_model"],
                "vram_gb": host_gate["vram_gb"],
                "ram_free_gb": host_gate["ram_free_gb"],
                "nvidia_smi": host_gate["nvidia_smi"],
                "bonsai_compatible": host_gate["bonsai_compatible"],
                "comfyui_online": host_gate["comfyui_online"],
                "block_reasons": host_gate["block_reasons"],
            },
            "scope": {
                "passed": scope_gate["passed"],
                "asset_role": scope_gate["asset_role"],
                "allowed_scopes": scope_gate["allowed_scopes"],
                "forbidden_scopes": scope_gate["forbidden_scopes"],
                "block_reasons": scope_gate["block_reasons"],
            },
        },
        "style_manifest_lookup": style_lookup,
        "fallback_chain": fallback_chain,
        "next_action": _derive_next_action(selected_source, license_gate, host_gate, scope_gate),
    }


def _derive_next_action(
    selected_source: str,
    license_gate: dict,
    host_gate: dict,
    scope_gate: dict,
) -> str:
    if selected_source in (
        "native_chat_image_generation_callable",
        "native_chat_inline_generation",
    ):
        return "use_native_channel"
    if selected_source == "license_blocked":
        return (
            "wait_for_human: create tools/ai_imagegen/runtime/bonsai/"
            "bonsai_license_ack.json per bonsai_license_ack.schema.json"
        )
    if selected_source == "scope_blocked":
        return (
            "fix_asset_role: must be one of "
            f"{scope_gate['allowed_scopes']}; current='{scope_gate['asset_role']}'"
        )
    if selected_source == "blocked_host_capability":
        return (
            "host_blocked: " + "; ".join(host_gate["block_reasons"])
            + ". Bonsai requires NVIDIA GPU (gemlite+HQQ/triton-windows) or Apple Silicon (mflux)."
        )
    return "ready"


# --- Bonsai commands ---


def cmd_bonsai_status(args):
    """Report Bonsai serve health + license gate + vendor manifest integrity."""
    license_gate = _license_gate_status()
    host_gate = _host_gate_status()
    online = _bonsai_serve_online()
    vendor_ok = True
    vendor_info: dict = {"present": False}
    if BONSAI_VENDOR_MANIFEST.exists():
        vendor_info["present"] = True
        try:
            vm = load_json(BONSAI_VENDOR_MANIFEST)
            vendor_info["commit_sha"] = vm.get("commit_sha", "")
            vendor_info["files"] = len(vm.get("files", []))
            vendor_info["missing_files"] = vm.get("missing_files", [])
        except Exception as e:
            vendor_ok = False
            vendor_info["error"] = str(e)
    report = {
        "timestamp": now_iso(),
        "backend": _bonsai_backend_label(),
        "port": BONSAI_PORT,
        "serve_online": online,
        "bonsai_dir_exists": BONSAI_DIR.exists(),
        "license": {
            "passed": license_gate["passed"],
            "ack_path": license_gate["ack_path"],
            "block_reasons": license_gate["block_reasons"],
        },
        "host": {
            "passed": host_gate["passed"],
            "bonsai_compatible": host_gate["bonsai_compatible"],
            "block_reasons": host_gate["block_reasons"],
        },
        "vendor": {
            "manifest_ok": vendor_ok,
            **vendor_info,
        },
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Backend: {report['backend']}  Port: {report['port']}")
        print(f"Serve online: {online}  Bonsai dir exists: {BONSAI_DIR.exists()}")
        print(f"License: {'PASS' if license_gate['passed'] else 'FAIL'}")
        print(f"Host: {'PASS' if host_gate['passed'] else 'FAIL'}")
        print(f"Vendor manifest: {'OK' if vendor_ok else 'FAIL'}")
    return report


def cmd_bonsai_install(args):
    """Clone Bonsai-Image-Demo (scripts only), generate vendor_manifest.json.

    Idempotent. Refuses if license ack is invalid.
    """
    license_gate = _license_gate_status()
    if not license_gate["passed"]:
        out = {
            "ok": False,
            "stage": "license_check",
            "block_reasons": license_gate["block_reasons"],
            "next_action": (
                "create tools/ai_imagegen/runtime/bonsai/bonsai_license_ack.json first"
            ),
        }
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print("REFUSED: license ack missing or invalid.")
        return out

    BONSAI_DIR.mkdir(parents=True, exist_ok=True)

    if (BONSAI_DIR / ".git").exists():
        ok, out, err = run_cmd(
            ["git", "-C", str(BONSAI_DIR), "pull", "--ff-only"], timeout=120
        )
    else:
        ok, out, err = run_cmd(
            ["git", "clone", "--depth", "1", BONSAI_REPO_URL, str(BONSAI_DIR)],
            timeout=600,
        )

    if not ok:
        report = {"ok": False, "stage": "git_clone", "stderr": err[:1000]}
        if args.json:
            print(json.dumps(report, indent=2))
        return report

    for ex in BONSAI_REPO_EXCLUDED:
        target = BONSAI_DIR / ex
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
            else:
                try:
                    target.unlink()
                except Exception:
                    pass

    commit_sha = ""
    ok_sha, out_sha, _ = run_cmd(
        ["git", "-C", str(BONSAI_DIR), "rev-parse", "HEAD"], timeout=10
    )
    if ok_sha:
        commit_sha = out_sha.strip()

    manifest_ok, manifest_path, missing = _write_vendor_manifest(
        BONSAI_DIR, BONSAI_REPO_URL, commit_sha, now_iso()
    )

    report = {
        "ok": manifest_ok,
        "bonsai_dir": str(BONSAI_DIR),
        "vendor_manifest": str(manifest_path),
        "commit_sha": commit_sha,
        "missing_files": missing,
        "excluded": BONSAI_REPO_EXCLUDED,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"OK={manifest_ok}  vendor_manifest={manifest_path}")
        if missing:
            print(f"Missing files: {missing}")
    return report


def cmd_bonsai_serve(args):
    """Start Bonsai serve in background. Refuses if license/host gates fail."""
    license_gate = _license_gate_status()
    host_gate = _host_gate_status()
    if not license_gate["passed"]:
        print("REFUSED: license ack missing or invalid.")
        return {"ok": False, "stage": "license"}
    if not host_gate["passed"]:
        print("REFUSED: host insufficient for Bonsai.")
        return {"ok": False, "stage": "host", "block_reasons": host_gate["block_reasons"]}

    BONSAI_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = BONSAI_LOG_DIR / f"serve_{uuid.uuid4().hex[:8]}.log"
    log_file = open(log_path, "w")

    ext = _bonsai_script_ext()
    serve_script = BONSAI_DIR / "scripts" / f"serve.{ext}"
    if not serve_script.exists():
        print(f"REFUSED: serve script not found at {serve_script}")
        print("Run: python tools/ai_imagegen/imagegen_tool.py bonsai install")
        return {"ok": False, "stage": "missing_serve_script"}

    if _is_windows():
        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(serve_script),
        ]
    else:
        cmd = ["bash", str(serve_script)]

    proc = subprocess.Popen(
        cmd, stdout=log_file, stderr=log_file, cwd=str(BONSAI_DIR)
    )

    session = {
        "backend": _bonsai_backend_label(),
        "port": BONSAI_PORT,
        "online": False,
        "pid": proc.pid,
        "started_at": now_iso(),
        "log_path": str(log_path),
        "model_id": "bonsai-4b-ternary",
        "model_variant": "ternary",
        "license_ack_path": license_gate["ack_path"],
        "license_ack_sha256": license_gate["ack_sha256"],
        "license_passed": True,
        "host_gpu_vendor": host_gate["gpu_vendor"],
        "host_gpu_model": host_gate["gpu_model"],
        "host_gpu_bonsai_compatible": host_gate["bonsai_compatible"],
    }
    save_json(BONSAI_SESSION_JSON, session)

    deadline = time.time() + (args.timeout or 120)
    while time.time() < deadline:
        if _bonsai_serve_online():
            session["online"] = True
            save_json(BONSAI_SESSION_JSON, session)
            if args.json:
                print(json.dumps({"ok": True, **session}, indent=2))
            else:
                print(f"Serve online at {_bonsai_serve_url()}  pid={proc.pid}")
            return {"ok": True, **session}
        time.sleep(2.0)

    if args.json:
        print(json.dumps({"ok": False, "stage": "timeout", "log_path": str(log_path)}, indent=2))
    else:
        print(f"Timed out waiting for serve. Log: {log_path}")
    return {"ok": False, "stage": "timeout", "log_path": str(log_path)}


def cmd_bonsai_generate(args):
    """Send a generation request to the running Bonsai serve.

    Refuses if license/scope/host gates fail. Writes prompt_pack_manifest.json.
    """
    license_gate = _license_gate_status()
    if not license_gate["passed"]:
        print("REFUSED: license ack missing or invalid.")
        return {"ok": False, "stage": "license"}
    scope_passed, _, scope_reasons = _validate_asset_scope(args.asset_role)
    if not scope_passed:
        print("REFUSED: asset_role out of Bonsai allowed_scopes.")
        print("Reasons:", scope_reasons)
        return {"ok": False, "stage": "scope", "block_reasons": scope_reasons}
    if not _bonsai_serve_online():
        print("REFUSED: Bonsai serve offline. Start with 'bonsai serve' first.")
        return {"ok": False, "stage": "serve_offline"}

    run_id = uuid.uuid4().hex[:12]
    ext = _bonsai_script_ext()
    send_script = BONSAI_DIR / "scripts" / f"send_request.{ext}"
    if not send_script.exists():
        print(f"REFUSED: send_request script missing at {send_script}")
        return {"ok": False, "stage": "missing_send_request"}

    out_dir_arg = args.output_dir or str(DATA_RAW_AI / run_id)
    out_dir = Path(out_dir_arg)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / "output.png"

    cmd = [
        "powershell" if _is_windows() else "bash",
        str(send_script),
        "-p",
        args.prompt or "",
        "--output",
        str(output_path),
    ]
    if args.seed is not None:
        cmd += ["--seed", str(args.seed)]
    if args.width and args.height:
        cmd += ["--size", f"{args.width}x{args.height}"]

    if args.dry_run:
        report = {
            "ok": False,
            "stage": "dry_run",
            "run_id": run_id,
            "command": cmd,
            "output_path": str(output_path),
        }
        print(json.dumps(report, indent=2))
        return report

    ok, out, err = run_cmd(cmd, cwd=str(BONSAI_DIR), timeout=args.timeout or 600)
    if not ok:
        print(f"FAILED: send_request exit_code!=0  stderr={err[:1000]}")
        return {"ok": False, "stage": "send_request", "stderr": err[:1000]}

    if not output_path.exists():
        print(f"FAILED: output not created at {output_path}")
        return {"ok": False, "stage": "no_output", "expected": str(output_path)}

    output_sha = _hash_file(output_path)
    profile_key = (
        "bonsai_4b_binary" if args.profile == "bonsai-4b-binary" else "bonsai_4b_ternary"
    )
    model_id = (
        "bonsai-4b-binary" if args.profile == "bonsai-4b-binary" else "bonsai-4b-ternary"
    )
    model_variant = "binary" if args.profile == "bonsai-4b-binary" else "ternary"

    pack_path = _write_prompt_pack_manifest(
        out_dir,
        run_id,
        args.prompt or "",
        args.negative or "",
        args.seed or 0,
        model_id,
        model_variant,
        "euler",
        4,
        1.0,
        args.width or 1024,
        args.height or 1024,
        profile_key,
        "local_bonsai_generation",
        output_sha,
        args.asset_role,
        license_gate["ack_sha256"],
        "",
    )

    gen_report = {
        "run_id": run_id,
        "timestamp": now_iso(),
        "source": "local",
        "profile": profile_key,
        "channel": "local_bonsai_generation",
        "asset_role": args.asset_role,
        "prompt": args.prompt or "",
        "negative_prompt": args.negative or "",
        "output_path": str(output_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "prompt_pack_path": str(pack_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "dimensions": f"{args.width or 1024}x{args.height or 1024}",
        "seed": args.seed or 0,
        "steps": 4,
        "cfg": 1.0,
        "model_id": model_id,
        "model_variant": model_variant,
        "license_ack_sha256": license_gate["ack_sha256"],
        "persisted_to_filesystem": True,
        "initial_status": "source_candidate",
    }
    save_json(out_dir / "generation_report.json", gen_report)

    if args.json:
        print(json.dumps({"ok": True, **gen_report}, indent=2))
    else:
        print(f"OK  output={output_path}  pack={pack_path}")
    return {"ok": True, **gen_report}


def cmd_vendor_manifest(args):
    """Verify SHA-256 of all vendored Bonsai scripts against vendor_manifest.json."""
    if not BONSAI_VENDOR_MANIFEST.exists():
        out = {"ok": False, "reason": "vendor_manifest.json not found"}
        print(json.dumps(out, indent=2))
        return out

    vm = load_json(BONSAI_VENDOR_MANIFEST)
    expected = {f["path"]: f["sha256"] for f in vm.get("files", [])}
    actual: dict = {}
    mismatches: list[dict] = []
    for rel, exp_sha in expected.items():
        p = BONSAI_DIR / rel
        if not p.exists():
            mismatches.append({"path": rel, "expected": exp_sha, "actual": "missing"})
            continue
        act_sha = _hash_file(p)
        actual[rel] = act_sha
        if act_sha != exp_sha:
            mismatches.append(
                {"path": rel, "expected": exp_sha, "actual": act_sha}
            )

    report = {
        "ok": len(mismatches) == 0,
        "checked": len(expected),
        "mismatches": mismatches,
        "commit_sha": vm.get("commit_sha", ""),
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"OK={report['ok']}  checked={report['checked']}  mismatches={len(mismatches)}")
        for m in mismatches:
            print(f"  MISMATCH: {m}")
    return report


def cmd_preflight(args):
    """Combined preflight: license + host + scope + style manifest + channel decision.

    Use --asset-role to enable the scope gate. Omit it for an advisory
    'just show host capability' preflight.
    """
    project_root: Path | None = None
    if args.project_root:
        project_root = Path(args.project_root).resolve()
    elif args.project:
        candidate = REPO_ROOT / "SGDK_projects" / args.project
        if candidate.exists():
            project_root = candidate

    asset_role = args.asset_role
    asset_role_required = bool(asset_role)

    report = _build_preflight_report(
        project_root=project_root,
        asset_role=asset_role,
        style_manifest_override=args.style_manifest,
        native_callable=args.native_callable,
        native_inline=args.native_inline,
        asset_role_required=asset_role_required,
    )

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        save_json(out_path, report)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Selected: {report['selected_source']}")
        print(f"Profile: {report['profile_used']}")
        print(f"License gate: {'PASS' if report['gates']['license']['passed'] else 'FAIL'}")
        print(f"Host gate:    {'PASS' if report['gates']['host']['passed'] else 'FAIL'}")
        print(f"Scope gate:   {'PASS' if report['gates']['scope']['passed'] else 'FAIL'}")
        print(f"Rationale: {report['rationale']}")
        print(f"Next: {report['next_action']}")
    return report


# --- CLI ---


def main():
    parser = argparse.ArgumentParser(
        description="MegaDrive_DEV Image Generation Toolchain"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Show host capability report")
    p_status.set_defaults(func=cmd_status)

    p_selfcheck = sub.add_parser(
        "self-check",
        help="Prove integrity of this tool's own artifacts (SGDK_GLOBAL.md secao 34)",
    )
    p_selfcheck.set_defaults(func=cmd_self_check)

    p_route = sub.add_parser("route", help="Decide generation channel (native vs local)")
    p_route.add_argument(
        "--native-callable",
        type=parse_bool_auto,
        default=None,
        help="Agent has callable native image gen",
    )
    p_route.add_argument(
        "--native-inline",
        type=parse_bool_auto,
        default=None,
        help="Agent has inline native image gen",
    )
    p_route.set_defaults(func=cmd_route)

    p_install = sub.add_parser("install", help="Install a generation profile (idempotent)")
    p_install.add_argument(
        "--profile",
        required=True,
        help="Profile name or alias (e.g. deck-safe, sdxl-lowvram, flux-schnell-gguf)",
    )
    p_install.add_argument("--dry-run", action="store_true")
    p_install.set_defaults(func=cmd_install)

    p_gen = sub.add_parser("generate", help="Generate an image via ComfyUI (local) profile")
    p_gen.add_argument("--profile", default="deck_safe_sd15")
    p_gen.add_argument("--prompt", default="")
    p_gen.add_argument("--negative", default="")
    p_gen.add_argument("--seed", type=int, default=None)
    p_gen.add_argument("--steps", type=int, default=None, help="Override sampler steps for this run")
    p_gen.add_argument("--width", type=int, default=None)
    p_gen.add_argument("--height", type=int, default=None)
    p_gen.add_argument("--timeout", type=float, default=600.0)
    p_gen.add_argument("--dry-run", action="store_true")
    p_gen.set_defaults(func=cmd_generate)

    p_conv = sub.add_parser("convert", help="Convert source_art image to SGDK-ready assets")
    p_conv.add_argument("--source", required=True, help="Path under data/source_art/")
    p_conv.add_argument("--spec", required=True, help="Path to tools/image-tools spec JSON")
    p_conv.add_argument(
        "--raw-path",
        default="",
        help="Optional original data/raw_ai/<run>/output.png for lineage trail",
    )
    p_conv.add_argument("--dry-run", action="store_true")
    p_conv.set_defaults(func=cmd_convert)

    p_hc = sub.add_parser("healthcheck", help="Run readiness checks (optionally per profile)")
    p_hc.add_argument(
        "--profile",
        default=None,
        help="Profile name or alias to check (defaults to recommended)",
    )
    p_hc.set_defaults(func=cmd_healthcheck)

    p_pre = sub.add_parser(
        "preflight",
        help="Combined preflight: license + host + scope + style manifest + channel decision",
    )
    p_pre.add_argument("--project", default=None, help="Project name (looked up under SGDK_projects/)")
    p_pre.add_argument("--project-root", default=None, help="Explicit project root path")
    p_pre.add_argument(
        "--asset-role",
        default=None,
        help="One of concept_art|tileset_concept|dither_mask|contrast_study|...",
    )
    p_pre.add_argument(
        "--style-manifest", default=None, help="Override path to master_style_manifest.json"
    )
    p_pre.add_argument(
        "--native-callable",
        type=parse_bool_auto,
        default=None,
    )
    p_pre.add_argument(
        "--native-inline",
        type=parse_bool_auto,
        default=None,
    )
    p_pre.add_argument("--out", default=None, help="Optional path to save preflight report")
    p_pre.set_defaults(func=cmd_preflight)

    p_vendor = sub.add_parser(
        "vendor-manifest", help="Verify SHA-256 of vendored Bonsai scripts"
    )
    p_vendor.set_defaults(func=cmd_vendor_manifest)

    p_bonsai = sub.add_parser(
        "bonsai", help="Bonsai-Image-Demo integration (license-gated, opt-in)"
    )
    bonsai_subs = p_bonsai.add_subparsers(dest="bonsai_command", required=True)

    p_bs_status = bonsai_subs.add_parser(
        "status", help="Report Bonsai serve + license + host + vendor status"
    )
    p_bs_status.set_defaults(func=cmd_bonsai_status)

    p_bs_install = bonsai_subs.add_parser(
        "install", help="Clone Bonsai-Image-Demo (scripts only) and emit vendor_manifest.json"
    )
    p_bs_install.set_defaults(func=cmd_bonsai_install)

    p_bs_serve = bonsai_subs.add_parser(
        "serve", help="Start Bonsai serve in background (requires license + host gates)"
    )
    p_bs_serve.add_argument("--timeout", type=float, default=120.0)
    p_bs_serve.set_defaults(func=cmd_bonsai_serve)

    p_bs_gen = bonsai_subs.add_parser(
        "generate", help="Send generation request to running Bonsai serve"
    )
    p_bs_gen.add_argument(
        "--profile",
        default="bonsai-4b-ternary",
        choices=["bonsai-4b-ternary", "bonsai-4b-binary"],
    )
    p_bs_gen.add_argument("--prompt", default="")
    p_bs_gen.add_argument("--negative", default="")
    p_bs_gen.add_argument(
        "--asset-role",
        required=True,
        choices=BONSAI_ALLOWED_SCOPES,
        help="MUST be one of the allowed_scopes for Bonsai",
    )
    p_bs_gen.add_argument("--seed", type=int, default=None)
    p_bs_gen.add_argument("--width", type=int, default=1024)
    p_bs_gen.add_argument("--height", type=int, default=1024)
    p_bs_gen.add_argument("--output-dir", default=None)
    p_bs_gen.add_argument("--timeout", type=float, default=600.0)
    p_bs_gen.add_argument("--dry-run", action="store_true")
    p_bs_gen.set_defaults(func=cmd_bonsai_generate)

    # Allow `--json` after the subcommand by hoisting it.
    if "--json" in sys.argv:
        idx = sys.argv.index("--json")
        rest = [a for i, a in enumerate(sys.argv) if i != idx]
        sys.argv = [rest[0], "--json"] + rest[1:]
    args = parser.parse_args()
    result = args.func(args)
    if isinstance(result, dict) and result.get("ok") is False:
        stage = result.get("stage", "unknown")
        # Map stage to a meaningful exit code that matches imagegen_circuit.py:
        # 2=license_blocked, 3=scope_blocked, 4=blocked_host_capability,
        # 5=forbidden scope, 6=backend refused, 7=filesystem error.
        stage_to_code = {
            "license": 2,
            "host": 4,
            "scope": 3,
            "missing_serve_script": 7,
            "missing_send_request": 7,
            "timeout": 6,
            "serve_offline": 6,
            "send_request": 6,
            "no_output": 7,
            "dry_run": 0,
        }
        sys.exit(stage_to_code.get(stage, 2))


if __name__ == "__main__":
    main()
