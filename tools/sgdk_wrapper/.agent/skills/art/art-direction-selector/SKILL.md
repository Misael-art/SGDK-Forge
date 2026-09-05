---
name: art-direction-selector
description: Use quando um projeto SGDK precisa escolher, registrar ou corrigir uma direcao estetica ou concept art direction antes de gerar, buscar, converter ou julgar arte visual.
---

# Art Direction Selector

Esta skill impede que um projeto avance com "pixel art generico" por falta de decisao estetica. Ela escolhe uma linguagem visual verificavel, registra alternativas descartadas, emite `concept_art_direction_brief` quando houver arte nova e preenche o `master_style_manifest` antes de qualquer prompt de imagem, sourcing, conversao ou julgamento visual.

## Ler antes de agir

1. `tools/sgdk_wrapper/.agent/references/art_style_catalog.json`
2. `tools/sgdk_wrapper/.agent/references/conception_agent_brief.md`
3. `doc/11-gdd.md`
3. `doc/13-spec-cenas.md`
4. `doc/01_game_design/02_reference_pillars.md` quando existir
5. `doc/03_art/00_art_bible.md` ou `doc/03_art/00_visual_quality_bar.md` quando existir
6. `doc/03_art/01_master_style_manifest.md` quando existir
7. `doc/03_art/17_concept_art_direction_system.md` quando houver arte nova, concept art, sourcing ou geracao
8. `doc/03_art/13_hud_ui_fx_decision_system.md` quando houver logo, title screen, menu ou front-end
9. `tools/sgdk_wrapper/schemas/brand_identity_manifest.schema.json` quando houver identidade de marca
10. `tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md`

## Quando usar

- projeto novo sem `master_style_manifest`
- projeto com GDD, mas sem direcao estetica congelada
- pedido de jogo AAA, stable, release, delivery ou piloto visual
- troca de tema, genero ou fantasia central
- drift visual entre assets gerados
- projeto legado com `master_style_manifest` antigo, mas sem `art_direction_decision_record`
- logo, title screen, press-start, menu principal ou front-end usando fonte generica ou sem sistema de marca

## Modo padrao

O modo padrao e `autonomous_with_escalation`.

O agente avalia o GDD, fantasia, genero, humor, benchmarks, plataforma, limites VDP e funcao de gameplay contra `art_style_catalog.json`. Ele calcula uma recomendacao conservadora com:

```text
(genre_affinity_match + mood_match + gameplay_readability_fit + production_fit + mega_drive_compatibility + differentiation_fit) - (clone_risk + vram_pressure_penalty)
```

Se a confianca for menor que o `confidence_threshold` declarado no catalogo, registre `art_direction_needs_human_choice` e apresente os 3 candidatos em vez de inventar uma escolha fraca. Se a confianca for suficiente, escolha e siga, registrando `auto_selected=true`.

Quando houver arte nova, tambem emita `concept_art_direction_brief` antes de qualquer prompt, sourcing, geracao, traducao ou conversao. O brief deve provar que a decisao visual nasceu de pelo menos um metodo valido: `production_driven`, `gameplay_driven`, `tone_driven` ou `market_driven`.

## Regras de seguranca artistica

- referencias sao ancoras tecnicas, nao fonte visual
- nunca use sprites, poses, silhuetas, paletas ou composicoes proprietarias como source art
- `reference_titles` do catalogo nao entram como comando de copia em prompt
- prompts devem usar `prompt_descriptors` tecnicos e neutros do catalogo, nao nomes de artistas vivos, estudios, marcas ou "in the style of"
- estilo `infeasible` so pode ser usado como norte conceitual com adaptacao explicita; nao autoriza promessa visual sem budget
- drift mid-project exige `style_drift_correction_brief` antes de regerar arte
- `master_style_manifest` antigo sem decision record fica `art_direction_pre_canonical`; pode ser mantido para projeto legado, mas nao fecha AAA novo

## Artefatos

### `art_direction_decision_record`

Campos minimos:

