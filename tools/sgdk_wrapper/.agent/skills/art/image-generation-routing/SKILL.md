---
name: image-generation-routing
description: Use para decidir o canal de geracao visual (nativo callable, nativo inline, API/CLI, ComfyUI local via ai_imagegen, ou bloqueado) antes de qualquer prompt de imagem. Nao use para escolher estilo visual, prompts ou converter assets brutos para SGDK.
---

# Image Generation Routing

Skill canonica de roteamento de geracao visual no MegaDrive_DEV. Resolve a pergunta: **qual canal vai produzir esta imagem agora?**

## Arvore de 3 ramos (obrigatoria antes de qualquer promessa)

Antes de responder o usuario "sim, gero", aplique a arvore da regra `SGDK_GLOBAL.md` secao 38
(capacidade declarada com prova). A ordem de canais 1-6 abaixo vive DENTRO desta arvore:

```
RAMO A — agente gera nativo com prova
    Sonda: existe ferramenta callable/inline nesta sessao?
    Probe passou -> gere e persista agora (canais 1-2).

RAMO B — host tem requisitos e preparo
    Sonda: imagegen_tool.py status + healthcheck do perfil.
    Probe passou (ou custo de install medido e aceito) -> circuito local (canais 3-5).

RAMO C — nem agente nem host
    Nao ha canal nativo, API/CLI falhou por estrutura, host sem GPU/runtime ou
    install recusada. Desfecho OBRIGATORIO: emitir successor_asset_directive
    (diretriz para modelo sucessor capaz) e registrar blocked_image_tooling com
    outcome_branch=C. Bloqueio morto sem diretriz e anti-padrao.
```

Estados de capacidade permitidos (sem quarto estado): `capaz_com_prova_agora`,
`capaz_apos_preparo_medido`, `nao_capaz_neste_host`.

Carregue esta skill antes de:

- gerar qualquer prompt de imagem em Rota A da `art-creation-sourcing`
- declarar `BLOCKED_IMAGE_TOOLING`
- recomendar instalacao de toolchain local
- aceitar imagem inline como entregue

Esta skill nao redige prompts, nao escolhe estilo e nao converte para VDP. Para isso, use `art-creation-sourcing`, `art-direction-selector`, `art-conversion-pipeline` ou `art-translation-to-vdp`.

---

## Entrada minima

- objetivo do asset e papel na cena;
- disponibilidade real de ferramenta nativa callable ou inline;
- estado conhecido de API/CLI externa, se houver;
- estado do toolchain local `tools/ai_imagegen/` quando os canais nativos nao existirem.

## Passa quando

- o canal selecionado esta explicitamente registrado;
- `procedural_renderer` nao e usado como fonte final AAA;
- bloqueio de imagem so ocorre depois de diferenciar nativo callable, nativo inline, API/CLI e ComfyUI local;
- qualquer uso local para AAA marca risco de qualidade e exige revisao humana antes de promocao.

## Ordem de canais (top-down)

Sempre avaliar nesta ordem e parar no primeiro canal disponivel:

1. `native_chat_image_generation_callable`
   - Ferramenta callable nativa (ex.: `image_gen`, `imagegen`) exposta ao agente.
   - Retorna imagem ou salva artefato. Preferencial sempre que existir.
   - Para assets AAA, personagem principal, boss, HUD heroico, cena identitaria ou qualquer arte premium, este e o default operacional do agente quando disponivel.
2. `native_chat_inline_generation`
   - Modelo/chat renderiza imagem inline na conversa, sem callable.
   - Conta como geracao real; nao bloqueie por ausencia de callable.
3. `api_cli_generation`
   - SDK, API ou CLI externa (OpenAI, Ideogram, Midjourney, etc.).
   - Pode falhar por billing, quota ou chave ausente; reportar motivo.
4. `local_comfyui_generation`
   - Toolchain local `tools/ai_imagegen/imagegen_tool.py` com ComfyUI gerenciado em `tools/ai_imagegen/runtime/`.
   - Fallback quando 1-3 nao existem.
   - Nao e fonte premium padrao para AAA no host atual; use como prova tecnica, laboratorio, triagem de prompt ou fallback documentado. Para promover arte critica gerada por este canal, exige revisao humana explicita de qualidade visual antes de qualquer conversao para `res/`.
   - Perfis ComfyUI: `deck_safe_sd15` (default seguro), `sdxl_lowvram`, `cpu_fallback`.
   - **`flux_schnell_gguf`** (FLUX.1 Schnell Q4_K_M, 8.2 GB) esta marcado como **`deprecated_pending_bonsai_validation`** em `imagegen_profiles.json` desde 2026-06-01. Continua funcional ate prova de equivalencia operacional do Bonsai 4B, mas NAO e mais o opt-in FLUX-class.
