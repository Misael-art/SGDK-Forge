# HYBRIDO MUAY THAI - fluxo ASCII de versoes e decisoes visuais

Status deste documento: registro pedagogico de processo.

Este arquivo explica, em forma de fluxo ASCII, como cada versao visual nasceu,
quais decisoes foram tomadas, quais artefatos foram produzidos e quando houve
intervencao humana. Ele nao substitui `doc/10-memory-bank.md`,
`doc/changelog/changelog.md`, contratos JSON, reports ou evidencia de emulador.

Regra de leitura:

```text
[VERSAO]
  INPUT        := fonte, premissa ou problema que iniciou a versao
  SYNTAX       := regra de decisao usada pelo agente
  OUTPUT       := artefatos realmente produzidos
  HUMAN        := intervencao humana registrada
  STATUS       := estado honesto da versao
  NEXT_SYNTAX  := regra que obrigou a proxima versao
```

Legenda rapida:

```text
OK_TECNICO     = arquivo/build/PNG/ROM existe e passa validacao tecnica
OK_VISUAL      = identidade, leitura e acting passam como arte
RUNTIME        = asset entrou no viewer/ROM
SOURCE         = fonte de direcao, nao asset final
BLOCKER        = algo impede promocao
HUMAN          = decisao, critica ou pedido humano
NEXT           = motivo que abre a versao seguinte
```

Fluxo macro:

```text
START
  |
  v
v001 placeholder tecnico
  |
  v
v002 IA + runtime lab 48x64
  |
  +-- HUMAN reprova anatomia/acting/fidelidade
  v
v003 novo source candidate
  |
  +-- HUMAN pede escala consistente, costas e marcador vermelho
  v
v005 novo source com turnaround
  |
  +-- HUMAN reprova material da mao lava
  v
v006 source + palette map
  |
  +-- HUMAN reprova endpoint da mao lava e ruido
  v
v007 brief/palette map + retentativa de geracao
  |
  +-- HUMAN pede retry e fonte melhor
  v
v008 model sheet com pose 5/paleta corrigidas
  |
  +-- HUMAN aceita apenas como direcao para traducao nativa
  v
v009 sprite sheet 48x64 runtime candidate
  |
  +-- HUMAN reprova: sprite ficou blocado/generico
  v
v010 gate arte+game design antes de asset
  |
  v
v010 runtime partial 48x64 + source-of-truth gate
  |
  +-- HUMAN reclama que qualidade ainda nao chega no padrao desejado
  v
v011 rota 96x96 hi-bit procedural/candidata
  |
  +-- HUMAN reprova rota simplista/procedural e exige geracao avancada
  v
v012 fontes avancadas + conversao VDP candidate
  |
  +-- ainda falta BlastEm fresco + VDP dump + 60fps + review humano
  v
NEXT: validar runtime, corrigir budget e fechar evidencia sem chamar de AAA antes do emulador
```

---

## v001 - placeholder tecnico inicial

```text
[v001]
  INPUT :=
    "preciso de um projeto SGDK com sprites de lutador para iniciar o estudo"

  SYNTAX :=
    IF nao existe pipeline visual maduro
       THEN criar placeholder tecnico em 48x64
       AND provar que resources.res + main.c + build funcionam.

  OUTPUT :=
    res/sprites/hibrido/*_v001.png
    doc/contracts/palette_role_map_v001.json
    doc/contracts/sprite_sheet_contract_v001.json
    out/rom.bin build_v001

  HUMAN :=
    Nenhuma aprovacao visual final.
    Posteriormente, o humano e a curadoria rebaixaram este material para
    placeholder tecnico.

  STATUS :=
    OK_TECNICO parcial.
    OK_VISUAL falso.
    RUNTIME de laboratorio, nao arte final.

  NEXT_SYNTAX :=
    IF placeholder nao preserva identidade
       THEN gerar fonte visual autoral e tratar v001 como baseline tecnico,
       NOT como baseline artistico.
```

Fluxo:

```text
placeholder tecnico
  -> build prova sintaxe SGDK
  -> visual_gate_blocked
  -> NEXT v002: fonte IA + runtime lab
```

---

## v002 - fonte IA + runtime lab

