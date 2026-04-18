---
name: sgdk-runtime-coder
description: Use quando a tarefa envolver codigo C SGDK 2.11 real, montagem de cena, sprites, BGs, HUD, audio, loop principal, build no Windows, scroll avancado, raster split, pseudo-3D, DMA scheduling e fechamento do ciclo ate ROM com evidencia em emulador. Nao substitui megadrive-elite, scene-state-architect, sgdk-build-wrapper-operator ou megadrive-vdp-budget-analyst; trabalha entre eles como o programador perito de runtime.
---

# SGDK Runtime Coder

Esta skill existe para o miolo operacional que faltava no framework:

- implementar e corrigir codigo C SGDK 2.11 real
- montar cena, sprites, BGs, HUD, audio e loop principal
- escolher a API certa entre `IMAGE`, `MAP`, `SPR_init`, `SPR_initEx`, `TILE_USER_INDEX`, `PAL_setPalette`, `SPR_setAnimAndFrame`, etc.
- buildar corretamente no Windows
- fechar o ciclo ate ROM + evidencia no emulador

## Nao substitui outras skills

Esta skill senta entre as outras:

- `megadrive-elite`
  - ponto de entrada do workspace
- `scene-state-architect`
  - modularidade, fronteiras de estado e responsabilidade
- `sgdk-build-wrapper-operator`
  - wrapper, layout e politica de build
- `megadrive-vdp-budget-analyst`
  - decisao de VRAM, DMA, sprites e extrapolacao

## Ler antes de agir

1. `references/sgdk_211_api_reality.json`
2. `references/runtime_scene_contracts.md`
3. `references/windows_toolchain_gotchas.md`
4. `references/pattern_catalog.json`
5. `doc/05_technical/92_sgdk_engine_pattern_frontdoor.md`
6. `doc/05_technical/92_sgdk_engine_pattern_registry.json`
7. `references/build_and_emulator_gate.md`
8. `doc/10-memory-bank.md` do projeto alvo
9. header relevante em `sdk/sgdk-2.11/inc/`

## Quando usar

- bug de compilacao ou link em SGDK 2.11
- bug de loop principal, VBlank ou ordem de atualizacao
- integracao de sprite, BG, HUD, texto, audio ou parallax
- escolha entre `VDP_drawImageEx` e `MAP_create`
- reset de estado entre cenas
- tune de `SPR_initEx`
- validacao de runtime com BlastEm

## Saidas obrigatorias

- `runtime_decision_log`
- `api_reality_check`
- `scene_reset_plan` quando houver transicao de cena
- `build_evidence`
- `emulator_evidence`
- `delivery_findings`

## Regras canonicas imediatas

- SGDK 2.11 real vence memoria do agente
- `extern` em header e definicao unica em `.c`
- `SYS_doVBlankProcess()` no loop principal
- ordem canonica:
  - `INPUT_update()`
  - `scene update`
  - `SPR_update()`
  - `SYS_doVBlankProcess()`
- reset de cena e obrigatorio ao sair
- index `0` realmente transparente nos PNGs integrados
- `TILE_USER_INDEX` e empilhamento de tilesets devem ser declarados
- no Windows, build sempre com caminho absoluto e `cmd //c`

## Classificacao de conhecimento

- `hard_fact_blocker`
  - quebra build, linker ou runtime se errar
- `canonical_pattern`
  - padrao seguro e reutilizavel
- `advanced_pattern_candidate`
  - padrao forte vindo do scan de engines, mas ainda sem promocao humana explicita
- `experimental_pattern`
  - so com prova forte e intencao explicita

## Senior Competencies

Esta skill deve ser lida como dona operacional das seguintes competencias seniores:

- `h_int_control_plane`
  - ownership unico de callback, arbitro de efeitos e contrato de reset
- `line scroll`
  - arrays por scanline, `DMA` e seam control
- `column scroll`
  - uso disciplinado de `VSRAM` e custo por frame
- `H-Int palette split`
  - split mid-frame, alias visual `mid-frame palette swap`, reset simetrico e risco de callback unico
- `procedural_raster_glitch_suite`
  - rasgo dirigido por `HScroll`, shock de paleta, corrupcao controlada de HUD e leitura dramatica sob controle
- `masked_shadow_highlight_lighting`
  - spotlight, lanterna ou weak spot de boss como ilusao de hardware; nunca vender como alpha blending ou iluminacao global
