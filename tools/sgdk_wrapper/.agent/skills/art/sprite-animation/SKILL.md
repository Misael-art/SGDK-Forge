---
name: sprite-animation
description: Use quando a tarefa envolver desenho, traducao, revisao, recorte ou validacao de sprite sheets, ciclos de animacao, continuidade de poses, pivots ou strips de personagem para Mega Drive. Nao use para composicao de cenario ou design geral de roster sem foco na animacao.
---

# Sprite Animation

Esta skill existe para garantir que animacao de sprite no Mega Drive seja:

- legivel frame a frame
- estavel por pivot e massa
- economica em VRAM
- coerente com o genero
- pronta para integracao SGDK

## Ler antes de agir

1. `doc/03_art/07_sprite_animation_standards.md`
2. `doc/03_art/02_visual_feedback_bank.md`
3. `tools/sgdk_wrapper/.agent/skills/art/megadrive-pixel-strict-rules/SKILL.md`
4. `references/animation_production_contract.md` quando for criar ou auditar personagem/sheet gerado por IA
5. `references/premium_motion_direction_contract.md` quando houver personagem heroico, luta, boss, golpe, dano, hitstop, smear ou alegacao de qualidade premium/AAA
6. `tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/SKILL.md` quando houver risco de budget
7. `art-direction-selector` quando estilo, personalidade visual ou linguagem de movimento ainda nao estiverem congelados
8. `tools/sgdk_wrapper/schemas/visual_dna_manifest.schema.json`, `design_inheritance.schema.json` e `animation_strip_contract.schema.json` quando a entrega precisar ser machine-readable
9. `tools/sgdk_wrapper/.agent/scripts/validate_strip.py` antes de aprovar strip gerada, recebida ou convertida

## Quando usar

- criacao ou traducao de `sprite_sheet`
- geracao por IA de personagem animado, key poses ou strips
- revisao de ciclo `idle`, `walk`, `run`, `jump`, `attack`, `hurt`, `death`
- normalizacao de frames por pivot
- validacao de timing, massa e reuso
- integracao de sprite sheet em `.res`

## Entregas obrigatorias

- `animation_spec`
- `asset_kind_declaration`
- `animation_state_plan`
- `pose_roster`
- `frame_budget_table`
- `pivot_and_scale_contract`
- `visual_dna_manifest.scale_contract` travado quando houver personagem novo, key poses ou alteracao de escala
- `model_sheet_to_sprite_fidelity_report` quando a animacao vier de model sheet aprovado
- `style_motion_reverse_engineering` para personagem, boss, NPC expressivo ou heranca visual declarada
- `turnaround_tracking_contract` quando houver 3/4, rotacao, direcoes multiplas, giro ou close-up em outro angulo
- `motion_physics_contract` para locomocao, pulo, queda, ataque, dano, boss ou acao premium
- `state_transition_motion_contract` para encadear idle, walk/run, jump/landing, attack/recovery, hurt/getup e cutscene/gameplay
- `motion_phase_map`
- `animation_direction_contract` para acoes premium, golpes, dano, boss ou jogo de luta
- `idle_breathing_cycle_contract` para personagem heroico, lutador ou boss em idle visivel
- `facial_expression_phase_map` para personagem heroico, lutador, boss ou NPC falante com rosto legivel
- `cloth_secondary_animation_contract` quando roupa, cabelo, faixa, capa, jaqueta ou acessorio secundario aparecer em movimento critico
- `hand_pose_keyframe_contract` quando maos, garras, arma, empunhadura ou gesto forem legiveis
- `pivot_policy`
- `frame_envelope`
- `timing_table`
- `timing_spacing_report`
- `impact_frame_contract` para golpes/dano
- `smear_frame_manifest` quando houver smear
- `recovery_curve_report` para golpes e movimentos com inercia
- `hit_reaction_contract` para hurt/knockdown
- `shading_motion_report`
- `palette_flash_policy` quando houver flash frame ou impacto especial
- `modular_boss_rig_contract` quando houver boss/veiculo/criatura grande segmentado
- `frame_delta_report`
- `pixel_perfect_animation_pass`
- `line_cleaning_report`
- `subpixel_shading_motion_report` quando houver micro-movimento por luz/sombra
- `cluster_motion_review`
- `sprite_artifact_report`
- `model_sheet_to_sprite_fidelity_report`
- `slicing_cell_contract`
- `animation_preview_evidence`
- `contact_sheet`
- `pivot_overlay`
- `foot_contact_report`
- `active_recovery_map` para golpes
- `state_belongs_to_character_fantasy`
- `tile_reuse_summary`
- `active_animation_window` quando o ciclo completo nao precisar ficar residente
- `residency_strategy`
- `delivery_findings`