```yaml
schema_version: 1
project_id: string
decision_id: string
mode: autonomous_with_escalation | interactive | legacy_pre_canonical
auto_selected: true | false
confidence: 0.0-1.0
confidence_threshold: 0.65
selected_style_id: string
catalog_path: tools/sgdk_wrapper/.agent/references/art_style_catalog.json
catalog_entry_hash: sha256 or recorded catalog version
inputs_consulted:
  - doc/11-gdd.md
  - doc/13-spec-cenas.md
top_candidates:
  - style_id: string
    score: number
    why_fit: string
    risks: string
rejected_candidates:
  - style_id: string
    reason: string
benchmark_used_as: scale | density | timing | presence | quality | none
clone_risk_policy: authoriality_gate_required
prompt_descriptor_policy: neutral_technical_descriptors_only
blocking_statuses: []
```

### `concept_art_direction_brief`

Campos minimos:

```yaml
schema_version: 1
visual_purpose: string
gameplay_readability_goal: string
production_constraints: string
hardware_constraints: string
tone_and_atmosphere: string
market_differentiation: string
style_selection_method:
  - production_driven | gameplay_driven | tone_driven | market_driven
nine_style_axes:
  dimensionality: string
  fidelity_detail: string
  color_theory: string
  lighting_shadow: string
  shape_language: string
  surface_material: string
  ui_integration: string
  motion_style: string
  vfx_language: string
five_approval_gates:
  scope_style_constraints: pass | fail | needs_human_choice
  silhouette_shape_language: pass | fail | needs_human_choice
  value_hierarchy: pass | fail | needs_human_choice
  palette_role_map: pass | fail | needs_human_choice
  polish_vfx_gameplay_signal: pass | fail | needs_human_choice
references_used_as:
  - scale | density | timing | presence | quality
blocking_statuses: []
```

Regra: o brief nao substitui `master_style_manifest`; ele explica por que a arte deve existir e quais sinais devem sobreviver ate o VDP.

### `style_candidate_matrix`

Tabela curta com os 3-5 candidatos avaliados, pontuacao, compatibilidade Mega Drive, pressao VDP, risco de clone e motivo de descarte.

### `master_style_manifest`

O manifesto final deve conter:

- `style_anchor_id`
- `selected_style_id`
- fantasia visual central em 1 paragrafo
- paleta master e dominios de paleta previstos
- line weight, escala, densidade de pixels, iluminacao e limite de drift
- regras de prompts derivadas dos `prompt_descriptors`
- `negative_descriptors` e anti-padroes
- referencias tecnicas com `inspiration_only=true`
- limite de similaridade e handoff para `authoriality_gate_report`

### `brand_identity_manifest`

Obrigatorio quando o projeto tiver logo, title screen, press-start, menu
principal ou front-end com identidade de produto.

Campos minimos:

- `logo_system`: nome principal, subtitulo, peso visual, metafora de gameplay
  e testes de silhueta, monocromatico, miniatura e fundo dinamico
- `typography_system`: fonte-display, fonte-body, fonte-HUD/narrativa quando
  aplicavel, charset PT-BR, politica anti-fonte-generica e `glyph_manifest_ref`
- `title_screen_export_plan`: camadas runtime, superficie VDP, dominio de
  paleta, animacao e fallback estatico
- `validation_plan`: leitura em 320x224 e evidencia BlastEm quando aprovado
  para runtime

Regra: o logo deve nascer do GDD e do `master_style_manifest`. Fonte bonita,
fonte default ou metafora decorativa sem funcao ficam `needs_review`.

### `style_drift_policy`

Define o que conta como drift:

- paleta fora do dominio
- line weight diferente
- iluminacao inconsistente
- densidade de detalhe incompativel
- face/corpo/costume que parecam de outro jogo
- prompt que ignora `negative_descriptors`

## Blockers

