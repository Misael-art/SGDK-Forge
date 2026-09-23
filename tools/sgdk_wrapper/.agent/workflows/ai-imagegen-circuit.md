# AI ImageGen Circuit — Runbook

> Runbook canonico do circuit de geracao visual para projetos SGDK/Mega Drive.
> Auto-invocacao: a partir de `art-creation-sourcing` Rota A passo 3, ou via
> comando explicito do usuario.

---

## 1. Visao em 3 aneis

```
AGENTE / USUARIO
   |
   v
RING 1 — imagegen_circuit.py (project-aware, gateado)
   |   scripts: tools/ai_imagegen/imagegen_circuit.py
   |   wrappers: tools/ai_imagegen/run_imagegen_circuit.{ps1,sh}
   v
RING 2 — imagegen_tool.py (host, profile, channel)
   |   subs: status, install, route, healthcheck, generate, convert,
   |         preflight, vendor-manifest, bonsai{status,install,serve,generate}
   v
RING 3a — ComfyUI      (SD 1.5 / SDXL / FLUX-Schnell GGUF)
RING 3b — Bonsai       (Bonsai-Image 4B ternary / binary, license-gated)
```

---

## 2. Triplo gate (cada um bloqueante)

| Gate | Fonte | Bloqueia quando |
|---|---|---|
| **license** | `tools/ai_imagegen/runtime/bonsai/bonsai_license_ack.json` | Ausente, schema invalido, ou falta campo obrigatorio (model_license, output_license, usage_policy, allowed_scopes, approver, approval_date, evidence_url) |
| **host** | GPU/VRAM/RAM detectados em runtime | GPU != NVIDIA/Apple Silicon, vram < 4 GB, ram < 6 GB |
| **scope** | `asset_role` enviado pelo chamador | Role nao esta em `{concept_art, tileset_concept, dither_mask, contrast_study}` OU esta em `{animated_sprite_final, hud_final, res_direct, aaa_final_asset}` |

A ordem canonica: **license > scope > host > native > local**. Se license falha, host nem e consultado. Se license+scope passam mas host falha, retorna `blocked_host_capability`.

---

## 3. Auto-invocacao a partir do agente

Origem: `art-creation-sourcing` SKILL.md, Rota A passo 3, **somente** quando:

1. `master_style_manifest.json` ja foi emitido e declara `style_id` compativel com 1-bit dithered OU `asset_role` explicito;
2. Nenhum canal nativo esta disponivel (callable=false, inline=false);
3. Host ja passou preflight (Fase A + B completas) e license ack esta assinado.

Sequencia canonica:

```powershell
# 1. Agente coleta style_manifest, asset_role, prompt do brief
# 2. Agente chama o circuit:
.\tools\ai_imagegen\run_imagegen_circuit.ps1 run `
    --project "AAA EFFECT LAB - profundidade-movimento [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]" `
    --asset-role concept_art `
    --style-manifest "<project>/doc/art/master_style_manifest.json" `
    --prompt "1-bit bonsai, monochrome dithered silhouette, ..." `
    --seed 42 `
    --json

# 3. Circuit emite:
#    <project>/out/logs/generation_channel_decision.json
#    <project>/out/logs/asset_lineage_record_<lineage_id>.json
#    <project>/data/raw_ai/<run>/output.png
#    <project>/data/raw_ai/<run>/prompt_pack_manifest.json
#    <project>/data/raw_ai/<run>/generation_report.json
#    <project>/data/source_art/<role>/source.png
#    <project>/data/source_art/<role>/premium_source_manifest.json
#    (status=source_candidate; NUNCA premium_source_accepted)
```

Apos o circuit, a promocao para `res/` NAO acontece aqui. A cadeia canonica e:

```
circuit -> source_candidate
  -> art-translation-to-vdp (humano + skill)
  -> megadrive-pixel-strict-rules (PASS)
  -> visual-excellence-standards (PASS)
  -> contact sheet (4-8 variantes)
  -> BlastEm screenshot (gate visual)
  -> SOMENTE ENTAO: premium_source_accepted + res/
```

---

## 4. Comando manual do usuario

Dry-run (read-only, nenhum arquivo criado):

```powershell
.\tools\ai_imagegen\run_imagegen_circuit.ps1 preflight `
    --project "AAA EFFECT LAB - profundidade-movimento [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]" `
    --asset-role concept_art `
    --write-decision `
    --json
```

Run real (requer license ack + host OK):

```powershell
.\tools\ai_imagegen\run_imagegen_circuit.ps1 run `
    --project "<nome>" `
    --asset-role concept_art `
    --prompt "1-bit bonsai tree silhouette, hard dithering, monochrome, retro Macintosh" `
    --seed 42 `
    --json
```

POSIX equivalente:

```bash
./tools/ai_imagegen/run_imagegen_circuit.sh preflight \
    --project "<nome>" --asset-role concept_art --write-decision --json

./tools/ai_imagegen/run_imagegen_circuit.sh run \
    --project "<nome>" --asset-role concept_art \
    --prompt "..." --seed 42 --json
```

---

## 5. Instalacao manual do backend Bonsai

So executar quando license ack ja foi assinado e host passou preflight:

```powershell
# 1. Instalar (clona scripts only, gera vendor_manifest.json)
python tools/ai_imagegen/imagegen_tool.py bonsai install