## Regras canonicas

- o pivot e definido uma vez e nao flutua dentro do ciclo
- personagem gerado por IA nao avanca para imagem sem `animation_state_plan`, `pose_roster`, `frame_budget_table` e `pivot_and_scale_contract`
- personagem novo ou alteracao de escala nao avanca para key poses aprovadas sem `visual_dna_manifest.scale_contract.scale_lock_status=locked`
- `style_motion_reverse_engineering` deve existir antes de mimetizar estilo, benchmark ou direcao visual autoral; nomes de jogos/artistas nao substituem regras de forma, proporcao, linha e shading
- `turnaround_tracking_contract` deve existir quando o personagem precisa girar, mirar em 3/4, andar em mais de uma direcao ou preservar volume em cutscene
- `motion_physics_contract` deve existir para acao critica com peso, gravidade, contato de pe, arma, golpe, queda, pulo, dano ou boss
- `state_transition_motion_contract` deve declarar frames ponte ou regra de retorno para impedir snap entre estados jogaveis
- personagem heroico/lutador/boss em AAA nao avanca para strips finais sem contratos de carisma aplicaveis: idle breathing, facial expression, cloth secondary e hand pose, ou `not_applicable` justificado
- o frame envelope e unico por sequencia
- strip gerada por IA so promove com `sprite_artifact_report.status=passed`
- `sprite_artifact_report.status=passed` aprova integridade tecnica da celula; se a sheet veio de model sheet aprovado, tambem exige `model_sheet_to_sprite_fidelity_report.status=passed`
- `slicing_cell_contract` declara se a celula veio de `max_bbox + padding` ou de celula fixa justificada; hardcode sem contrato volta para `rework`
- se o relatorio apontar `FRAME_EDGE_CLIPPING`, `NON_INDEX0_BACKGROUND_MATTE`, `TRANSPARENCY_INDEX0_BACKGROUND_MISMATCH`, `SMALL_ISLAND_DEBRIS`, `STRAY_LARGE_COMPONENT`, `SCALE_INCONSISTENCY` ou `BAKED_FX_IN_CHARACTER_SHEET`, a acao volta para `rework`
- producao deve seguir passes: model sheet, key poses, strips por acao, sheet final, QA
- toda imagem deve declarar `asset_kind`: `model_sheet`, `key_pose_sheet`, `animation_strip` ou `final_sprite_sheet`
- `key_pose_sheet` nunca passa como `animation_strip`; pose boa isolada nao prova fluxo de animacao
- `animation_strip` contem uma unica acao e exige `motion_phase_map`; multi-acao na mesma strip vira `rejeitado_multi_action_sheet`
- strip de entrega exige preview animado/GIF ou equivalente, contact sheet, pivot overlay e foot-lock/contact report
- golpe exige `active_recovery_map` com startup, active e recovery legiveis
- golpe premium exige `animation_direction_contract`, `timing_spacing_report`, `impact_frame_contract` e `recovery_curve_report`; ataque que comeca direto no active frame volta para `rework`
- idle premium exige `idle_breathing_cycle_contract` com areas, duracao, amplitude e personalidade; loop mecanico sem respiracao fica `needs_review`
- personagem com rosto legivel exige `facial_expression_phase_map`; dor, esforco, surpresa e fala precisam de assimetria/intencao quando o estilo permitir
- cabelo, faixa, capa, jaqueta, mangas ou pano solto exigem `cloth_secondary_animation_contract` com delay, damping e amplitude, sem dobrar frames sem budget
- maos legiveis exigem `hand_pose_keyframe_contract`; punho, palma, grip, apontar e relaxado nao podem virar a mesma massa generica
- smear frame so passa quando declarado em `smear_frame_manifest` e legivel como movimento, nao como sujeira, halo ou componente desconectado
- hurt/knockdown exige `hit_reaction_contract` com direcao da forca, quebra de postura, hitstop frame e retorno de escala
- `shading_motion_report` deve provar que highlights/sombras acompanham rotacao, contracao e extensao; contorno movendo com luz estatica nao aprova premium
- `turnaround_tracking_contract` deve provar que linhas de olho, ombro, cintura, joelho, pe e solo continuam coerentes entre frente, perfil, costas e 3/4
- `motion_physics_contract` deve provar curva de centro de massa, arco de membros/armas, contato de solo, conservacao de massa e ordem de inercia secundaria
- transicoes entre estados devem preservar momentum: ataque nao volta para idle sem recovery, landing nao ignora queda e hurt/getup nao troca escala ou ground_y sem justificativa
- subpixel visual real nao existe; micro-movimento so pode ser simulado por `subpixel_shading_motion_report`, sem mover a silhueta externa nem criar AA
- diagonais em movimento exigem `line_cleaning_report`; jaggies, double corners e pixels orfaos viram blocker visual
- animacao deve mover clusters de massa coerentes; linhas isoladas tremendo sem massa geram `cluster_motion_noise`
- flash frame precisa de `palette_flash_policy`; flash acidental por re-quantizacao ou mistura de slots bloqueia entrega visual
- boss ou personagem colossal deve preferir `modular_boss_rig_contract` com partes, pivots e budget antes de aceitar sheet full-body gigante
- todo estado de personagem exige `state_belongs_to_character_fantasy=true`
- estados BJJ precisam comunicar BJJ: base baixa, grips, entrada de queda, clinch, queda, guarda ou linguagem corporal propria
- timing e em VBlank, nunca em intuicao vaga
- anticipation e follow-through sao obrigatorios em acoes
- flip horizontal e hardware, nao duplicacao de sheet
- ciclo completo que nao cabe residente nao significa "impossivel"; propor `active_animation_window`, SGDK auto VRAM alloc ou streaming manual com budget de DMA validado
- compressao do `SPRITE` em `.res` altera ROM/load, nao reduz tiles residentes do frame descompactado
- frame bonito em zoom nao vale se falhar em 320x224 nativo

