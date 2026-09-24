# CHECKPOINT — Bonsai-Image-Demo Integration (v2)

Data: 2026-06-01
Status: **Fase A + B concluidas. Aguardando Fase C (license ack humano).**
Proxima fase: C (license ack humano) → D (install + run real) — **trava ate**
C ser assinado.

## Decisao

Integrar `PrismML-Eng/Bonsai-Image-Demo` como novo canal `local_bonsai_generation`,
**opt-in** e com **triplo gate** (license > scope > host). **NAO substituir
`flux_schnell_gguf`** imediatamente: este continua ativo com status
`deprecated_pending_bonsai_validation` ate Bonsai provar equivalencia
operacional (Fase D completa).

## Escopo v1

**Aceito** (escopo Bonsai):

- `concept_art`
- `tileset_concept`
- `dither_mask`
- `contrast_study`

**Proibido** (escopo Bonsai):

- `animated_sprite_final`
- `hud_final`
- `res_direct`
- `aaa_final_asset`

Status inicial de qualquer saida Bonsai: `source_candidate`. Promocao a
`premium_source_accepted` exige `art-translation-to-vdp` +
`megadrive-pixel-strict-rules` + `visual-excellence-standards` + contact
sheet + BlastEm screenshot.

## Comportamento por host

| Host | Resposta canonica |
|---|---|
| Bonsai instalado + license ack + GPU NVIDIA + VRAM >= 4 + RAM >= 6 + asset_role permitido | `selected_source: bonsai_4b_ternary` ou `bonsai_4b_binary` |
| Native callable/inline disponivel | `selected_source: native_chat_image_generation_callable` ou `native_chat_inline_generation` |
| License ack ausente/invalido e sem canal nativo/API | `selected_source: license_blocked` |
| asset_role fora da allowlist e sem canal nativo/API | `selected_source: scope_blocked` |
| GPU AMD/Intel (Bonsai nao roda), VRAM<4, RAM<6 e sem canal nativo/API | `selected_source: blocked_host_capability` |

No host atual, quando a sessao do agente expoe geracao nativa, a resposta
canonica e `native_chat_image_generation_callable`; Bonsai/ComfyUI nao entram
como blocker. Se a mesma auditoria for executada em CLI puro, sem nativo/API,
o fallback local continua respeitando o gate Bonsai (`license_blocked` antes
de `blocked_host_capability`).

## Arquivos tocados (Fase A)

### Novos (12)

| Path | Funcao |
|---|---|
| `tools/ai_imagegen/imagegen_circuit.py` | Ring 1; preflight, dispatch, persist project-aware |
| `tools/ai_imagegen/run_imagegen_circuit.ps1` | wrapper PowerShell com bypass `--%` |
| `tools/ai_imagegen/run_imagegen_circuit.sh` | wrapper POSIX |
| `tools/ai_imagegen/reports/schema/bonsai_license_ack.schema.json` | schema do ack |
| `tools/ai_imagegen/reports/schema/bonsai_session.schema.json` | health do backend Bonsai |
| `tools/ai_imagegen/reports/schema/prompt_pack_manifest.schema.json` | evidencia por run |
| `tools/ai_imagegen/reports/schema/master_style_manifest_lookup.schema.json` | resultado do lookup multi-path |
| `tools/sgdk_wrapper/.agent/workflows/ai-imagegen-circuit.md` | runbook da auto-invocacao |
| `tools/ai_imagegen/CHECKPOINT_bonsai_integration.md` | este changelog |
| `tools/ai_imagegen/README.md` | atualizado (A12) |
| (2 skills rewrites) | image-generation-routing x2 |
| (3 skills edits) | art-creation-sourcing, art-translation-to-vdp, megadrive-pixel-strict-rules, art-asset-diagnostic |

### Modificados (8)

