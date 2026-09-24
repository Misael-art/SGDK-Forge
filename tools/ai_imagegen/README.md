# ai_imagegen

Toolchain canonico de geracao visual local do MegaDrive_DEV. Atua como fallback
quando a geracao nativa do chat (callable ou inline) e a API/CLI externa nao
estao disponiveis.

Skills relacionadas:
- `tools/sgdk_wrapper/.agent/skills/art/image-generation-routing/SKILL.md`
  (controladora de canal)
- `tools/sgdk_wrapper/.agent/skills/art/art-creation-sourcing/SKILL.md`
  (consumidora upstream via `art-generation-brief`)
- `tools/sgdk_wrapper/.agent/workflows/ai-imagegen-circuit.md` (runbook)

## Estrutura

```
tools/ai_imagegen/
  imagegen_tool.py        # CLI principal (Ring 2)
  imagegen_circuit.py     # Ring 1: project-aware, gateado
  run_imagegen_circuit.ps1
  run_imagegen_circuit.sh
  config/imagegen_profiles.json
  models/manifest.json    # IDs canonicos de modelos (pesos ficam fora do Git)
  models/checkpoints/     # destino real de downloads (gitignored)
  workflows/comfyui/      # workflows JSON para cada perfil ComfyUI
  reports/schema/         # JSON Schemas dos artefatos emitidos
  runtime/                # ComfyUI + venv local (gitignored)
  runtime/bonsai/         # Bonsai-Image-Demo (clonado, scripts only)
  runtime/bonsai/bonsai_license_ack.json  # OBRIGATORIO antes de install
  runtime/bonsai/vendor_manifest.json     # gerado por install
  cache/                  # caches locais (gitignored)
```

## CLI (Ring 2)

O roteamento e **native-first**. Em Codex/ChatGPT com ferramenta de imagem
nativa, `route`/`preflight` devem selecionar
`native_chat_image_generation_callable` por default. ComfyUI e Bonsai sao
fallbacks locais quando o agente atual nao possui canal nativo/API.

```powershell
# Diagnostico de host
python tools/ai_imagegen/imagegen_tool.py --json status

# Roteamento (responder native_callable / native_inline conforme realidade do agente)
python tools/ai_imagegen/imagegen_tool.py --json route --native-callable false --native-inline false

# Healthcheck por perfil
python tools/ai_imagegen/imagegen_tool.py --json healthcheck --profile deck_safe_sd15

# Instalacao idempotente (sempre rode --dry-run primeiro)
python tools/ai_imagegen/imagegen_tool.py install --profile deck-safe --dry-run
python tools/ai_imagegen/imagegen_tool.py install --profile deck-safe

# Geracao real (requer ComfyUI online em runtime/ComfyUI)
python tools/ai_imagegen/imagegen_tool.py generate `
    --profile deck_safe_sd15 `
    --prompt "pixel art hero, side view, limited palette"

# Conversao para SGDK (origem em data/source_art/, nunca em data/raw_ai/)
python tools/ai_imagegen/imagegen_tool.py convert `
    --source data/source_art/<asset>.png `
    --spec tools/image-tools/specs/<spec>.json

# Preflight combinado (license + host + scope + style_manifest lookup + channel decision)
python tools/ai_imagegen/imagegen_tool.py preflight `
    --project "<NOME>" `
    --asset-role concept_art `
    --style-manifest "<P>/doc/art/master_style_manifest.json" `
    --json

# Verificar integridade do vendor Bonsai
python tools/ai_imagegen/imagegen_tool.py vendor-manifest

# Bonsai (opt-in, license-gated)
python tools/ai_imagegen/imagegen_tool.py bonsai status
python tools/ai_imagegen/imagegen_tool.py bonsai install
python tools/ai_imagegen/imagegen_tool.py bonsai serve --timeout 180
python tools/ai_imagegen/imagegen_tool.py bonsai generate `
    --asset-role concept_art `
    --prompt "1-bit bonsai silhouette"
```

## CLI (Ring 1, project-aware)

```powershell
# Preflight read-only (sempre funciona, retorna selected_source; auto-detecta nativo)
.\tools\ai_imagegen\run_imagegen_circuit.ps1 preflight `
    --project "<NOME DO PROJETO>" `
    --asset-role concept_art `
    --write-decision `
    --json

# Run real pelo circuit para backend local. Se selected_source for nativo,
# o proximo passo e usar a ferramenta de imagem da sessao e persistir lineage.
.\tools\ai_imagegen\run_imagegen_circuit.ps1 run `
    --project "<NOME DO PROJETO>" `
    --asset-role concept_art `
    --prompt "..." `
    --seed 42 `
    --json