## Gates de aprovacao

- `mass_consistency`
- `pivot_stability`
- `timing_feel`
- `frame_economy`
- `readability_at_native`
- `style_rule_consistency`
- `pose_continuity`
- `volume_consistency`
- `turnaround_volume_tracking`
- `pivot_consistency`
- `motion_physics_readability`
- `state_transition_continuity`
- `frame_flow_readability`
- `adjacent_frame_delta`
- `gameplay_state_coverage`
- `rom_playback` quando a iteracao chegar ao benchmark

## Anti-padroes

- sheet com frames desalinhados
- mesma duracao para todos os frames
- golpe sem anticipation
- golpe sem follow-through
- golpe que inicia no frame ativo
- golpe sem frame de hitstop visualmente forte
- recovery instantaneo para idle depois de impacto medio/pesado
- locomocao, pulo ou aterrissagem sem centro de massa, contato de pe ou gravidade legivel
- rotacao/3/4 sem linhas de tracking e volumes consistentes
- estado que estala para outro sem frame ponte, recovery, anticipation ou regra de transicao
- smear frame usado como blur, ruido, ilha ou residuo de celula
- hurt sem direcao de forca ou sem quebra de postura
- sombra/highlight congelado enquanto o corpo gira
- subpixel artificial feito com AA, blur ou cores novas fora da rampa
- jaggies, cantos duplos ou pixels orfaos em diagonais de membros/tecido
- clusters de sombra movendo sem relacao com tronco, membro ou material
- flash frame produzido por quantizacao suja em vez de politica de paleta/runtime
- boss gigante em sheet full-body sem contrato modular e budget
- idle heroico estatico ou respiracao simetrica/mecanica sem personalidade
- cabelo, faixa, manga ou capa congelados enquanto o corpo acelera
- rosto de dor/esforco/surpresa identico ao idle
- maos rigidas ou genericas em golpe, agarramento, arma ou pose iconica
- gerar "sprite sheet completo" antes de aprovar model sheet e key poses
- aceitar prancha multi-acao como animacao jogavel
- aceitar strip que parece desenhos soltos sem fluxo temporal
- gerar strip sem `motion_phase_map`
- aprovar strip sem `frame_delta_report`, preview animado ou sequencia numerada
- aprovar strip sem contact sheet, pivot overlay ou foot-lock/contact report
- aprovar golpe sem active/recovery map
- aprovar estado de BJJ que parece karateka recolorido ou pose marcial generica
- aceitar personagem que muda roupa, anatomia, escala, rosto ou volume entre frames
- aceitar sheet que preserva pivo/celula mas perde o DNA do model sheet em rosto, feature assinatura, roupa, material ou acting
- aceitar key poses, inbetweens ou strips com escala ainda em `draft`
- aceitar celula com pe/mao/cabeca cortados, fragmento deslocado, retangulo de matte ou sujeira de fundo so porque o PNG compila
- aceitar FX de dano/spark embutido na sheet do personagem quando o FX deveria ser sprite separado
- duplicar direcao esquerda/direita em PNG
- aprovar animacao sem calcular tiles unicos do ciclo
- reprovar sheet grande sem antes avaliar janela ativa, scene-local preload e custo real de DMA por frame