| Path | Mudanca |
|---|---|
| `tools/ai_imagegen/config/imagegen_profiles.json` | + `bonsai_4b_ternary`, + `bonsai_4b_binary`; `flux_schnell_gguf.status = deprecated_pending_bonsai_validation` |
| `tools/ai_imagegen/models/manifest.json` | (nenhuma mudanca nesta fase; adicao de modelos Bonsai fica para Fase D) |
| `tools/ai_imagegen/reports/schema/generation_channel_decision.schema.json` | enum: +`bonsai_4b_ternary`, +`bonsai_4b_binary`, +`license_blocked`, +`blocked_host_capability`, +`scope_blocked`; +bloco `gates` |
| `tools/ai_imagegen/reports/schema/asset_lineage_record.schema.json` | +`prompt_pack_path`, +`vendor_manifest_sha256`, +`license_ack_sha256`, +`style_manifest_*`, +`asset_role`, +`initial_status` |
| `tools/ai_imagegen/imagegen_tool.py` | +`cmd_bonsai_status/install/serve/generate`; +`preflight`; +`cmd_vendor_manifest`; +helpers de license, scope, host, style lookup, prompt pack; +constants BONSAI_* |
| `tools/sgdk_wrapper/.agent/skills/art/image-generation-routing/SKILL.md` (canonica) | canal 5 = Bonsai; `flux_schnell_gguf` deprecated; secao `imagegen_circuit.py` |
| `tools/sgdk_wrapper/modelo/.agent/skills/art/image-generation-routing/SKILL.md` (espelho) | mesmo conteudo da canonica |
| `tools/sgdk_wrapper/.agent/skills/art/art-creation-sourcing/SKILL.md` | passo 3 chama o circuit; tabela de escopos Bonsai |
| `tools/sgdk_wrapper/.agent/skills/art/art-translation-to-vdp/SKILL.md` | caso "Bonsai 1-bit dithered source → VDP" |
| `tools/sgdk_wrapper/.agent/skills/art/megadrive-pixel-strict-rules/SKILL.md` | caso "Bonsai 1-bit dithered → 16-color palette mapping" |
| `tools/sgdk_wrapper/.agent/skills/art/art-asset-diagnostic/SKILL.md` | cenario 3: rodar `imagegen_circuit.py preflight` em paralelo |

### Deletados (0)

`flux_schnell_gguf` permanece (com `status: deprecated_pending_bonsai_validation`).
Workflow ComfyUI correspondente tambem permanece.

## Pre-flight local/Bonsai, sem canal nativo (ja provado em build mode)

Os resultados abaixo continuam validos apenas quando o roteamento e forçado
para fallback local, por exemplo com `--native-callable false --native-inline
false` ou em CLI puro sem Codex/ChatGPT. Em sessao com geracao nativa, o
resultado esperado e `native_chat_image_generation_callable`.

- `python imagegen_tool.py preflight --asset-role concept_art --json`
  → `selected_source: license_blocked` (CA1 OK)
- `python imagegen_tool.py preflight --asset-role animated_sprite_final --json`
  → `selected_source: license_blocked` (license precede scope; CA5 OK)
- `python imagegen_tool.py --json status`
  → host bloqueado, GPU Unknown (wmic indisponivel), RAM 1.9 GB
  (CA2 OK apos o host ser investigado)
- `imagegen_circuit.py preflight` end-to-end via `run_imagegen_circuit.ps1`
  → retorna `license_blocked` com `gates.license.block_reasons=["bonsai_license_ack.json not found"]`

## Auditoria Fase B local/Bonsai (2026-06-01, todos PASS)

| ID | Descricao | Resultado |
|---|---|---|
| CA1 | Dry-run sem license → `selected_source: license_blocked` | PASS |
| CA2 | Dry-run com license stub valida → `selected_source: blocked_host_capability` (host gate dispara) | PASS |
| CA2b | Dry-run com license stub invalida (campo faltando) → `license_blocked` com `ack parse error` | PASS |
| CA5 | asset_role ∈ forbidden_scopes (`animated_sprite_final`) → scope gate `passed: false` (license precede em selected_source) | PASS |
| CA6 | asset_role `hud_final` → scope gate `passed: false` | PASS |
| CA7 | `--style-manifest <path>` respeitado: lookup emite `paths_tried=[<user-path>]` | PASS |
| CA8 | `paths_tried[]` emitido em todos os reports (preflight + channel_decision) | PASS |
| CA9 | `imagegen_circuit.py preflight --json` e `run --json` aceitam `--json` no subparser | PASS |
| CA10 | 6 comandos (4 preflights em 4 allowed_scopes + 2 runs) deixam `res/` intocado | PASS |
| B2 | 18/18 validacoes de schema (bonsai_license_ack, bonsai_session, prompt_pack_manifest, master_style_manifest_lookup, generation_channel_decision) | PASS |
| B3 | grep em `reports/` e `runtime/` por 3 forbidden claims (`creative_ready`, `ready_for_aaa`, `fonte_premium_aprovada`) = 0 hits | PASS |
| B4 | `Get-ChildItem res -Recurse -File` em todos os projetos nao-backup = 0 arquivos criados pelo circuit | PASS |

