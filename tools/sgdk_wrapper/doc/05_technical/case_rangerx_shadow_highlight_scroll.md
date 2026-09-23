# Case Study - Shadow/Highlight, VSCROLL_COLUMN e scroll FX

Status: `case_study_candidate`
Owner principal: `shadow-highlight-scroll-fx`
Owners complementares: `scene-direction-curator`, `megadrive-vdp-budget-analyst`, `multi-plane-composition`

## Licao util

Efeitos de alto impacto no Mega Drive costumam nascer de combinacao de planos,
scroll por linha/coluna, Shadow/Highlight, palette cycling e H-Int. Eles nao sao
filtros aplicados depois da arte: fazem parte da arquitetura de cena.

## O que o agente deve absorver

- Shadow/Highlight nao e alpha blending.
- VSCROLL_COLUMN serve para offset vertical por colunas, nao para velocidade
  horizontal por faixa.
- HSCROLL_LINE exige arte autorada por bandas para evitar rasgos visuais.
- Palette cycling precisa de slots CRAM, cadence, owner e reset.
- H-Int precisa de owner unico, cadeia declarada e fallback.

## Gate recomendado

Antes de runtime:

1. `scene_direction_record`
2. `parallax_layer_contract`
3. `scroll_fx_contract`
4. `palette_cycle_decision_card`, quando CRAM muda
5. `raster_fx_ownership_map`, quando H-Int existe
6. `palette_slot_audit`
7. `worst_frame_budget`
8. BlastEm screenshot; `visual_vdp_dump` quando o claim for AAA/release

## Limites

- Efeito sem funcao de gameplay/narrativa fica `decorative_only_blocked`.
- Mid-frame CRAM write sem mapa de linhas e owner fica bloqueado.
- Tecnica que so parece boa no editor nao sobe acima de `lab_candidate`.

## Falha que previne

Evita que o agente prometa efeito "Ranger X-like" e entregue apenas paleta
escura, dither decorativo ou scroll sem ownership.