# 2. Verificar SHA-256 dos scripts clonados
python tools/ai_imagegen/imagegen_tool.py vendor-manifest

# 3. Subir serve em background (FastAPI :8000)
python tools/ai_imagegen/imagegen_tool.py bonsai serve --timeout 180

# 4. Status do backend
python tools/ai_imagegen/imagegen_tool.py bonsai status --json
```

Apos o serve online, o circuit faz o resto via `send_request.ps1` (Windows) ou `send_request.sh` (POSIX).

---

## 6. Bloqueios e saidas

| Saida | Significado | Acao do agente |
|---|---|---|
| `selected_source: native_chat_image_generation_callable` | Canal nativo tem callable | Nao usar circuit; ir direto |
| `selected_source: native_chat_inline_generation` | Inline funciona | Nao usar circuit; ir direto |
| `selected_source: license_blocked` | License ack ausente/invalido | `wait_for_human`; agente NAO tenta gerar |
| `selected_source: scope_blocked` | asset_role proibido | Agente corrige role ou pede ao usuario |
| `selected_source: blocked_host_capability` | GPU/VRAM/RAM insuficiente | `host_blocked`; reportar; nao tentar install |
| `selected_source: bonsai_4b_ternary` | Tudo passou, Bonsai selecionado | Prossegue com `run` (nao `preflight`) |

---

## 7. Criterios de aceite (auditados na Fase B)

| ID | Criterio | Como provar |
|---|---|---|
| CA1 | Dry-run sem license retorna `license_blocked=true` | preflight sem ack |
| CA2 | Dry-run no host bloqueado retorna `blocked_host_capability` | preflight no host atual |
| CA3 | 4 schemas novos parseiam JSON-Schema draft-07 | `python -m jsonschema -i <json> <schema>` |
| CA4 | `convert` recusa `asset_role` proibido com `res/asset_role_forbidden` | feed de manifest proibido |
| CA5 | asset-role fora da allowlist retorna `scope_blocked` | preflight com role invalido |
| CA6 | `flux_schnell_gguf.status == deprecated_pending_bonsai_validation` | `jq .profiles.flux_schnell_gguf.status config/imagegen_profiles.json` |
| CA7 | install aborta se SHA-256 nao bate | rodar install, alterar arquivo, rodar vendor-manifest |
| CA8 | lookup `master_style_manifest` tenta 4 paths e reporta `paths_tried[]` | preflight com --project valido |
| CA9 | Zero arquivo em `res/` apos qualquer comando do circuit | `Get-ChildItem res/ -Recurse` antes/depois |
| CA10 | Zero claim `creative_ready`/`ready_for_aaa` em reports emitidos | grep em todos os reports |

---

## 8. Onde encontrar cada peca

| Peca | Path |
|---|---|
| Ring 1 CLI | `tools/ai_imagegen/imagegen_circuit.py` |
| Ring 1 wrappers | `tools/ai_imagegen/run_imagegen_circuit.{ps1,sh}` |
| Ring 2 CLI | `tools/ai_imagegen/imagegen_tool.py` |
| Profiles + license paths | `tools/ai_imagegen/config/imagegen_profiles.json` |
| Model manifest | `tools/ai_imagegen/models/manifest.json` |
| Schemas | `tools/ai_imagegen/reports/schema/` |
| License ack template | `runtime/bonsai/bonsai_license_ack.json` (criado pelo humano) |
| Vendor manifest | `runtime/bonsai/vendor_manifest.json` (gerado por `install`) |
| Bonsai scripts | `runtime/bonsai/scripts/` (clonado de Bonsai-Image-Demo) |
| Skill controladora | `tools/sgdk_wrapper/.agent/skills/art/image-generation-routing/SKILL.md` |
| Skill consumidora upstream | `tools/sgdk_wrapper/.agent/skills/art/art-creation-sourcing/SKILL.md` |
| Skill de traducao VDP | `tools/sgdk_wrapper/.agent/skills/art/art-translation-to-vdp/SKILL.md` |
| Skill pixel-strict | `tools/sgdk_wrapper/.agent/skills/art/megadrive-pixel-strict-rules/SKILL.md` |
| Skill diagnostico | `tools/sgdk_wrapper/.agent/skills/art/art-asset-diagnostic/SKILL.md` |

---

## 9. Foras de escopo (travas explicitas)

- Sprites animados: usem `art-creation-sourcing` + `sprite-animation` (LoRA SD 1.5, nao Bonsai)
- HUD heroico: mesmo caminho
- Promover para `res/`: este circuit NAO faz. A promocao e via `imagegen_tool.py convert` apos VDP translation + BlastEm gate
- Substituir `deck_safe_sd15` como default: Bonsai e opt-in
- Remover `flux_schnell_gguf` agora: ele vive com `status: deprecated_pending_bonsai_validation` ate prova de equivalencia
- Ignorar gates: impossivel. Cada gate tem bypass=zero.

---

## 10. Changelog

- 2026-06-01 — v2 inicial. Coexistir flux_schnell_gguf ate prova. Bonsai opt-in. Triplo gate (license > scope > host). Status inicial sempre `source_candidate`. Promocao a `res/` exige pipeline externo.
