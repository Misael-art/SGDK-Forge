---
name: visual-excellence-standards
description: Use quando a tarefa pedir julgamento estetico, legibilidade, contraste entre planos, dithering funcional, leitura CRT-aware, eficiencia perceptiva de paleta ou canonizacao de feedback visual para assets Mega Drive. Esta skill trata arte como recurso de VDP com barra AAA e memoria acumulada. Nao use para diagnosticar qual cenario de arte o projeto possui, converter tecnicamente assets ja aprovados para o pipeline, buscar assets externos ou validar restricoes pixel-rigidas sem contexto estetico.
---

# Visual Excellence Standards

Esta skill e o cerebro estetico do workspace MegaDrive_DEV.

Quando a entrada principal for uma imagem-fonte high-res, concept art ou arte de IA que precise ser reinterpretada para o VDP, use esta skill em conjunto com `art-translation-to-vdp`.

Quando o alvo for sprite, sheet, objeto ou FX autoral, use tambem
`native-sprite-production`. O julgamento nativo exige o mesmo hash em quatro
vistas: 1x, ampliacao nearest, fundo claro e fundo escuro. E proibido aprovar
por zoom sem verificar 1x ou estimar cores visualmente: conte PLTE/indices com a
ferramenta pixel-strict.

Quando houver historico ou varias epocas, leia
`tools/sgdk_wrapper/.agent/references/visual-workset-and-freeze-contract.md`.
Somente `production_sources` do `active_epoch` podem possuir pixels novos;
material arquivado ou de runtime continua inelegivel mesmo que pareca melhor.

Se a candidata passar tecnicamente e falhar em rosto, maos, pes, guarda,
contato ou feature assinatura, o status e `technical_pass_visual_fail`. Registre
`scale_density_mismatch` quando a densidade nao couber; nao compense com AA,
microcores, detalhe high-res ou troca silenciosa de escala.

Se o `source` vier como prancha editorial, spritesheet com residuos, tile/object sheet ou board misto, a primeira pergunta nao e "qual paleta usar?".
A primeira pergunta e "o que dessa prancha e cena util e o que e ruido semantico?".

Todo asset deve ser tratado como recurso de hardware:
- paleta compartilhada
- tiles 8x8
- custo de VRAM
- legibilidade em 320x224
- contraste entre planos
- potencial de reuso via flip e duplicata

Nao existe "imagem bonita" isolada do hardware. Existe composicao visual que sobrevive ao VDP do Mega Drive.

## Contrato de qualidade de producao

Antes de elogiar, aprovar ou promover um asset, leia
`tools/sgdk_wrapper/.agent/references/production_visual_quality_contract.md`. Quando o projeto possuir
uma `quality_reference_board`, ela e o baseline do papel visual do asset. Nao
aceite melhoria relativa a placeholder, build verde ou screenshot como qualidade
de producao. Registre `source_detail_lost`, `flattened_scene_or_fake_modularity`
ou `decorative_fx_only` quando aplicavel e retorne ao asset/contrato dono.

Piso vivo 2026: `doc/03_art/18_live_scene_bar.md`. Handles RheoGamer/PigsyRetro
sao oficio (densidade arcade legal; traducao de fonte rica), nunca source_art.
Abaixo dos 12 checks da barra → `needs_review`. Sem
`out/logs/live_scene_bar_report.json` o claim visual nao existe.

## Contrato Operacional

### Entrada minima

- fonte visual (ou assets traduzidos por layer) e seu papel na cena
- `context_pack_manifest` quando a arte nasceu de sourcing, IA ou referencia externa
- `art_direction_decision_record`, `master_style_manifest`, `style_drift_policy`, `asset_lineage_record` e `style_memory_index` quando existirem
- `doc/03_art/02_visual_feedback_bank.md` e barra de qualidade quando existirem
- `premium_source_manifest`, `source_to_rom_asset_map`, `benchmark_match_report` e `live_scene_bar_report` quando houver alegacao de `AAA`, `pronto`, `delivery` ou promocao para ROM
- contexto de composicao (`layer_plan` / `shared_canvas_contract`) quando houver multi-plano
- `camera_motion_contract` e `parallax_layer_contract` quando houver palco de
  luta, camera horizontal/vertical, fonte MUGEN/DEF, Tiled parallax ou cena com
  deltas por camada
- `scene_direction_record`, `scene_signature_techniques`, `parallax_layer_contract`, `palette_cycle_decision_card`, `raster_fx_ownership_map` e `background_ecology_card` quando o cenario declarar perfil competente, monumental, signature-only ou qualquer efeito de plano
- `ui_decision_card` quando a surface formal for HUD/UI/overlay/menu
- `ui_pixel_surface_contract` quando a UI formal tiver barra, caixa, micro-icone, cursor, fonte ou surface pixel-perfect de entrega
- `brand_identity_manifest` quando houver logo, title screen, press-start, menu principal ou front-end com identidade de produto
- `text_presentation_profile` quando texto, fala, alerta cinetico ou flavor tiver peso dramatico
- `cutscene_scene_contract`, `cutscene_panel_layout`, `cutscene_palette_script` e `cutscene_text_timing_map` quando houver abertura, cutscene, contexto, briefing ou final
- `scene_transition_card` quando houver transicao formal de cena, zona, ato, menu, cutscene ou estado visual
- `feedback_fx_decision_card`, `boss_setpiece_card`, `advanced_tilemap_design_card` ou `audio_architecture_card` quando a cena tocar esses dominios
- `asset_kind_declaration`, `animation_state_plan`, `pose_roster`, `frame_budget_table`, `pivot_and_scale_contract`, `motion_phase_map` e `frame_delta_report` quando a fonte for personagem animado gerado por IA
- `visual_dna_manifest.scale_contract` quando houver personagem novo, mudanca de escala, key poses ou strips
- `lineart_blocking_1px` quando houver personagem critico, heroi, lutador, boss, NPC expressivo ou asset autoral ainda antes de color blocking/shading
- `style_motion_reverse_engineering`, `turnaround_tracking_contract`, `motion_physics_contract` e `state_transition_motion_contract` quando houver personagem, boss, rotacao, locomocao, golpe, dano, pulo, cutscene animada ou alegacao premium/AAA
- `animation_direction_contract`, `timing_spacing_report`, `impact_frame_contract`, `recovery_curve_report`, `hit_reaction_contract`, `shading_motion_report` e `palette_flash_policy` quando houver lutador, golpe, dano, smear, hitstop, boss ou alegacao premium/AAA
- `source_validity_report`, `authoriality_gate_report` e `clone_risk_report` quando houver asset critico autoral
- `authorial_model_sheet` para personagem principal e `authorial_stage_concept` para cenario autoral
- `visual_dna_manifest`, `design_inheritance`, `project_bible`, `benchmark_usage_policy`, `authorial_consistency_report` e `style_drift_report` quando a revisao envolver autoria, benchmark ou identidade de projeto
- `model_sheet_to_sprite_fidelity_report` quando um personagem, lutador, boss, inimigo grande ou NPC expressivo virar sprite sheet a partir de model sheet aprovado
- `creative_director_radar` quando o projeto for novo, reseed,
  vertical_slice_candidate, ready_for_aaa, front-end autoral, cena assinatura ou
  parecer de lacuna de personalidade
- `art_gameplay_direction_gate` quando houver model sheet, background,
  sprite art, key pose, animation strip, sprite sheet final, FX sheet, HUD
  heroico, title/menu ou asset critico sendo gerado, convertido, revisado ou
  promovido
- `white_material_palette_contract` quando sprite heroico usar gi branco ou tecido claro
- `sprite_artifact_report` quando asset critico for personagem animado, lutador, inimigo grande ou boss
- `model_sheet_to_sprite_fidelity_report` com decisao por traço `must_preserve` quando houver source/model sheet e sprite sheet derivado
- `native_sprite_production_record` validado quando concept, raster high-res ou
  arte de IA tiver destino sprite/sheet/objeto/FX autoral

### Saida minima