```text
[v002]
  INPUT :=
    "substituir placeholder por lutador hibrido Muay Thai com braco lava"

  SYNTAX :=
    IF fonte IA existe
       THEN registrar como SOURCE candidate
       AND converter para strips 48x64 apenas como laboratorio.

    IF build/PNG/BlastEm passam
       THEN marcar OK_TECNICO
       BUT nao marcar OK_VISUAL sem fidelidade.

  OUTPUT :=
    data/raw_ai/hibrido_fighter_v002/
    data/source_art/hibrido_fighter_v002/
    data/builders/build_hibrido_fighter_assets_v002.py
    res/sprites/hibrido/*_v002.png
    out/logs/hibrido_v002_visual_rejection_report.json
    out/logs/hibrido_v002_input_gatekeeper_report.json
    out/logs/hibrido_v002_runtime_fidelity_report.json
    out/rom.bin sha256 246b33725b479402cccf41cd28a1be79f6687c4524af0dbd74b4062021a978bc

  HUMAN :=
    Reprovacao humana:
      - pose 3 le como tres bracos;
      - acting facial frio;
      - runtime 48x64 perdeu olhos, lava arm, shorts e contraste quente.

  STATUS :=
    RUNTIME funcional.
    OK_TECNICO verdadeiro.
    OK_VISUAL falso.
    ready_for_aaa falso.

  NEXT_SYNTAX :=
    IF anatomia/acting/fidelidade falham
       THEN fonte precisa passar input gatekeeper
       AND nao pode haver downscale direto para sprite final.
```

Fluxo:

```text
source IA
  -> conversao tecnica 48x64
  -> build + BlastEm parcial
  -> HUMAN reprova semantica visual
  -> aprendizado: tecnico != visual
  -> NEXT v003: novo source candidate
```

---

## v003 - novo source candidate

```text
[v003]
  INPUT :=
    "corrigir anomalia grosseira e melhorar acting/material"

  SYNTAX :=
    IF v002 falha por anatomia e acting
       THEN gerar novo model/source candidate
       AND bloquear runtime ate validacao humana.

  OUTPUT :=
    data/source_art/hibrido_fighter_v003/source_concept.png
    doc/contracts/human_validation_record_v003.md

  HUMAN :=
    Feedback humano:
      - avancou;
      - ainda nao passa como fonte canonica;
      - primeira pose maior que as demais;
      - falta pose de costas;
      - marcador vermelho do biceps inconsistente.

  STATUS :=
    SOURCE candidate.
    RUNTIME falso.
    OK_VISUAL insuficiente.

  NEXT_SYNTAX :=
    IF model sheet nao tem escala, costas e marcadores consistentes
       THEN gerar nova fonte com scale_lock + back_pose + marker continuity.
```

Fluxo:

```text
v003 source
  -> precheck melhor
  -> HUMAN aponta escala/costas/faixa
  -> NEXT v005
```

---

## v004 - tentativa intermediaria superseded

```text
[v004]
  INPUT :=
    "tentativa intermediaria entre v003 e v005"

  SYNTAX :=
    IF a tentativa nao vence os problemas humanos principais
       THEN preservar historico
       AND nao promover como baseline.

  OUTPUT :=
    tentativa preservada como superseded_by_v005

  HUMAN :=
    A intervencao humana que guiou v004 foi a mesma critica aplicada a v003.

  STATUS :=
    superseded.
    nao e fonte ativa.

  NEXT_SYNTAX :=
    IF tentativa intermediaria nao resolve requisito
       THEN gerar v005 com turnaround e marcadores.
```

Fluxo:

```text
v004 tentativa
  -> nao vira baseline
  -> NEXT v005
```

---

## v005 - source com turnaround e marcadores

```text
[v005]
  INPUT :=
    "corrigir escala, incluir costas e manter faixa vermelha"

  SYNTAX :=
    IF humano pediu consistencia de model sheet
       THEN gerar front/back/guard/knee/teep com marcadores preservados.

  OUTPUT :=
    data/source_art/hibrido_fighter_v005/source_concept.png
    doc/contracts/human_validation_record_v005.md

  HUMAN :=
    Reprovacao humana:
      - mao lava/rocha na ultima pose le como faixa ou luva;
      - faltava mapa de paleta/material para orientar producao futura.

  STATUS :=
    SOURCE candidate needs_rework.
    OK_VISUAL ainda falso para baseline canonico.

  NEXT_SYNTAX :=
    IF personagem e assimetrico
       THEN travar material por membro
       AND criar palette/material map antes de sprite sheet.
```

