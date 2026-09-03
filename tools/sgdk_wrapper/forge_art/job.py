#!/usr/bin/env python3
"""Jobs imutaveis do forge-art (P0.4).

Contrato, conforme secao 5 do plano:

    out/visual_jobs/<asset_id>/<job_id>/
      input_manifest.json
      source_hashes.json
      toolchain_versions.json
      route_decision.json
      reports/
      basic/            (technical_candidate)
      review/
      promotion_candidate/
      job_state.json

Invariantes que este modulo garante e mede:

1. **Mesma fonte + mesma spec + mesmas versoes = mesmo `job_id`.** O id e o
   SHA-256 de um documento canonico (JSON com chaves ordenadas). Mudou o
   conteudo da fonte, um parametro, a versao de uma ferramenta ou a versao do
   schema, muda o id — logo o cache invalida sozinho, sem heuristica de data.

2. **`data/`, `res/` e TODA fonte declarada sao read-only.** O manifesto
   protegido cobre as duas arvores mais cada fonte da spec, esteja ela onde
   estiver no disco. E medido arquivo a arquivo na abertura e reconferido no
   fechamento — inclusive quando `work` levanta excecao, porque a reconciliacao
   roda em `finally`. Modificacao, criacao ou remocao reprova com
   `protected_tree_mutated`, o job NAO grava resultado, e o que da para desfazer
   e desfeito (fonte restaurada do backup, arquivo criado removido). O que nao
   da vem nomeado em `unrestorable`. Isto e contabilidade e reversao, **nao
   sandbox**: `work` e Python arbitrario.

2b. **Job sem evidencia real nao fica verde.** Nao basta ter arquivo em
   `basic/` ou em `reports/`. Exige-se: ao menos um PNG candidato em `basic/`,
   um `reports/pixel_compliance_report.json`, e que o relatorio fale do
   candidato **por hash canonico**, com `blocking == false` e o mesmo
   `index0_role` do job. Relatorio de outro arquivo nao e evidencia deste.

2c. **Cache hit e reconferido.** `job_state.json` registra o hash de tudo que
   foi publicado; `--resume` revalida contra o disco e reprova com
   `cache_tampered` se alguem editou um job ja fechado.

3. **Escrita atomica com rollback.** Todo o trabalho acontece em um diretorio
   temporario irmao, e so no fim ele e movido para o lugar definitivo por um
   unico `os.replace`. Falha no meio nao deixa job parcial no caminho canonico.

4. **Output parcial nunca substitui aprovado.** Um job que ja esta `completed`
   nunca e sobrescrito: `--resume` devolve o resultado existente e
   `--force-new-job` cria um id novo, sem apagar o antigo.

5. **Execucoes concorrentes nao colidem.** O diretorio temporario carrega pid e
   um sufixo aleatorio, e a publicacao usa `os.replace` sobre um destino que so
   e criado uma vez.

Limite declarado: isto garante procedencia, determinismo e auditabilidade do
processo. Nao diz nada sobre a QUALIDADE do que foi gerado. Job verde com
`status: technical_candidate` continua precisando de decisao humana registrada
para virar `visually_approved`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import sys
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

try:
    from forge_art import pixel_contract, schema_gate, vdp_color
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from forge_art import pixel_contract, schema_gate, vdp_color

SCHEMA_VERSION = "1.0.0"
TOOL_NAME = "forge_art.job"
TOOL_VERSION = "1.1.0"

JOB_ID_LENGTH = 16
JOBS_ROOT = Path("out") / "visual_jobs"

#: Arvores que a suite NUNCA pode escrever. Medidas antes e depois do trabalho.
#: `data/` guarda fonte; `res/` guarda o que ja foi promovido — nenhum job de
#: maquina promove nada sozinho.
PROTECTED_ROOTS = ("data", "res")

#: `asset_id` vira componente de caminho. Slug plano: sem separador, sem `..`,
#: sem nome relativo. Um `..` sozinho nao tem separador e escaparia do
#: `out/visual_jobs/` — por isso a checagem e por lista branca, nao por proibir
#: caracteres um a um.
ASSET_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

#: Diretorios fixos de todo job. `basic/` recebe saida de maquina; `review/`
#: recebe contact sheet e comparacoes; `promotion_candidate/` so e populado
#: depois de decisao humana registrada.
JOB_SUBDIRS = ("reports", "basic", "review", "promotion_candidate")

STATUS_PENDING = "pending"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

#: Status de saida. Nenhum job de maquina pode nascer `visually_approved`.
OUTPUT_TECHNICAL_CANDIDATE = "technical_candidate"
OUTPUT_VISUALLY_APPROVED = "visually_approved"

ROUTE_TECHNICAL = "technical_conversion"
ROUTE_ASSISTED = "assisted_native_translation"
ROUTES = (ROUTE_TECHNICAL, ROUTE_ASSISTED)


class JobContractError(RuntimeError):
    def __init__(self, blocker: str, message: str, next_action: str) -> None:
        super().__init__(f"[{blocker}] {message} | proxima acao: {next_action}")
        self.blocker = blocker
        self.next_action = next_action


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical_json(payload: Any) -> str:
    """JSON estavel: chaves ordenadas, separadores fixos, sem espaco variavel."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def toolchain_versions() -> dict[str, str]:
    """Versoes que participam do `job_id`.

    Mudar qualquer uma delas invalida o cache. E isso que impede o caso da
    secao 34: ferramenta obsoleta com self-check verde produzindo resultado que
    parece atual.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "forge_art.job": TOOL_VERSION,
        "forge_art.vdp_color": vdp_color.TOOL_VERSION,
        "forge_art.pixel_contract": pixel_contract.TOOL_VERSION,
        "python": platform.python_version(),
    }


@dataclass(frozen=True)
class JobSpec:
    """Entrada declarada de um job. Congelada: nao muda depois de criada."""

    asset_id: str
    sources: tuple[Path, ...]
    route: str
    index0_role: str
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not ASSET_ID_RE.match(self.asset_id or "") or ".." in self.asset_id:
            raise JobContractError(
                "invalid_asset_id",
                f"asset_id {self.asset_id!r} nao e um slug plano "
                f"(padrao {ASSET_ID_RE.pattern}, sem '..')",
                "use um identificador plano em snake_case, ex.: taina_idle_48x64",
            )
        if self.route not in ROUTES:
            raise JobContractError(
                "unknown_route",
                f"rota {self.route!r} invalida; validas: {list(ROUTES)}",
                f"classifique a fonte: pixel nativo -> {ROUTE_TECHNICAL}; "
                f"high-res de identidade -> {ROUTE_ASSISTED}",
            )
        if self.index0_role not in pixel_contract.INDEX0_ROLES:
            raise JobContractError(
                "index0_role_undeclared",
                f"papel do index 0 {self.index0_role!r} invalido",
                "declare transparent0 ou unused0 no contrato do asset",
            )
        if not self.sources:
            raise JobContractError(
                "no_source_declared",
                "job sem nenhuma fonte declarada",
                "declare ao menos uma fonte; job com denominador zero nao "
                "pode retornar sucesso",
            )
        for src in self.sources:
            if not Path(src).is_file():
                raise JobContractError(
                    "source_missing",
                    f"fonte {src} nao existe",
                    "confirme o caminho da fonte antes de abrir o job",
                )


def source_hashes(spec: JobSpec) -> dict[str, str]:
    """Hash de cada fonte, chaveado por caminho POSIX estavel."""
    return {Path(s).as_posix(): sha256_file(Path(s)) for s in spec.sources}


def compute_job_id(spec: JobSpec, hashes: dict[str, str] | None = None) -> str:
    """`job_id` deterministico.

    Deriva de: conteudo das fontes (nao do nome, do caminho ou do mtime), rota,
    papel do index 0, parametros e versoes do toolchain. Duas maquinas com o
    mesmo estado chegam ao mesmo id.

    O caminho absoluto da fonte NAO entra no documento. Se entrasse, o mesmo
    arquivo byte a byte em `/home/a/` e em `/home/b/` produziria ids
    diferentes, e o cache deixaria de ser portatil entre maquinas e entre
    checkouts — que e justamente o que ele promete.
    """
    hashes = hashes if hashes is not None else source_hashes(spec)
    document = {
        "asset_id": spec.asset_id,
        "route": spec.route,
        "index0_role": spec.index0_role,
        "params": spec.params,
        "source_content": sorted(hashes.values()),
        "toolchain": toolchain_versions(),
    }
    return hashlib.sha256(_canonical_json(document).encode("utf-8")).hexdigest()[:JOB_ID_LENGTH]


def job_dir(root: Path, spec: JobSpec, job_id: str) -> Path:
    return Path(root) / JOBS_ROOT / spec.asset_id / job_id


# ---------------------------------------------------------------------------
# Contencao de escrita
# ---------------------------------------------------------------------------

def tree_manifest(roots: Sequence[Path],
                  extra_files: Sequence[Path] = ()) -> dict[str, str]:
    """Mapa caminho -> SHA-256 de tudo que existe sob `roots`, mais `extra_files`.

    Serve para provar que o job nao tocou em nada protegido. Detecta as tres
    formas de dano: modificacao, criacao e remocao.

    `extra_files` existe porque uma fonte declarada nao precisa morar sob
    `data/`. Ela pode estar em qualquer lugar do disco — e uma versao anterior
    deste modulo so vigiava `data/` e `res/`, entao fonte externa era corrompida
    e o job ainda declarava `source_intact: true`. Toda fonte declarada entra
    aqui, esteja onde estiver.
    """
    manifest: dict[str, str] = {}
    for root in roots:
        root = Path(root)
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and not path.is_symlink():
                manifest[path.as_posix()] = sha256_file(path)
    for path in extra_files:
        path = Path(path)
        if path.is_file():
            manifest[path.as_posix()] = sha256_file(path)
        else:
            # Fonte removida durante o job tambem e dano. Sem entrada aqui, o
            # diff a veria como "deleted" — que e exatamente o que queremos.
            manifest.pop(path.as_posix(), None)
    return manifest


def _protected_paths(root: Path, spec: JobSpec) -> tuple[list[Path], list[Path]]:
    """Arvores protegidas e fontes declaradas, no formato de `tree_manifest`."""
    return ([Path(root) / name for name in PROTECTED_ROOTS],
            [Path(s) for s in spec.sources])


def _diff_manifest(before: dict[str, str], after: dict[str, str]) -> dict[str, list[str]]:
    return {
        "modified": sorted(k for k in before if k in after and after[k] != before[k]),
        "created": sorted(k for k in after if k not in before),
        "deleted": sorted(k for k in before if k not in after),
    }


# ---------------------------------------------------------------------------
# Execucao
# ---------------------------------------------------------------------------

#: Nome fixo do relatorio pixel-strict dentro de `reports/`. Fixo de proposito:
#: nome livre permitiria que qualquer arquivo em `reports/` passasse por
#: evidencia.
PIXEL_REPORT_NAME = "pixel_compliance_report.json"


def verify_evidence(staging: Path, index0_role: str) -> dict:
    """Exige candidato real E relatorio pixel-strict que corresponda a ele.

    A versao anterior so reprovava quando `basic/` e `reports/` estavam AMBOS
    vazios. Um `note.txt` em qualquer um dos dois comprava um
    `technical_candidate` — sem PNG, sem validacao, sem relacao entre o que foi
    produzido e o que foi medido. O vinculo e por hash: o relatorio tem que
    falar do arquivo que esta ali.

    E o relatorio NAO e autoridade. Casar o hash provava apenas que o relatorio
    se referia ao arquivo certo, nao que o veredito era verdadeiro: um JSON
    forjado com o hash correto e `blocking: false` aprovava um PNG que reprovava
    de fato. Por isso cada candidato e **remedido aqui**, e o relatorio entregue
    pela etapa de trabalho serve so como corroboracao — divergir dele e
    `pixel_report_contradicts_measurement`.
    """
    candidates = sorted(p for p in (staging / "basic").rglob("*.png") if p.is_file())
    if not candidates:
        raise JobContractError(
            "job_produced_no_candidate",
            f"basic/ nao contem nenhum PNG (conteudo: "
            f"{[p.name for p in (staging / 'basic').rglob('*') if p.is_file()][:6]})",
            "produza o candidato em basic/<nome>.png, ou reporte a falha da "
            "etapa de conversao em vez de concluir o job",
        )

    report_path = staging / "reports" / PIXEL_REPORT_NAME
    if not report_path.is_file():
        raise JobContractError(
            "job_missing_pixel_report",
            f"reports/{PIXEL_REPORT_NAME} ausente; ha candidato mas nao ha medicao",
            f"meça cada PNG de basic/ com forge_art.pixel_contract.validate_png "
            f"e grave o resultado em reports/{PIXEL_REPORT_NAME}",
        )
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise JobContractError(
            "pixel_report_corrupt", f"{PIXEL_REPORT_NAME} nao e JSON valido: {exc}",
            "regrave o relatorio; arquivo corrompido falha fechado",
        ) from exc

    entries = payload if isinstance(payload, list) else [payload]
    by_hash = {e.get("content_sha256"): e for e in entries if isinstance(e, dict)}

    verified: dict[str, str] = {}
    for candidate in candidates:
        digest = pixel_contract.canonical_content_hash(candidate)
        entry = by_hash.get(digest)
        rel = candidate.relative_to(staging).as_posix()
        if entry is None:
            raise JobContractError(
                "candidate_without_matching_report",
                f"{rel} tem hash canonico {digest[:16]}... e nenhuma entrada de "
                f"{PIXEL_REPORT_NAME} declara esse hash "
                f"(declarados: {[h[:16] for h in by_hash if h][:4]})",
                "o relatorio precisa medir o arquivo que foi realmente gravado; "
                "relatorio de outro arquivo nao e evidencia deste",
            )
        # Remedimos aqui. O relatorio da etapa de trabalho nao decide nada.
        measured = pixel_contract.validate_png(candidate, index0_role)
        # O callback so corrobora se entregou o laudo canonico completo. Um
        # JSON minimo com hash correto nao e evidencia auditavel.
        required = ("schema_version", "tool", "tool_version", "file",
                    "index0_role", "oracle", "width", "height", "bit_depth",
                    "color_type", "plte_entries", "visible_colors",
                    "content_sha256", "scope", "status", "blocking",
                    "blocking_statuses", "blockers")
        missing = [k for k in required if k not in entry]
        if missing:
            raise JobContractError("pixel_report_schema_incomplete",
                f"{rel}: relatorio sem campos canonicos {missing}",
                "grave o resultado completo de pixel_contract.validate_png")
        if entry["tool"] != pixel_contract.TOOL_NAME:
            raise JobContractError("pixel_report_tool_mismatch", f"{rel}: tool={entry['tool']!r}",
                "use forge_art.pixel_contract para medir o candidato")
        if entry["tool_version"] != pixel_contract.TOOL_VERSION or entry["schema_version"] != pixel_contract.SCHEMA_VERSION:
            raise JobContractError("pixel_report_version_mismatch", f"{rel}: versao/schema divergente",
                "regenere o relatorio com a versao atual da ferramenta")
        if measured["blocking"]:
            raise JobContractError(
                "candidate_rejected_by_pixel_contract",
                f"{rel} reprovou na medicao independente: "
                f"{measured['blocking_statuses']} "
                f"(o relatorio entregue dizia blocking={entry.get('blocking')})",
                "corrija o candidato; job com candidato reprovado nao pode se "
                "declarar technical_candidate",
            )
        if bool(entry.get("blocking")) != bool(measured["blocking"]) or \
                sorted(entry.get("blocking_statuses") or []) != measured["blocking_statuses"]:
            raise JobContractError(
                "pixel_report_contradicts_measurement",
                f"{rel}: relatorio declara blocking={entry.get('blocking')} "
                f"{entry.get('blocking_statuses')}, medicao independente diz "
                f"blocking={measured['blocking']} {measured['blocking_statuses']}",
                "o relatorio nao pode divergir da medicao; investigue quem o "
                "gerou antes de confiar em qualquer saida deste job",
            )
        canonical_fields = ("index0_role", "oracle", "width", "height", "bit_depth",
                            "color_type", "plte_entries", "visible_colors", "content_sha256",
                            "scope", "status", "blockers")
        if any(entry[k] != measured[k] for k in canonical_fields):
            raise JobContractError("pixel_report_measurement_mismatch",
                f"{rel}: campos tecnicos do relatorio divergem da remedição",
                "publique exatamente a medicao canônica do pixel_contract")
        if entry.get("index0_role") != index0_role:
            raise JobContractError(
                "pixel_report_role_mismatch",
                f"{rel} foi medido com index0_role={entry.get('index0_role')!r} "
                f"mas o job declara {index0_role!r}",
                "meça o candidato com o mesmo papel de index 0 declarado no job",
            )
        verified[rel] = digest
    return verified


def output_hashes(job_root: Path) -> dict[str, str]:
    """SHA-256 de todo arquivo publicado, exceto o proprio `job_state.json`."""
    out: dict[str, str] = {}
    for path in sorted(Path(job_root).rglob("*")):
        if path.is_file() and path.name != "job_state.json":
            out[path.relative_to(job_root).as_posix()] = sha256_file(path)
    return out


#: Campo que carrega o selo do proprio `job_state.json`.
STATE_SEAL_FIELD = "state_seal_sha256"


def compute_state_seal(state: dict) -> str:
    """Selo do proprio `job_state.json`.

    `output_hashes` cobria todo arquivo publicado MENOS o `job_state.json` —
    entao editar so o `job_state.json` passava batido, e `--resume` devolvia
    alegremente um estado adulterado para `visually_approved` com
    `promotable: true`. Essa e a fraude mais grave possivel neste modulo,
    porque e exatamente o portao que separa saida de maquina de decisao humana.

    O selo e o SHA-256 do JSON canonico do estado sem o proprio campo do selo.
    """
    return hashlib.sha256(
        _canonical_json({k: v for k, v in state.items() if k != STATE_SEAL_FIELD})
        .encode("utf-8")).hexdigest()


def verify_published_job(job_root: Path, spec: JobSpec) -> dict:
    """Reconfere um job JA publicado antes de reaproveita-lo.

    Chamado tanto pelo `--resume` quanto pelo caminho de publicacao concorrente
    — o perdedor da corrida lia o `job_state.json` do vencedor e o devolvia sem
    conferir nada, o que abria a mesma fraude por uma porta lateral.

    Confere, nesta ordem: selo do proprio estado, hashes de todo arquivo
    publicado, status de saida (nenhum job de maquina pode estar
    `visually_approved` nem `promotable`), e a evidencia — candidato remedido.
    """
    job_root = Path(job_root)
    state_path = job_root / "job_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    job_id = state.get("job_id", job_root.name)

    # Checksum interno detecta acidente; a defesa útil contra reseal e a
    # rederivação de tudo que veio da entrada viva.
    live_hashes = source_hashes(spec)
    expected_id = compute_job_id(spec, live_hashes)
    expected = {"schema_version": SCHEMA_VERSION, "tool": TOOL_NAME,
                "tool_version": TOOL_VERSION,
                "asset_id": spec.asset_id, "job_id": expected_id,
                "route": spec.route, "index0_role": spec.index0_role,
                "sources": list(live_hashes), "source_hashes": live_hashes,
                "toolchain_versions": toolchain_versions()}
    mismatch = [k for k, v in expected.items() if state.get(k) != v]
    if mismatch or job_root != job_dir(job_root.parents[3], spec, expected_id):
        raise JobContractError("cached_job_spec_mismatch",
            f"job publicado diverge da spec/fonte/toolchain viva: {mismatch}",
            "nao reescreva cache; refaça o job a partir da entrada atual")

    seal = state.get(STATE_SEAL_FIELD)
    if seal is None:
        raise JobContractError(
            "cache_without_state_seal",
            f"job {job_id} foi fechado por uma versao anterior, sem selo de "
            "estado; nao da para provar que o job_state.json nao foi editado",
            "use --force-new-job para refazer o job com o contrato atual",
        )
    if seal != compute_state_seal(state):
        raise JobContractError(
            "job_state_tampered",
            f"o job_state.json de {job_id} nao confere com o proprio selo: "
            f"declarado {seal[:16]}..., recalculado "
            f"{compute_state_seal(state)[:16]}...",
            "job concluido e imutavel; investigue quem editou "
            f"{state_path} e use --force-new-job para refazer",
        )

    declared = state.get("output_hashes")
    if declared is None:
        raise JobContractError(
            "cache_without_output_hashes",
            f"job {job_id} foi fechado sem registro de hash de saida",
            "use --force-new-job para refazer o job com o contrato atual",
        )
    actual = output_hashes(job_root)
    if actual != declared:
        drift = sorted(set(declared) ^ set(actual)) or sorted(
            k for k in declared if actual.get(k) != declared[k])
        raise JobContractError(
            "cache_tampered",
            f"conteudo do job {job_id} mudou depois de fechado: {drift[:6]}",
            "output concluido e imutavel; investigue quem editou "
            f"{job_root} e use --force-new-job para refazer",
        )

    if state.get("status") != STATUS_COMPLETED or state.get("output_status") != OUTPUT_TECHNICAL_CANDIDATE \
            or state.get("promotion", {}).get("promotable") or \
            state.get("promotion", {}).get("visual_gate") != "pending_human_decision" or \
            state.get("promotion", {}).get("technical_gate") != "see reports/":
        raise JobContractError(
            "cached_job_claims_visual_approval",
            f"job {job_id} publicado declara output_status="
            f"{state.get('output_status')!r} promotable="
            f"{state.get('promotion', {}).get('promotable')!r}; saida de "
            "maquina nunca satisfaz o portao visual",
            "aprovacao visual e decisao humana registrada fora do job_state; "
            "investigue quem escreveu isso",
        )

    # A evidencia e remedida, nao relida. Relatorio publicado nao e autoridade.
    verify_evidence(job_root, spec.index0_role)
    return state


def run_job(
    root: Path,
    spec: JobSpec,
    work: Callable[[Path], dict] | None = None,
    dry_run: bool = False,
    resume: bool = True,
    force_new_job: bool = False,
    explain: bool = False,
) -> dict:
    """Executa um job imutavel e devolve o `job_state`.

    `work` recebe o diretorio de staging do job e devolve um dict de resultado.
    Ele pode escrever livremente **ali dentro**; nada disso e publicado se ele
    levantar excecao.

    Contencao de escrita (limite declarado): `work` e codigo Python arbitrario
    e este modulo NAO e um sandbox — nao ha como impedir por construcao que ele
    chame `open()` em qualquer lugar. O que este modulo garante e:
    contabilidade completa e reversao. As arvores protegidas
    (`PROTECTED_ROOTS` sob `root`, mais toda fonte declarada) sao medidas
    arquivo a arquivo antes e depois. Qualquer modificacao, criacao ou remocao
    ali dentro reprova o job com `protected_tree_mutated`, e:

      - fonte modificada ou removida e **restaurada** do backup tirado na
        abertura;
      - arquivo criado dentro de arvore protegida e **removido**;
      - arquivo pre-existente de `res/` que o job modificou ou removeu nao tem
        backup e vem reportado em `unrestorable`, com o proximo passo nomeado.

    Sandbox de verdade (namespace read-only / bind mount) fica como trabalho
    futuro declarado; sem ele, isto e deteccao e reversao, nao prevencao.
    """
    root = Path(root)
    if work is None and not dry_run:
        raise JobContractError(
            "job_without_work_step",
            "run_job chamado sem etapa de trabalho: nenhum PNG, validacao ou "
            "relatorio seria produzido, mas o job terminaria 'completed'",
            "passe um callable `work` que produza evidencia, ou use "
            "dry_run=True se a intencao era so planejar",
        )
    hashes = source_hashes(spec)
    job_id = compute_job_id(spec, hashes)
    if force_new_job:
        # Um job forcado precisa de id proprio para nao apagar o determinstico.
        job_id = hashlib.sha256(
            (job_id + uuid.uuid4().hex).encode("utf-8")
        ).hexdigest()[:JOB_ID_LENGTH]

    final = job_dir(root, spec, job_id)

    plan = {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "asset_id": spec.asset_id,
        "job_id": job_id,
        "route": spec.route,
        "index0_role": spec.index0_role,
        "job_dir": str(final),
        "sources": list(hashes),
        "source_hashes": hashes,
        "toolchain_versions": toolchain_versions(),
        "cache_key_inputs": [
            "conteudo de cada fonte (SHA-256)", "rota", "papel do index 0",
            "parametros", "versoes de schema e ferramentas",
        ],
    }

    if explain:
        plan["explanation"] = (
            f"O job_id {job_id} deriva do conteudo de {len(hashes)} fonte(s), da rota "
            f"{spec.route}, do papel de index 0 {spec.index0_role}, dos parametros "
            f"declarados e de {len(toolchain_versions())} versoes de toolchain. "
            "Qualquer mudanca em qualquer um desses itens produz um id diferente, "
            "e por isso o cache nao precisa de invalidacao por data. "
            "A fonte nunca e escrita: os hashes acima sao reconferidos no fim."
        )

    # --- cache / resume -----------------------------------------------------
    state_path = final / "job_state.json"
    if state_path.is_file():
        existing = json.loads(state_path.read_text(encoding="utf-8"))
        if existing.get("status") == STATUS_COMPLETED:
            if not resume:
                raise JobContractError(
                    "job_already_completed",
                    f"job {job_id} ja concluido em {final}",
                    "use --resume para reaproveitar ou --force-new-job para "
                    "criar um id novo; output aprovado nunca e sobrescrito",
                )
            verify_published_job(final, spec)
            existing = json.loads(state_path.read_text(encoding="utf-8"))
            existing["cache_hit"] = True
            existing.update({k: v for k, v in plan.items() if k not in existing})
            return existing

    if dry_run:
        plan.update(status="dry_run", cache_hit=False,
                    would_create=[str(final / d) for d in JOB_SUBDIRS])
        return plan

    # --- trabalho em diretorio temporario irmao -----------------------------
    final.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(
        prefix=f".{job_id}.{os.getpid()}.", dir=final.parent))

    # Contabilidade das arvores protegidas + backup das fontes, ANTES do work.
    protected_roots, protected_files = _protected_paths(root, spec)
    before_tree = tree_manifest(protected_roots, protected_files)
    source_backup = {Path(s).as_posix(): Path(s).read_bytes() for s in spec.sources}
    reconciled = False

    def reconcile() -> None:
        """Confere as arvores protegidas e desfaz o que der.

        Roda no caminho feliz (antes de publicar) E no `finally` (caso `work`
        tenha levantado). Sem a segunda chamada, um callback que corrompe a
        fonte e depois levanta excecao ia direto para o rollback do staging, e
        a fonte ficava corrompida com o dano nao reportado — a proxima execucao
        mediria a corrupcao como se fosse a fonte.
        """
        nonlocal reconciled
        if reconciled:
            return
        reconciled = True
        diff = _diff_manifest(before_tree, tree_manifest(protected_roots, protected_files))
        if not any(diff.values()):
            return
        restored, unrestorable = _restore_protected(diff, source_backup)
        raise JobContractError(
            "protected_tree_mutated",
            f"arvore protegida ou fonte declarada escrita durante o job: "
            f"modificados={diff['modified'][:6]} criados={diff['created'][:6]} "
            f"removidos={diff['deleted'][:6]}; restaurados={restored}; "
            f"NAO restauraveis={unrestorable}",
            "data/, res/ e toda fonte declarada sao read-only para a suite; "
            "corrija a etapa de trabalho que escreveu fora do staging antes de "
            "confiar em qualquer saida deste job"
            + (f"; restaure manualmente de git: {unrestorable}" if unrestorable else ""),
        )

    try:
        for sub in JOB_SUBDIRS:
            (staging / sub).mkdir(parents=True, exist_ok=True)

        _write(staging / "input_manifest.json", {
            "schema_version": SCHEMA_VERSION,
            "asset_id": spec.asset_id, "job_id": job_id,
            "route": spec.route, "index0_role": spec.index0_role,
            "params": spec.params, "sources": list(hashes),
            "created_at": _utc_now(),
        })
        _write(staging / "source_hashes.json",
               {"schema_version": SCHEMA_VERSION, "algorithm": "sha256",
                "hashes": hashes})
        _write(staging / "toolchain_versions.json",
               {"schema_version": SCHEMA_VERSION, "versions": toolchain_versions()})
        route_decision = {
            "schema_version": SCHEMA_VERSION,
            "route": spec.route,
            "rationale": spec.params.get("route_rationale", "nao declarado"),
            "constraint": (
                "technical_conversion resolve conformidade e produz "
                "technical_candidate. assisted_native_translation exige "
                "construcao em canvas nativo e decisao humana registrada."
            ),
        }
        schema_gate.validate_named(route_decision, "route_decision")
        _write(staging / "route_decision.json", route_decision)

        result = work(staging)

        # --- nada protegido foi tocado? ------------------------------------
        reconcile()

        # --- o job produziu evidencia REAL? --------------------------------
        # Candidato PNG em basic/ + relatorio pixel-strict que fala DELE, por
        # hash. Denominador zero nao retorna verde (SGDK_GLOBAL secao 37), e
        # relatorio que nao corresponde ao artefato tambem nao e evidencia.
        produced = {
            sub: sorted(p.name for p in (staging / sub).rglob("*") if p.is_file())
            for sub in JOB_SUBDIRS
        }
        # Sem parametro de bypass. `require_evidence=False` existia e permitia
        # concluir um job vazio como technical_candidate — uma porta que anula
        # o proprio contrato nao pode ser opcional.
        verified = verify_evidence(staging, spec.index0_role)

        state = dict(plan)
        state.update({
            "status": STATUS_COMPLETED,
            "output_status": OUTPUT_TECHNICAL_CANDIDATE,
            "cache_hit": False,
            "completed_at": _utc_now(),
            "source_intact": True,
            "protected_trees_intact": True,
            "protected_roots": [p.as_posix() for p in protected_roots],
            "protected_files": [p.as_posix() for p in protected_files],
            "produced": produced,
            "verified_candidates": verified,
            "result": result,
            "promotion": {
                "technical_gate": "see reports/",
                "visual_gate": "pending_human_decision",
                "promotable": False,
                "why": (
                    "Promocao para res/ exige technical_candidate E "
                    "visually_approved. Saida de maquina nunca satisfaz o segundo."
                ),
            },
        })
        # Hashes de tudo que sera publicado, para que `--resume` possa provar
        # que o cache nao foi adulterado depois de fechado.
        state["output_hashes"] = output_hashes(staging)
        state[STATE_SEAL_FIELD] = compute_state_seal(state)
        schema_gate.validate_named(state, "job_state")
        _write(staging / "job_state.json", state)

        # --- publicacao atomica --------------------------------------------
        if final.exists():
            # Outro processo publicou o mesmo id enquanto trabalhavamos. Como o
            # id e deterministico, o conteudo e equivalente: descarta o nosso em
            # vez de sobrescrever trabalho de terceiro. Mas "equivalente" e
            # hipotese, nao fato: o job do vencedor passa pela MESMA validacao
            # do --resume antes de ser aceito.
            shutil.rmtree(staging, ignore_errors=True)
            return verify_published_job(final, spec)
        try:
            os.replace(staging, final)
            return state
        except OSError as exc:
            # TOCTOU: outro vencedor pode publicar entre exists() e replace().
            # Nunca devolvemos seu estado cru; revalidamos ou falhamos fechado.
            if final.exists():
                shutil.rmtree(staging, ignore_errors=True)
                return verify_published_job(final, spec)
            raise exc

    except Exception:
        # Rollback: nada parcial sobrevive no caminho canonico.
        shutil.rmtree(staging, ignore_errors=True)
        raise
    finally:
        # Rede de seguranca: se `work` levantou, o caminho feliz nunca chamou
        # `reconcile()`. Sem isto, corromper a fonte e levantar em seguida
        # escapava da deteccao E da restauracao.
        try:
            reconcile()
        except JobContractError:
            if sys.exc_info()[0] is None:
                raise
            # Ja ha uma excecao em voo (a do `work`). Nao a substituimos, mas o
            # dano ja foi revertido acima e o estrago fica registrado no stderr
            # para nao sumir em silencio.
            print("[forge-art] AVISO: a etapa de trabalho tambem corrompeu "
                  "arvore protegida; o dano foi revertido. Ver "
                  "protected_tree_mutated.", file=sys.stderr)


def _restore_protected(
    diff: dict[str, list[str]], source_backup: dict[str, bytes]
) -> tuple[list[str], list[str]]:
    """Desfaz o que der, e nomeia o que nao der.

    Detectar sem reverter deixa a arvore protegida suja depois de um job
    reprovado — o proximo job abriria sobre um estado ja corrompido e mediria a
    corrupcao como se fosse a fonte. Por isso a reversao acontece aqui, antes
    do rollback do staging.
    """
    restored: list[str] = []
    unrestorable: list[str] = []
    for key in diff["created"]:
        try:
            Path(key).unlink()
            restored.append(key)
        except OSError as exc:
            unrestorable.append(f"{key} ({exc.__class__.__name__})")
    for key in diff["modified"] + diff["deleted"]:
        blob = source_backup.get(key)
        if blob is None:
            # Sem backup: e um arquivo pre-existente de arvore protegida que
            # nao era fonte declarada deste job. Nao inventamos conteudo.
            unrestorable.append(key)
            continue
        try:
            Path(key).parent.mkdir(parents=True, exist_ok=True)
            Path(key).write_bytes(blob)
            restored.append(key)
        except OSError as exc:
            unrestorable.append(f"{key} ({exc.__class__.__name__})")
    return sorted(restored), sorted(unrestorable)


def _write(path: Path, payload: Any) -> None:
    """Escrita atomica de um arquivo do job."""
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------

def _fixture(name: str, kind: str, passed: bool, detail: str) -> dict:
    return {"fixture": name, "kind": kind,
            "status": "passed" if passed else "failed", "detail": detail}


def self_check() -> dict:
    fixtures: list[dict] = []

    with tempfile.TemporaryDirectory(prefix="forge_art_job_") as tmp:
        root = Path(tmp)
        src_dir = root / "data" / "source_art"
        src_dir.mkdir(parents=True)
        source = src_dir / "hero.png"
        pixel_contract._write_ok_sprite(source, 16, 16)

        def evidence(note: Any = 0):
            """Etapa de trabalho minima porem REAL: escreve artefato e relatorio.

            Existe porque `work` que nao produz nada nao pode gerar job verde.
            """
            def _work(staging: Path) -> dict:
                candidate = staging / "basic" / "out.png"
                pixel_contract._write_ok_sprite(candidate, 16, 16)
                _write(staging / "reports" / PIXEL_REPORT_NAME,
                       pixel_contract.validate_png(
                           candidate, pixel_contract.ROLE_TRANSPARENT0))
                return {"wrote": note}
            return _work

        def spec_for(**over) -> JobSpec:
            base = dict(asset_id="hero", sources=(source,),
                        route=ROUTE_TECHNICAL,
                        index0_role=pixel_contract.ROLE_TRANSPARENT0,
                        params={})
            base.update(over)
            return JobSpec(**base)

        spec = spec_for()

        # POSITIVA: id deterministico
        ids = {compute_job_id(spec) for _ in range(8)}
        fixtures.append(_fixture("job_id_is_deterministic", "positive",
                                 len(ids) == 1, f"id={ids.pop() if len(ids)==1 else ids}"))

        # POSITIVA: dry-run nao cria nada
        plan = run_job(root, spec, dry_run=True)
        created = (root / JOBS_ROOT).exists()
        fixtures.append(_fixture("dry_run_writes_nothing", "positive",
                                 plan["status"] == "dry_run" and not created,
                                 f"status={plan['status']} jobs_root_criado={created}"))

        # POSITIVA: --explain nomeia a causa do id
        expl = run_job(root, spec, dry_run=True, explain=True)
        fixtures.append(_fixture("explain_states_cache_key", "positive",
                                 "explanation" in expl and "job_id" in expl["explanation"],
                                 "explicacao presente e cita o job_id"))

        # POSITIVA: execucao cria a estrutura completa
        state = run_job(root, spec, work=evidence(0))
        jd = Path(state["job_dir"])
        expected = ["input_manifest.json", "source_hashes.json",
                    "toolchain_versions.json", "route_decision.json", "job_state.json"]
        missing = [f for f in expected if not (jd / f).is_file()]
        missing += [d for d in JOB_SUBDIRS if not (jd / d).is_dir()]
        fixtures.append(_fixture("job_dir_has_full_contract", "positive",
                                 not missing, f"faltando={missing or 'nada'}"))

        # POSITIVA: saida nasce technical_candidate e nao e promovivel
        fixtures.append(_fixture(
            "output_is_technical_candidate_only", "positive",
            state["output_status"] == OUTPUT_TECHNICAL_CANDIDATE
            and state["promotion"]["promotable"] is False
            and state["promotion"]["visual_gate"] == "pending_human_decision",
            f"output_status={state['output_status']} promotable={state['promotion']['promotable']}"))

        # POSITIVA: rerun = cache hit no MESMO diretorio
        again = run_job(root, spec, work=evidence(999), resume=True)
        fixtures.append(_fixture("resume_hits_cache", "positive",
                                 again.get("cache_hit") is True
                                 and again["job_dir"] == state["job_dir"]
                                 and again["result"] == {"wrote": 0},
                                 f"cache_hit={again.get('cache_hit')} "
                                 f"resultado preservado={again['result']}"))

        # POSITIVA: mudar parametro muda o id
        other = run_job(root, spec_for(params={"dither": "bayer2x2"}),
                        work=evidence(1))
        fixtures.append(_fixture("param_change_changes_job_id", "positive",
                                 other["job_id"] != state["job_id"],
                                 f"{state['job_id']} != {other['job_id']}"))

        # POSITIVA: mudar versao de toolchain invalida o cache
        real = vdp_color.TOOL_VERSION
        try:
            vdp_color.TOOL_VERSION = "9.9.9"
            bumped = compute_job_id(spec)
        finally:
            vdp_color.TOOL_VERSION = real
        fixtures.append(_fixture("toolchain_bump_invalidates_cache", "positive",
                                 bumped != state["job_id"],
                                 f"versao nova gera id {bumped} != {state['job_id']}"))

        # POSITIVA: --force-new-job nao apaga o anterior
        forced = run_job(root, spec, work=evidence(2), force_new_job=True)
        fixtures.append(_fixture("force_new_job_preserves_previous", "positive",
                                 forced["job_id"] != state["job_id"]
                                 and Path(state["job_dir"]).is_dir(),
                                 f"job anterior preservado em {state['job_dir']}"))

        # POSITIVA: fonte intacta byte a byte
        fixtures.append(_fixture("source_is_read_only", "positive",
                                 sha256_file(source) == state["source_hashes"][source.as_posix()],
                                 "hash da fonte identico ao da abertura"))

        # NEGATIVA: falha no meio nao deixa job parcial (rollback)
        def exploding(_d: Path) -> dict:
            raise RuntimeError("failure injection: quantizacao falhou")

        crash_spec = spec_for(params={"inject": "crash"})
        crash_dir = job_dir(root, crash_spec, compute_job_id(crash_spec))
        try:
            run_job(root, crash_spec, work=exploding)
            rolled, detail = False, "NAO levantou (falso verde)"
        except RuntimeError:
            leftovers = list(crash_dir.parent.glob(".*")) if crash_dir.parent.exists() else []
            rolled = not crash_dir.exists() and not leftovers
            detail = (f"job_dir criado={crash_dir.exists()} "
                      f"staging orfao={len(leftovers)}")
        fixtures.append(_fixture("failure_injection_rolls_back", "negative", rolled, detail))

        # NEGATIVA: fonte mutada durante o job reprova e nao publica
        mut_spec = spec_for(params={"inject": "mutate"})
        mut_dir = job_dir(root, mut_spec, compute_job_id(mut_spec))

        def mutate(_d: Path) -> dict:
            with open(source, "ab") as fh:
                fh.write(b"\x00")
            return {}

        original_bytes = source.read_bytes()
        try:
            run_job(root, mut_spec, work=mutate)
            mut_ok, mut_detail = False, "NAO levantou (falso verde)"
        except JobContractError as exc:
            mut_ok = (exc.blocker == "protected_tree_mutated"
                      and not mut_dir.exists())
            mut_detail = f"levantou {exc.blocker}; job publicado={mut_dir.exists()}"
        fixtures.append(_fixture("rejects_source_mutation", "negative", mut_ok, mut_detail))

        # NEGATIVA: e a fonte foi RESTAURADA, nao apenas detectada.
        # Detectar sem reverter deixa a proxima execucao medindo a corrupcao.
        fixtures.append(_fixture(
            "restores_mutated_source", "negative",
            source.read_bytes() == original_bytes,
            "fonte voltou byte a byte ao estado da abertura"))
        source.write_bytes(original_bytes)

        # NEGATIVA: escrita externa em res/ e barrada e desfeita
        res_dir = root / "res"
        res_dir.mkdir(exist_ok=True)
        injected = res_dir / "injected.txt"
        ext_spec = spec_for(params={"inject": "external_write"})
        ext_dir = job_dir(root, ext_spec, compute_job_id(ext_spec))

        def writes_outside(staging: Path) -> dict:
            injected.write_text("promocao automatica disfarcada de conversao")
            return {}

        try:
            run_job(root, ext_spec, work=writes_outside)
            ext_ok, ext_detail = False, "NAO levantou (falso verde)"
        except JobContractError as exc:
            ext_ok = (exc.blocker == "protected_tree_mutated"
                      and not injected.exists() and not ext_dir.exists())
            ext_detail = (f"levantou {exc.blocker}; arquivo injetado sobreviveu="
                          f"{injected.exists()}; job publicado={ext_dir.exists()}")
        fixtures.append(_fixture("rejects_external_write_to_res", "negative",
                                 ext_ok, ext_detail))

        # NEGATIVA: evidencia ausente, parcial ou desalinhada nao vira verde.
        # Cada caso abaixo passava na versao anterior, que so exigia "algum
        # arquivo em basic/ OU em reports/".
        def only_reports(staging: Path) -> dict:
            (staging / "reports" / "note.txt").write_text("nada a ver")
            return {}

        def only_basic(staging: Path) -> dict:
            (staging / "basic" / "note.txt").write_text("nem PNG e")
            return {}

        def png_without_report(staging: Path) -> dict:
            pixel_contract._write_ok_sprite(staging / "basic" / "out.png", 16, 16)
            return {}

        def report_of_another_file(staging: Path) -> dict:
            pixel_contract._write_ok_sprite(staging / "basic" / "out.png", 16, 16)
            outro = staging / "review" / "outro.png"
            pixel_contract._write_ok_sprite(outro, 24, 16)
            _write(staging / "reports" / PIXEL_REPORT_NAME,
                   pixel_contract.validate_png(outro, pixel_contract.ROLE_TRANSPARENT0))
            return {}

        for name, blocker, fn in (
            ("rejects_job_without_evidence", "job_produced_no_candidate",
             lambda d: {"note": "nao fiz nada"}),
            ("rejects_evidence_only_in_reports", "job_produced_no_candidate", only_reports),
            ("rejects_evidence_only_in_basic", "job_produced_no_candidate", only_basic),
            ("rejects_candidate_without_report", "job_missing_pixel_report",
             png_without_report),
            ("rejects_report_of_another_file", "candidate_without_matching_report",
             report_of_another_file),
        ):
            try:
                run_job(root, spec_for(params={"inject": name}), work=fn)
                ok, detail = False, "NAO levantou (falso verde)"
            except JobContractError as exc:
                ok = exc.blocker == blocker
                detail = f"levantou {exc.blocker} (esperado {blocker})"
            fixtures.append(_fixture(name, "negative", ok, detail))

        # NEGATIVA: run_job sem etapa de trabalho falha fechado
        try:
            run_job(root, spec_for(params={"inject": "no_work"}), work=None)
            nw_ok, nw_detail = False, "NAO levantou (falso verde)"
        except JobContractError as exc:
            nw_ok = exc.blocker == "job_without_work_step"
            nw_detail = f"levantou {exc.blocker}"
        fixtures.append(_fixture("rejects_job_without_work_step", "negative",
                                 nw_ok, nw_detail))

        # NEGATIVA: fonte declarada FORA de data/ e res/ tambem e protegida.
        # A versao anterior so vigiava as duas arvores, entao fonte externa era
        # corrompida e o job ainda devolvia source_intact=true.
        outside = root / "fora_das_arvores"
        outside.mkdir()
        ext_source = outside / "hero_externo.png"
        pixel_contract._write_ok_sprite(ext_source, 16, 16)
        ext_original = ext_source.read_bytes()
        ext_src_spec = JobSpec(asset_id="hero_externo", sources=(ext_source,),
                               route=ROUTE_TECHNICAL,
                               index0_role=pixel_contract.ROLE_TRANSPARENT0,
                               params={"inject": "external_source"})

        def corrupts_external(staging: Path) -> dict:
            ext_source.write_bytes(b"\x89PNG\r\n\x1a\ncorrompido")
            return evidence(0)(staging)

        try:
            st = run_job(root, ext_src_spec, work=corrupts_external)
            ext_ok2 = False
            ext_detail2 = (f"NAO levantou (falso verde): status={st['status']} "
                           f"source_intact={st.get('source_intact')}")
        except JobContractError as exc:
            ext_ok2 = (exc.blocker == "protected_tree_mutated"
                       and ext_source.read_bytes() == ext_original)
            ext_detail2 = (f"levantou {exc.blocker}; fonte externa restaurada="
                           f"{ext_source.read_bytes() == ext_original}")
        ext_source.write_bytes(ext_original)
        fixtures.append(_fixture("protects_source_outside_data_and_res",
                                 "negative", ext_ok2, ext_detail2))

        # NEGATIVA: mutar a fonte E levantar excecao nao escapa da restauracao.
        # O caminho feliz nunca roda nesse cenario; quem salva e o `finally`.
        def mutate_then_raise(staging: Path) -> dict:
            source.write_bytes(b"mutated then raised")
            raise RuntimeError("failure injection depois de sujar a fonte")

        mr_spec = spec_for(params={"inject": "mutate_then_raise"})
        try:
            run_job(root, mr_spec, work=mutate_then_raise)
            mr_ok, mr_detail = False, "NAO levantou (falso verde)"
        except (RuntimeError, JobContractError) as exc:
            mr_ok = source.read_bytes() == original_bytes
            mr_detail = (f"levantou {type(exc).__name__}; fonte restaurada="
                         f"{source.read_bytes() == original_bytes}")
        source.write_bytes(original_bytes)
        fixtures.append(_fixture("restores_source_when_work_raises", "negative",
                                 mr_ok, mr_detail))

        # NEGATIVA: job concluido editado por fora nao e reaproveitado como cache.
        tamper_spec = spec_for(params={"inject": "tamper"})
        tampered = run_job(root, tamper_spec, work=evidence(7))
        (Path(tampered["job_dir"]) / "basic" / "out.png").write_bytes(b"editado por fora")
        try:
            run_job(root, tamper_spec, work=evidence(7), resume=True)
            tp_ok, tp_detail = False, "NAO levantou (cache adulterado aceito)"
        except JobContractError as exc:
            tp_ok = exc.blocker == "cache_tampered"
            tp_detail = f"levantou {exc.blocker}"
        fixtures.append(_fixture("rejects_tampered_cache", "negative", tp_ok, tp_detail))

        # NEGATIVA: relatorio forjado com o hash CERTO nao aprova PNG reprovado.
        # Casar o hash so provava que o relatorio falava do arquivo certo, nao
        # que o veredito era verdadeiro.
        def forged_report(staging: Path) -> dict:
            from PIL import Image
            candidate = staging / "basic" / "off_grid.png"
            img = Image.new("P", (16, 16))
            img.putpalette([0x00, 0x00, 0x00, 0xFF, 0x80, 0x00] + [0] * 762)
            px = img.load()
            for y in range(16):
                for x in range(16):
                    px[x, y] = 0 if (x == 0 or y == 0) else 1
            img.save(candidate, "PNG", bits=4, transparency=0)
            real = pixel_contract.validate_png(
                candidate, pixel_contract.ROLE_TRANSPARENT0)
            fake = dict(real)
            fake.update(blocking=False, blocking_statuses=[],
                        status="technical_candidate")
            _write(staging / "reports" / PIXEL_REPORT_NAME, fake)
            return {}

        try:
            run_job(root, spec_for(params={"inject": "forged"}), work=forged_report)
            fg_ok, fg_detail = False, "NAO levantou (relatorio forjado aceito)"
        except JobContractError as exc:
            fg_ok = exc.blocker == "candidate_rejected_by_pixel_contract"
            fg_detail = f"levantou {exc.blocker}"
        fixtures.append(_fixture("rejects_forged_pixel_report", "negative",
                                 fg_ok, fg_detail))

        # P0.4.3: laudo minimo ou com identidade da ferramenta adulterada nao
        # pode comprar evidencia, mesmo para PNG valido.
        for name, mutate_report, blocker in (
            ("rejects_minimal_pixel_report", lambda r: {k:r[k] for k in ("content_sha256","index0_role","blocking","blocking_statuses")}, "pixel_report_schema_incomplete"),
            ("rejects_report_tool_mismatch", lambda r: dict(r, tool="forged.tool"), "pixel_report_tool_mismatch"),
            ("rejects_report_version_mismatch", lambda r: dict(r, tool_version="0.0"), "pixel_report_version_mismatch"),
            ("rejects_report_measurement_mismatch", lambda r: dict(r, width=99), "pixel_report_measurement_mismatch"),
        ):
            def bad_report(staging, mut=mutate_report):
                candidate = staging / "basic" / "out.png"
                pixel_contract._write_ok_sprite(candidate, 16, 16)
                _write(staging / "reports" / PIXEL_REPORT_NAME,
                       mut(pixel_contract.validate_png(candidate, pixel_contract.ROLE_TRANSPARENT0)))
                return {}
            try:
                run_job(root, spec_for(params={"inject": name}), work=bad_report)
                ok, detail = False, "NAO levantou"
            except JobContractError as exc:
                ok, detail = exc.blocker == blocker, exc.blocker
            fixtures.append(_fixture(name, "negative", ok, detail))

        # NEGATIVA: editar SO o job_state.json para se autoaprovar e barrado.
        # `output_hashes` cobria todo arquivo menos o proprio job_state.
        seal_spec = spec_for(params={"inject": "seal"})
        sealed = run_job(root, seal_spec, work=evidence(11))
        state_file = Path(sealed["job_dir"]) / "job_state.json"
        forged_state = json.loads(state_file.read_text(encoding="utf-8"))
        forged_state["output_status"] = OUTPUT_VISUALLY_APPROVED
        forged_state["promotion"] = {"promotable": True, "visual_gate": "passed"}
        state_file.write_text(json.dumps(forged_state), encoding="utf-8")
        try:
            back = run_job(root, seal_spec, work=evidence(11), resume=True)
            sl_ok = False
            sl_detail = (f"NAO levantou: output={back['output_status']} "
                         f"promotable={back['promotion']['promotable']}")
        except JobContractError as exc:
            sl_ok = exc.blocker == "job_state_tampered"
            sl_detail = f"levantou {exc.blocker}"
        fixtures.append(_fixture("rejects_self_approved_job_state", "negative",
                                 sl_ok, sl_detail))

        # NEGATIVA: e mesmo se o selo fosse recalculado, o estado autoaprovado
        # nao passa. Sao duas barreiras independentes de proposito.
        forged_state[STATE_SEAL_FIELD] = compute_state_seal(forged_state)
        state_file.write_text(json.dumps(forged_state), encoding="utf-8")
        try:
            run_job(root, seal_spec, work=evidence(11), resume=True)
            sl2_ok, sl2_detail = False, "NAO levantou (autoaprovacao selada aceita)"
        except JobContractError as exc:
            sl2_ok = exc.blocker == "cached_job_claims_visual_approval"
            sl2_detail = f"levantou {exc.blocker}"
        fixtures.append(_fixture("rejects_resealed_visual_gate_passed", "negative",
                                 sl2_ok, sl2_detail))

        lineage_spec = spec_for(params={"inject": "resealed_lineage"})
        lineage = run_job(root, lineage_spec, work=evidence(12))
        lineage_file = Path(lineage["job_dir"]) / "job_state.json"
        fake_lineage = json.loads(lineage_file.read_text(encoding="utf-8"))
        fake_lineage.update(asset_id="outro_asset", source_hashes={"fonte_inventada.png": "0" * 64}, toolchain_versions={"fake":"0.0"})
        fake_lineage[STATE_SEAL_FIELD] = compute_state_seal(fake_lineage)
        lineage_file.write_text(json.dumps(fake_lineage), encoding="utf-8")
        try:
            run_job(root, lineage_spec, work=evidence(12), resume=True)
            ln_ok, ln_detail = False, "NAO levantou"
        except JobContractError as exc:
            ln_ok, ln_detail = exc.blocker == "cached_job_spec_mismatch", exc.blocker
        fixtures.append(_fixture("rejects_resealed_lineage", "negative", ln_ok, ln_detail))

        # NEGATIVA: vencedor TOCTOU adulterado entre exists() e replace().
        race_spec = spec_for(params={"inject": "toctou_adversarial"})
        real_replace = os.replace
        def race_replace(src, dst):
            if Path(dst) == job_dir(root, race_spec, compute_job_id(race_spec)):
                shutil.copytree(src, dst)
                winner = Path(dst) / "job_state.json"
                payload = json.loads(winner.read_text(encoding="utf-8"))
                payload["promotion"]["visual_gate"] = "passed"
                payload[STATE_SEAL_FIELD] = compute_state_seal(payload)
                winner.write_text(json.dumps(payload), encoding="utf-8")
                raise FileExistsError("adversarial winner published")
            return real_replace(src, dst)
        os.replace = race_replace
        try:
            run_job(root, race_spec, work=evidence(13))
            race_ok, race_detail = False, "NAO levantou"
        except JobContractError as exc:
            race_ok, race_detail = exc.blocker == "cached_job_claims_visual_approval", exc.blocker
        finally:
            os.replace = real_replace
        leftovers = list(job_dir(root, race_spec, compute_job_id(race_spec)).parent.glob(".*"))
        fixtures.append(_fixture("concurrent_winner_is_revalidated", "negative",
                                 race_ok and not leftovers, f"{race_detail}; staging={len(leftovers)}"))

        # NEGATIVA: arquivo pre-existente de res/ modificado nao e restauravel,
        # mas tem que ser reprovado E nomeado — nao inventamos o conteudo dele.
        guard = res_dir / "ja_promovido.png"
        pixel_contract._write_ok_sprite(guard, 16, 16)
        before_tree_guard = guard.read_bytes()
        pre_spec = spec_for(params={"inject": "overwrite_res"})

        def overwrites_res(staging: Path) -> dict:
            guard.write_bytes(b"sobrescrito")
            return evidence(0)(staging)

        try:
            run_job(root, pre_spec, work=overwrites_res)
            pr_ok, pr_detail = False, "NAO levantou (falso verde)"
        except JobContractError as exc:
            pr_ok = (exc.blocker == "protected_tree_mutated"
                     and "restaure manualmente" in exc.next_action)
            pr_detail = (f"levantou {exc.blocker}; nomeou o nao-restauravel="
                         f"{'restaure manualmente' in exc.next_action}")
        guard.write_bytes(before_tree_guard)
        fixtures.append(_fixture("names_unrestorable_res_file", "negative",
                                 pr_ok, pr_detail))

        # POSITIVA: duas execucoes do mesmo job nao colidem nem se corrompem.
        conc_spec = spec_for(params={"inject": "concurrent"})
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(run_job, root, conc_spec, work=evidence(9))
                       for _ in range(2)]
            outcomes = []
            for fut in futures:
                try:
                    outcomes.append(fut.result())
                except JobContractError as exc:
                    outcomes.append(exc)
        states = [o for o in outcomes if isinstance(o, dict)]
        conc_ok = (len(states) == 2
                   and states[0]["job_dir"] == states[1]["job_dir"]
                   and Path(states[0]["job_dir"]).is_dir()
                   and not list(Path(states[0]["job_dir"]).parent.glob(".*")))
        fixtures.append(_fixture(
            "concurrent_runs_do_not_collide", "positive", conc_ok,
            f"{len(states)}/2 concluiram no mesmo job_dir; staging orfao="
            f"{len(list(Path(states[0]['job_dir']).parent.glob('.*'))) if states else 'n/a'}"))

        # POSITIVA: o mesmo conteudo em outro caminho gera o MESMO job_id.
        # Cache que depende do caminho absoluto nao e portatil entre maquinas.
        elsewhere = root / "outra_arvore"
        elsewhere.mkdir()
        twin = elsewhere / "outro_nome.png"
        twin.write_bytes(source.read_bytes())
        fixtures.append(_fixture(
            "job_id_is_portable_across_paths", "positive",
            compute_job_id(spec) == compute_job_id(spec_for(sources=(twin,))),
            f"id={compute_job_id(spec)} identico para o mesmo conteudo em "
            f"caminho e nome diferentes"))

        # NEGATIVA: job concluido nao e sobrescrito sem resume
        try:
            run_job(root, spec, work=evidence(3), resume=False)
            ovw, ovw_detail = False, "NAO levantou (falso verde)"
        except JobContractError as exc:
            ovw = exc.blocker == "job_already_completed"
            ovw_detail = f"levantou {exc.blocker}"
        still = json.loads((Path(state["job_dir"]) / "job_state.json").read_text())
        fixtures.append(_fixture("completed_job_never_overwritten", "negative",
                                 ovw and still["result"] == {"wrote": 0},
                                 f"{ovw_detail}; resultado original preservado"))

        # NEGATIVA: rota desconhecida falha fechado
        for name, blocker, kwargs in (
            ("rejects_unknown_route", "unknown_route", {"route": "quantize_and_pray"}),
            ("rejects_undeclared_index0_role", "index0_role_undeclared",
             {"index0_role": "whatever"}),
            ("rejects_missing_source", "source_missing",
             {"sources": (src_dir / "nao_existe.png",)}),
            ("rejects_empty_source_list", "no_source_declared", {"sources": ()}),
            ("rejects_invalid_asset_id", "invalid_asset_id", {"asset_id": "../escape"}),
            # `..` sozinho nao tem separador: escapava de out/visual_jobs/ para out/.
            ("rejects_dotdot_asset_id", "invalid_asset_id", {"asset_id": ".."}),
            ("rejects_empty_asset_id", "invalid_asset_id", {"asset_id": ""}),
        ):
            try:
                spec_for(**kwargs)
                ok, detail = False, "NAO levantou (falso verde)"
            except JobContractError as exc:
                ok = exc.blocker == blocker
                detail = f"levantou {exc.blocker}"
            fixtures.append(_fixture(name, "negative", ok, detail))

        # NEGATIVA: saida de maquina nunca se declara visually_approved
        serialized = _canonical_json(state)
        fixtures.append(_fixture(
            "machine_output_never_visually_approved", "negative",
            OUTPUT_VISUALLY_APPROVED not in serialized
            or state["output_status"] != OUTPUT_VISUALLY_APPROVED,
            "job_state nao carrega visually_approved como status de saida"))

    failed = [f for f in fixtures if f["status"] != "passed"]
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "rule_ref": "plano forge-art secao 5; SGDK_GLOBAL.md secoes 34 e 37",
        "exercised": (
            "determinismo do job_id; dry-run sem escrita; --explain; estrutura "
            "completa do job; cache hit por resume; invalidacao por parametro e "
            "por versao de toolchain; --force-new-job preservando o anterior; "
            "fonte read-only; failure injection com rollback; mutacao de fonte "
            "reprovada; job concluido nunca sobrescrito; 5 blockers de spec."
        ),
        "limitation": (
            "Garante procedencia, determinismo e auditabilidade do processo. "
            "Nao julga a qualidade do que foi gerado."
        ),
        "fixtures_total": len(fixtures),
        "fixtures_passed": len(fixtures) - len(failed),
        "fixtures": fixtures,
        "blocking": bool(failed),
        "blocking_statuses": sorted({f"job_self_check_failed:{f['fixture']}" for f in failed}),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Jobs imutaveis do forge-art.")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)

    if args.self_check:
        report = self_check()
        print(json.dumps(report, indent=2, sort_keys=True))
        if report["blocking"]:
            print("[FAIL] self-check de jobs reprovou; proxima acao: corrija a "
                  "fixture listada em blocking_statuses", file=sys.stderr)
            return 1
        print(f"[OK] {report['fixtures_passed']}/{report['fixtures_total']} fixtures "
              "(positivas e negativas) passaram", file=sys.stderr)
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