- julgamento estetico com criterio observavel (nao apenas subjetivo)
- metricas canonicas aplicadas (ex.: `palette_efficiency`, `layer_separation`)
- `style_cohesion_check` quando houver `master_style_manifest`
- `qa_findings` e `correction_request` quando houver drift, incoerencia de estilo ou arte forte isolada que nao pertence ao projeto
- `style_drift_correction_brief` quando o asset contradizer `art_direction_decision_record` ou `style_drift_policy`
- `animation_coherence_check` quando houver sprite sheet, key poses ou strip de personagem
- `lineart_cleanliness_check` quando houver personagem critico antes de paleta final
- `motion_performance_check` quando houver golpe, dano, locomocao premium, boss ou lutador
- `style_motion_consistency_check` quando houver estilo alvo, benchmark ou model sheet autoral
- `turnaround_volume_check` quando houver 3/4, rotacao, direcoes multiplas ou close-up com angulo diferente
- `motion_physics_check` quando houver peso, gravidade, contato, arco, pulo, queda, golpe ou dano
- `state_transition_motion_check` quando estados jogaveis/cutscene forem encadeados
- `sprite_strip_integrity_check` quando houver strip ou sheet de personagem promovido para runtime
- `asset_kind_check` bloqueando `key_pose_sheet` promovido como `animation_strip`
- `visual_delivery_gate_report` quando houver asset critico indo para ROM ou entrega AAA
- `authorial_consistency_report.json` quando houver asset critico autoral
- `style_drift_report.json` quando o asset mudar linguagem, paleta, line weight, material ou staging do projeto
- `signature_gap_report` quando o asset, cena, HUD, front-end ou efeito estiver
  correto mas generico diante da promessa do projeto
- `art_gameplay_direction_gate_report` quando a revisao envolver asset critico
  que precise provar supervisao conjunta de art director e contexto de game
  design antes de producao ou promocao
- `palette_vitality_check` quando a diretriz visual pedir cor vibrante, quando
  a fonte tiver alta diferenciacao cromatica, quando houver `pass_with_degradation`
  ou quando nearest-color/remap/quantizacao puder apagar material, atmosfera ou
  separacao de planos
- `camera_composition_check` quando o runtime ou screenshot vier de camera com
  scroll horizontal/vertical, palco de luta, zoffset, verticalfollow,
  parallax ou foco em personagens
- `source_to_rom_asset_map` com match visual contra a fonte premium quando a ROM ja usa o asset
- `benchmark_match_report` quando o projeto declarar benchmark de engine, genero ou prototipo
- leitura de `attention_profile` e `hud_density` quando houver UI formal
- `ui_pixel_surface_check` quando houver `ui_pixel_surface_contract`
- `brand_identity_check` quando houver logo, title screen, press-start, menu principal ou front-end autoral
- leitura de `text_surface_class`, ritmo, ancoragem e voz de texto quando houver apresentacao expressiva
- leitura de composicao de painel, rosto, emocao, ritmo de texto e linguagem anime 90s quando houver cutscene
- leitura de `scene_profile`, `signature_techniques`, profundidade, clima, narrativa ambiental, funcao de gameplay e custo perceptivo quando houver direcao de cenario
- leitura de `transition_role`, `continuity_model` e clareza visual quando houver transicao formal
- leitura de `gameplay_signal`, `weak_point_model`, `route_readability_gate` e `audio_role` quando houver cards de espetaculo runtime
- leitura de `typography_role` e contraste tipografico quando houver anexo tipografico
- bloqueios visuais registrados quando aplicavel (ex.: `visual_gate_blocked`)
- recomendacao objetiva de proxima etapa (budget/runtime)
- decisao explicita se baseline pode ser atualizado agora ou se a evidencia ainda esta stale

### Passa quando

- a leitura em 320x224 nativo foi considerada
- para `aaa_game`, vertical slice, asset critico ou `ready_for_aaa`, existe
  `live_scene_bar_report` valido contra
  `tools/sgdk_wrapper/schemas/live_scene_bar_report.schema.json` com
  `status=passed`; ausencia ou `failed` bloqueia `elite_ready`
- handles Rheo/Pigsy (e qualquer praticante da cena viva) entram so como
  `benchmark_used_as: quality_bar`; pixels deles em `data/source_art` bloqueiam
- para arte nova, `art_direction_decision_record` consultou `art_style_catalog.json` antes de qualquer julgamento de excelencia; legado sem record fica `art_direction_pre_canonical`, nao AAA novo
- se houver `master_style_manifest`, assets novos foram comparados contra paleta, line weight, iluminacao, densidade e limite de drift
- se houver `style_drift_policy`, drift nao corrigido gera `style_drift_uncorrected` e bloqueia `elite_ready`
- prompt, manifest ou julgamento estetico nao usam nome de artista vivo, estudio, marca, jogo ou IP como comando de copia; referencias sao tecnicas e `inspiration_only`
- se houver animacao, strips foram julgadas por asset kind, continuidade de pose, volume, pivot, delta entre frames e fluxo; desenhos soltos ou prancha multi-acao nao passam como animacao
- se houver `scene_direction_record`, a cena foi julgada como `minimal`, `competent`, `monumental` ou `signature_only` com base em leitura real, nao em promessa textual
- `scene_direction_record.profile=monumental` exige pelo menos uma tecnica assinada com funcao narrativa ou de gameplay; parallax bonito sem funcao vira `decorative_only_blocked`
- `scene_direction_record.profile=signature_only` exige fallback visual seguro e nao pode ser vendido como equivalente nativo de SNES Mode 7, rotacao livre ou alpha blending
- quando houver `scene_signature_techniques`, cada tecnica precisa do card correspondente: `parallax_layer_contract`, `palette_cycle_decision_card`, `raster_fx_ownership_map` ou `background_ecology_card`
- `archetype_catalog_not_consulted`, `scene_direction_undeclared`, `monumental_promised_without_budget`, `decorative_only_blocked`, `mode7_claim_on_megadrive`, `raster_fx_owner_collision` e `palette_cycle_ownership_conflict` bloqueiam `elite_ready`
- asset critico em `needs_review`, `rework` ou `placeholder` bloqueia `pronto`, `AAA`, `delivery` e `ready_for_aaa=true`
- asset critico em `debug_lab` ou `benchmark-derived` tambem bloqueia `pronto`, `AAA`, `delivery` e `ready_for_aaa=true`
- `perceptual_quality=nao_medido` bloqueia `ready_for_aaa=true`
- `pass_with_degradation` em paleta, remap ou conversao de asset critico nao e
  aprovacao visual; se a diretriz pedir cor vibrante ou a fonte depender de
  contraste cromatico, a entrega precisa de `palette_vitality_check=passed`
  antes de qualquer claim visual
- nearest-color remap massivo, reducao severa de cores uteis ou perda de papeis
  de material recebe `palette_vibrancy_lost`, mesmo quando cada tile cabe em
  uma sub-paleta
- palco de luta com camera X/Y precisa preservar chao, zoffset, foco de
  personagens e planos; screenshot visivel sem `camera_composition_check`
  fica no maximo `lab_evidence`
- `measurement_level` precisa ser `measured`, `emulator_verified` ou `vdp_dump_verified` para qualquer asset critico e para o `visual_delivery_gate_report`; `declared` e `estimated` sao planejamento
- `leaf_blocker_propagation=true` e obrigatorio: se uma folha/asset folha tiver `needs_review`, ilha, stale, `index0_high_risk`, `vdp_dump_missing` ou `measured=false`, o report final herda o blocker e força `ready_for_aaa=false`
- `source_validity=true` precisa existir antes de qualquer `source_to_rom_visual_match`
- `authoriality_gate=passed`, `clone_risk_score` e `benchmark_similarity_index` precisam respeitar os limites declarados pelo `authoriality_gate_report` ou pelo `benchmark_profile` do projeto
- `project_bible` e `visual_dna_manifest` nao podem contradizer o julgamento; divergencia exige `style_drift_report` ou blocker de autoria
- se houver `creative_director_radar`, o julgamento precisa responder aos
  pilares assinatura, aos gaps propositivos e ao primeiro candidato de cena
  memoravel; arte correta mas sem payoff do radar recebe `signature_gap`
- se houver `art_gameplay_direction_gate`, o julgamento precisa responder ao
  review do art director, ao contexto de game design, a perspectiva da camera,
  as interacoes previstas e a lista `must_preserve`; cabelo, olho, roupa,
  emblema, cicatriz, caracteristica fisica unica, arma, acessorio, material,
  assimetria, landmark ou sinal de UI que mude sem justificativa gera
  `cohesion_drift`
- model sheet, background, sprite art, key pose, animation strip, sprite sheet
  final, FX sheet, HUD heroico, title/menu ou asset critico sem
  `art_gameplay_direction_gate` valido ficam no maximo `needs_review` e nao
  podem promover `elite_ready`, `delivery`, baseline ou `ready_for_aaa`