Fluxo:

```text
v005 model sheet
  -> turnaround melhora
  -> HUMAN detecta drift de material na mao lava
  -> NEXT v006: material lock + palette map
```

---

## v006 - source + palette/material map

```text
[v006]
  INPUT :=
    "travar braco/mao lava como rocha exposta, sem faixa/luva"

  SYNTAX :=
    IF material do membro especial driftou
       THEN criar mapa de paleta/material
       AND forcar mao lava sempre rocha exposta com fissuras laranja.

  OUTPUT :=
    data/source_art/hibrido_fighter_v006/source_concept.png
    doc/contracts/hibrido_fighter_v006_palette_map.json
    data/processed/reports/hibrido_v006_palette_map.png
    doc/contracts/human_validation_record_v006.md

  HUMAN :=
    Reprovacao humana:
      - braco lava sem mao/punho legivel;
      - excesso de microdetalhe/spray vira tile-noise;
      - precisa de cluster shading e endpoint de membro claro.

  STATUS :=
    SOURCE candidate rejected.
    OK_VISUAL falso.

  NEXT_SYNTAX :=
    IF endpoint do membro especial nao le
       THEN nova geracao deve priorizar punho/mao legivel
       AND reduzir ruido fino para leitura 16-bit.
```

Fluxo:

```text
v006 source + palette map
  -> material lock documentado
  -> HUMAN reprova endpoint/ruido
  -> NEXT v007: brief mais restritivo
```

---

## v007 - brief/palette map + retentativa de geracao

```text
[v007]
  INPUT :=
    "gerar fonte com endpoint de mao lava claro e menos ruido"

  SYNTAX :=
    IF geracao direta falha por tooling
       THEN registrar blocker
       AND produzir brief/palette map sem inventar asset final.

    IF humano pede nova tentativa
       THEN tentar canal nativo novamente
       AND preservar reports de falha/decisao.

  OUTPUT :=
    doc/contracts/hibrido_fighter_v007_generation_brief.md
    doc/contracts/hibrido_fighter_v007_palette_map.json
    data/processed/reports/hibrido_v007_single_palette_map.png
    data/source_art/hibrido_fighter_v007/source_concept.png
    out/logs/hibrido_v007_generation_attempt_report.json
    out/logs/hibrido_v007_model_sheet_precheck_report.json
    out/logs/generation_channel_decision.json

  HUMAN :=
    Pedido humano:
      - tentar gerar novamente o model sheet.

  STATUS :=
    Fonte v007 gerada apos retentativa.
    SOURCE candidate pending human validation.
    Tooling local ainda bloqueado por ambiente/licenca.

  NEXT_SYNTAX :=
    IF v007 melhora mas ainda precisa correcao de pose e paleta embutida
       THEN gerar v008 com pose 5 corrigida e lista de cores no sheet.
```

Fluxo:

```text
brief v007
  -> tooling falha
  -> HUMAN pede retry
  -> source v007 gerado
  -> NEXT v008
```

---

## v008 - model sheet com pose 5 e paleta corrigidas

```text
[v008]
  INPUT :=
    "refazer model sheet com mao de lava da quinta pose mais clara, aberta e acima da perna; incluir paleta"

  SYNTAX :=
    IF humano especifica correcao anatomica/material
       THEN gerar model sheet novo
       AND embutir paleta/cores como guia de traducao.

  OUTPUT :=
    data/source_art/hibrido_fighter_v008/source_concept.png
    data/source_art/hibrido_fighter_v008/source_concept_raw.png
    doc/contracts/hibrido_fighter_v008_palette_map.json
    doc/contracts/human_validation_record_v008.md
    out/logs/hibrido_v008_model_sheet_precheck_report.json

  HUMAN :=
    Pedido humano:
      - corrigir pose 5;
      - incluir paleta no proprio model sheet.

    Decisao humana posterior:
      - v008 aceito como direcao para traducao nativa;
      - nao aceito como runtime art direto.

  STATUS :=
    SOURCE de direcao aprovado para traducao.
    RUNTIME falso.
    Proibido downscale direto.

  NEXT_SYNTAX :=
    IF source aprovado e nao pode virar runtime direto
       THEN reconstruir sprite em grid nativo, com lineart/cluster/paleta,
       AND gerar fidelity report model_sheet -> sprite.
```

