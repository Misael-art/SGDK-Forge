# Art Generation Brief - MARE_BRAVA (CAIS_01) — v2 pos-parecer curatorial

> CORREÇÃO CURATORIAL (2026-07-03): a v1 deste brief pedia sprite sheets completos
> gerados por IA. Isso viola o gate de canal (IA permitida somente para
> `concept_art`; `animated_sprite_final` é proibido). Rota correta em 3 etapas.

## Etapa A — Concepts via IA (scope permitido: concept_art)

Prompts prontos e específicos em `doc/art/prompt_pack/` (um doc por asset).
O humano gera num modelo capaz (ou canal aprovado futuro), salva em
`data/source_art/concept/<asset>/` e registra no `premium_source_manifest`.

Saídas da Etapa A: model sheets de personagem, painéis de mundo do cais,
estudos de logo e estudos de HUD/FX. NADA disso vai direto para `res/`.

Gate de saída: ratificação humana da direção de arte com contact sheet
320x224 + quantização 16 cores (ver `doc/art/master_style_manifest.json#vdp_survival_proof`).

## Etapa B — Autoral (proibido gerar por IA)

1. Model sheet autoral consolidado por personagem (limpar/decidir sobre os concepts)
2. Lineart 1px sobre o model sheet (grid de pixel, proporção travada no scale_contract)
3. Key poses por ação (4-6 por estado, frame data como guia de timing)
4. Strips por ação em PNG indexado (15 cores + index 0, grid 8x8)

## Etapa C — Conversão e prova

`art-translation-to-vdp` → `megadrive-pixel-strict-rules` → contact sheet →
`visual-excellence-standards` → aprovação humana → só então `res/` e build.

## Regras herdadas

- `doc/art/style_drift_policy.json` (drift para correção antes de regerar)
- `doc/contracts/art_gameplay_direction_gate.json` (escopo de produção autorizado)
- Canal de geração: `out/logs/generation_channel_decision.json` (bloqueado no host)