- `benchmark_usage_policy` impede que benchmark vire fonte visual, prompt de copia ou asset em `data/source_art`
- benchmark tecnico nao pode virar `source_art`; use benchmark apenas para escala, densidade, timing, presenca, budget e qualidade
- assets criticos promovidos para `res/` possuem fonte premium real em `data/source_art/` e `source_to_rom_visual_match >= 8`
- assets criticos promovidos para `res/` possuem `elite_ready=true`
- personagem animado critico em `res/` possui `sprite_artifact_report.status=passed`
- personagem animado critico derivado de model sheet possui `model_sheet_to_sprite_fidelity_report.status=passed`; `sprite_artifact_report.status=passed` sem fidelidade visual e apenas conformance tecnica
- personagem novo, heroi, inimigo relevante, lutador, boss ou NPC expressivo possui `visual_dna_manifest.scale_contract` com bbox em multiplos de 8, `scale_lock_status=locked` antes de key poses, FOV/hitbox/workload declarados e politica de mudanca sem resize silencioso
- personagem critico, heroi, lutador, boss, NPC expressivo ou asset autoral passa `lineart_blocking_1px` antes de color blocking; lineart deve ser 1 px, hard-edge, uma cor escura temporaria, sem AA/blur/degraus/double corners/pixels orfaos
- personagem grande animado em `res/` possui `slicing_cell_contract`, `motion_phase_map`, `frame_delta_report`, `contact_sheet`, `pivot_overlay` e `foot_contact_report` reais; relatorio mecanico sem medicao nao aprova animacao
- `pivot_overlay`, `foot_contact_report` e `frame_delta_report` possuem nivel de medicao formal; artefatos sinteticos, declarados pre-geracao ou constantes por construcao bloqueiam `elite_ready`
- personagem heroico, lutador, boss ou acao premium possui `animation_direction_contract` e passa `timing_spacing_report`, `impact_frame_contract`, `recovery_curve_report`, `shading_motion_report` e, quando aplicavel, `hit_reaction_contract`; pose limpa sem timing/spacing de gameplay fica no maximo `needs_review`
- personagem, boss ou NPC expressivo com estilo alvo passa `style_motion_reverse_engineering`; proporcao, line weight, forma e shading nao podem variar entre model sheet, key poses e strips
- rotacao, 3/4, direcoes multiplas ou close-up em outro angulo passam `turnaround_tracking_contract`; partes do corpo nao podem flutuar entre angulos
- locomocao, pulo, queda, ataque, dano ou boss premium passam `motion_physics_contract`; centro de massa, arcos, contato, gravidade e inercia precisam ser legiveis em 320x224
- transicoes jogaveis/cutscene passam `state_transition_motion_contract`; snap visual entre estados bloqueia `elite_ready`
- ataque que comeca direto no active frame, sem anticipation, sem recovery ou com hitstop frame fraco bloqueia `elite_ready`
- smear frame so aprova quando declarado e legivel como movimento; se parecer sujeira, ilha, blur ou fragmento de celula, bloqueia como artefato
- flash frame depende de `palette_flash_policy`; flash sujo por quantizacao, perda de material ou conflito de slots bloqueia visual delivery
- boss/chefao grande so passa como premium se `modular_boss_rig_contract` existir quando o full-body sheet exceder budget seguro
- `FRAME_EDGE_CLIPPING`, `NON_INDEX0_BACKGROUND_MATTE`, `TRANSPARENCY_INDEX0_BACKGROUND_MISMATCH`, `SMALL_ISLAND_DEBRIS`, `STRAY_LARGE_COMPONENT`, `SCALE_INCONSISTENCY` e `BAKED_FX_IN_CHARACTER_SHEET` bloqueiam `elite_ready`
- `local_author_pixel_rasterization` e `procedural_renderer` nao aparecem como fonte final de asset critico
- ROM de entrega que parece painel de debug, matriz ASCII, lista de efeitos ou amostra procedural deve receber `lab_not_delivery=true`; `VDP_drawText` dominante, `lab_bg_b` unico, `safe rhythm lane`, `efeito empurra`, nomes de efeito em tela ou fallback procedural repetido bloqueiam `ready_for_aaa=true`
- fallback visual so passa quando preserva a intencao perceptiva e mecanica especifica do efeito; fallback generico reutilizado para varios efeitos vira `mass_generic_procedural_fallback`
- `PALETTE_WASTE` em asset critico bloqueia visual delivery; quantizacao automatica nao substitui palette pass manual
- material critico precisa de `material_color_ramp_plan` com hue shift curado ou justificativa explicita para rampa neutra; straight shading lavado, sombra cinza morta ou highlight sem funcao bloqueiam arte premium
- gi branco ou tecido claro passa por `white_material_palette_contract` com sombras frias azul/roxo, highlights limpos/quentes, distancia tonal minima e funcao declarada por slot
- quando houver `benchmark_profile.required_match`, `benchmark_match` precisa atingir esse valor; HAMOOPIG e apenas um perfil possivel, nao regra global
- `budget_pass` e `visual_pass` permanecem separados; runtime com folga nao justifica arte pobre
- os sintomas foram traduzidos em diagnostico tecnico e heuristica preventiva quando necessario
- a decisao resultante nao contradiz o hardware sem declarar tradeoff
- quando houver UI formal, `attention_profile`, `hud_density` e clareza da arquitetura ficam registrados
- quando houver `ui_pixel_surface_contract`, ele valida contra `tools/sgdk_wrapper/schemas/ui_pixel_surface_contract.schema.json`; runtime aprovado exige leitura nativa, movimento inteiro, budget de atlas e evidencia BlastEm
- health bar de entrega declara container, buffer de dano latente, fill ativo, passos inteiros de pixel, edge hard-aliased, threshold critico e low-HP feedback; retangulo simples sem buffer fica no maximo `needs_review`
- quando houver title/logo/front-end autoral, `brand_identity_manifest` valida contra `tools/sgdk_wrapper/schemas/brand_identity_manifest.schema.json`
- logo/title aprovado para runtime passa silhueta, monocromatico, miniatura, fundo dinamico e leitura em 320x224
- metafora visual do logo reforca mecanica, mundo ou fantasia sem prejudicar leitura do nome
- quando houver `creative_director_radar`, benchmark citado no parecer fica
  limitado a eixo de qualidade; copiar layout, paleta, pose, musica, historia,
  logo ou personagem bloqueia autoria
- fonte SGDK default ou fonte generica fica restrita a debug/fallback; identidade final exige fonte-display/fonte-body planejadas e `glyph_manifest`
- camadas runtime do logo possuem superficie VDP, dominio de paleta, fallback estatico e budget referenciado
- HUD de entrega nao parece debug e declara `ui_attention_profile`, densidade alvo, hierarquia, area ocupada, contraste e interferencia no gameplay
- quando houver texto expressivo, legibilidade, ritmo, personalidade e funcao dramatica vencem ornamentacao
- quando houver cutscene, o visual passa por barra anime 90s: rosto expressivo, olhos legiveis, silhueta de cabelo/pose, linework duro, rampas com hue-shift, paineis com foco claro e texto sem brigar com a imagem
- cutscene com arte suave, blur, gradiente de IA, retrato sem expressao, painel morto ou texto jogado por cima fica no maximo `needs_review`
- cutscene AAA sem `cutscene_motion_beat_map`, blink/mouth/reaction aplicavel ou `stillness_justification` fica no maximo `needs_review`
- cutscene fullscreen sem justificativa de tiles/paleta e fallback de painel/pan nao pode ser `elite_ready`
- tile-first e obrigatorio para portabilidade, mas nao pode destruir a alma visual; aprovacoes de cena exigem comparacao `original/basic/elite/rom` quando a tarefa for portabilidade de cenario/cena
- quando houver transicao formal, a tecnica comunica causa, geografia, tom, risco ou ritmo; se for so bonita, reprovar
- quando houver feedback FX, boss/setpiece, tilemap avancado ou audio senior, a leitura de gameplay vence excesso visual, ruido e ambiguidade
- quando houver tipografia relevante, fonte-display, fonte-body, acentos e separacao contra o fundo ficam julgados
- baseline visual so pode ser atualizado depois de captura deterministica, `expected_app_scene_id` confirmado e `freshness_audit_report.json` sem stale bloqueante
- `frozen_case_study` nunca atualiza baseline nem recebe nova arte; seus
  artefatos servem somente como evidencia positiva/negativa das regras extraidas