5. `local_bonsai_generation` (Bonsai 4B — opt-in, license-gated)
   - **Bonsai-Image 4B** (PrismML-Eng), 4B-parametros destilado da arquitetura FLUX, quantizado em **ternary (1.58-bit, ~1.21 GB)** ou **binary (1-bit, ~0.85 GB)**.
   - Backends: NVIDIA via `gemlite+HQQ` (Linux/Windows) ou `triton-windows` (Windows nativo, sem WSL2); Apple Silicon via `mflux+MLX`. **Nao roda em AMD nem Intel iGPU.**
   - Triplo gate bloqueante: `license` (license ack JSON) > `scope` (asset_role ∈ {concept_art, tileset_concept, dither_mask, contrast_study}) > `host` (NVIDIA/Apple Silicon, >=4 GB VRAM, >=6 GB RAM livre).
   - Status inicial de qualquer saida Bonsai e **`source_candidate`**. NUNCA `premium_source_accepted`. Promocao exige pipeline externo: `art-translation-to-vdp` + `megadrive-pixel-strict-rules` + `visual-excellence-standards` + contact sheet + BlastEm screenshot.
   - Scopes proibidos: `animated_sprite_final`, `hud_final`, `res_direct`, `aaa_final_asset`.
   - Cobertura de assets: **apenas concept art, tileset concept, dither_mask, contrast_study**. Sprites animadas e HUD usam SD 1.5 / SDXL / nativo.
   - Comandos: `imagegen_tool.py bonsai {status,install,serve,generate}` e `imagegen_circuit.py {preflight,run}`.
6. `procedural_renderer`
   - Scripts locais desenhando shapes/placeholders.
   - Nunca fonte final AAA. So produz `debug_lab`, `visual_lab_control` ou `placeholder`.

## Comandos canonicos do toolchain local

Use exatamente estas chamadas; nomes de perfil aceitos incluem aliases (`deck-safe`, `sdxl-lowvram`, `flux-schnell-gguf`).

```powershell
# 1. Estado do host
python tools/ai_imagegen/imagegen_tool.py --json status

# 2. Roteamento (auto detecta Codex/ChatGPT; use false/true para override)
python tools/ai_imagegen/imagegen_tool.py --json route

# 3. Healthcheck especifico do perfil
python tools/ai_imagegen/imagegen_tool.py --json healthcheck --profile deck_safe_sd15

# 4. Instalacao idempotente (dry-run primeiro)
python tools/ai_imagegen/imagegen_tool.py install --profile deck-safe --dry-run
python tools/ai_imagegen/imagegen_tool.py install --profile deck-safe

# 5. Geracao real (ComfyUI deve estar online)
python tools/ai_imagegen/imagegen_tool.py generate --profile deck_safe_sd15 --prompt "..."

# 6. Conversao com lineage (origem em data/source_art/)
python tools/ai_imagegen/imagegen_tool.py convert --source data/source_art/<asset>.png --spec tools/image-tools/specs/<spec>.json
```

## Regra de selecao

- Se `native_callable=true` ou o ambiente do agente auto-detectar Codex/ChatGPT
  com ferramenta nativa, retornar `native_chat_image_generation_callable`.
- Senao, se `native_inline=true`, retornar `native_chat_inline_generation`.
- Senao, se `api_cli_generation` disponivel e nao falhar por billing/quota/key, retornar `api_cli_generation`.
- Senao, rodar `status` + `healthcheck` do perfil recomendado:
  - se ComfyUI ou modelo do perfil ausente -> retornar `local_install_required` com `profile_recommended` e a instrucao de install.
  - se healthcheck passar -> retornar o perfil local (`deck_safe_sd15`/`sdxl_lowvram`/`flux_schnell_gguf`).
- Senao, declarar `blocked_image_tooling: true` com motivo agregado.

Regra AAA:

- Se a tarefa pedir asset premium/AAA e `native_chat_image_generation_callable` estiver disponivel, nao descer para `local_comfyui_generation` por conveniencia.
- `local_comfyui_generation` so pode ser escolhido para AAA quando os canais 1-3 estiverem indisponiveis ou explicitamente rejeitados, e o relatorio deve marcar `local_ai_quality_risk=true`.
- Resultado local que seja apenas "legivel" mas longe do padrao AAA fica `aceito_com_restricoes`, nunca `fonte_premium_aprovada`.

