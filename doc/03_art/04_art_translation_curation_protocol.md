# 04 - Art Translation Skill Curation Protocol

## Objetivo

Este protocolo existe para curar e medir a acuracia da skill `art-translation-to-vdp`.

A skill so pode ser considerada madura quando produz traducoes consistentes para hardware real em casos variados, mantendo:

- alma visual
- legibilidade
- economia de hardware
- prova objetiva de vantagem entre versao `basic` e versao `elite`

## O que significa "acuracia" aqui

Para esta skill, acuracia nao significa copiar a imagem-fonte pixel por pixel.

Acuracia significa:

1. preservar o que realmente importa na imagem
2. simplificar sem matar a identidade visual
3. respeitar as restricoes do VDP
4. vencer a traducao direta e ingênua

## Pacote canonico de curadoria

Cada caso de curadoria deve ter:

- `source_image`
- `semantic_parse_report`
- `observed_ir`
- `derived_structure_ir`
- `source_inventory`
- `layout_complexity`
- `drop_policy`
- `composition_schema`
- `scene_truth_kind`
- `source_semantic_map`
- `translation_case_manifest`
- `basic_translation`
- `elite_translation`
- `translation_report`
- `aesthetic_report`
- `hardware_budget_review` quando o alvo for `tilemap` ou `scene_slice`
- painel humano `original + basic + elite`
- painel humano `source -> semantic parse`
- painel humano `source -> drop regions`
- painel humano `source -> inferred A/B/C -> recomposed scene`
- painel humano semantico `ORIGINAL -> A/B/C extraidos -> ELITE remontado` quando houver `source_semantic_map`
- `palette_strip` por layer quando o caso for `tilemap` ou `scene_slice`
- `tileset_sheet` por layer quando o caso for `tilemap` ou `scene_slice`
- resumo de reuso estrutural com duplicatas e oportunidades de `H-Flip`
- evidencia em ROM quando o asset for promovido para benchmark ou projeto real
- nota de budget do VDP quando a traducao usar reparticao de VRAM, `sprite grafts` ou `compare_flat`
- declaracao explicita quando o caso usar `plane size tuning`, `window alias`, `hscroll slack reuse` ou `SAT reuse`
- criterio explicito de pareamento: `basic` so recebe `paired_bg` quando a variante realmente representa uma composicao intencional de planos; controle ingenuo nao ganha credito de layer separation como se fosse direcao de arte madura

## Decomposicao semantica obrigatoria da fonte

Antes da primeira passada `basic`/`elite`, o agente deve classificar a fonte.

Campos minimos:

- `source_layout_type`
  - `single_frame`
  - `scene_sheet`
  - `sprite_sheet`
  - `tilemap_sheet`
  - `editorial_board`
- `intent_summary`
- `usable_regions`
- `auxiliary_regions`
- `annotation_regions`
- `animation_ranges` quando houver animacao
- `exotic_elements` quando houver elementos isolaveis ou ambiguos

Objetivo:

- distinguir o que e cena jogavel
- distinguir o que e preview, crop, nota editorial ou credito
- distinguir o que e dado auxiliar util, como `palette_strip`, nomes, ranges ou bloco tecnico
- distinguir inicio e fim de animacoes em sheets
- distinguir elementos exoticos que podem virar layer separada, sprite graft, FX isolado ou referencia descartavel

Regra:

- a traducao nao pode começar enquanto a fonte ainda estiver semanticamente ambigua
- o agente deve emitir um `semantic_parse_report` antes de produzir qualquer variante `basic` ou `elite`
- a fase semantica operacional deve sempre produzir `observed_ir.json` e `derived_structure_ir.json`
- `observed_ir` guarda so fatos visuais; `derived_structure_ir` guarda a hipotese estrutural minima com confianca por dimensao
- se a fonte for `scene_sheet`, `sprite_sheet` ou `editorial_board`, a primeira tarefa do agente e desmontar a fonte, nao quantizar
- se a fonte vier com sprites + nomes + paleta + creditos + avatar + mockup, a skill precisa inventariar cada classe antes de promover qualquer regiao para cena util
- se a desmontagem gerar camadas estruturais em canvas transparente, o manifesto deve usar papeis semanticos:
  - `midground_layer` para massa estrutural entre `BG_B` e o plano jogavel
  - `foreground_layer` para massa de frente, destrocos ou ornamento composicional que nao deve ser julgado como actor sprite