- baseline comparativo e obrigatorio para validacao visual AAA; screenshot capturada sem baseline persistido prova execucao, nao prova regressao visual
- `visual_vdp_dump.bin` e obrigatorio para entrega AAA e tambem quando screenshot indicar faixa indevida, plano descoberto, garbage/tile corruption, conflito de paleta ou suspeita VRAM
- `workspace_scope_isolation=true` deve constar quando o workspace global estiver sujo; sujeira fora do projeto nao pode entrar no score nem ser usada como prova de entrega
- closeout nao pode ser `ok` se `validation_report.blocking_statuses` nao estiver vazio; `visual_gate_blocked` produz status final `blocked`

### Handoff para proxima etapa

- se a rota visual estiver congelada: entregar para `hardware/megadrive-vdp-budget-analyst`
- se ainda faltar traducao: entregar para `art/art-translation-to-vdp` com lista objetiva de ajustes

## Regra de Ouro

Nenhum feedback humano corrige PNG diretamente.

Fluxo obrigatorio:
1. Capturar o sintoma em linguagem observavel.
2. Traduzir o sintoma em diagnostico tecnico.
3. Escrever uma heuristica preventiva em [doc/03_art/02_visual_feedback_bank.md](doc/03_art/02_visual_feedback_bank.md).
4. Atualizar esta skill se a heuristica passar a valer como regra geral.
5. So entao corrigir o asset.

Se o agente pular esse fluxo, a melhoria nao foi canonizada. Foi improvisada.

## Gate de direcao arte + game design

Antes de gerar, converter, aceitar ou promover model sheet, background, sprite
art, key pose, animation strip, sprite sheet final, FX sheet, HUD heroico,
title/menu ou asset critico, emitir `art_gameplay_direction_gate` validado
contra `tools/sgdk_wrapper/schemas/art_gameplay_direction_gate.schema.json`.

O gate deve provar:

- supervisao do `art-director` ou parecer humano equivalente;
- contexto de game design: GDD/spec, papel no gameplay, camera/perspectiva,
  oponente/obstaculos/cenario e interacoes relevantes;
- continuidade de identidade: cabelo, olhos, rosto, roupa, emblemas,
  cicatrizes, caracteristicas fisicas unicas, armas, acessorios, materiais,
  assimetrias, landmarks e sinais de UI;
- movimento e carisma quando aplicavel: cabelo, tecido, faixa, expressao
  facial, maos, peso, anticipation, active, recovery e follow-through;
- decisao de bloquear, seguir para geracao, seguir para conversao ou voltar
  para lineart/blocking.

Sem esse gate, o maximo status permitido e `needs_review`. Se o asset ja foi
produzido, a ausencia do gate vira blocker retroativo: `director_gate_unapproved`.

## Gate obrigatorio para model sheet e sprite de personagem

Para personagem critico, lutador, boss, inimigo grande ou NPC expressivo,
o primeiro julgamento visual e topologia, nao textura.

Antes de aceitar model sheet, key pose ou frame individual:

- contar exatamente 2 bracos, 2 pernas, 1 cabeca e 1 tronco, salvo excecao
  explicitamente declarada no design;
- confirmar que cada braco nasce de um ombro plausivel e cada perna nasce de
  um quadril plausivel;
- rejeitar membro duplicado no mesmo ombro/quadril, membro fantasma,
  sobreposicao ambigua que pareca membro extra ou extremidade amorfa;
- auditar maos, pes, dedos e polegares quando a silhueta permite leitura;
- verificar consistencia de escala estrutural entre poses: cabeca, torso,
  ombros, quadris e proporcao base nao podem mudar arbitrariamente;
- exigir pose de costas/turnaround quando o model sheet pretende virar fonte
  canonica de producao longa;
- `authorial_model_sheet` so vira fonte de producao quando `scale_contract`,
  `turnaround_tracking_contract`, marcadores de figurino/material e mapa de
  paleta/material estiverem travados; sem isso, ele e apenas direcao visual e
  nao autoriza spritesheet final;
- listar marcadores de figurino, emblemas, acessorios, cores e materiais
  obrigatorios por pose; eles nao podem sumir, trocar de lado ou mudar de
  material sem oclusao/acao justificavel;
- para personagem assimetrico, declarar contrato por membro/lado antes de
  spritesheet;
- em membro especial/assimetrico, validar endpoint: ombro, cotovelo,
  punho/mao, pe ou extremidade equivalente precisam estar presentes e legiveis
  em todas as poses aplicaveis;
- exigir mapa de paleta/material quando a fonte for candidata a personagem
  recorrente, lutador, boss ou heroi;
- para personagem SGDK/VDP, preferir shading por clusters limpos com 2-3 tons
  bem espacados por material; spray, ruido de detalhe, textura miuda e
  micro-pixels que viram tile-noise bloqueiam fonte candidata a spritesheet;
- planejar personagem em 1 paleta de 16 entradas (15 uteis + transparencia)
  sempre que possivel; FX separado pode usar outro slot apenas quando estiver
  em strip/camada distinta;
- exigir acting facial por estado: idle focado, golpe com mandibula
  tensionada/dentes/kiai/olhos estreitos, dano com dor ou choque;
- conferir eye tracking: olhos miram a linha de ataque/oponente, nao o chao
  ou o proprio corpo sem intencao.

Falha nesse gate bloqueia conversao final, `visual_aprovado`, `delivery`,
`ready_for_aaa` e qualquer promocao de baseline, mesmo que o asset compile.

## Sintaxe tecnica nao e semantica visual

PNG indexado, PLTE <= 16, grid 9-bit, build SGDK e screenshot BlastEm
provam que o pipeline roda. Nao provam que a arte e boa.

Todo lutador/personagem critico em 48x64 precisa responder, em runtime:

1. olhos, arma/braco/feature assinatura e roupa principal sao identificaveis?
2. a paleta preserva materiais e temperatura cromatica do concept?
3. o sprite parece pixel art nativa de 16 bits, nao foto/render encolhido?

Se a resposta de 1 ou 2 for "nao", ou 3 indicar imagem degradada, o asset
fica `placeholder`/`needs_rework` e o gate visual continua fechado.

## Gate de fidelidade model sheet -> sprite sheet

Para personagem, lutador, boss, inimigo grande ou NPC expressivo derivado de
model sheet, o agente deve provar heranca visual antes de aceitar a folha.

`sprite_strip_integrity`, PNG modo P, PLTE <= 16, celula 48x64 e pivots
estaveis medem sintaxe e integridade. Eles nao medem se o personagem ainda e o
mesmo.

Antes de promover para `res/`, baseline visual, `elite_ready`, `delivery` ou
`ready_for_aaa`, emitir `model_sheet_to_sprite_fidelity_report` validando:

- anatomia e proporcao do model sheet;
- rosto, olhos, expressao e direcao do olhar;
- feature assinatura, arma, membro especial ou silhueta proprietaria;
- roupa, marcadores, paleta/material e contraste semantico;
- acting por estado, especialmente ataque, dano, idle e locomocao;
- comparacao lado a lado `model_sheet + sprite_sheet + contact_sheet`, em
  escala nativa e ampliacao de review.

Falhas canonicas:

- `signature_feature_loss`
- `anatomy_simplified_into_block_mass`
- `face_or_eye_readability_lost`
- `material_palette_semantics_lost`
- `generic_blocky_redraw`

Qualquer falha acima deixa `visual_pass=false`, mesmo quando
`technical_pass=true`. A proxima rota e voltar para `lineart_blocking_1px` por
estado/acao; nao remendar o PNG final nem compensar no runtime.

## Gate de topologia de materiais

Mapa anatomico e mapa de materiais respondem perguntas diferentes. `torso`
nao decide onde um crop top termina; `arms_or_guard` nao decide se um pixel e
pele, manga, bracelete ou outline. Depois do color blocking e antes de sombra:

- exigir `material_region_contract` em candidatos novos (`schema_version=1.4.0`)
- atribuir um proprietario a cada pixel visivel e uma rampa exclusiva a cada
  material; somente outline/deep shadow declarado pode ser compartilhado
- declarar fronteiras criticas de figurino/material e inspeciona-las em 1x
- reprovar cor de roupa dentro de pele, cor de pele dentro de roupa e qualquer
  AA hibrido sem papel explicito como `material_palette_leakage`
- preferir borda dura de 1 px. Sombra de roupa permanece no lado da roupa;
  sombra de pele permanece no lado da pele

Ao receber feedback humano sobre vazamento, preserve a candidata em rework e aplique o
menor patch causal: primeiro a fronteira mais legivel/identitaria, depois as
secundarias. Regeneracao integral so e permitida se a topologia, e nao apenas a
cor, estiver errada. O review deve mostrar mapa de materiais, overlay de
fronteiras, 1x e nearest; zoom sozinho nao aprova.