## Senior Competencies

Esta skill deve declarar dominio explicito sobre:

- `frame economy`
  - ciclos bonitos que ainda cabem em VRAM
- `active_animation_window`
  - separar sheet completa, ciclos ativos e frames que realmente precisam estar residentes agora
- `tile flipping por hardware`
  - reaproveitar direcao e simetria sem sheet duplicada
- `sprite_temporal_multiplexing`
  - alternancia temporal pode servir para FX densos, nunca para leitura critica
- `sprite_midframe_sat_reuse awareness`
  - reuso real de SAT mid-frame e outra tecnica, mais perigosa, e nao deve ser confundida com alternancia temporal
- `multiplexing proibido para gameplay critico`
  - heroi, hitbox chave e leitura de golpe nao entram em alternancia temporal nem em SAT reuse por reflexo
- `boss articulation readiness`
  - sheets e pivots preparados para juntas ou partes acopladas
- `FX-heavy readability`
  - animacao permanece legivel mesmo com chuva, glow, split ou fondo agressivo
- `pixel_perfect_animation_pass`
  - bloquear escala, silhueta, inbetweens, limpeza de linha e sombreamento antes de promover strip
- `style_motion_reverse_engineering`
  - tratar estilo como restricoes de forma, proporcao, linha e luz, nao como copia nominal
- `turnaround_tracking_contract`
  - preservar volume, altura de articulacoes, ground_y, pivot e foreshortening entre angulos
- `motion_physics_contract`
  - planejar peso, gravidade, arcos, contato e inercia antes de polimento
- `state_transition_motion_contract`
  - manter continuidade entre estados de gameplay e cutscene sem snap visual

Regra:

- esta skill continua dona da qualidade do ciclo
- `forward-kinematics-rigging` entra apenas quando a animacao deixa de ser puramente frame a frame

## Integracao

