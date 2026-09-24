"""CLI do mugen2sgdk_forge.

    python3 -m mugen2sgdk_forge inventory <acervo> --out <json>
    python3 -m mugen2sgdk_forge install-runtime <projeto_sgdk>
    python3 -m mugen2sgdk_forge convert-char <pacote.zip|pasta> --id ken --project <projeto_sgdk>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from . import character, inventory
from .converters import bgfx as bgfx_conv
from .converters import sounds as snd_conv
from .converters import sprites as spr_conv
from .generators import sgdk
from .source import Source

TOOL_VERSION = "0.3.0"
RUNTIME_DIR = Path(__file__).resolve().parent.parent / "runtime"
RUNTIME_FILES = ["mg_types.h", "mg_runtime.h", "mg_vm.c", "mg_char.c", "mg_fight.c"]


def install_runtime(project: Path) -> dict:
    """Copia o runtime para src/mg/ e inc/mg/ e regenera mg_ops.h do contrato atual."""
    src, inc = project / "src" / "mg", project / "inc" / "mg"
    src.mkdir(parents=True, exist_ok=True)
    inc.mkdir(parents=True, exist_ok=True)
    out = {}
    ops = sgdk.ops_header()
    (RUNTIME_DIR / "mg_ops.h").write_text(ops, encoding="utf-8")
    for name in RUNTIME_FILES + ["mg_ops.h"]:
        dst = (inc if name.endswith(".h") else src) / name
        banner = f"/* COPIADO de tools/mugen2sgdk_forge/runtime/{name} (v{TOOL_VERSION}). Edite na fonte. */\n"
        body = (RUNTIME_DIR / name).read_text(encoding="utf-8")
        if name.endswith(".c"):   # headers vivem em inc/mg/ (-Iinc); fontes em src/mg/
            body = body.replace('#include "mg_', '#include "mg/mg_')
        data = banner + body
        dst.write_text(data, encoding="utf-8")
        out[dst.relative_to(project).as_posix()] = hashlib.sha256(data.encode()).hexdigest()
    return out


def _used_sounds(ch) -> set[int]:
    used = set()
    for st in ch.states.values():
        for c in st.controllers:
            for k in ("hitsound", "guardsound", "sound"):
                v = c.sym.get(k, -1)
                if v is not None and v >= 0:
                    used.add(v)
    return used


def convert_char(pkg: Path, char_id: str, project: Path, vivid_clothing: bool = False) -> dict:
    src = Source(pkg)
    ch = character.load(src)
    spr = spr_conv.convert(ch, vivid_clothing=vivid_clothing)
    used = _used_sounds(ch)
    snds, snd_rep = snd_conv.convert(ch, used)
    fx = bgfx_conv.detect(ch, spr.report["unsupported_images"])
    recovered = {(f.group) for f in fx}
    spr.report["unsupported_images"] = [u for u in spr.report["unsupported_images"] if u["sprite"][0] not in recovered]
    spr.report["bgfx"] = [f.report for f in fx]
    gen = sgdk.generate(ch, spr, snds, char_id, project, fx)

    cid = sgdk.ident(char_id)
    report = {
        "schema": "mugen2sgdk_forge.character_report/v1",
        "tool_version": TOOL_VERSION,
        "character": {"name": ch.name, "author": ch.author, "def": ch.def_path, "id": cid},
        "input": {"package": pkg.name, "sha256": ch.source_sha256},
        "license": {
            "status": "user_authorized_local_use",
            "redistribution": "not_verified",
            "note": "Conteudo de terceiros. Saidas ficam fora do Git ate permissao do autor.",
        },
        "classification": {
            "tool": "tools/mugen2sgdk_forge",
            "original_data": "pacote MUGEN (somente leitura, fora do repositorio)",
            "converted_data": "res/mugen/" + cid + "/ (technical_candidate; aprovacao visual humana pendente)",
            "generated_code": ["src/mg_gen/mg_" + cid + ".c", "inc/mg_gen/mg_" + cid + ".h", "res/mgres_" + cid + ".res"],
            "authored_by_forge": ["common_forge.cns (estados comuns)", "runtime mg_*.c"],
        },
        "fidelity": ch.report,
        "sprites": spr.report,
        "sounds": snd_rep,
        "generator": {k: v for k, v in gen.items() if k != "outputs"},
        "outputs": gen["outputs"],
        "warnings": ch.warnings,
    }
    doc = project / "doc" / "mugen"
    doc.mkdir(parents=True, exist_ok=True)
    (doc / f"{cid}_conversion_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True, default=str) + "\n", encoding="utf-8")
    _update_provenance(project, cid, ch, spr, snds)
    return report


def convert_hud(pkg: Path, project: Path) -> dict:
    """HUD de luta a partir de um pacote de lifebars MUGEN (fight.def). Saidas fora do Git (terceiros)."""
    import io as _io
    from .converters import hud as hud_conv
    h = hud_conv.convert(pkg)
    out_dir = project / "res" / "mugen" / "hud"
    out_dir.mkdir(parents=True, exist_ok=True)
    (project / "src" / "mg_gen").mkdir(parents=True, exist_ok=True)
    (project / "inc" / "mg_gen").mkdir(parents=True, exist_ok=True)
    outputs = {}

    def write(p, data):
        p.write_bytes(data)
        outputs[p.relative_to(project).as_posix()] = hashlib.sha256(data).hexdigest()

    def png(im):
        b = _io.BytesIO()
        im.save(b, format="PNG", optimize=False)
        return b.getvalue()

    res = ["// GERADO por mugen2sgdk_forge (convert-hud). Conteudo de terceiros: nao redistribuir.",
           'TILESET mg_hud_tiles "mugen/hud/hud_tiles.png" NONE NONE']
    write(out_dir / "hud_tiles.png", png(h.tiles))
    msg_rows = []
    for name, parts in h.messages.items():
        syms = []
        for k, im in enumerate(parts):
            fn = f"msg_{name}_{k}.png"
            write(out_dir / fn, png(im))
            sym = f"mg_hud_msg_{name}_{k}"
            res.append(f'SPRITE {sym} "mugen/hud/{fn}" {im.width // 8} {im.height // 8} FAST 0 NONE BALANCED')
            syms.append((sym, im.width, im.height))
        msg_rows.append((name, syms))
    write(project / "res" / "mgres_hud.res", ("\n".join(res) + "\n").encode())
    hdr = ["/* GERADO por mugen2sgdk_forge (convert-hud). Nao editar. */", "#ifndef MG_GEN_HUD_H", "#define MG_GEN_HUD_H",
           '#include "mg/mg_types.h"', f"#define MG_HUD_FIRST_SLOT {hud_conv.FIRST_SLOT}"]
    hdr += [f"#define MG_HUD_T_{k.upper()} {v}" for k, v in h.tile_index.items()]
    hdr += ["#define MG_HUD_MSG_PARTS 3",
            "typedef struct { const SpriteDefinition *def[MG_HUD_MSG_PARTS]; u8 nparts; u16 w[MG_HUD_MSG_PARTS], h; } MgHudMsg;",
            "enum { " + ", ".join(f"MG_HUD_MSG_{n.upper()}" for n, _ in msg_rows) + ", MG_HUD_NMSG };",
            "extern const MgHudMsg mg_hud_msgs[];", "extern const u16 mg_hud_pal[16];",
            "extern const TileSet mg_hud_tiles;", "#endif", ""]
    write(project / "inc" / "mg_gen" / "hud_gen.h", "\n".join(hdr).encode())
    c = ["/* GERADO por mugen2sgdk_forge (convert-hud). Nao editar. */", '#include "mg_gen/hud_gen.h"',
         '#include "mgres_hud.h"',
         "const u16 mg_hud_pal[16] = { " + ", ".join(f"0x{w:03X}" for w in h.palette) + " };",
         "const MgHudMsg mg_hud_msgs[] = {"]
    for name, syms in msg_rows:
        if len(syms) > 3:
            raise ValueError(f"mensagem {name} com {len(syms)} partes (limite 3)")
        d = ", ".join([f"&{s}" for s, _, _ in syms] + ["0"] * (3 - len(syms)))
        ws = ", ".join([str(w) for _, w, _ in syms] + ["0"] * (3 - len(syms)))
        c.append(f"    {{ {{ {d} }}, {len(syms)}, {{ {ws} }}, {syms[0][2]} }}, /* {name} */")
    c += ["};", ""]
    write(project / "src" / "mg_gen" / "hud_gen.c", "\n".join(c).encode())
    rep = dict(h.report, input={"package": pkg.name, "sha256": hashlib.sha256(pkg.read_bytes()).hexdigest()},
               outputs=outputs, license={"status": "user_authorized_local_use", "redistribution": "not_verified"})
    (project / "doc" / "mugen").mkdir(parents=True, exist_ok=True)
    (project / "doc" / "mugen" / "hud_conversion_report.json").write_text(
        json.dumps(rep, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    path = project / "doc" / "asset_provenance_manifest.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"schema_version": "1.0.0", "entries": []}
    data["entries"] = [e for e in data.get("entries", []) if not e.get("res_symbol", "").startswith("mg_hud_")]
    for sym, kind, ap in [("mg_hud_tiles", "TILESET", "mugen/hud/hud_tiles.png")] + \
            [(s, "SPRITE", f"mugen/hud/{s[len('mg_hud_'):]}.png") for _, syms in msg_rows for s, _, _ in syms]:
        data["entries"].append({"res_symbol": sym, "res_kind": kind, "asset_path": ap,
                                "source_kind": "third_party_mugen_conversion", "acceptance_status": "technical_candidate",
                                "generated_by": "tools/mugen2sgdk_forge (converters/hud.py)",
                                "notes": f"{pkg.name} (SFA2 Lifebars, Chok); uso local autorizado; redistribuicao nao verificada."})
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return rep


def _update_provenance(project: Path, cid: str, ch, spr, snds):
    """Registra cada simbolo do .res gerado em doc/asset_provenance_manifest.json (regra do Forge)."""
    path = project / "doc" / "asset_provenance_manifest.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"schema_version": "1.0.0", "entries": []}
    prefix = f"mg_{cid}_"
    data["entries"] = [e for e in data.get("entries", []) if not e.get("res_symbol", "").startswith(prefix)]
    for sh in spr.sheets:
        data["entries"].append({
            "res_symbol": f"mg_{cid}_{sh.name}", "res_kind": "SPRITE",
            "asset_path": f"mugen/{cid}/sheets/{sh.name}.png",
            "source_kind": "third_party_mugen_conversion", "acceptance_status": "technical_candidate",
            "generated_by": "tools/mugen2sgdk_forge (converters/sprites.py)",
            "notes": f"{ch.name} por {ch.author}; uso local autorizado pelo usuario; redistribuicao nao verificada."})
    extra = [("portrait", "TILESET", "retrato MUGEN 9000,0 (direto, paleta do corpo)"),
             ("shadow", "SPRITE", "DERIVADA: silhueta 0,0 achatada 32x8 + xadrez 50% (P5); aprovacao visual pendente")]
    for name, kind, note in extra:
        if (project / "res" / "mugen" / cid / f"{name}.png").exists():
            data["entries"].append({
                "res_symbol": f"mg_{cid}_{name}", "res_kind": kind, "asset_path": f"mugen/{cid}/{name}.png",
                "source_kind": "third_party_mugen_conversion", "acceptance_status": "technical_candidate",
                "generated_by": "tools/mugen2sgdk_forge (generators/sgdk.py)",
                "notes": f"{ch.name} por {ch.author}; {note}; redistribuicao nao verificada."})
    for rep in spr.report.get("bgfx", []):
        data["entries"].append({
            "res_symbol": f"mg_{cid}_bgfx_{rep['group']}", "res_kind": "IMAGE",
            "asset_path": f"mugen/{cid}/bgfx_{rep['group']}.png",
            "source_kind": "third_party_mugen_conversion", "acceptance_status": "technical_candidate",
            "generated_by": "tools/mugen2sgdk_forge (converters/bgfx.py)",
            "notes": f"{ch.name} por {ch.author}; fundo em tela cheia animado por paleta; geometria {rep['strategy']}."})
    for so in snds:
        data["entries"].append({
            "res_symbol": f"mg_{cid}_snd_{so.group}_{so.sample}", "res_kind": "WAV",
            "asset_path": f"mugen/{cid}/snd/{so.group}_{so.sample}.wav",
            "source_kind": "third_party_mugen_conversion", "acceptance_status": "technical_candidate",
            "generated_by": "tools/mugen2sgdk_forge (converters/sounds.py)",
            "notes": f"{ch.name} por {ch.author}; som {so.group},{so.sample}; redistribuicao nao verificada."})
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="mugen2sgdk_forge")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("inventory")
    a.add_argument("root")
    a.add_argument("--out", required=True)
    hb = sub.add_parser("convert-hud")
    hb.add_argument("package", type=Path)
    hb.add_argument("--project", type=Path, required=True)
    b = sub.add_parser("install-runtime")
    b.add_argument("project", type=Path)
    c = sub.add_parser("convert-char")
    c.add_argument("package", type=Path)
    c.add_argument("--id", required=True)
    c.add_argument("--project", type=Path, required=True)
    c.add_argument("--vivid-clothing", action="store_true",
                   help="redistribui o brilho das rampas de roupa (matiz/saturacao preservados; ver relatorio)")
    args = ap.parse_args(argv)
    if args.cmd == "inventory":
        return inventory.main([args.root, "--out", args.out])
    if args.cmd == "convert-hud":
        rep = convert_hud(args.package, args.project)
        print(json.dumps({"tiles": rep["tiles"], "messages": rep["messages"], "palette": rep["palette_slots"]}, indent=2))
        return 0
    if args.cmd == "install-runtime":
        print(json.dumps(install_runtime(args.project), indent=2))
        return 0
    rep = convert_char(args.package, args.id, args.project, args.vivid_clothing)
    fid = rep["fidelity"]
    print(json.dumps({"character": rep["character"], "controller_fidelity": fid["controller_fidelity"],
                      "missing_refs": fid["missing_refs"], "sheets": rep["sprites"]["sheets"],
                      "unsupported_images": len(rep["sprites"]["unsupported_images"]),
                      "sounds_rom_bytes": rep["sounds"]["rom_bytes_total"],
                      "bytecode_bytes": rep["generator"]["bytecode_bytes"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