- em stage boards, preferir semantica estrutural:
  - `scene_plane_sky`
  - `scene_plane_architecture`
  - `scene_plane_ground`
- em tile/object sheets, distinguir:
  - `tile_cluster`
  - `overlay_cluster`
  - `object_animation_sequence`
- em sprite sheets, `palette_strip` deve entrar como `auxiliary_region`, nao como frame jogavel
- segmentacao por cor ou threshold bruto, sem leitura semantica de ceu/arquitetura/chao/massa frontal, nao e considerada decomposicao valida

## Corpus supervisionado para alfabetizacao semantica

Antes de chamar a skill de madura, ela deve passar por um corpus supervisionado de parsing semantico em:

- `assets/reference/translation_curation/composição_de_cenas/`

Trilhas minimas:

- `scene boards`
- `fighter sheets`
- `tile/object sheets`
- `maps/oversized boards`

Casos iniciais canônicos:

- `metal_slug_urban_sunset_source_semantics`
- `china_arena_stage_board_source_semantics`
- `ryu_sprite_sheet_source_semantics`
- `double_dragon_stage1_tileset_objects_source_semantics`

Regra:

- essa trilha treina leitura de `source`
- nao substitui a curadoria `basic vs elite`
- ela vem antes

## Ordem canonica do pipeline

Para `scene_slice` e casos equivalentes, a ordem correta e:

1. interpretar semanticamente a fonte
2. extrair layers preservando informacao original
3. construir mattes / alpha por layer
4. recompor em espaço comum por `alpha compositing`
5. so depois quantizar ou indexar para o destino Mega Drive

Anti-padroes:

- pular direto para `basic`/`elite` sem `semantic_parse_report`
- exportar como `final` uma estrutura ainda bloqueada por conflito global, baixa confianca critica ou falha visual de recomposicao
- quantizar a fonte inteira antes da separacao semantica
- gerar `B` e `C` por edge detection ou threshold puro
- recompor por sobreposicao dura sem matte
- deixar cada layer mudar de enquadramento ou alinhamento espacial

## Tipos de caso obrigatorios

O conjunto de curadoria da skill deve cobrir, no minimo:

### 1. Personagem metalico

Valida:

- leitura de material
- dithering funcional
- separacao de volumes

### 2. Personagem organico

Valida:

- rosto
- pele
- tecido
- leitura de silhueta sem armadura pesada

### 3. Fundo atmosferico

Valida:

- gradiente
- profundidade
- papel de BG_A e BG_B

### 4. Tilemap modular

Valida:

- repeticao inteligente
- variacao sem ruido
- disciplina de tile reutilizavel

### 5. Sprite sheet pequeno

Valida:

- consistencia entre frames
- massa
- reuso
- economia de tiles

## Casos avancados opt-in

### 6. Reparticao de VRAM

Valida:

- se a cena so passa quando a reserva do sprite engine e ajustada
- se o agente sabe justificar o uso de `SPR_initEx(u16 vramSize)`
- se o ganho de background nao destruiu o budget de sprite

### 7. Profundidade por sprite graft

Valida:

- uso de sprites auxiliares para simular plano extra
- custo por scanline
- legibilidade real versus flicker

### 8. Quirk de hardware

Valida:

- comportamento de bug ou exploit do VDP
- intencao declarada
- reproducao em BlastEm

Regra:

- casos desta categoria nunca sao baseline da skill
- entram apenas como trilha avancada e explicitamente marcada

## Taxonomia de tecnicas de montagem do VDP

### `canonica_segura`

- `plane size tuning`
- `SPR_initEx(u16 vramSize)` quando a medicao pedir
- `3+1 palette split`
- `compare_flat` para prova em ROM

### `avancada_com_tradeoff`

- `window alias`
- `hscroll slack reuse`
- `sprite graft`

### `opt_in_de_cena_especial`

- `SAT reuse`
- quirks e exploits de mascaramento do VDP

Regra operacional:

- `canonica_segura` pode ser proposta pela skill por padrao
- `avancada_com_tradeoff` exige justificativa no manifesto e nota de budget
- `opt_in_de_cena_especial` exige benchmark dedicado e memoria operacional explicita