- combinar com `character-design` quando a tarefa mexer na identidade do personagem
- combinar com `art-translation-to-vdp` quando a sheet vier de uma fonte high-res ou editorial
- combinar com `sgdk-runtime-coder` quando a tarefa entrar em runtime, `.res`, callbacks ou troca de animacao em C
- combinar com `forward-kinematics-rigging` quando o personagem ou boss exigir cadeias articuladas

## Contrato Operacional

### Entrada minima

- personagem, inimigo, boss ou FX animado com papel de gameplay declarado
- sheet existente, fonte visual ou lista de acoes a produzir
- `asset_kind_declaration`; sem isso, tratar como nao classificavel
- `animation_state_plan`, `pose_roster`, `frame_budget_table` e `pivot_and_scale_contract` quando a arte nascer de IA
- `visual_dna_manifest.scale_contract` com `scale_lock_status=locked` antes de key poses aprovadas
- `style_motion_reverse_engineering` quando houver estilo alvo, benchmark, autoralidade ou personagem expressivo
- `turnaround_tracking_contract` quando houver 3/4, rotacao, direcoes multiplas ou close-up em outro angulo
- `motion_physics_contract` quando a acao depender de gravidade, peso, contato, ataque, dano, pulo, queda ou boss
- `state_transition_motion_contract` quando estados de gameplay ou cutscene forem encadeados
- `motion_phase_map` para cada `animation_strip`
- `animation_direction_contract` quando houver golpe, dano, boss, personagem heroico ou qualidade premium/AAA
- `idle_breathing_cycle_contract`, `facial_expression_phase_map`, `cloth_secondary_animation_contract` e `hand_pose_keyframe_contract` quando aplicaveis ao personagem e ao alvo AAA
- `asset_lineage_record` quando a sheet veio de IA/sourcing
- escala, paleta e pivot esperados pelo character/design ou cena
- restricoes preliminares de VRAM, scanline e residencia de frames

### Saida minima

- `animation_spec`
- `asset_kind_declaration`
- `animation_state_plan`
- `pose_roster`
- `frame_budget_table`
- `pivot_and_scale_contract`
- `scale_lock_check`
- `style_motion_reverse_engineering` quando aplicavel
- `turnaround_tracking_contract` quando aplicavel
- `motion_physics_contract` quando aplicavel
- `state_transition_motion_contract` quando aplicavel
- `motion_phase_map`
- `pivot_policy`
- `style_anchor_inheritance` quando houver `master_style_manifest`
- `idle_breathing_cycle_contract` quando aplicavel
- `facial_expression_phase_map` quando aplicavel
- `cloth_secondary_animation_contract` quando aplicavel
- `hand_pose_keyframe_contract` quando aplicavel
- `frame_envelope`
- `timing_table`
- `timing_spacing_report`
- `impact_frame_contract` quando houver golpe ou dano
- `smear_frame_manifest` quando houver smear
- `recovery_curve_report` quando houver inercia/follow-through
- `hit_reaction_contract` quando houver hurt/knockdown
- `shading_motion_report`
- `palette_flash_policy` quando houver flash frame
- `modular_boss_rig_contract` quando houver boss/veiculo/criatura grande segmentado
- `frame_delta_report`
- `pixel_perfect_animation_pass`
- `line_cleaning_report`
- `subpixel_shading_motion_report` quando aplicavel
- `cluster_motion_review`
- `sprite_artifact_report`
- `model_sheet_to_sprite_fidelity_report`
- `slicing_cell_contract`
- `tile_reuse_summary`
- `active_animation_window` quando aplicavel
- `animation_preview_evidence` com contact sheet, preview ou overlays quando houver frames produzidos
- `contact_sheet`, `pivot_overlay`, `foot_contact_report` e `active_recovery_map` quando houver golpes
- `visual_dna_manifest` e `design_inheritance` quando houver personagem, boss, roupa, paleta ou identidade autoral a preservar
- `model_sheet_to_sprite_fidelity_report` quando houver model sheet aprovado como fonte visual da sheet
- `animation_strip_contract` por strip de acao unica; exemplo canonico em `references/agentic_aaa_contracts/examples/animation_strip_contract.example.json`
- `validate_strip_report` gerado por `scripts/validate_strip.py` quando houver JSON de strip
- `state_belongs_to_character_fantasy` comprovado por estado
- `residency_strategy`
- `delivery_findings`

