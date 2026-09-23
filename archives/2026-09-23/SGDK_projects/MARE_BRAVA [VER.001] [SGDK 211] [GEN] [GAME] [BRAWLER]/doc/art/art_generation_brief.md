# Art Generation Brief - MARE_BRAVA (CAIS_01) — v3 level-art modular

> CORREÇÃO CURATORIAL (2026-07-03): a v1 deste brief pedia sprite sheets completos
> gerados por IA. Isso viola o gate de canal (IA permitida somente para
> `concept_art`; `animated_sprite_final` é proibido). Rota correta em 3 etapas.
>
> CORREÇÃO CURATORIAL (2026-07-03, pós-revisão humana): a v2 ainda pedia
> painéis de cenário prontos demais. Isso delegava level design, composição e
> autoria do CAIS_01 ao modelo de imagem. Para cena jogável AAA, a IA deve gerar
> matéria-prima modular (`scene_kit`), e o agente canônico deve montar o level
> a partir de `level_blueprint`, câmera, streaming, ritmo de fase e gameplay.
>
> CORREÇÃO CURATORIAL (2026-07-04): o agente de imagem é fornecedor de
> matéria-prima premium organizada. Para personagens, gera identidade/model
> sheet conceitual; para o cais, gera kits modulares; para HUD/logo/FX, gera
> estudos com leitura em 320x224. Nada gerado nesta etapa entra em `res/`.
>
> CORREÇÃO CURATORIAL (2026-07-04, traco autoral): a direcao
> `angular_cps2_fighter` sozinha é vaga demais. Antes de nova geração, todo
> prompt deve consumir `doc/art/authorial_line_style_contract.json` e declarar
> linha, silhueta, rosto, maos/pes, assimetria, materiais e blockers contra
> arte generica.

## Etapa A0 — Level-art assembly contract (obrigatório antes do novo cais)

Antes de pedir nova arte do CAIS_01, ler e seguir:

- `doc/contracts/level_art_assembly_contract.json`
- `doc/contracts/level_blueprint.json`
- `doc/contracts/tilemap_streaming_contract.json`
- `doc/art/authorial_line_style_contract.json`
- `doc/11-gdd.md`
- `doc/13-spec-cenas.md`

O agente deve construir uma gramática de montagem visual: objetos, regras de
posição, densidade por arena, landmarks, camadas de parallax, foreground,
oclusão, animações ambientais e sinais de gameplay. O modelo de imagem não
decide o mapa final.

## Etapa A1 — Concepts via IA (scope permitido: concept_art)

Prompts prontos e específicos em `doc/art/prompt_pack/` (um doc por asset).
O humano gera num modelo capaz (ou canal aprovado futuro), salva em
`data/source_art/concept/<asset>/` e registra no `premium_source_manifest`.

Nenhum prompt de asset critico é valido se nao citar o contrato de traco
autoral. Falhas devem receber `authorial_line_contract_missing` ou
`generic_prompt_style_blocker`, mesmo que a imagem pareça tecnicamente bonita.

Saídas da Etapa A1:

- model sheets de personagem;
- prancha conjunta de silhueta TAÍNA/CRIA/ESTIVADOR em preto puro;
- `dock_scene_kit` modular do CAIS_01 (tiles, objetos, foreground, BG_B,
  ecology loops, pickups pequenos e landmarks), não panorama final;
- estudos de logo;
- estudos de HUD/FX.
- `doc/art/prompt_revision_report.md` com prompts finais e motivo das mudanças;
- `doc/art/asset_acceptance_report.json` com aceitos, descartados, pendentes e gaps.

NADA disso vai direto para `res/`.
Todos os novos resultados aceitos entram com status `source_candidate`.
Status proibidos nesta etapa: `ready_for_conversion`, `ready_for_res_promotion`,
`ready_for_aaa`, `sprite_final`, `tilemap_final` e
`production_tilemap_source`.

Os painéis de cais recebidos em 2026-07-03 ficam reclassificados como
`mood_reference_only` / `landmark_reference_only`: servem para paleta,
atmosfera, leitura de materiais e alguns landmarks, mas não autorizam produção
como tilemap final nem como fonte de streaming.

Gate de saída: ratificação humana da direção de arte com contact sheet
320x224 + quantização 16 cores (ver `doc/art/master_style_manifest.json#vdp_survival_proof`)
e revisão do `dock_scene_kit` contra o `level_art_assembly_contract`.

## Etapa B — Autoral (proibido gerar por IA)

1. Model sheet autoral consolidado por personagem (limpar/decidir sobre os concepts).
2. Lineart 1px sobre o model sheet (grid de pixel, proporção travada no scale_contract).
3. Key poses por ação (4-6 por estado, frame data como guia de timing).
4. Strips por ação em PNG indexado (15 cores + index 0, grid 8x8).
5. Montagem autoral do CAIS_01 pelo agente: `world_layout_board` 1344x224,
   `object_placement_map`, `parallax_layer_contract`, `background_ecology_card`,
   `collision_visual_contract` e plano de streaming por colunas.

## Etapa C — Conversão e prova

`level-design-canonical` → `multi-plane-composition` →
`scene-direction-curator` → `art-translation-to-vdp` →
`megadrive-pixel-strict-rules` → `megadrive-vdp-budget-analyst` →
contact sheet → `visual-excellence-standards` → aprovação humana → só então
`res/` e build.

## Regras herdadas

- `doc/art/style_drift_policy.json` (drift para correção antes de regerar)
- `doc/art/authorial_line_style_contract.json` (traco autoral e blockers contra arte generica)
- `doc/contracts/art_gameplay_direction_gate.json` (escopo de produção autorizado)
- `doc/contracts/level_art_assembly_contract.json` (gramática modular e autoria do level)
- Canal de geração: `out/logs/generation_channel_decision.json` deve ser
  native-first. Em Codex/ChatGPT com ferramenta de imagem, usar
  `native_chat_image_generation_callable`; Bonsai/ComfyUI ficam apenas como
  fallback local quando não houver canal nativo/API.