## Gate de fonte visual canonica

Para personagem, lutador, boss, NPC expressivo ou asset autoral gerado em
etapas, `model_sheet_to_sprite_fidelity_report.status=passed` significa apenas
"candidato medido". Nao significa fonte autorizada para a proxima geracao.

Se houver `human_visual_review_missing_for_aaa`, `visual_vdp_dump_missing`,
`visual_gate_blocked`, `runtime_candidate_not_source` ou falha visual humana:

- marcar a sheet, strip, contact sheet e GIF como
  `obsolete_for_generation_source`;
- usar esses arquivos apenas como `negative_evidence`, `comparison_only` ou
  `runtime_evidence_only`;
- bloquear qualquer prompt, contrato, builder ou relatorio que use esses
  arquivos como `source`, `baseline`, `reference_for_generation`,
  `img2img_base`, `generation_source` ou `image_reference`;
- exigir `visual_source_of_truth` e validacao por
  `tools/sgdk_wrapper/validate_visual_source_of_truth.ps1`;
- a proxima sheet nasce do model sheet aprovado/travado, visual DNA, brief de
  direcao, `art_gameplay_direction_gate`, lineart 1 px por estado e key poses.

## Baseline Visual

- nao atualize baseline para esconder diferenca estetica causada por runtime instavel
- screenshot bonito sem `scene_id` esperado, MDRT coerente e freshness recente continua sendo artefato de bancada
- se o diff visual for grande, classifique primeiro: rework estetico, corrupcao de VRAM/tilemap, cena errada ou baseline obsoleto
- quando a classificacao for `baseline_obsoleto`, registre a causa e rode o closeout da cena antes de promover

## Leitura obrigatoria

Antes de qualquer iteracao visual relevante:
1. Ler [doc/03_art/18_live_scene_bar.md](doc/03_art/18_live_scene_bar.md) (piso vivo; brief se o contexto estiver curto)
2. Ler [doc/03_art/02_visual_feedback_bank.md](doc/03_art/02_visual_feedback_bank.md)
3. Ler [doc/03_art/00_visual_quality_bar.md](doc/03_art/00_visual_quality_bar.md)
4. Ler [doc/03_art/01_visual_cohesion_system.md](doc/03_art/01_visual_cohesion_system.md)
5. Ler `references/source_to_rom_visual_gate.md` quando houver entrega, ROM ou asset critico
6. Conferir o budget da cena e a funcao do asset no gameplay
7. Se a fonte for complexa, exigir `semantic_parse_report` antes de julgar a traducao

## Metricas canonicas

Estas metricas devem ser usadas pelo agente, pelo `analyze_aesthetic.py` e pelo discurso tecnico sobre arte:

### `palette_efficiency`
- Mede se a paleta esta trabalhando a favor do asset ou desperdicando slots.
- Penaliza cores redundantes, pouca distancia tonal util e cores quase indistinguiveis.
- Pergunta base: "Cada cor ganhou o direito de existir?"

### `tile_efficiency`
- Mede aproveitamento real dos tiles 8x8.
- Penaliza bordas vazias, bounding box frouxo e excesso de tile morto.
- Pergunta base: "Quanto desse sprite consome VRAM sem entregar leitura?"

### `detail_density_8x8`
- Mede riqueza de detalhe por tile sem confundir ruido com acabamento.
- O alvo e densidade legivel, nao sujeira.
- Pergunta base: "O tile conta materia e volume ou so empilha pixel?"

### `dithering_density`
- Mede se o dithering foi usado como ferramenta de gradiente e material, nao como muleta aleatoria.
- Bom dithering cria transicao e textura controlada.
- Mau dithering parece ruido ou xadrez sem funcao.

### `silhouette_readability`
- Mede se a massa principal do sprite e clara em 1 frame.
- Outline, massa, pose e contraste interno devem colaborar.
- Pergunta base: "O jogador reconhece a forma antes de ler detalhes?"

### `layer_separation`
- Mede separacao tonal e luminosa entre sprite e fundo, ou entre BG_A e BG_B.
- O plano importante deve vencer a disputa de leitura.
- Pergunta base: "O gameplay salta do fundo ou afunda nele?"

### `reuse_opportunity`
- Estima quanto do asset poderia ser reorganizado para maior reuso em VRAM.
- Considera duplicatas, espelhamentos e oportunidades de consolidacao de tiles.
- Pergunta base: "Estamos pagando VRAM por informacao nova ou por repeticao desorganizada?"

### `style_cohesion`
- Mede se o asset pertence ao mesmo mundo visual dos assets aceitos.
- Usa `master_style_manifest`, `style_memory_index` e `asset_lineage_record` quando existirem.
- Pergunta base: "Este asset fortalece a linguagem do projeto ou parece importado de outro jogo?"

## Traducao de estetica para hardware

## Exploracao controlada de rotas visuais

Quando o usuario pedir alternativas, ou quando uma cena critica admitir duas leituras fortes sem quebrar o hardware, esta skill deve julgar as rotas como uma familia controlada, nao como experimentos soltos.

Para sprite derivado de raster high-res, consumir tambem
`../native-sprite-production/references/source-route-triage-protocol.md` e o
`route_shootout_report`. Reprovar antes do julgamento estetico quando:

- a fonte direta contem sombra, poeira, fumaça, nuvem, particula, floor line,
  checkerboard ou oclusao que pode ser confundida com anatomia/material;
- o nome da rota nao esta ligado causalmente ao output;
- a alternativa e uma mascara/recolor/near-duplicate, e nao uma hipotese visual;
- personagem foi desenhado por primitivas, spans ou coordenadas hardcoded;
- uma probe mecanica esta sendo apresentada como lineart ou sprite nativa.

Entregas esperadas:

- `route_exploration_board`
- `route_comparison_matrix`
- `route_preferred_by_judge`
- `locked_visual_direction` apos escolha humana

Regras:

- todas as rotas devem compartilhar o mesmo `shared_canvas_contract`
- todas as rotas devem respeitar o mesmo teto de paleta e a mesma historia espacial
- cada rota deve declarar qual eixo esta variando
- rotas nao podem competir por geometrias ou enquadramentos incompatíveis

Eixos aceitaveis de variacao:

- ceu e atmosfera
- temperatura global
- contraste e densidade de sombra
- peso do `BG_B` versus `BG_A`
- limpeza versus aspereza do material

Eixos proibidos sem nova rodada de composicao:

- perspectiva
- distribuicao de massas principais
- posicao do ponto focal
- papel estrutural dos planos

Protocolo de julgamento:

1. eliminar rotas que so parecem fortes ampliadas
2. eliminar rotas que sacrificam gameplay para ganhar ilustracao
3. ranquear as sobreviventes por leitura, atmosfera, coerencia de projeto e risco de budget
4. recomendar uma rota, mas preservar a escolha do usuario quando mais de uma ainda for valida

## Regra de incumbencia

Quando ja existir uma rota padrao aprovada no projeto, ela passa a ser o `incumbent visual method`.

As rotas alternativas podem ser apresentadas ao usuario, mas nao substituem o incumbente por default.

Para um desafiante substituir o incumbente, ele precisa vencer em dois niveis ao mesmo tempo:

1. `perceptual win`
   - leitura igual ou melhor
   - identidade da cena igual ou melhor
   - coerencia com a linguagem do projeto igual ou melhor
2. `system win`
   - budget igual ou melhor
   - risco estrutural igual ou menor
   - promocao para ROM igual ou mais honesta

Regra:

- se o desafiante so vencer em "imagem bonita isolada", ele nao toma o lugar do incumbente
- se o incumbente for multi-plano, o julgamento precisa acontecer em contexto composto, nao apenas na layer isolada
- na ausencia de vitoria clara do desafiante, o default continua sendo o metodo padrao ja consolidado

Aplicacao pratica:

- `visual_excellence_score` isolado nao pode derrubar sozinho um metodo incumbente multi-plano
- a decisao final de rota deve considerar tambem reuse, pressao de tiles e aderencia ao `source` como cena

Regra de ouro:

- o foco AAA nao significa impor uma unica resposta
- significa oferecer poucas rotas excelentes, cada uma honesta com o hardware, e depois congelar a direcao escolhida para manter coerencia visual

### Dithering
- Nao e enfeite.
- E mecanismo para simular gradiente, materiais e atmosfera com poucas cores.
- Em metal, ceu, pedra e fumaca, a ausencia de dithering so e aceitavel se houver outra solucao de volume igualmente forte.