## Regras de host

- **Steam Deck / SteamOS / host limitado**: default obrigatorio `deck_safe_sd15`. SDXL e FLUX so se healthcheck do perfil aprovar; nunca como default automatico.
- **Linux desktop / Windows com >=8GB VRAM**: pode subir para `sdxl_lowvram` se healthcheck aprovar.
- **>=12GB VRAM** e modelo FLUX instalado: liberar `flux_schnell_gguf` quando user opt-in.
- **Sem GPU detectada**: aceitar `cpu_fallback` apenas se user confirmar lentidao explicitamente.

## Artefatos obrigatorios antes de bloqueio

Antes de declarar `BLOCKED_IMAGE_TOOLING`, emitir os dois reports (schemas em `tools/ai_imagegen/reports/schema/`):

- `tooling_capability_report` (schema `capability_report.schema.json`)
- `generation_channel_decision` (schema `generation_channel_decision.schema.json`)

Se o desfecho for o **Ramo C** (nem agente nem host gera), emitir tambem:

- `successor_asset_directive` (schema `tools/sgdk_wrapper/schemas/successor_asset_directive.schema.json`,
  template em `tools/sgdk_wrapper/.agent/references/successor_asset_directive_template.md`) —
  a diretriz para um modelo sucessor capaz assumir o papel de criador de assets.

Campos minimos da decisao:

```yaml
agent_native_probe_attempted: true|false
host_readiness_probed: true|false
native_chat_image_generation_callable: true|false
native_chat_inline_generation_available: true|false
api_cli_generation_attempted: true|false
api_cli_failure_reason: none|billing_hard_limit_reached|insufficient_quota|missing_key|other
local_comfyui_available: true|false
local_comfyui_profile_ready: true|false
capability_state: capaz_com_prova_agora|capaz_apos_preparo_medido|nao_capaz_neste_host
outcome_branch: A_generate_now|B_host_fallback|C_successor_directive
successor_directive_emitted: true|false   # obrigatorio true quando outcome_branch=C
procedural_generation_used_as_asset_source: false
selected_generation_channel: <um dos canais 1-4 ou blocked>
blocked_image_tooling: true|false
```

`selected_generation_channel: procedural_renderer` e proibido para asset final AAA.

## Persistencia inline

Se imagem renderizou inline mas ainda nao foi salva:

- `native_image_generation_available: true`
- `blocked_image_tooling: false`
- `generation_channel: native_chat_inline_generation`
- `persistence_status: generated_inline_pending_persistence`

O agente deve tentar persistir em `data/raw_ai/<run_id>/output.png`. Se a persistencia falhar, manter o status como pending; nao alegar caminho de arquivo que nao existe.

Para asset premium aceito, pending persistence nao basta: persistir em `data/source_art/`, atualizar `premium_source_manifest` e seguir para conversao.

## Lineage por asset

Para cada geracao registrar (`asset_lineage_record.schema.json`):

- `generation_channel`
- `tool_callable`
- `image_rendered_inline`
- `persisted_to_filesystem`
- `output_path` (somente se o arquivo existir)
- `chat_asset_label` (quando inline)
- `prompt_hash`
- `source_prompt`

## Saida minima desta skill

Sempre devolva:

- `tooling_capability_report` (do comando `status` ou equivalente)
- `generation_channel_decision` (do comando `route` ou equivalente)
- comando exato a executar a seguir (gerar, instalar, ou usar canal nativo)
- ou motivo agregado de bloqueio se nenhum canal existir

## Handoff

- Apos roteamento aprovado, voltar para `art-creation-sourcing` Rota A para o `art_generation_brief` e prompts.
- Apos imagem persistida, seguir para `art-conversion-pipeline` ou `art-translation-to-vdp`.
- Antes de promover para `res/`, usar `visual-excellence-standards`.

## Auto-invocacao via `imagegen_circuit.py` (Ring 1, projeto-aware)

A partir de 2026-06-01, o agente NAO chama `imagegen_tool.py generate` diretamente em Rota A passo 3. Em vez disso, chama o circuit:

```powershell
# Dry-run (read-only, sempre funciona; nativo e auto-detectado por default)
.\tools\ai_imagegen\run_imagegen_circuit.ps1 preflight `
    --project "<NOME DO PROJETO>" `
    --asset-role concept_art `
    --write-decision `
    --json

# Run real pelo circuit e apenas para backends locais; se o preflight retornar
# `native_chat_image_generation_callable` ou `native_chat_inline_generation`,
# o agente deve usar a ferramenta nativa da sessão, persistir o output em
# data/source_art/ e registrar lineage/status source_candidate.
.\tools\ai_imagegen\run_imagegen_circuit.ps1 run `
    --project "<NOME DO PROJETO>" `
    --asset-role concept_art `
    --prompt "1-bit bonsai tree silhouette, monochrome dithered" `
    --seed 42 `
    --json