Fluxo:

```text
v008 model sheet
  -> HUMAN aceita como direcao
  -> nao downscale
  -> NEXT v009: sprite sheet nativo 48x64
```

---

## v009 - sprite sheet 48x64 runtime candidate

```text
[v009]
  INPUT :=
    "traduzir v008 para sprite sheet nativo Mega Drive"

  SYNTAX :=
    IF model sheet foi aceito como direcao
       THEN redesenhar em celula 48x64
       AND gerar strips idle/walk/guard/jab/knee/teep
       AND validar PNG modo P, PLTE<=16, index0 transparente.

    IF build/BlastEm parcial funcionam
       THEN marcar OK_TECNICO
       BUT exigir fidelidade visual antes de promocao.

  OUTPUT :=
    data/builders/build_hibrido_fighter_sprite_sheet_v009.py
    data/processed/spritesheets/hibrido_fighter_complete_sprite_sheet_48x64_v009.png
    data/processed/reports/hibrido_fighter_complete_contact_sheet_with_palette_v009.png
    data/processed/lineart/hibrido_fighter_lineart_blocking_48x64_v009.png
    res/sprites/hibrido/*_v009.png
    doc/contracts/visual_dna_manifest_v009.json
    doc/contracts/animation_direction_contract_v009.json
    doc/contracts/human_validation_record_v009.md
    out/logs/hibrido_v009_model_sheet_to_sprite_fidelity_report.json

  HUMAN :=
    Reprovacao humana:
      - sprite sheet ficou blocado/generico;
      - perdeu rosto/olhos, anatomia, braco lava, shorts, bandagens e acting;
      - tecnica de celula/PLTE nao basta.

    Intervencao humana adicional:
      - arte precisa passar por direcao de arte + game design antes de gerar asset.

  STATUS :=
    OK_TECNICO verdadeiro.
    OK_VISUAL falso.
    v009 = obsolete_negative_evidence.
    ready_for_res_promotion falso.
    ready_for_aaa falso.

  NEXT_SYNTAX :=
    IF sprite sheet perde DNA do model sheet
       THEN nao polir a sheet ruim
       AND criar art_gameplay_direction_gate
       AND voltar para direcao/brief/model sheet antes de qualquer asset.
```

Fluxo:

```text
v008 source aprovado
  -> v009 sprite 48x64
  -> build/validacao passam tecnicamente
  -> HUMAN reprova qualidade/fidelidade
  -> art_gameplay_direction_gate nasce
  -> NEXT v010: recovery direction gate
```

---

## v010 - recovery gate: direcao antes de asset

```text
[v010-gate]
  INPUT :=
    "refazer corretamente, sem reutilizar v009 como baseline aprovado"

  SYNTAX :=
    IF v009 reprovada
       THEN bloquear asset novo
       AND criar gate de arte/game design
       AND auditar coesao do model sheet anterior.

  OUTPUT :=
    doc/contracts/art_gameplay_direction_gate_v010.json
    doc/contracts/hibrido_fighter_v010_model_sheet_generation_brief.md
    doc/contracts/visual_dna_manifest_v010.json
    doc/contracts/animation_state_plan_v010.json
    doc/contracts/pose_roster_v010.json
    doc/contracts/frame_budget_table_v010.json
    doc/contracts/pivot_and_scale_contract_v010.json
    doc/contracts/motion_phase_map_v010.json
    doc/contracts/animation_direction_contract_v010.json
    doc/contracts/model_sheet_to_sprite_fidelity_report_v010.json
    out/logs/hibrido_v010_model_sheet_cohesion_audit_report.json
    data/processed/reports/hibrido_v010_blocked_direction_comparison_board.png

  HUMAN :=
    Pedido humano:
      - atuar como recovery agent;
      - nao gerar asset antes de direcao de arte/game design;
      - v009 reprovada nao pode ser baseline.

  STATUS :=
    Gate de direcao passa para planejamento.
    Asset novo bloqueado ate brief/model sheet coerente.

  NEXT_SYNTAX :=
    IF gate libera planejamento e brief existe
       THEN produzir pacote nativo apenas como candidato,
       mantendo v009 como evidencia negativa.
```