- `palette cycling`
  - escrita segura em `CRAM`, timing tables e ownership de paleta
- `window_plane_static_hud`
  - `WINDOW` como plano fixo para HUD, lifebar e score sem consumir sprite slot
- `interlaced_448 orchestration`
  - modo 448 como tecnica `special_scene_only`, nunca como default de cena
- `BG_B bypassing`
  - boss gigante como tilemap, tradeoff com parallax e plane takeover
- `pseudo-3D`
  - `zmap`, curves, hills, banding e budget de raster
- `software_affine_pseudo3d`
  - transformacao por software tratada como trilha separada do road-stack
- `mutable_tile_decal_mutation`
  - dano persistente local via `RAM shadow copy`, `mutable tile pool` e dirty uploads limitados
- `cellular_microbuffer_sim`
  - microframebuffer local, solver delimitado e update cadence declarada; nunca tratar como sandbox global
- `DMA scheduling`
  - uploads no VBlank, leakage control e worst-frame discipline
- `XGM/XGM2 integration boundaries`
  - ownership de canal, pause/resume e limites de integracao com gameplay

Regra:

- esta skill pode orquestrar todas essas tecnicas
- ela NAO as promove para default sozinha
- promocao para `senior_default` exige `lib_case`, scene dedicada no `BENCHMARK_VISUAL_LAB`, `validation_report` com `blastem_gate = true` e gate humano
- `WINDOW` normal e plano fixo legitimo; `window alias` continua tecnica separada e nao-default
- `pseudo3d_road_stack` e `software_affine_pseudo3d` nunca devem compartilhar status
- `sprite_midframe_sat_reuse` depende formalmente de `h_int_control_plane`

## Regra para engine scan

- padrao vindo de `SGDK_Engines` nao vira canon so porque apareceu em codigo real
- o front door em `doc/05_technical/92_sgdk_engine_pattern_frontdoor.md` define a leitura correta
- o registry em `doc/05_technical/92_sgdk_engine_pattern_registry.json` e a fonte machine-readable dos candidatos
- se um padrao estiver como `candidate_for_canon` ou `verified_example`, trate como referencia valiosa, nao como default obrigatorio
- nenhum padrao novo deve entrar como `canonical_pattern` sem `lib_case` correspondente e gate humano explicito

## Como decidir

### `IMAGE` vs `MAP`

- usar `IMAGE` quando a arte cabe no plano efetivo e nao pede streaming de mapa
- usar `MAP_create` quando o cenario for maior que o plano, precisar de scroll de mapa ou streaming
- nao usar `MAP_create` por reflexo se `VDP_drawImageEx` resolver com menos complexidade

### `SPR_init` vs `SPR_initEx`

- `SPR_init()` para reserva padrao
- `SPR_initEx(n)` quando o fundo estiver pressionando VRAM e o budget real pedir ajuste
- a escolha deve citar custo e impacto

### Scene exit reset

Ao sair de cena, avaliar obrigatoriamente:

- `SPR_reset()`
- `VDP_clearPlane()`
- `VDP_setHorizontalScroll(BG_B, 0)` e equivalentes
- limpeza de HUD / WINDOW / texto

## Anti-padroes

- inventar getter SGDK inexistente
- chamar `SYS_doVBlankProcess()` dentro da cena em vez do loop principal
- redeclarar globais em mais de um `.c`
- confiar em build manual sem wrapper e sem caminho absoluto
- chamar a cena de pronta sem ROM rodando em BlastEm

## Lib case obrigatoria

Antes de generalizar uma tecnica, consulte:

- `tools/sgdk_wrapper/.agent/lib_case/sgdk-runtime/`
- `doc/05_technical/92_sgdk_engine_pattern_registry.json`

Cada caso ali existe para travar um aprendizado real em forma reproduzivel.

## Integracao

- combinar com `sprite-animation` para runtime de animacao
- combinar com `multi-plane-composition` quando a decisao envolver BG_A/BG_B/foreground
- combinar com `character-design` quando uma decisao de runtime depender de palette swap ou escala do roster
- combinar com `forward-kinematics-rigging` quando a tarefa envolver juntas, correntes, tentaculos ou membros articulados
- combinar com `xgm2-audio-director` quando a tarefa envolver ownership de canal, mix de PCM e arquitetura de audio