**Fixes aplicados durante a auditoria:**

1. Schema `bonsai_license_ack.schema.json`: adicionado `"pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"` em `approval_date` (o `format: date` no Draft 7 nao e enforced por padrao).
2. Runtime `_load_license_ack()` em `imagegen_tool.py`: adicionado check de pattern na data, validacao de que `allowed_scopes` nao contem valores fora do enum canonico, e que nenhum item e de `BONSAI_FORBIDDEN_SCOPES`. Schema = syntactic; runtime = semantic policy.

## Travas explicitas

- **Zero arquivo em `res/`** por qualquer comando do circuit
- **Zero claim** `creative_ready`, `ready_for_aaa`, `fonte_premium_aprovada`
  em reports emitidos pelo circuit
- **Bonsai backend NUNCA e default**; so e opt-in
- **Asset role** fora da allowlist ou dentro da blocklist e rejeitado
  ANTES de chamar o backend
- **License ack** ausente ou schema invalido bloqueia o fallback Bonsai (mesmo
  CA1 local dry-run retorna `license_blocked`), mas nao bloqueia canal nativo
  quando `native_chat_image_generation_callable`/inline estiver disponivel

## Proximas fases (NAO executadas neste turno)

### Fase B — auditoria read-only (CONCLUIDA 2026-06-01)

Todos os 12 criterios CA1-CA10 + B2-B4 passaram. Detalhes na secao
"Auditoria Fase B" acima.

### Fase C — gate humano

- C1: usuario abre `bonsai-image-4b-whitepaper.pdf` em
  `runtime/bonsai/bonsai-image-4b-whitepaper.pdf` (ou URL do repo)
- C2: confirma licenca do modelo e dos outputs
- C3: cria `runtime/bonsai/bonsai_license_ack.json` conforme schema
- C4: reporta se o host tera GPU NVIDIA/Apple Silicon + >=6 GB RAM no
  momento do run real (ou aceita `blocked_host_capability` como
  estado final ate migrar de hardware)

### Fase D — primeiro run real (SOMENTE apos C)

- D1: `python imagegen_tool.py bonsai install` (clona scripts only,
  gera `vendor_manifest.json`)
- D2: `python imagegen_tool.py bonsai serve --timeout 180` (background)
- D3: `python imagegen_circuit.py run --project <P> --asset-role
  concept_art --prompt "..." --json`
- D4: verificar `<P>/data/raw_ai/<run>/` e `<P>/data/source_art/<role>/`
- D5: NAO promover para `res/`. Aguardar `art-translation-to-vdp`
  humano + `megadrive-pixel-strict-rules` + BlastEm gate.
- D6: apos equivalencia provada, considerar remocao de
  `flux_schnell_gguf` (decisao registrada em changelog).

## Anti-regressao

- Nenhum asset Bonsai pode entrar em `res/` sem passar pelo pipeline
  externo. O circuit nao faz isso. O `imagegen_tool.py convert` tambem
  tem `convert` com checagem de role (a ser implementada em C1/D1).
- O profile `flux_schnell_gguf` NAO pode ser removido sem prova de
  equivalencia documentada no `CHECKPOINT_bonsai_integration.md`.
- O `bonsai_license_ack.json` NAO pode ser commitado automaticamente;
  o usuario o cria apos revisao do whitepaper.

## Referencias

- Runbook: `tools/sgdk_wrapper/.agent/workflows/ai-imagegen-circuit.md`
- Skill controladora: `tools/sgdk_wrapper/.agent/skills/art/image-generation-routing/SKILL.md`
- Skill consumidora: `tools/sgdk_wrapper/.agent/skills/art/art-creation-sourcing/SKILL.md`
- Skill de traducao: `tools/sgdk_wrapper/.agent/skills/art/art-translation-to-vdp/SKILL.md`
- Skill pixel-strict: `tools/sgdk_wrapper/.agent/skills/art/megadrive-pixel-strict-rules/SKILL.md`
- Repositorio upstream: https://github.com/PrismML-Eng/Bonsai-Image-Demo
- Whitepaper: `runtime/bonsai/bonsai-image-4b-whitepaper.pdf` (a ser baixado em D1)