Fluxo:

```text
HUMAN recovery request
  -> art_gameplay_direction_gate_v010
  -> audit hair/turnaround/scale/fidelity
  -> sem asset final ainda
  -> NEXT v010-runtime package
```

---

## v010 - pacote nativo runtime parcial 48x64

```text
[v010-runtime]
  INPUT :=
    "produzir pacote visual candidato seguindo contratos v010"

  SYNTAX :=
    IF contratos v010 existem
       THEN gerar source/key poses/sprite sheet/contact/GIF/overlay
       AND promover strips para runtime
       AND testar build/BlastEm sem claim AAA.

  OUTPUT :=
    data/builders/build_hibrido_fighter_visual_package_v010.py
    data/source_art/hibrido_fighter_v010/source_concept.png
    data/processed/model_sheets/hibrido_fighter_model_sheet_native_key_poses_48x64_v010.png
    data/processed/spritesheets/hibrido_fighter_complete_sprite_sheet_48x64_v010.png
    data/processed/reports/hibrido_fighter_motion_preview_v010.gif
    data/processed/reports/hibrido_fighter_pivot_overlay_v010.png
    data/processed/reports/hibrido_v010_delivery_comparison_board.png
    res/sprites/hibrido/*_v010.png
    out/evidence/blastem/screenshot.png
    out/evidence/blastem/save.sram

  HUMAN :=
    Nenhuma aprovacao final.
    A versao continuou sob a intervencao anterior: nao declarar AAA sem emulador/VDP/human review.

  STATUS :=
    RUNTIME parcial testado no BlastEm com screenshot/SRAM.
    visual_vdp_dump ausente.
    performance_60fps nao medida.
    ready_for_aaa falso.

  NEXT_SYNTAX :=
    IF runtime candidato ainda nao e fonte canonica
       THEN criar visual_source_of_truth
       AND impedir usar sheet parcial como base de geracao.
```

Fluxo:

```text
contratos v010
  -> pacote 48x64 nativo
  -> runtime parcial
  -> evidencia BlastEm parcial
  -> source-of-truth gate
```

---

## v010 - visual source of truth anti-polimento

```text
[v010-source-of-truth]
  INPUT :=
    "evitar remendar ou usar sheets reprovadas/parciais como fonte"

  SYNTAX :=
    IF sheet e runtime_candidate_not_aaa_not_source
       THEN pode servir como evidencia
       BUT nao pode virar source/baseline/img2img/reference.

  OUTPUT :=
    doc/contracts/visual_source_of_truth_v010.json
    out/logs/visual_source_lineage_report.json

  HUMAN :=
    Regra derivada diretamente das reprovacoes humanas anteriores.

  STATUS :=
    Gate de linhagem passou.
    Nenhum asset novo gerado.

  NEXT_SYNTAX :=
    IF a proxima rota exigir qualidade maior
       THEN gerar a partir de fonte/model sheet/direcao,
       NOT a partir do sprite sheet parcial.
```

Fluxo:

```text
v009/v010 parcial
  -> marcar como nao-source
  -> lineage report passed
  -> NEXT v011/v012 nao podem copiar sheet ruim
```

---

## v011 - rota 96x96 hi-bit/procedural candidata