```

Exit codes (espelham `imagegen_circuit.py`):

- 0 ok
- 2 license_blocked
- 3 scope_blocked
- 4 blocked_host_capability
- 6 backend refused
- 7 filesystem error

## Perfis e aliases

| Alias aceito | Profile id | Status | Uso |
|--------------|------------|--------|-----|
| `deck-safe`, `deck_safe`, `deck_safe_sd15` | `deck_safe_sd15` | available | Default seguro (Steam Deck/host limitado) |
| `sdxl-lowvram`, `sdxl_lowvram` | `sdxl_lowvram` | available | >=6-8 GB VRAM com offload |
| `bonsai-ternary`, `bonsai_4b_ternary` | `bonsai_4b_ternary` | experimental (opt-in) | Bonsai 4B ternary (~1.21 GB), NVIDIA/Apple Silicon + license ack |
| `bonsai-binary`, `bonsai_4b_binary` | `bonsai_4b_binary` | experimental (opt-in) | Bonsai 4B binary 1-bit (~0.85 GB), NVIDIA/Apple Silicon + license ack |
| `flux-schnell-gguf`, `flux_schnell_gguf` | `flux_schnell_gguf` | **deprecated_pending_bonsai_validation** | coexiste ate prova de equivalencia Bonsai |
| `cpu-fallback`, `cpu_fallback` | `cpu_fallback` | available | Sem GPU; muito lento |
| `native-callable` | `native_chat_image_generation_callable` | available | alias para canal nativo |
| `native-inline` | `native_chat_inline_generation` | available | alias para canal nativo |

## Triplo gate (Bonsai)

Cada gate e bloqueante somente para o fallback Bonsai. Eles nao bloqueiam
geracao quando `native_chat_image_generation_callable` ou
`native_chat_inline_generation` estiver selecionado. A ordem canonica local e:
**license > scope > host**.

| Gate | Falha → | selected_source |
|---|---|---|
| License | `bonsai_license_ack.json` ausente ou invalido | `license_blocked` |
| Scope | asset_role ∉ `{concept_art, tileset_concept, dither_mask, contrast_study}` OU ∈ `{animated_sprite_final, hud_final, res_direct, aaa_final_asset}` | `scope_blocked` |
| Host | GPU != NVIDIA/Apple Silicon OU VRAM<4 OU RAM<6 | `blocked_host_capability` |

## Pipeline canonico

1. `data/raw_ai/<run_id>/output.png` — saida bruta. NAO promovida.
2. `data/source_art/<role>/source.png` — `premium_source_manifest.json` com
   status `source_candidate` (nativo/API/local). Requer traducao VDP + BlastEm
   gate para virar `premium_source_accepted`.
3. `data/processed/` — candidatos convertidos (apos `imagegen_tool.py convert`).
4. `res/` — promocao final, **somente** apos `batch_resize_index.py` +
   `megadrive-pixel-strict-rules` + `visual-excellence-standards` +
   contact sheet + BlastEm screenshot.

`procedural_renderer` nunca e fonte final AAA; so produz `debug_lab`,
`visual_lab_control` ou `placeholder`.

## Bonsai license ack (template)

`tools/ai_imagegen/runtime/bonsai/bonsai_license_ack.json` (criado pelo humano
apos revisar o whitepaper `bonsai-image-4b-whitepaper.pdf`):

```json
{
  "model_license": "apache-2.0",
  "output_license": "cc-by-4.0",
  "usage_policy": "comercial permitido, atribuicao obrigatoria",
  "allowed_scopes": ["concept_art", "tileset_concept", "dither_mask", "contrast_study"],
  "approver": "<seu nome>",
  "approval_date": "2026-06-01",
  "evidence_url": "tools/ai_imagegen/runtime/bonsai/bonsai-image-4b-whitepaper.pdf"
}
```

Validado por `reports/schema/bonsai_license_ack.schema.json`.

## Exit codes e persistencia

`imagegen_tool.py` retorna dict e o `main()` propaga exit code nao-zero quando
`result["ok"]` for False. Os stages mapeados para exit codes (espelha
`imagegen_circuit.py`):

| Stage retornado | Exit code | Significado |
|---|---|---|
| `license` | 2 | `bonsai_license_ack.json` ausente/invalido |
| `scope` | 3 | asset_role fora de `allowed_scopes` |
| `host` | 4 | GPU/VRAM/RAM insuficiente para Bonsai |
| `timeout` | 6 | serve/generate excedeu timeout |
| `serve_offline` | 6 | serve nao esta online |
| `send_request` | 6 | send_request retornou != 0 |
| `no_output` | 7 | output esperado nao foi criado |
| `missing_serve_script` / `missing_send_request` | 7 | arquivo ausente |

Outros stages caem em 2 (default seguro). Em `dry_run`, o script NAO chama
subprocessos e NAO persiste; apenas imprime o comando planejado.

## Status de licenca no manifest (Canonical Hardening v2)

`tools/ai_imagegen/models/manifest.json` marca cada modelo com
`license_status`. Bonsai usa `pending_license_validation` e
`source_status: pending_source_verification` ate o humano emitir
`bonsai_license_ack.json` e o gate de licenca passar. Ate la, o audit
de game design NAO aceita Bonsai como fonte final AAA — apenas
`concept_art`, `tileset_concept`, `dither_mask`, `contrast_study`.

## Artefatos emitidos (schemas)

- `status` -> `capability_report.schema.json`
- `route` / `preflight` -> `generation_channel_decision.schema.json`
- `generate` -> `generation_report.schema.json` + `prompt_pack_manifest.schema.json`
- `convert` -> `asset_lineage_record.schema.json`
- Bonsai session -> `bonsai_session.schema.json`
- Master style manifest lookup -> `master_style_manifest_lookup.schema.json`

## Regra de bloqueio

Antes de declarar `BLOCKED_IMAGE_TOOLING`, ler
`tools/sgdk_wrapper/.agent/skills/art/art-creation-sourcing/references/image_generation_capability_routing.md`
e a skill `image-generation-routing`, e emitir os dois reports acima.
O circuit (`imagegen_circuit.py preflight`) ja faz isso em um unico comando.

## Changelog

- 2026-06-01 — v2: integracao Bonsai 4B opt-in com triplo gate
  (license > scope > host). `flux_schnell_gguf` marcado
  `deprecated_pending_bonsai_validation` (coexiste ate prova de
  equivalencia). Ring 1 (`imagegen_circuit.py`) adicionado como
  entry point project-aware. Auto-invocacao a partir de
  `art-creation-sourcing` Rota A passo 3. Ver
  `tools/ai_imagegen/CHECKPOINT_bonsai_integration.md` para detalhes.