### Outline
- Outline serve para separar massa, fixar silhueta e impedir que o sprite suma no fundo.
- Outline nao precisa ser preto absoluto em todos os casos, mas precisa produzir leitura.

### Volume
- Todo material principal precisa de pelo menos tres estados legiveis: luz, base e sombra.
- Volume sem direcao de luz nao existe. E borrado.

### Materiais
- Metal: highlights agressivos, contraste alto, transicoes controladas
- Pedra: massa opaca, textura rustica, quebra de superficie
- Pele: rampas mais suaves, leitura de plano, contraste localizado
- Tecido: sombra mais larga, menos brilho especular

### Contraste de planos
- BG_B deve competir menos que BG_A.
- Sprite principal deve competir menos consigo mesmo do que com o fundo.
- Se tudo brilha igual, nada conduz gameplay.

### Economia de paleta
- Compartilhar paleta nao e sacrificio. E planejamento.
- Paleta boa serve a mais de um sistema da cena sem destruir hierarquia visual.
- Em traducao elite, quantizacao cega so pode servir de controle.
- O resultado canônico vem de curadoria manual semantica: escolher quais rampas ficam, quais tons fundem e qual highlight realmente merece sobreviver.

### Review de tileset
- `palette_strip`, `tileset_sheet` e auditoria de `H-Flip` ajudam a revelar disciplina estrutural real.
- Isso e criterio de review e planejamento de VRAM, nao objetivo estetico isolado.
- Se a imagem fica mais "organizada" mas menos legivel, o review esta certo e a transformacao visual esta errada.

### Leitura em 320x224
- Avalie sempre em escala nativa.
- Se um detalhe so funciona ampliado, ele ainda nao existe no jogo.

## Menus e Title Screens

Menu forte no Mega Drive nao e tela parada com lista de opcoes. E uma cena de apresentacao.
Referencia longa: `doc/03_art/12_menu_visual_language.md`.
Doutrina complementar obrigatoria: `doc/03_art/13_hud_ui_fx_decision_system.md`.

Checklist canonico:
- o menu precisa compor a proposta do jogo, nao uma estetica generica solta
- o fundo deve permanecer vivo em idle, via parallax, cycling, wobble, timeline curta ou equivalente tematico
- o olhar deve ser conduzido por uma geometria forte, como piso em perspectiva ou outra estrutura espacial coerente com o tema
- a tipografia deve vencer o fundo com outline, sombra dura ou separacao de valor igualmente forte
- a opcao selecionada deve ter feedback ativo visivel, nao apenas troca de cor
- a paleta deve ter contraste alto e hierarquia perceptiva clara

Defaults fortes:
- 2 a 3 camadas de profundidade
- um eixo visual dominante no fundo
- item selecionado com pulso, seta viva, brilho corrido ou cycling controlado

Regra de versatilidade:
- `grade infinita` e referencia historica, nao obrigacao universal
- o equivalente correto depende do projeto: energia, ruina, arquitetura, magia, industria, horizonte urbano ou outro motivo espacial forte

Anti-padroes:
- fundo sem vida
- excesso de detalhe atras do texto
- menu que parece overlay de debug
- identidade visual desconectada do jogo

### Identidade minima de front-end

Regra generalizada para identidade minima de front-end.

Em `aaa_game`, logo, fonte, menu e creditos entram cedo como contrato de
primeira impressao. Nao precisam ser arte final no planejamento, mas precisam
ter:

- `brand_identity_manifest` para logo/title/press-start/front-end autoral
- perfil de fonte/texto quando a tipografia carrega genero, tom ou narrativa
- contrato de menu com input, feedback selecionado, layout e fallback
- contrato de creditos quando houver cena de creditos planejada
- teste futuro de leitura em 320x224, silhueta/monocromatico/thumbnail quando
  houver logo

Branding/texto puro com `VDP_drawText` e aceitavel como debug/seed, mas nao como
identidade final. Mockup local pode orientar composicao somente quando tem hash
e status `mockup_reference_only`; ele nao substitui pixel art final, captura
BlastEm, paleta auditada ou visual delivery gate.

## HUD, interface e overlay

- quando houver surface formal de UI, ler o `ui_decision_card` antes de julgar a imagem
- `attention_profile` define quanta disputa visual a interface pode criar por segundo
- `hud_density` nao pode subir alem do que a mecanica consegue sustentar
- `typography_role` decide a rota:
  - `hud_critical` tende a `fixed_custom_hud_font`
  - `narrative_text` tende a `variable_width_tidytext`
  - `front_end_premium` pode pedir `display_font_plus_body_font`
- `window_plane_static_hud` continua sendo o default seguro para leitura constante
- `fixed_custom_hud_font` e o default forte para timer, score, ammo, labels e leitura rapida
- `variable_width_tidytext` sobe para dialogo, credito, lore e corpo de texto premium em PT-BR
- reprovar fonte ornamental pesada ou compositor proporcional em HUD de combate
- `window_plane_lifebar` e `sonic_hud_physics_family` sao referencias de pattern, nao defaults universais
- health bar forte nao e retangulo colorido: precisa moldura legivel, fill ativo, buffer de dano latente, drenagem por pixels inteiros e feedback critico controlado
- UI pixel art nao pode usar subpixel, engine free-scale ou interpolacao; texto e barras devem se mover/renderizar no grid inteiro
- `raster_enhanced_ui` e `procedural_raster_glitch_suite` so passam quando houver ganho perceptivo real, `fx_ownership_map` e fallback honesto

## Texto narrativo expressivo

Doutrina complementar: `doc/03_art/16_expressive_narrative_text_presentation.md`.

- quando texto virar cena, fala, alerta, painel, balao, retrato ou flavor, ler `text_presentation_profile`
- `panel_sequence_text` precisa conduzir ritmo e reacao; painel bonito sem leitura dramatica deve cair para texto simples
- `diegetic_speech_balloon` precisa ter anchor claro e nao cobrir HUD, rota, hitbox ou leitura de risco
- `animated_portrait_dialog` precisa comunicar vida por blink, mouth frames ou emocao simples; retrato estatico e fallback honesto
- `kinetic_hype_text` deve ser lido em 1 segundo antes de virar FX
- `typewriter_voice_text` precisa combinar cadence visual, pausa e som sem roubar SFX critico
- `flavor_text_interaction` deve recompensar exploracao; texto generico repetido nao e polish AAA
- reprovar qualquer apresentacao que seja apenas "texto charmoso" sem funcao de ritmo, personagem, mundo, alerta ou recompensa

## Transicoes contextualizadas

- quando houver transicao formal, ler o `scene_transition_card` antes de julgar a imagem
- `transition_role` precisa explicar por que a troca existe: geografia, causa narrativa, ritmo, risco, humor, maquina, sonho ou palco
- `continuity_model` decide o julgamento visual:
  - `spatial_scroll_bridge` precisa preservar leitura de camera e esconder o seam
  - `scripted_avatar_bridge` precisa fazer o avatar parecer agente da passagem, nao passageiro de cutscene vazia
  - `lighting_state_transition` precisa manter silhueta, paleta e prioridade de gameplay legiveis
  - `raster_distortion_bridge` precisa servir agua, impacto, sonho, corrupcao ou choque fisico, nao enfeite solto
  - `pseudo3d_perspective_bridge` precisa justificar o custo como setpiece e declarar fallback
- se a transicao tocar HUD, menu, title, overlay ou texto, consumir tambem o `ui_decision_card`
- `palette_fade_bridge` e fallback honesto, mas nao deve substituir uma passagem espacial clara quando o mundo poderia conectar as cenas
- reprovar efeito que esconda estado do jogador, confunda direcao de movimento ou quebre o ritmo sem payoff dramatico

## Espetaculo runtime AAA

Doutrina complementar obrigatoria: `doc/03_art/15_aaa_runtime_spectacle_decision_system.md`.

- quando houver raster, H-Int, line scroll, palette split, Shadow/Highlight, palette cycling, hit sparks ou particulas, ler `feedback_fx_decision_card`
- `gameplay_signal` decide a permissao do FX; se nao comunica impacto, risco, estado ou recompensa, reprovar
- `readability_target` nao pode perder para brilho, poeira, shake, debris ou choque de paleta
- `lighting_state` precisa manter silhueta, volume critico e `palette_slot_audit`
- `sprite_particles` e `tile_particles` precisam reforcar direcao de impacto, nao virar confete visual
- quando houver boss ou setpiece, ler `boss_setpiece_card`
- `telegraph_profile` precisa ser lido em tempo real: startup, active, recovery e weak point precisam parecer intencionais
- quando houver tilemap avancado, ler `advanced_tilemap_design_card`
- `route_readability_gate` precisa responder para onde o jogador olha em 1 segundo
- quando houver audio senior, ler `audio_architecture_card` para coerencia dramatica entre imagem, stinger, impacto e silencio
- maximalismo visual nao autoriza ambiguidades: efeito caro sem leitura clara e bloqueio visual

