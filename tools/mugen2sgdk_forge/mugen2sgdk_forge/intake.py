"""Indice unico de intake das licoes MUGEN -> owners existentes do Forge.

O indice e GERADO a partir das fontes, nunca editado a mao, para nao virar mais
um lugar com status proprio:
  - licoes:   doc/curation/lessons_*mugen*.json (registros de candidatas);
  - status:   o parecer mais recente em doc/curation/*/lesson_adjudication.json
              (sem parecer: o enforcement_state do proprio registro);
  - owner:    proposed_owner do registro, resolvido contra o que EXISTE no repo
              (skill em tools/sgdk_wrapper/.agent/skills/**/<owner>/SKILL.md ou
              ferramenta em tools/<owner>/);
  - commit/hash: ultimo commit git que tocou o registro e o blob sha1 do arquivo.

`check()` e o lint de deriva: indice desatualizado, owner inexistente ou licao
marcada como promovida sem `canonized_in` reprovam.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

INDEX_JSON = "doc/curation/mugen_intake_index.json"
INDEX_MD = "doc/curation/mugen_intake_index.md"
SKILLS = "tools/sgdk_wrapper/.agent/skills"


def _git(repo: Path, *args: str) -> str:
    """Saida do git, ou "" se falhar (ex.: repo sem commits ainda)."""
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def _resolve_owner(repo: Path, owner: str) -> str | None:
    for skill in sorted((repo / SKILLS).glob(f"**/{owner}/SKILL.md")):
        return skill.relative_to(repo).as_posix()
    tool = repo / "tools" / owner
    return f"tools/{owner}/" if tool.is_dir() else None


def _adjudications(repo: Path) -> dict[str, dict]:
    """id -> parecer mais recente (pastas de curadoria sao datadas; a ultima vence)."""
    out: dict[str, dict] = {}
    for path in sorted((repo / "doc" / "curation").glob("*/lesson_adjudication.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for row in data.get("lessons", []):
            out[row["id"]] = dict(row, _file=path.relative_to(repo).as_posix())
    return out


def build(repo: Path) -> dict:
    adj = _adjudications(repo)
    rows = []
    for reg in sorted((repo / "doc" / "curation").glob("lessons_*mugen*.json")):
        rel = reg.relative_to(repo).as_posix()
        data = json.loads(reg.read_text(encoding="utf-8"))
        commit = _git(repo, "log", "-1", "--format=%H", "--", rel) or "uncommitted"
        blob = _git(repo, "hash-object", rel)
        for les in data["lessons"]:
            a = adj.get(les["id"])
            rows.append({
                "id": les["id"],
                "lesson": les["lesson"],
                "source": rel,
                "source_commit": commit,
                "source_blob_sha1": blob,
                "owner": les["proposed_owner"],
                "owner_path": _resolve_owner(repo, les["proposed_owner"]),
                "status": a["verdict"] if a else les.get("enforcement_state", "candidate"),
                "status_source": a["_file"] if a else rel,
                "promotion": (a or {}).get("promotion", "pending_human_review"),
                "canonized_in": les.get("canonized_in") or (a or {}).get("canonized_in") or [],
                "next_action": (a or {}).get("next_action", ""),
            })
    rows.sort(key=lambda r: (r["source"], r["id"]))
    return {
        "schema": "mugen2sgdk_forge.intake_index/v1",
        "generated_from": sorted({r["source"] for r in rows} | {r["status_source"] for r in rows}),
        "rule": "Gerado por `python3 -m mugen2sgdk_forge intake-index`. Nao editar: status mora nas fontes.",
        "lessons": rows,
    }


def render_md(index: dict) -> str:
    lines = [
        "# Indice de intake MUGEN -> owners",
        "",
        "Gerado por `python3 -m mugen2sgdk_forge intake-index` a partir das fontes abaixo; **nao editar**.",
        "Status mora no parecer de curadoria (ou no registro, sem parecer). Nenhuma linha aqui promove licao.",
        "",
        "Fontes: " + ", ".join(f"`{s}`" for s in index["generated_from"]),
        "",
        "|licao|owner (existente)|status|proxima acao|fonte@commit (blob)|",
        "|---|---|---|---|---|",
    ]
    for r in index["lessons"]:
        lines.append(
            f"|`{r['id']}`|{r['owner']} → `{r['owner_path']}`|{r['status']} ({r['promotion']})|"
            f"{r['next_action'] or '-'}|`{r['source']}`@{r['source_commit'][:8]} ({r['source_blob_sha1'][:8]})|")
    return "\n".join(lines) + "\n"


def write(repo: Path) -> dict:
    index = build(repo)
    (repo / INDEX_JSON).write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (repo / INDEX_MD).write_text(render_md(index), encoding="utf-8")
    return {"lessons": len(index["lessons"]), "json": INDEX_JSON, "md": INDEX_MD}


def check(repo: Path) -> list[str]:
    """Lint de deriva. Lista vazia = indice coerente com as fontes."""
    problems = []
    index = build(repo)
    for path, want in ((INDEX_JSON, json.dumps(index, indent=2, ensure_ascii=False) + "\n"),
                       (INDEX_MD, render_md(index))):
        cur = (repo / path).read_text(encoding="utf-8") if (repo / path).exists() else None
        if cur != want:
            problems.append(f"{path} desatualizado: rode `python3 -m mugen2sgdk_forge intake-index`")
    for r in index["lessons"]:
        if r["owner_path"] is None:
            problems.append(f"{r['id']}: owner '{r['owner']}' nao existe no repositorio")
        if r["promotion"] not in ("pending_human_review",) and not r["canonized_in"]:
            problems.append(f"{r['id']}: promocao '{r['promotion']}' sem canonized_in")
    return problems