- `art_direction_undeclared`: nao existe decision record nem manifest valido
- `style_catalog_not_consulted`: manifest foi inventado sem catalogo
- `style_clone_risk_unbounded`: referencia virou fonte visual ou risco de clone nao foi medido
- `style_drift_uncorrected`: drift detectado sem correction brief
- `concept_art_brief_missing`: arte nova tentou avancar sem brief de direcao de concept art
- `style_chosen_by_taste_only`: escolha visual sem metodo de producao, gameplay, tom ou mercado
- `concept_art_gate_failed`: pelo menos um dos cinco gates de concept art falhou
- `art_direction_low_confidence`: confianca abaixo do limiar e nenhuma escolha humana
- `brand_identity_missing_for_frontend`: logo/title/front-end avancou sem manifesto de marca
- `generic_font_used_as_final`: fonte default ou generica foi usada como identidade final
- `logo_thumbnail_readability_failed`: logo nao le em miniatura/nativo
- `logo_monochrome_readability_failed`: logo depende de gradiente/cor para ser compreendido

## Anexo: `moodboard_manifest`

Quando a iteracao tocar direcao visual, paleta, mood, lighting, anti-tom ou referencia tecnica, esta skill deve emitir tambem um `moodboard_manifest` validado contra `tools/sgdk_wrapper/schemas/moodboard_manifest.schema.json`.

O `moodboard_manifest` declara:

- `style_anchor_id` e `style_id` escolhidos (cross-ref com `art_direction_decision_record`)
- paleta master, dominios de paleta e limite de similaridade
- descritores de humor (mood, lighting, time_of_day, weather, weather_variation, hazard_density, idle_breathing, anti_tone)
- `reference_titles` com `inspiration_only=true` (nunca fonte visual)
- `negative_descriptors` e anti-padroes de drift
- `palette_sharing_rules` entre mecanicas, inimigos, chefe e HUD

O `moodboard_manifest` nao substitui o `master_style_manifest`; ele materializa a jornada emocional cena-a-cena para a equipe de arte e audio. Ele e o que `audio-architecture` e `xgm2-audio-director` usam para calibrar `adaptive_music_state_map.json`.

## Contrato Operacional

### Entrada minima

- `doc/11-gdd.md` ou briefing com fantasia, genero e escopo
- `doc/13-spec-cenas.md` ou lista de cenas alvo quando houver
- `art_style_catalog.json` canonico
- referencias declaradas pelo usuario ou `reference_pillars` quando existirem
- plataforma alvo Mega Drive/SGDK e nivel de entrega desejado

### Saida minima

- `art_direction_decision_record`
- `style_candidate_matrix`
- `master_style_manifest`
- `brand_identity_manifest` quando houver logo, title screen, press-start, menu principal ou front-end autoral
- `style_drift_policy`
- `style_drift_correction_brief` quando houver drift
- status honesto: `passed`, `art_direction_pre_canonical`, `art_direction_low_confidence` ou blocker correspondente

### Passa quando

- o catalogo canonico foi consultado
- pelo menos 3 candidatos foram avaliados ou a justificativa de candidato unico foi registrada
- o estilo escolhido tem compatibilidade Mega Drive declarada e risco de clone delimitado
- o `master_style_manifest` usa descritores tecnicos neutros
- `brand_identity_manifest` valida contra o schema quando houver logo/title/front-end de identidade
- o logo nao falha em silhueta, monocromatico, miniatura ou fundo dinamico quando aprovado para runtime
- SGDK default font fica restrita a debug/fallback e nunca vira identidade final
- quando houver arte nova, `concept_art_direction_brief` declarou metodo de escolha, nove eixos visuais e cinco gates sem falha
- o handoff para sourcing, conversao e excelencia visual esta claro
- projetos AAA/stable/release nao deixam `art_direction_undeclared`, `style_catalog_not_consulted` ou `style_drift_uncorrected` ativos

### Handoff

- para `art-creation-sourcing`: entregar `concept_art_direction_brief`, `art_direction_decision_record`, `master_style_manifest` e `style_drift_policy`
- para `visual-excellence-standards`: entregar criterios de coesao e anti-padroes
- para `sprite-animation`: entregar personalidade visual, line weight, paleta e regras de movimento que afetam strips
- para `art-translation-to-vdp`: entregar descritores de material, hue-shift, dithering e limites de drift
- para `scene-state-architect` e `megadrive-vdp-budget-analyst`: entregar `brand_identity_manifest` quando o logo/title tiver camadas runtime