## Rubrica canonica

Cada caso deve ser julgado em 5 eixos:

### A. Preservacao da alma visual

- `0`: perdeu identidade
- `1`: preserva so a ideia geral
- `2`: preserva o foco e a forma
- `3`: preserva identidade, material e impacto

### B. Conformidade de hardware

- `0`: quebra regra basica do VDP
- `1`: cabe mal e exige correcoes obvias
- `2`: cabe com poucos ajustes
- `3`: cabe limpo no pipeline

### C. Qualidade perceptiva Mega Drive

- `0`: parece apenas reduzido
- `1`: parece convertido, nao reinterpretado
- `2`: parece traduzido com consciencia de hardware
- `3`: parece arte nativa do console

### D. Eficiencia estrutural

- `0`: desperdicio severo
- `1`: reuso fraco
- `2`: organizacao boa
- `3`: organizacao exemplar para VRAM e tile reuse

### E. Delta `elite > basic`

- `0`: elite nao vence basic
- `1`: elite vence pouco
- `2`: elite vence com clareza
- `3`: elite mostra salto didatico e reproduzivel

## Regra de aceite do caso

Um caso so pode ser considerado `canonizado` quando:

- `elite > basic`
- o delta minimo do caso e atingido
- nao ha `rework` no laudo principal
- a alma visual foi preservada em nivel aceitavel
- o caso gera pelo menos uma heuristica reutilizavel ou confirma uma heuristica existente

## Taxonomia de falhas da skill

Estas falhas devem ser classificadas na curadoria:

- `SOUL_LOSS`
  - perdeu a identidade central da imagem
- `DIRECT_QUANTIZATION_LOOK`
  - parece so um downscale quantizado
- `PLASTIC_MATERIAL`
  - material rico virou superficie chapada
- `FACE_COLLAPSE`
  - rosto ou leitura facial colapsou
- `WEAK_PLANE_SEPARATION`
  - fundo e plano jogavel brigam pela mesma leitura
- `OVERDETAIL_NOISE`
  - detalhe demais para o tamanho
- `TILE_WASTE`
  - solucoes visuais boas, mas estruturalmente ruins para VDP
- `NO_ELITE_DELTA`
  - a versao elite nao demonstrou superioridade clara
- `BROKEN_ALPHA_MATTE`
  - o recorte da layer destruiu profundidade, abriu buracos ou tapou areas que deveriam permanecer visiveis
- `EARLY_QUANTIZATION_LOSS`
  - gradiente, volume ou leitura estrutural foram perdidos porque a paleta foi reduzida cedo demais

## Sinais canônicos do laudo de budget

Quando `analyze_translation_case.py` emitir `hardware_budget_review`, estes sinais devem ser tratados como orientacao operacional da skill:

- `WHOLE_IMAGE_CONVERSION_RISK`
  - significa que a variante ainda se comporta como imagem inteira comprimida
  - acao esperada: redistribuir detalhe por plano, modularizar e reduzir a dependencia de tiles unicos
- `COMPARE_FLAT_CANDIDATE`
  - significa que a curadoria offline esta boa, mas a prova em ROM tende a estourar o teto pratico de tiles do fundo
  - acao esperada: permitir `compare_flat` para benchmark e registrar essa fusao como escolha de budget, nao como downgrade silencioso
- `MANUAL_VRAM_PARTITION_CANDIDATE`
  - significa que a cena mistura foreground e fundo pesado e pode pedir reserva manual de VRAM
  - acao esperada: abrir medicao com `megadrive-vdp-budget-analyst` e avaliar `SPR_initEx(u16 vramSize)` antes de promover a cena

## Sinais de tecnica avancada fora do laudo automatico

Estes sinais ainda dependem de leitura humana e decisao estrutural:

- `PLANE_SIZE_TUNING_CANDIDATE`
  - a fase usa mapas maiores do que o scroll real exige
  - acao esperada: testar `VDP_setPlaneSize(..)` antes de reciclar tabelas
- `WINDOW_ALIAS_CANDIDATE`
  - a Window esta fora do design da cena e sem uso por HUD, console ou debug
  - acao esperada: considerar alias apenas como tecnica avancada com registro explicito