```text
[v011]
  INPUT :=
    "48x64 nao entrega rosto, anatomia e material no padrao desejado"

  SYNTAX :=
    IF 48x64 nao suporta leitura facial/material desejada
       THEN tentar escala maior 96x96
       AND reservar pivot/ground_y/celula maior
       AND manter FX separados.

  OUTPUT :=
    data/builders/build_hibrido_fighter_arcade_hi_bit_v011.py
    data/processed/model_sheets/hibrido_fighter_arcade_hi_bit_key_poses_96x96_v011.png
    data/processed/spritesheets/hibrido_fighter_arcade_hi_bit_sprite_sheet_96x96_v011.png
    data/processed/reports/hibrido_fighter_arcade_hi_bit_delivery_board_v011.png
    data/processed/reports/hibrido_fighter_arcade_hi_bit_motion_preview_v011.gif
    data/processed/reports/hibrido_v011_runtime_stage_sprite_mockup.png
    res/sprites/hibrido/*_v011.png
    doc/contracts/art_gameplay_direction_gate_v011.json
    doc/contracts/visual_dna_manifest_v011.json
    doc/contracts/animation_direction_contract_v011.json
    doc/contracts/model_sheet_to_sprite_fidelity_report_v011.json

  HUMAN :=
    Intervencao humana posterior:
      - qualidade grafica abaixo do padrao desejado;
      - rota simplista/procedural nao pode prosseguir;
      - sprite/stage precisam usar capacidade de geracao visual avancada.

  STATUS :=
    Candidate tecnico/procedural.
    Nao aprovado como baseline artistico.
    Nao usar como fonte de geracao.

  NEXT_SYNTAX :=
    IF humano reprova rota simplista
       THEN gerar fontes avancadas novas para personagem e arena
       AND converter para VDP sem copiar marcas/IP.
```

Fluxo:

```text
v010 48x64 insuficiente
  -> v011 96x96 procedural/hi-bit
  -> HUMAN reprova padrao grafico
  -> NEXT v012: advanced source generation + VDP conversion
```

---

## v012 - fontes avancadas + conversao VDP candidate

```text
[v012]
  INPUT :=
    "humano exige graficos de alto nivel como ambicao visual, com arena e sprite sheet muito acima do simplista"

  SYNTAX :=
    IF humano exige qualidade visual superior
       THEN usar geracao avancada como SOURCE premium
       AND copiar fontes para data/source_art
       AND converter para PNG modo P/PLTE<=16/index0 transparente
       AND manter v009/v010/v011 como evidencia negativa, nao baseline.

    IF referencia externa cita marcas/IP
       THEN usar apenas composicao/ambicao
       AND remover marcas/personagens reais.

    IF stage estoura VRAM
       THEN reduzir tiles unicos por reuso de tiles similares
       AND ajustar SPR_initEx para reserva realista.

  OUTPUT :=
    data/source_art/hibrido_stage_v012/source_concept.png
    data/source_art/hibrido_fighter_v012/source_concept.png
    data/source_art/hibrido_sprite_sheet_v012/source_pixel_sheet.png
    data/source_art/hibrido_stage_pixel_v012/source_pixel_stage.png
    data/builders/build_hibrido_ai_visual_package_v012.py
    res/bg/hibrido_arena_stage_320x224_v012.png
    res/sprites/hibrido/*_v012.png
    data/processed/spritesheets/hibrido_fighter_ai_sprite_sheet_96x96_v012.png
    data/processed/reports/hibrido_fighter_ai_motion_preview_v012.gif
    data/processed/reports/hibrido_fighter_ai_pivot_overlay_v012.png
    data/processed/reports/hibrido_v012_runtime_stage_sprite_mockup.png
    data/processed/reports/hibrido_v012_ai_delivery_board.png
    doc/contracts/art_gameplay_direction_gate_v012.json
    doc/contracts/visual_dna_manifest_v012.json
    doc/contracts/animation_direction_contract_v012.json
    doc/contracts/model_sheet_to_sprite_fidelity_report_v012.json
    out/logs/visual_delivery_gate_report.json
    out/logs/hibrido_v012_*_report.json

  HUMAN :=
    Intervencao humana:
      - reclamou que ring/stage e sprite estavam abaixo do padrao;
      - anexou referencia de arena de luta com densidade e espetaculo;
      - pediu parar de insistir em arte simplista e usar geracao avancada.

  STATUS :=
    Fonte visual muito superior a v011.
    VDP candidate integrado em resources.res/src/main.c.
    Build anterior v012 gerou ROM sha256:
      c83ccec0cd2c0c5b9fc29bbceab333ec49463883482a4a32d7da4a141112a363
    Ajuste local posterior detectou e corrigiu risco de VRAM:
      stage unique tiles: 1066 -> 996
      reserva de sprites ajustada para SPR_initEx(420)
    Rebuild/captura fresca ainda pendentes apos esse ajuste local.
    ready_for_aaa falso.

  NEXT_SYNTAX :=
    IF assets v012 ja sao candidatos visuais fortes
       THEN proxima etapa nao e nova imagem
       BUT validacao runtime:
         - rebuild apos ajuste VRAM;
         - res_graph sem collision_risk;
         - validate_resources com juiz visual ativo;
         - BlastEm fresco;
         - visual_vdp_dump.bin;
         - metrics 60fps;
         - review humano.
```