```

O circuit:

1. Carrega `master_style_manifest.json` via lookup multi-path (`--style-manifest` > `doc/art/` > `data/source_art/<role>/` > `out/logs/`).
2. Antes de qualquer gate local, resolve canal nativo: callable > inline.
3. Se o canal nativo existir, retorna `selected_source: native_chat_image_generation_callable` ou `native_chat_inline_generation` e `next_action: use_native_channel`; nao pedir license Bonsai, nao instalar ComfyUI, nao bloquear por host AMD.
4. So se nao houver canal nativo/API, avalia os 3 gates Bonsai em ordem: **license** > **scope** > **host**.
5. Se license ack ausente/invalido, retorna `selected_source: license_blocked` e nao cria arquivo.
6. Se asset_role nao esta em `{concept_art, tileset_concept, dither_mask, contrast_study}` OU esta em `{animated_sprite_final, hud_final, res_direct, aaa_final_asset}`, retorna `scope_blocked`.
7. Se host nao tem GPU NVIDIA/Apple Silicon OU VRAM<4 OU RAM<6, retorna `blocked_host_capability`.
8. Se todos os gates locais passam, despacha para `imagegen_tool.py bonsai generate` (Bonsai) ou ComfyUI (default).
9. Persiste em `<P>/data/raw_ai/<run>/{output.png, prompt_pack_manifest.json, generation_report.json}` e `<P>/data/source_art/<role>/{source.png, premium_source_manifest.json}` (sempre status=`source_candidate`) quando o backend local produzir arquivo; para nativo inline/callable, o agente deve salvar manualmente o arquivo real e registrar lineage equivalente.
10. Emite `<P>/out/logs/generation_channel_decision.json` e `asset_lineage_record_<lineage>.json`.
11. **NUNCA** escreve em `<P>/res/`. Promocao a `res/` e via `imagegen_tool.py convert` apos pipeline externo.

Schemas novos (canonicos):

- `tools/ai_imagegen/reports/schema/bonsai_license_ack.schema.json`
- `tools/ai_imagegen/reports/schema/bonsai_session.schema.json`
- `tools/ai_imagegen/reports/schema/prompt_pack_manifest.schema.json`
- `tools/ai_imagegen/reports/schema/master_style_manifest_lookup.schema.json`
- `tools/ai_imagegen/reports/schema/generation_channel_decision.schema.json` (enum estendido com `bonsai_4b_ternary`, `bonsai_4b_binary`, `license_blocked`, `blocked_host_capability`, `scope_blocked`)
- `tools/ai_imagegen/reports/schema/asset_lineage_record.schema.json` (campos `prompt_pack_path`, `vendor_manifest_sha256`, `license_ack_sha256`, `style_manifest_*`, `asset_role`, `initial_status`)

## Anti-padroes

- prometer geracao ao usuario sem sonda executada nesta sessao (regra `SGDK_GLOBAL.md` secao 38)
- alegar canal nativo por fama do modelo ou memoria de outra sessao, sem `probe_attempted`
- confundir "host capaz" com "host preparado": GPU existente nao dispensa healthcheck e install medida
- declarar bloqueio no Ramo C sem emitir `successor_asset_directive`
- gerar prompt sem rodar `route` ou declarar canal selecionado
- declarar Bonsai/ComfyUI bloqueante quando o agente atual possui geracao nativa callable ou inline
- declarar `BLOCKED_IMAGE_TOOLING` sem rodar `healthcheck` do perfil recomendado
- usar `procedural_renderer` como fonte final
- promover `data/raw_ai/` direto para `res/`
- declarar perfil local como pronto sem ComfyUI instalado e modelo presente
- chamar Bonsai sem `bonsai_license_ack.json` valido
- usar asset_role fora de `{concept_art, tileset_concept, dither_mask, contrast_study}` para Bonsai
- tratar saida Bonsai como `premium_source_accepted` direto (sempre `source_candidate` no primeiro run)
- promover asset Bonsai para `res/` sem `art-translation-to-vdp` + `megadrive-pixel-strict-rules` + BlastEm gate
- remover `flux_schnell_gguf` enquanto `deprecated_pending_bonsai_validation` (coexiste ate prova de equivalencia)
