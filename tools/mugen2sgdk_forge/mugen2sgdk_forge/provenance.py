"""Proveniencia por simbolo no schema canonico do Forge
(tools/sgdk_wrapper/schemas/asset_provenance_manifest.schema.json).

O conversor gravava `source_kind: third_party_mugen_conversion` e
`acceptance_status: technical_candidate`, que nao existem no schema. O manifesto
inteiro ficava invalido e cada simbolo virava `asset_provenance_undeclared`, e
esse falso "sem proveniencia" escondia os achados reais.

Mapeamento, sem inventar enum:
  - source_kind = procedural_composed_from_authored: o codigo so recorta,
    quantiza e paletiza arte autoral que ja existia (o pacote MUGEN); a fonte e
    o hash ficam em authored_source / authored_source_hash, como o schema exige.
  - acceptance_status = placeholder: saida de maquina nao e arte final ate
    aprovacao visual humana, e a redistribuicao de terceiros nao foi verificada.
  - license declara a permissao como NAO verificada, em vez de omiti-la.
Sons nao sao simbolos visuais (o schema nao tem WAV): vao para
doc/mugen/<id>_audio_provenance.json.
"""
from __future__ import annotations

import json
from pathlib import Path

SOURCE_KIND = "procedural_composed_from_authored"
ACCEPTANCE = "placeholder"
LICENSE = "terceiros: uso local autorizado pelo usuario; redistribuicao NAO verificada"
PENDING = "technical_candidate: aprovacao visual humana pendente"
VISUAL_KINDS = {"IMAGE", "SPRITE", "TILESET", "TILEMAP", "MAP", "BITMAP", "PALETTE"}


def entry(symbol: str, kind: str, asset_path: str, generated_by: str,
          package: str, package_sha256: str, notes: str) -> dict:
    return {
        "res_symbol": symbol,
        "res_kind": kind,
        "asset_path": asset_path,
        "source_kind": SOURCE_KIND,
        "acceptance_status": ACCEPTANCE,
        "generated_by": generated_by,
        "authored_source": f"mugen-package:{package}",
        "authored_source_hash": f"sha256:{package_sha256}",
        "license": LICENSE,
        "notes": f"{notes}; {PENDING}",
    }


def write_visual(project: Path, prefix: str, entries: list[dict]) -> Path:
    """Troca as entradas com `prefix` pelas novas e grava o manifesto do projeto."""
    for e in entries:
        if e["res_kind"] not in VISUAL_KINDS:
            raise ValueError(f"{e['res_symbol']}: {e['res_kind']} nao e simbolo visual")
    path = project / "doc" / "asset_provenance_manifest.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
        "schema_version": "1.0.0", "declared_at": "1970-01-01T00:00:00Z", "entries": []}
    data["project_name"] = project.name
    data["entries"] = [e for e in data.get("entries", []) if not e.get("res_symbol", "").startswith(prefix)]
    data["entries"].extend(entries)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def write_audio(project: Path, cid: str, package: str, package_sha256: str, sounds: list[dict]) -> Path:
    path = project / "doc" / "mugen" / f"{cid}_audio_provenance.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "schema": "mugen2sgdk_forge.audio_provenance/v1",
        "package": package, "package_sha256": package_sha256, "license": LICENSE,
        "sounds": sounds,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def migrate(project: Path) -> dict:
    """Converte entradas antigas do conversor (enums fora do schema) sem reconverter.

    A fonte e o hash vem dos relatorios de conversao do proprio projeto; entradas
    WAV saem do manifesto visual para o arquivo de audio do personagem.
    """
    path = project / "doc" / "asset_provenance_manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    reports = {}
    for rep in (project / "doc" / "mugen").glob("*_conversion_report.json"):
        r = json.loads(rep.read_text(encoding="utf-8"))
        cid = r.get("character", {}).get("id") or rep.name.split("_conversion_report")[0]
        reports[cid] = r["input"]
    kept, audio, changed = [], {}, 0
    for e in data.get("entries", []):
        if e.get("source_kind") != "third_party_mugen_conversion":
            kept.append(e)
            continue
        sym = e["res_symbol"]
        cid = "hud" if sym.startswith("mg_hud_") else sym[3:].split("_", 1)[0]
        src = reports.get(cid)
        if src is None:
            raise ValueError(f"{sym}: sem relatorio de conversao para '{cid}'")
        if e["res_kind"] == "WAV":
            audio.setdefault(cid, (src, []))[1].append(
                {"res_symbol": sym, "asset_path": e["asset_path"], "notes": e.get("notes", "")})
            changed += 1
            continue
        notes = e.get("notes", "").split("; redistribuicao")[0].split("; uso local")[0]
        kept.append(entry(sym, e["res_kind"], e["asset_path"], e["generated_by"],
                          src["package"], src["sha256"], notes))
        changed += 1
    data["entries"] = kept
    data["project_name"] = project.name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for cid, (src, sounds) in audio.items():
        write_audio(project, cid, src["package"], src["sha256"], sounds)
    return {"migrated": changed, "audio_files": sorted(audio)}