## Extrapolacao legitima do VDP

### Repartir budget e melhor que fingir que o limite nao existe

- O caminho elite nao e forcar uma cena impossivel.
- O caminho elite e reorganizar budget com intencao.
- A primeira resposta estrutural deve ser a menos fragil.
- Em cenas de cenario grande, `VDP_setPlaneSize(..)` vem antes de alias de tabela.
- Se o foreground realmente precisa de uma paleta propria, mover o background para `3+1` pode ser decisao superior.
- Se a profundidade pede um elemento intermediario, `sprite graft` pode ser legitimo.
- Se a prova em ROM nao comporta dois planos completos, `compare_flat` pode ser a forma honesta de provar leitura sem mentir sobre o hardware.

### Taxonomia de montagem avancada

- `canonica_segura`
  - `plane size tuning`
  - reorganizacao de paleta
  - `SPR_initEx(u16 vramSize)` quando a medicao pedir
  - `compare_flat`
- `avancada_com_tradeoff`
  - `window alias`
  - `hscroll slack reuse`
  - `sprite graft`
- `opt_in_de_cena_especial`
  - `SAT reuse`
  - quirks de mascaramento ou comportamento off-screen
  - `borrowed_fx_ramp`

Regra:

- tecnica de layout nao e virtude estetica por si so
- ela so sobe de categoria quando preserva leitura e reduz fragilidade do layout

### Auditoria de slot em Shadow/Highlight

- Em cenas que usam Shadow/Highlight para afetar fundo e sprite juntos, o ultimo slot visivel da paleta do sprite deve ser tratado como auditado.
- Nao colocar ali:
  - highlight principal de pele
  - highlight principal de metal
  - volume critico que deve reagir normalmente a sombra
- Esse slot pode ser sacrificado de forma defensiva ou usado de forma intencional para ponto emissivo.
- Sem `palette_slot_audit`, a cena com Shadow/Highlight nao esta madura.

### Waterline e palette split

- Separacao de agua, atmosfera ou gradiente dramatico por split mid-frame deve preservar coerencia cromatica entre os dois hemisferios da tela.
- A parte abaixo da linha nao pode parecer "outra fase" sem causa.
- Se a linha oscilar, a leitura precisa continuar estavel quadro a quadro.

### Leitura sob interlace

- `interlaced_448` nunca deve ser julgado apenas por "caber mais coisa".
- O criterio visual minimo e: shimmer toleravel, tipografia legivel e ganho real de layout em relacao ao modo normal.
- Se a cena treme mais do que informa, o modo foi mal aplicado.

### Ilusoes modernas honestas

- `masked_shadow_highlight_lighting`
  - deve ser julgado como spotlight, lanterna ou weak spot de boss, nunca como luz suave de engine moderna
- `procedural_raster_glitch_suite`
  - so funciona quando o ruído e dirigido e o jogador continua lendo risco, hitbox e objetivo
- `mutable_tile_decal_mutation`
  - o valor visual esta na persistencia localizada e na narrativa do impacto, nao em prometer destruicao universal
- `cellular_microbuffer_sim`
  - so e elite quando uma ilha pequena parece organica sem trair o budget; aumentar a area sem necessidade e erro de direcao

### Gate `high_color_illusion`

Origem: itens de high-color/true-color do lote `curation_batch_2026_06_16`,
evidencia `E1_text`, expansao candidata. Reusa os contratos/cards existentes
(`raster_fx_ownership_map`, `palette_cycle_decision_card`, `scroll_fx_contract`,
`palette_role_map`); nao cria schema novo e nao promete AAA/runtime.

- toda cena que parecer ter mais cores que o limite real (60 visiveis em 4
  sub-paletas) deve declarar a tecnica que produz a ilusao: H-Int palette swap,
  Shadow/Highlight, palette cycling, dithering estrutural ou composicao por
  planos. Ilusao high-color sem tecnica declarada fica `high_color_illusion_undeclared`.
- gradiente suave real nao existe; usar rampas discretas, dither estrutural ou
  troca de paleta. Claim de gradiente continuo sem tecnica vira blocker.
- benchmark visual de jogo referencia e comparacao de restricoes (escala,
  densidade, presenca, budget), nao licenca para copiar um resultado impossivel
  no VDP.
- producao real ainda exige screenshot e, quando o efeito depender de estado
  mid-frame, VDP/CRAM/scroll dump; sem isso, no maximo `lab_evidence`.

### Fundo enorme nao e virtude por si so

- Conversao direta de ilustracao inteira costuma gerar muitos tiles unicos e pouca inteligencia estrutural.
- O agente deve desconfiar de toda cena bonita que "so cabe" porque ninguem mediu o VDP ainda.

## Quirks e exploits opt-in

- Bugs e comportamentos de mascaramento do VDP sao ferramentas avancadas, nao defaults.
- O agente nao deve explorar quirk de sprite off-screen por padrao.
- So liberar exploit quando existir:
  - intencao declarada
  - benchmark dedicado
  - evidencia em BlastEm
  - memoria operacional descrevendo riscos e motivacao

## Protocolo de referencias

Nenhum asset critico pode ser iniciado sem:
1. Tres jogos reais de Mega Drive.
2. Heranca explicita por jogo.
3. Justificativa do que esta sendo herdado.

Formato obrigatorio:
- `referencia_1`: jogo + heranca tecnica
- `referencia_2`: jogo + heranca tecnica
- `referencia_3`: jogo + heranca tecnica

Exemplo de heranca aceitavel:
- `Streets of Rage 3`: contraste de silhueta e musculatura sombreada
- `Monster World IV`: delicadeza de textura e clareza cromatica
- `Shinobi III`: leitura de sprite contra fundos movimentados

Exemplo de heranca invalida:
- "quero algo bonito tipo Sega"

## Protocolo de feedback

Todo feedback corretivo deve sair desta estrutura:

```markdown
sintoma: "o rosto esta borrado"
diagnostico_tecnico: "faltou separacao entre plano do maxilar e sombra de bochecha em 16x16"
heuristica_preventiva: "rostos abaixo de 24x24 precisam de contorno mandibular explicito e highlight de testa isolado"
metricas_afetadas:
- silhouette_readability
- detail_density_8x8
benchmark_referencia:
- Monster World IV
check_em_rom: "validar no BENCHMARK_VISUAL_LAB em BlastEm com fundo claro e escuro"
```

## Gatilhos de reprovacao

Reprovar imediatamente quando houver:
- sprite flat sem volume convincente
- paleta desperdicada com cores quase iguais
- fundo engolindo sprite critico
- material sem leitura do que e
- tile vazio em excesso
- ruido confundido com detalhe
- dithering aleatorio sem funcao
- asset cuja leitura so existe ampliada
- asset critico com `claims.critical_motion=required` promovido a `elite_ready`/`delivered` sem todos os sinais do `perceptual_motion_gate`
- asset critico com `visual_aesthetic_report.status == "rework"` ainda em uso (gate `critical_visual_rework_blocker`)
- logo/title/front-end final sem `brand_identity_manifest`
- logo que falha em silhueta, monocromatico, miniatura, fundo dinamico ou leitura 320x224
- fonte SGDK default usada como identidade final fora de debug/fallback
- UI/health bar final sem `ui_pixel_surface_contract` quando a surface depende de pixel-perfect, fonte, atlas ou barra
- health bar sem buffer de dano latente quando o jogo depende de leitura de impacto
- UI que usa free-scale, subpixel motion, AA ou interpolacao para parecer lisa
- personagem com escala alterada depois de key poses sem reseed
- sprite sheet derivado de model sheet que vira boneco blocado/generico ou perde feature assinatura
- material critico com straight shading lavado ou paleta de microvariacoes
- projeto, cena ou front-end tecnicamente limpo, mas sem momento assinatura,
  sem identidade autoral ou sem resposta aos gaps aceitos no
  `creative_director_radar`
- `live_scene_bar_failed`, `name_drop_without_craft`, `pixel_art_prompted_as_final`,
  `hardware_used_as_excuse` ou `fake_pixel_art_rejection`

## Curadoria - perceptual_motion_gate e critical_visual_rework_blocker