- `HSCROLL_SLACK_REUSE_CANDIDATE`
  - a cena esta travada em `HSCROLL_PLANE` e o resto da tabela parece sobrando
  - acao esperada: tratar como tecnica de risco controlado e provar em BlastEm
- `SAT_REUSE_CANDIDATE`
  - a cena e menu, title screen ou cutscene com uso nulo ou minimo de sprites
  - acao esperada: liberar apenas em trilha opt-in de cena especial

## Workflow da curadoria

1. Escolher uma imagem-fonte
2. Emitir `source inventory`, `layout classification`, `semantic region parsing`, `drop policy` e `recomposition hypothesis`
3. Materializar `observed_ir.json` e `derived_structure_ir.json`
4. Rodar o gate estrutural com conflito global, `engine_affordance` e verificador visual
5. Exportar `final` ou `provisional`
6. Ler `delivery_findings` antes de qualquer entrega humana:
   - `frame spill` entre bandas
   - oportunidade de `internal key-hole alpha`
   - `drop regions` grandes preservadas em `drops/`
   - nota de `shared_canvas` RGBA para scene layers
6. Se o caso for pedagogico, rodar `analyze_source_semantics.py`
7. Preencher o manifesto do caso
8. Produzir `basic` e `elite` apenas quando o pacote semantico estiver apto
6. Rodar `analyze_translation_case.py`
7. Registrar score, falhas e sinais do `hardware_budget_review`
8. Apresentar o painel `original + basic + elite` para validacao humana
9. Quando o caso for `tilemap` ou `scene_slice`, revisar o pacote estrutural de tileset:
   - `palette_strip`
   - `tileset_sheet`
   - resumo de `tile reuse`
10. Confirmar que a revisao estrutural nao piorou leitura, material ou profundidade
11. Se `hardware_budget_review` pedir `compare_flat`, `sprite graft` ou reparticao manual de VRAM, registrar a decisao antes da prova em ROM
12. Se a curadoria apontar `plane size tuning`, `window alias`, `hscroll slack reuse` ou `SAT reuse`, classificar a tecnica na taxonomia acima e registrar por que ela foi ou nao foi adotada
13. Se houver feedback humano novo:
   - escrever no `02_visual_feedback_bank.md`
   - atualizar a skill se a regra for geral
14. So depois disso promover o caso para benchmark ou uso de projeto

## Regra de astucia pre-entrega

O agente nao pode depender de descoberta manual tardia para falhas recorrentes de composicao e recorte.

Antes de entregar qualquer pacote semanticamente exportado, ele deve provar que avaliou:

- se algum frame de sprite sheet invade a banda vizinha
- se o frame tem oportunidade real de alpha interno por cor-chave enclausurada
- se regioes descartadas grandes ainda precisam de revisao humana
- se layers de cena em canvas comum precisam de `tight preview` para nao parecerem buracos ou perda de preenchimento

## Regra de protecao da alma visual

Em casos de `scene_slice`, o review de tileset e uma tecnica de auditoria e estruturacao, nao uma licenca para degradar a imagem.

Se uma passada guiada por tiles:

- reduzir o contraste entre planos
- achatar materiais
- matar atmosfera
- derrubar o score `elite` sem ganho estrutural relevante

entao o correto e:

1. manter `palette_strip` e `tileset_sheet` como artefatos de review
2. desfazer a transformacao visual agressiva
3. reintroduzir apenas o aprendizado estrutural que nao destrua a leitura

## Artefatos canônicos

- protocolo: este documento
- sprint: `doc/03_art/03_ai_source_to_vdp_sprint.md`
- skill: `tools/sgdk_wrapper/.agent/skills/art/art-translation-to-vdp/SKILL.md`
- diretorio de casos: `assets/reference/translation_curation/`
- template de caso: `tools/image-tools/specs/art_translation_case.template.json`
- avaliador: `tools/image-tools/analyze_translation_case.py`

## Criterio de maturidade da skill

Considere a skill pronta para uso amplo apenas quando:

- houver pelo menos 5 casos canônicos cobrindo os tipos obrigatorios
- a maioria dos casos ficar em `elite_delta_confirmed`
- as falhas recorrentes estiverem virando heuristica e nao retrabalho casual
- o agente parar de depender de "sorte de prompt" para traduzir bem
