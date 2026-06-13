# Source To ROM Visual Gate

Use este gate sempre que uma entrega queira usar termos como `AAA`, `pronto`, `delivery`, `aprovado_para_conversao` ou `ready_for_aaa`.

Schema de apoio: `tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json`.

## Regra central

Funcionalidade nao substitui qualidade visual. Uma ROM pode compilar, rodar e responder controle, mas fica `visual_gate_blocked` se os assets criticos nao preservarem a arte premium aprovada.

## Fonte premium obrigatoria

Arte premium so existe para o pipeline quando estiver persistida no projeto:

- caminho canonico: `data/source_art/`
- manifesto: `data/source_art/premium_source_manifest.json`
- hash ou tamanho + `mtime` registrado
- lineage apontando para a imagem real

Imagem inline no chat, print, prompt, descricao ou anexo nao salvo fica `generated_inline_pending_persistence`. Nao pode entrar em `data/processed/`, `res/` ou `resources.res` como fonte final ate virar arquivo em `data/source_art/`.

## Benchmark nao e fonte visual

Benchmark tecnico nunca pode virar `source_art`, nem fornecer pose, silhueta, paleta, stage layout, timing copiado frame a frame ou estrutura visual de asset critico.

Uso permitido:

- escala
- densidade
- timing como sensacao de responsividade
- presenca de tela
- budget
- qualidade de leitura

Se o asset critico tiver similaridade estrutural alta com o benchmark, bloquear. O threshold precisa vir de `benchmark_profile.max_similarity` ou do `authoriality_gate_report`; use `0.35` apenas como default conservador quando o perfil nao trouxer valor proprio. O metodo de medicao deve ficar em `clone_risk_method` ou `benchmark_similarity_method`.

## Source validity antes de source_to_rom

`source_validity` deve passar antes de `source_to_rom_visual_match`.

Se a fonte premium for clone, benchmark-derived, sem autoria ou derivada sem licenca/autorizacao rastreavel, `source_to_rom_visual_match` nao pode aprovar nada. Pare a conversao e marque `source_validity_failed` + `visual_gate_blocked`.

## Authoriality gate

Antes da conversao de asset critico:

- personagem principal exige `authorial_model_sheet`
- cenario exige `authorial_stage_concept`
- todo asset critico exige `clone_risk_report`
- `clone_risk_score` respeita o limite declarado pelo `authoriality_gate_report`

Campos obrigatorios no manifesto do asset critico:

- `license`
- `authorial_source`
- `derivative_of`
- `derivative_license_status`
- `clone_risk_score`
- `clone_risk_method`
- `benchmark_used_as`

`benchmark_used_as` deve declarar uso tecnico, como escala, densidade, timing, presenca, budget ou qualidade. Valor como `source_art`, `pose_source`, `palette_source`, `stage_source` ou equivalente bloqueia.

`derivative_of` pode existir quando a licenca permitir derivacao. Nesse caso `derivative_license_status` precisa ser `authorized`, `licensed`, `cc0`, `cc-by-ok` ou equivalente aprovado. Derivacao sem esse status bloqueia.

## Estados de rota visual

- `delivery_candidate`: fonte premium autoral existe, passou por `source_validity`, autoria, paleta/animação quando aplicavel e pode seguir para conversao/runtime.
- `blocked_image_tooling`: nao ha geracao callable, inline persistivel, API/CLI funcional, fonte fornecida pelo usuario ou fonte licenciada aceitavel. Nao criar ROM visual.
- `blocked_no_premium_source`: nao ha fonte visual premium persistida para asset critico. Nao criar runtime de producao visual.
- `lab_not_delivery`: build ou ROM pode existir apenas para testar wrapper, input, cenas, validator ou closeout; deve ficar fora da narrativa de entrega visual.

Quando `blocked_image_tooling` ou `blocked_no_premium_source` ocorrer, o pipeline visual para antes do runtime de producao. Qualquer ROM criada depois disso e laboratorio e precisa declarar `lab_not_delivery=true`.

## Raster local e procedural

`local_author_pixel_rasterization`, `procedural_renderer`, scripts `draw_*` e PNGs gerados por primitivas locais sao permitidos apenas como:

- `debug_lab`
- `visual_lab_control`
- `placeholder`
- prova de runtime sem alegacao AAA

Eles nunca podem ser fonte final de personagem, cenario, HUD heroico, boss ou asset critico de uma entrega AAA. Se um desses canais aparecer como fonte de asset critico em `res/`, o status obrigatorio e `local_rasterization_used_as_final` + `visual_gate_blocked`.

## Artefatos obrigatorios

Antes de promover asset critico para entrega:

- `premium_source_manifest`
- `source_validity_report`
- `authoriality_gate_report`
- `clone_risk_report`
- `asset_lineage_record`
- `source_to_rom_asset_map`
- `benchmark_match_report`
- `visual_delivery_gate_report`
- screenshot/captura da ROM vigente quando o asset ja estiver integrado

## Promocao para res/

Asset critico so entra em `res/` com `elite_ready=true`.

Bloqueiam promocao:

- `needs_review`
- `placeholder`
- `debug_lab`
- `benchmark-derived`
- `rework`
- `perceptual_quality=nao_medido`
- `source_validity=false`
- `authoriality_gate!=passed`

Se for laboratorio, use `lab_not_delivery=true`. Laboratorio pode compilar, mas nao fecha `delivery`.

## Paleta e gi branco

Recolor mecanico e proibido como arte final de sprite heroico.

Gi branco ou tecido claro exige `white_material_palette_contract` com:

- sombras frias azul/roxo
- highlights limpos/quentes
- distancia tonal minima entre sombra, base e highlight
- funcao declarada por slot de paleta

`PALETTE_WASTE` em asset critico bloqueia visual delivery. Quantizacao automatica nao substitui palette pass manual.

## Animacao arcade

Para personagem ou sprite jogavel, o gate visual deve receber:

- `sprite_artifact_report` produzido por `analyze_sprite_strip_integrity.py`
- preview animado, GIF ou equivalente
- contact sheet por animacao
- pivot overlay
- foot-lock/contact report
- active/recovery map para golpes
- `state_belongs_to_character_fantasy=true`

Estados BJJ precisam comunicar BJJ: base baixa, grips, entrada de queda, clinch, queda, guarda ou linguagem corporal propria.

Bloqueios especificos de sprite sheet/strip:

- `FRAME_EDGE_CLIPPING`: pe, mao, cabeca ou kimono encostam/cortam na borda da celula.
- `NON_INDEX0_BACKGROUND_MATTE`: retangulo/cor de fundo sobreviveu dentro da celula e sera renderizado.
- `TRANSPARENCY_INDEX0_BACKGROUND_MISMATCH`: fundo nao esta no indice 0 da paleta.
- `SMALL_ISLAND_DEBRIS`: particulas/fragmentos desconectados indicam limpeza ruim ou restos de celula vizinha.
- `STRAY_LARGE_COMPONENT`: massa desconectada relevante indica pedaco de pose vizinha, recorte ruim ou vazamento de celula.
- `SCALE_INCONSISTENCY`: personagem encolhe/cresce entre estados sem justificativa.
- `BAKED_FX_IN_CHARACTER_SHEET`: spark/impacto ficou colado na animacao do corpo.

Qualquer blocker acima impede `elite_ready=true` para o asset critico e exige retorno ao builder/spec, nao compensacao no runtime.

## HUD formal

HUD de entrega nao pode parecer debug. O report precisa declarar:

- `ui_attention_profile`
- densidade alvo
- hierarquia
- area ocupada
- contraste
- interferencia no gameplay

Se a UI parece overlay de debug, marque `hud_debug_delivery` + `visual_gate_blocked`.

## Budget nao e visual pass

`budget_pass` e `visual_pass` sao eixos separados. Se o runtime cabe com folga, budget nao pode justificar arte pobre. Build limpo e BlastEm observado nao reduzem a exigencia visual.

## Thresholds

Para asset critico:

- `source_validity=true`
- `authoriality_gate=passed`
- `clone_risk_score` dentro do limite declarado
- `source_to_rom_visual_match >= 8`
- `perceptual_quality != nao_medido`
- nenhum status `needs_review`
- nenhum status `rework`
- nenhum status `placeholder`
- nenhum status `debug_lab`
- nenhum status `benchmark-derived`
- `elite_ready=true` quando houver promocao para `res/`

Para prototipo de luta que usa HAMOOPIG como alvo tecnico:

- `benchmark_profile_id: HAMOOPIG_KOF94_MINIMALIST`
- `benchmark_profile.required_match >= 8`
- `benchmark_match >= benchmark_profile.required_match`

Se qualquer threshold falhar, a ROM pode ser `buildado` ou `testado_em_emulador`, mas nao pode ser `pronto`, `AAA`, `delivery` ou `ready_for_aaa=true`.

## Saida minima de `visual_delivery_gate_report`

```yaml
schema: visual_delivery_gate_report.v1
ready_for_aaa: false
blocking_status: visual_gate_blocked
critical_assets:
  - asset_id: player_bjj_fighter
    role: player_character
    premium_source_path: data/source_art/player_bjj_fighter_source.png
    rom_asset_path: res/sprites/player_bjj_fighter_sheet.png
    resources_symbol: spr_player_bjj_fighter
    runtime_usage: src/scenes/<scene>.c
    source_to_rom_visual_match: 0
    perceptual_quality: nao_medido
    visual_status: needs_review
    benchmark_profile: HAMOOPIG_KOF94_MINIMALIST
    benchmark_profile_required_match: 8
    benchmark_match: 0
    source_validity: false
    authoriality_gate: failed
    clone_risk_score: 1.0
    clone_risk_method: hash_or_perceptual_compare
    benchmark_similarity_index: 1.0
    benchmark_similarity_method: structural_or_perceptual_compare
    benchmark_used_as: source_art
    license: missing
    authorial_source: missing
    derivative_of: benchmark
    derivative_license_status: missing
    elite_ready: false
    lab_not_delivery: false
    decision: visual_gate_blocked
```

## Status bloqueantes

- `source_validity_failed`
- `authoriality_gate_failed`
- `clone_risk_too_high`
- `benchmark_similarity_too_high`
- `benchmark_derived_source`
- `license_missing`
- `authorial_source_missing`
- `premium_source_missing`
- `source_to_rom_mismatch`
- `benchmark_match_failed`
- `critical_asset_needs_review`
- `perceptual_quality_unmeasured`
- `local_rasterization_used_as_final`
- `placeholder_promoted_to_res`
- `res_promotion_without_elite_ready`
- `palette_waste`
- `white_material_palette_contract_missing`
- `animation_arcade_gate_missing`
- `sprite_artifact_report_missing`
- `frame_edge_clipping`
- `non_index0_background_matte`
- `small_island_debris`
- `stray_large_component`
- `scale_inconsistency`
- `baked_fx_in_character_sheet`
- `hud_debug_delivery`