Fluxo:

```text
HUMAN exige padrao grafico maior
  -> advanced source fighter/stage
  -> VDP conversion 16 cores
  -> runtime candidate v012
  -> res_graph acha risco stage x sprite reserve
  -> dedupe stage tiles + SPR_initEx(420)
  -> NEXT: rebuild + BlastEm + VDP dump + 60fps
```

---

## Sintaxe final de tomada de decisao

Esta e a gramatica que deve governar as proximas versoes:

```text
RULE 01 - Tecnico nao aprova visual
IF PNG indexed AND PLTE<=16 AND build OK
THEN technical_pass=true
BUT visual_pass ainda depende de leitura, identidade e acting.

RULE 02 - Humano reprova visual, nao se remenda por cima
IF HUMAN reprova sprite sheet como generica/blocada
THEN sheet vira negative_evidence
AND proxima geracao volta para source/model sheet/gate.

RULE 03 - Model sheet nao vira sprite por downscale
IF source == high_res_model_sheet
THEN usar como guia de identidade
AND redesenhar/reconstruir em grid nativo.

RULE 04 - Personagem critico exige must_preserve
IF asset == fighter/main_character
THEN verificar cabelo, olhos, rosto, anatomia, lava arm, fissuras,
     shorts, faixa vermelha, bandagens, pele, materiais, assimetria.

RULE 05 - Arte bonita sem game design nao passa
IF asset critico nao declara camera, escala, hitbox, alcance, contato,
   estados e relacao com inimigo/cenario
THEN production_allowed=false.

RULE 06 - Stage e sprite competem por VDP
IF background unique_tiles + sprite_reserve > tile_budget
THEN ajustar reuso de tiles, reserva, janela ativa ou arquitetura
BEFORE claim de entrega.

RULE 07 - Claim AAA so com runtime
IF nao existe BlastEm fresco + screenshot + SRAM + visual_vdp_dump + 60fps
THEN ready_for_aaa=false
AND final_delivery=false.

RULE 08 - Intervencao humana vira proxima sintaxe
IF HUMAN aponta uma falha
THEN registrar falha
AND converter em regra da proxima versao
AND nunca apagar o historico da versao anterior.
```

Fluxo operacional daqui para frente:

```text
v012 candidate
  |
  v
rebuild apos ajuste de VRAM
  |
  v
res_graph_audit
  |
  +-- collision_risk? ---- yes ---> reduzir tiles/reserva/arquitetura -> rebuild
  |                         no
  v
validate_resources com juiz visual ativo
  |
  +-- errors? ------------ yes ---> corrigir asset/recurso/contrato -> rebuild
  |                         no
  v
BlastEm capture fresco
  |
  +-- screenshot/SRAM? ---- no ----> blocker honesto
  |                         yes
  v
visual_vdp_dump.bin
  |
  +-- ausente? ----------- yes ---> ready_for_aaa=false
  |                         no
  v
runtime_metrics 60fps
  |
  +-- instavel? ---------- yes ---> reduzir custo
  |                         no
  v
review humano
  |
  +-- reprova? ----------- yes ---> registrar HUMAN e abrir v013 com nova sintaxe
  |                         no
  v
candidate_to_delivery_gate
```

Resumo honesto:

```text
O projeto avancou de "sprite compila" para "pipeline visual com fonte premium,
gates de arte/game design, source-of-truth, fidelidade model sheet -> sprite,
budget VDP e evidencia visual".

Ainda nao avancou para "AAA entregue", porque a regra final permanece:
se nao foi visto rodando no emulador com evidencia fresca, nao existe como
entrega final.
```