### Passa quando

- pivot e envelope nao flutuam entre frames da mesma acao
- `asset_kind` foi classificado corretamente; `key_pose_sheet` nao foi promovido como `animation_strip`
- frames gerados mantem o mesmo `style_anchor_id`, line weight, iluminacao e densidade visual
- quando houver model sheet aprovado, frames preservam os traços `must_preserve`; perda de rosto/olhos, feature assinatura, roupa/material ou acting vira `model_sheet_to_sprite_fidelity_failed`
- quando houver `style_motion_reverse_engineering`, primitive shape, proportion matrix, line weight e shading model permanecem estaveis entre model sheet, key poses e strips
- quando houver `turnaround_tracking_contract`, alturas de articulacao, ground_y, pivot e foreshortening permanecem coerentes entre angulos
- quando houver `motion_physics_contract`, centro de massa, arcos, contato de solo, gravidade e inercia secundaria sao legiveis em 320x224
- quando houver personagem novo ou mudanca de escala, `visual_dna_manifest.scale_contract` esta travado e nao contradiz FOV, hitbox, pivot, tile budget ou carga de animacao
- quando houver `state_transition_motion_contract`, as transicoes preservam momentum e nao estalam de um estado para outro
- cada `animation_strip` contem apenas uma acao, segue `motion_phase_map` e passa no `frame_delta_report`
- cada `animation_strip_contract` passa em `validate_strip.py` ou registra blocker explicito (`metadata_only_asset_not_approved`, `multi_action_sheet`, `pivot_drift_over_threshold`, `bbox_drift_over_threshold` ou `palette_drift_over_threshold`)
- cada strip promovida passa em integridade de celula, index 0, escala e ausencia de FX embutido indevido
- strips apresentam continuidade de pose, volume e pivot; se parecerem desenhos soltos, o status e `rejeitado_sem_fluxo_animacao`
- estados P0 do genero estao cobertos; se faltarem, o status e `revisar_frame_roster`
- estados BJJ comunicam base baixa, grips, queda, clinch, guarda ou linguagem corporal propria; se virarem karate/beat-em-up generico, o status e `state_fantasy_mismatch`
- timing comunica peso, anticipation e recovery em VBlank
- premium/luta comunica timing e spacing por startup, anticipation, active, hitstop, follow-through e recovery; desenho limpo sem performance de movimento nao passa
- locomocao, salto, queda e aterrissagem comunicam fisica visual antes de polish: contato, compressao pre-renderizada, arco, gravity beat e retorno
- o frame de hitstop foi escolhido e e legivel, sem clipping, sem smear sujo e com silhueta forte
- dano comunica direcao de forca, squash/stretch leve quando aplicavel e quebra de postura sem perder escala
- highlights e sombras acompanham volume em movimento; se a luz ficar estatica sobre corpo girando, status maximo e `needs_review`
- subpixel por sombreamento usa apenas cores da rampa ja aprovada e nao altera contorno externo
- diagonais e curvas passam por limpeza de linha antes de paleta final
- clusters principais de sombra/base/highlight seguem massa e articulacao, nao ruido frame a frame
- sheet nao duplica direcao que pode ser flipada por hardware
- ciclos grandes declaram janela ativa, preload ou streaming antes de serem rejeitados
- leitura critica permanece estavel em 320x224 nativo

### Handoff para proxima etapa

- entregar sheet e tabela de timing para `art-conversion-pipeline`
- entregar contagem de frames/tiles para `megadrive-vdp-budget-analyst`
- entregar callbacks, anim ids e residencia para `sgdk-runtime-coder`