Regra generalizada para separar readiness tecnico, criativo e AAA em
LAB/TECHDEMO.

### `perceptual_motion_gate` antes de promover critico

Asset critico (hero, boss, veiculo, FX principal) NAO sobe para `elite_ready` ou `delivered` sem a composicao simultanea de:

1. `motion_gif` (ou `webp` animado) com todos os frames do ciclo de animacao.
2. `perceptual_check` (de `runtime_metrics.json`) preenchido com valores nao-zero em `fluidez`, `leitura`, `naturalidade` e `impacto`. Zero em qualquer eixo = gate falho.
3. `screenshot.png` dedicado da janela do BlastEm (nao screenshot colado de folder).
4. `save.sram` fresco (`fresh_sram_confirmed=true`).
5. `visual_vdp_dump.bin` capturado e vinculado a ROM vigente.
6. `human_approval_record.md` apontando explicitamente para o asset.

Nao ha bypass por um sinal isolado. O gate so se aplica quando `doc/project_methodology_manifest.json > claims.critical_motion.applicability=required`; palavras soltas ou a simples existencia de runtime metrics nao criam esse claim.

### `critical_visual_rework_blocker` nao aceitam override "por GIF"

Se `out/logs/visual_aesthetic_report.json` marcar um asset critico com `status: "rework"`, esse asset NAO pode ser usado em runtime de entrega, mesmo quando o usuario humano registra aprovacao por GIF/MOV.

Condicoes para override:

- `human_approval_record.md` datado e assinado, com link para o asset novo.
- `visual_aesthetic_report.json` atualizado com o novo status (ou entrada removida).
- `visual_vdp_dump.bin` confirmando o asset em runtime apos a troca.
- `motion_gif` ou captura multi-frame do novo asset.

Caso contrario, o asset permanece `rework` no painel e o status do projeto reflete isso em `creative_blocking_statuses`.

### Piso honesto: `visual_lab_static_floor`

Para projetos em `LAB/TECHDEMO` (claim_ceiling `technical_lab_validated`):

- `technical_ready` pode ser `true` mesmo sem `perceptual_motion_gate` satisfeito, desde que o build rode no BlastEm.
- `creative_ready` permanece `false` ate o gate perceptivo passar.
- `ready_for_aaa` permanece `false` ate o projeto sair de `LAB/TECHDEMO`.

Esse piso evita que "ta rodando" vire "ta pronto".

## Curadoria - Visual-first project lifecycle

Regra generalizada a partir de comparacao de rotas de producao, sem promover
projetos em amadurecimento a referencia canonica.

### Rota visual-first economiza tempo e tokens

Em `aaa_game`, o agente deve preferir a rota visual-first antes do runtime de
entrega:

1. identidade visual e cena assinatura no GDD/spec;
2. fonte premium local com autoria, licenca, hash e papel no gameplay;
3. aprovacao humana ou painel de aprovacao imutavel;
4. `art_gameplay_direction_gate` com camera, interacoes e `must_preserve`;
5. conversao VDP e budget;
6. runtime e BlastEm.

O padrao positivo bloqueia o runtime final ate existir rota visual, fonte
premium e gates humanos. Isso nao aprova automaticamente os assets; apenas
reduz improviso e mantem o agente no caminho certo.

### Runtime tecnico com visual bloqueado nao e maturidade AAA

ROM, rotas BlastEm e first playable tecnico podem coexistir com
`creative_quality=blocked` quando a arte ainda e placeholder, procedural, pouco
autoral ou abaixo da promessa AAA.

Nessa situacao, a proxima iteracao visual nao deve ser "mais um build" nem
"mais um refresh de screenshot". Deve atacar um destes blockers:

- `blocked_no_premium_source`;
- `blocked_no_human_asset_approval`;
- `blocked_no_vdp_conversion`;
- `live_scene_bar_failed` / `live_scene_bar_report_missing`;
- `visual_gate_blocked`;
- `visual_direction_failed`;
- `perceptual_motion_unvalidated`;
- `source_to_rom_visual_match` ausente ou abaixo do contrato;
- `visual_delivery_gate_report` ausente, stale ou nao canonico.

Se a mudanca proposta nao remove ou reduz um desses blockers, ela pode ser
valida como smoke/lab, mas nao como progresso visual AAA.

### Estagios visuais canonicos

- `visual_first_ready_for_translation`: fonte e gate existem; falta conversao,
  budget e runtime.
- `technical_runtime_creative_blocked`: ROM ou rota existe; visual, animacao,
  audio ou identidade ainda bloqueiam.
- `lab_evidence_not_delivery`: laboratorio provou tecnica ou fixture, nao
  produto.
- `smoke_only`: boot/build valida estrutura, nao qualidade.
- `ready_for_visual_closeout`: fonte, ROM, budget, motion/evidencia e gate
  visual estao coerentes para closeout.

O menor estagio entre direcao visual, fonte, budget, runtime e evidencia define
o teto do projeto.

## Integracao com agentes

### `art-director`
- Usa esta skill como barreira de veto.
- Nenhum asset critico pode ser aprovado sem passar pelas metricas canonicas.

### `mega-drive-pixel-engineer`
- Traduz diretriz visual em custo de hardware.
- Deve sempre reportar leitura visual junto com custo de VRAM.

### `art-creator`
- Usa esta skill para formular prompts, buscar referencias e filtrar assets externos.
- Nao pode descrever arte apenas em termos subjetivos.

### `art-pipeline-operator`
- Usa esta skill para transformar diagnostico visual em gate operacional.
- Deve chamar o juiz estetico e refletir a leitura no `validation_report.json`.

## Governanca operacional

- A validacao visual AAA nao substitui a validacao tecnica. Ela a complementa.
- Asset tecnicamente valido ainda pode ser reprovado por legibilidade ruim.
- Asset bonito mas inviavel para VDP continua reprovado.

## O Segredo da Profundidade

- `BG_B` deve carregar atmosfera e massa distante com contraste menor e densidade de detalhe menor.
- `BG_A` deve carregar estrutura de cena, mas continuar subordinado ao plano jogavel.
- O sprite ou elemento heroico deve ser o pico de leitura da composicao.
- Separacao tonal vem antes de separacao por matiz.
- Quando o fundo parece mais agressivo que o personagem, a cena esta visualmente errada mesmo que esteja "bonita".
- Densidade precisa obedecer hierarquia:
  - `BG_B`: respiracao
  - `BG_A`: estrutura
  - `sprite`: decisao
- Regra de reprovação:
  - se `BG_A` ou `BG_B` exigem mais atencao do olho que o elemento jogavel, falhou o criterio de profundidade canônica.

## Benchmark Lab

Novas heuristicas so viram doutrina canonizada quando:
1. entram em [doc/03_art/02_visual_feedback_bank.md](doc/03_art/02_visual_feedback_bank.md)
2. atualizam esta skill
3. sao provadas em `BENCHMARK_VISUAL_LAB` com ROM observada no BlastEm

## Nunca faca

- Tratar PNG como fim em si mesmo
- Aceitar feedback humano como remendo local sem generalizar
- Confundir ruido com riqueza
- Confundir mais cores com melhor paleta
- Corrigir legibilidade com detalhe extra quando o problema e silhueta
- Declarar excelencia visual sem prova em ROM

## Senior Competencies

Esta skill deve assumir pericia explicita em:

- `waterline readability`
  - leitura acima e abaixo da linha de split sem ruptura cromatica acidental
- `palette split coherence`
  - transicao cromatica dramatica sem perder pertencimento de cena
- `interlace tolerance`
  - shimmer aceitavel e hierarquia visual ainda legivel em 448
- `dithering funcional`
  - gradiente, material e atmosfera; nunca xadrez aleatorio
- `CRT-aware reading`
  - distinguir leitura de LCD ampliado de leitura perceptual em tela nativa
- `shadow/highlight slot audit`
  - proteger slots criticos de volume e brilho do sprite
- `material readability under VDP limits`
  - metal, pedra, pele, tecido e fogo sob 15 cores por paleta
- `palette cycling hierarchy`
  - cor em movimento sem destruir prioridade dos planos
- `FX-heavy readability`
  - personagem continua vencendo fundo mesmo sob wobble, split, glow ou chuva
- `brand identity readability`
  - logo, fonte-display e familia tipografica comunicam genero, tom e qualidade sem sacrificar leitura ou budget

Regra:

- esta skill pode reprovar arte tecnicamente valida se a leitura falhar
- ela tambem pode aprovar recuo visual honesto quando isso preserva a cena no hardware
