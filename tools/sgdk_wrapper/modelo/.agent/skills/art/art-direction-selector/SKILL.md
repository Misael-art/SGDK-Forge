---
name: art-direction-selector
description: Use quando um projeto SGDK precisa escolher, registrar ou corrigir uma direcao estetica antes de gerar, buscar, converter ou julgar arte visual.
---

# Art Direction Selector

Esta skill impede que um projeto avance com "pixel art generico" por falta de decisao estetica. Ela escolhe uma linguagem visual verificavel, registra alternativas descartadas e preenche o `master_style_manifest` antes de qualquer prompt de imagem, sourcing, conversao ou julgamento visual.

## Ler antes de agir

1. `tools/sgdk_wrapper/.agent/references/art_style_catalog.json`
2. `doc/11-gdd.md`
3. `doc/13-spec-cenas.md`
4. `doc/01_game_design/02_reference_pillars.md` quando existir
5. `doc/03_art/00_art_bible.md` ou `doc/03_art/00_visual_quality_bar.md` quando existir
6. `doc/03_art/01_master_style_manifest.md` quando existir
7. `tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md`

## Quando usar

- projeto novo sem `master_style_manifest`
- projeto com GDD, mas sem direcao estetica congelada
- pedido de jogo AAA, stable, release, delivery ou piloto visual
- troca de tema, genero ou fantasia central
- drift visual entre assets gerados
- projeto legado com `master_style_manifest` antigo, mas sem `art_direction_decision_record`

## Modo padrao

O modo padrao e `autonomous_with_escalation`.

O agente avalia o GDD, fantasia, genero, humor, benchmarks, plataforma e limites VDP contra `art_style_catalog.json`. Ele calcula uma recomendacao conservadora com:

```text
(genre_affinity_match + mood_match + mega_drive_compatibility) - (clone_risk + vram_pressure_penalty)
```

Se a confianca for menor que o `confidence_threshold` declarado no catalogo, registre `art_direction_needs_human_choice` e apresente os 3 candidatos em vez de inventar uma escolha fraca. Se a confianca for suficiente, escolha e siga, registrando `auto_selected=true`.

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
- `art_direction_low_confidence`: confianca abaixo do limiar e nenhuma escolha humana

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
- `style_drift_policy`
- `style_drift_correction_brief` quando houver drift
- status honesto: `passed`, `art_direction_pre_canonical`, `art_direction_low_confidence` ou blocker correspondente

### Passa quando

- o catalogo canonico foi consultado
- pelo menos 3 candidatos foram avaliados ou a justificativa de candidato unico foi registrada
- o estilo escolhido tem compatibilidade Mega Drive declarada e risco de clone delimitado
- o `master_style_manifest` usa descritores tecnicos neutros
- o handoff para sourcing, conversao e excelencia visual esta claro
- projetos AAA/stable/release nao deixam `art_direction_undeclared`, `style_catalog_not_consulted` ou `style_drift_uncorrected` ativos

### Handoff

- para `art-creation-sourcing`: entregar `art_direction_decision_record`, `master_style_manifest` e `style_drift_policy`
- para `visual-excellence-standards`: entregar criterios de coesao e anti-padroes
- para `sprite-animation`: entregar personalidade visual, line weight, paleta e regras de movimento que afetam strips
- para `art-translation-to-vdp`: entregar descritores de material, hue-shift, dithering e limites de drift
