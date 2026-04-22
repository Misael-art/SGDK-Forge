# 13 - Spec de Cenas

## scene_roadmap

### Cena 0 - Front End Curado

- papel: porta de entrada do laboratorio
- objetivo: provar que o front-end ja sustenta a dupla funcao de showcase premium e ferramenta tecnica
- entrega minima: menu navegavel, leitura forte, estado visual vivo e base pronta para expansao
- dependencia principal: `front_end_profile`

### Cena 1 - Multiplane Showcase

- nome de trabalho: `scene_multiplane_showcase_v2`
- papel: baseline de profundidade, composicao por planos e leitura de personagem/foreground
- objetivo: estabelecer uma cena bonita, legivel e comparavel como referencia do laboratorio
- dependencia principal: traducao forte de BG_A/BG_B, sprite principal e overlay seguro

### Cena 2 - Water FX Showcase

- nome de trabalho: `scene_water_fx_showcase_v2`
- papel: validar FX de line scroll com leitura controlada e efeito colateral visual coerente
- objetivo: provar que o laboratorio consegue fechar um caso de raster/scroll com evidência forte e sem ambiguidade de leitura
- dependencia principal: ownership de overlay, tabela de scroll, budget e captura rastreavel

### Cena 3 - Depth Tower Showcase

- nome de trabalho: `scene_depth_tower_showcase_v2`
- papel: validar profundidade por `VSCROLL_COLUMN` e regras de teardown/reset deterministico
- objetivo: provar que a V2 nasce preparada para cenas complexas de scroll especial sem repetir fragilidade de contexto
- dependencia principal: cleanup de scroll, overlay em `WINDOW`, regressao deterministica e evidencia correta

### Expansoes planejadas depois do slice

- masked light / palette split
- boss kinematics
- audio XGM2 lab
- demais showcases visuais avancados que entrarem no roadmap aprovado

## Contratos Canonicos Transversais

### `ui_decision_card` - `front_end_main_menu`

- `scene_or_surface_id`: `front_end_main_menu`
- `surface_kind`: `menu_title_front_end`
- `profile_kind`: `front_end_profile`
- `ui_role`: porta de entrada do laboratorio, seletor de cenas e primeira prova de curadoria visual
- `diegese_level`: `meta_frame_ui`
- `hud_density`: `media`, com leitura tecnica clara e impacto visual premium
- `ui_psychology_goal`: fazer o jogador/agente perceber que esta entrando em um showroom tecnico vivo, nao em um menu neutro
- `attention_profile`: titulo forte, selecao legivel, estado tecnico secundario e nenhum texto critico em plano rolavel
- `plane_ownership_map`: `WINDOW` para texto tecnico/estado, `BG_B` para atmosfera, `BG_A` para moldura e estrutura visual, `SPRITES` apenas para cursor/feedback se o budget permitir
- `ui_architecture_choice`: `meta_frame_ui` com fallback `window_plane_static_hud`
- `budget_decision`: `nao_medido`
- `fallback_plan`: reduzir animacao de cursor/parallax antes de sacrificar legibilidade

### Semantica de budget obrigatoria por cena

Todo laudo futuro deve separar:

- `rom_asset_cost`
- `vram_resident_set`
- `load_time_dma_cost`
- `per_frame_dma_cost`
- `active_animation_window`
- `scene_local_scope`
- `scanline_sprite_pressure`

Regra local: `SPR_initEx(768)` e `VDP_setPlaneSize(64, 32, TRUE)` fazem parte do baseline de budget e nao podem ficar fora do parecer.

## Detalhamento do Slice 1

### Cena 1 - `scene_multiplane_showcase_v2`

- classe de problema: composicao multi-plano com leitura premium e base de showroom
- objetivo visual: provar profundidade real, separacao forte entre `BG_B` e `BG_A`, foreground legivel e um elemento heroico que sustente a cena sem parecer colado
- papel no projeto: baseline de beleza, clareza espacial e linguagem visual da V2
- budget alvo:
  - `cabe` em layout de dois planos mais um sprite heroico sem exigir hack estrutural
  - tiles de background dentro de particao honesta de VRAM
  - pressao de sprites baixa o bastante para preservar margem para expansoes futuras de FX
  - overlay em `WINDOW` sem competir com planos rolantes
- resource_budget_model:
  - `scene_local_scope`: somente assets da cena multi-plano, sprite heroico e overlay tecnico
  - `rom_asset_cost`: `nao_medido`; `resources.res` ainda nao declara assets reais
  - `vram_resident_set`: BG_B, BG_A, fonte/overlay em `WINDOW`, sprite engine reservado por `SPR_initEx(768)` e sprite heroico futuro
  - `load_time_dma_cost`: preload de tiles/mapas/paletas da cena permitido na entrada da cena
  - `per_frame_dma_cost`: `nao_medido`; esperado baixo ate haver animacao/streaming real
  - `active_animation_window`: sem ciclo obrigatorio por enquanto; se houver sprite animado, manter apenas a janela ativa residente
  - `scanline_sprite_pressure`: `nao_medido`; alvo baixo, sem flicker como solucao de baseline
  - `runtime_loading_model`: `scene_local_preload`
  - `fallback_plan`: reduzir tiles unicos, reorganizar paleta, simplificar foreground ou usar `compare_flat`
- riscos de VDP:
  - duplicacao semantica entre `BG_A` e `BG_B`
  - excesso de tiles unicos por tentar converter ilustracao inteira
  - foreground pesado demais virando pseudo-terceiro-plano imaginario
  - paleta sem hierarquia, fazendo o plano heroico afundar no fundo
- contrato de evidencia:
  - screenshot dedicada em BlastEm
  - `save.sram`
  - `visual_vdp_dump.bin`
  - captura com overlay `off` e `on`
  - laudo de budget por cena com veredito `cabe`, `cabe com recuo` ou `nao cabe`
  - navegacao deterministica da cena a partir do menu

### Cena 2 - `scene_water_fx_showcase_v2`

- classe de problema: `HSCROLL_LINE` com agua viva e leitura controlada
- objetivo visual: provar um caso de FX de agua com movimento perceptivel, ritmo elegante e acoplamento coerente com a geografia da cena
- papel no projeto: estabelecer a primeira cena de scroll especial da V2 com ownership de efeito e leitura rastreavel
- budget alvo:
  - `cabe` com tabela de line scroll previsivel por frame
  - DMA/VBlank dentro de margem estavel para nao matar atualizacoes criticas
  - nenhuma dependencia de terceiro plano imaginario
  - HUD/overlay preservado em `WINDOW`
- resource_budget_model:
  - `scene_local_scope`: assets da agua, faixa afetada por scroll, overlay tecnico e dados da tabela de scroll
  - `rom_asset_cost`: `nao_medido`; `resources.res` ainda nao declara assets reais
  - `vram_resident_set`: tiles/mapas locais, fonte/overlay em `WINDOW`, sprite engine reservado por `SPR_initEx(768)` e buffers de scroll necessarios
  - `load_time_dma_cost`: preload de tiles/paletas da cena permitido na entrada; tabela base pode ser preparada fora do gameplay responsivo
  - `per_frame_dma_cost`: `nao_medido`; deve incluir atualizacao da tabela `HSCROLL_LINE` e qualquer tile animation concorrente
  - `active_animation_window`: apenas banda/tiles visiveis da agua; nao carregar variantes de cenas futuras
  - `scanline_sprite_pressure`: `nao_medido`; preferir scroll/tile animation a sprites decorativos de agua
  - `runtime_loading_model`: `scene_local_preload`, com possibilidade futura de `tilemap_streaming` se a cena crescer
  - `fallback_plan`: reduzir granularidade do line scroll, usar palette cycling ou recuar para FX menos denso
- riscos de VDP:
  - texto corrompido por escrever em plano sob `HSCROLL_LINE`
  - custo de tabela ou cadence de update competindo com uploads do frame
  - agua chamativa demais e sem funcao espacial, virando ruido
  - prova bonita offline que nao fecha em ROM real
- contrato de evidencia:
  - screenshot dedicada em BlastEm
  - `save.sram`
  - `visual_vdp_dump.bin`
  - captura curta comprovando oscilacao viva da agua
  - regressao deterministica chegando na cena e capturando estados `overlay_off` e `overlay_on`
  - registro do owner do efeito e do reset de cena

### Cena 3 - `scene_depth_tower_showcase_v2`

- classe de problema: profundidade por `VSCROLL_COLUMN` com teardown deterministico
- objetivo visual: provar profundidade vertical/espacial mais agressiva, com leitura de massa e reset limpo ao sair da cena
- papel no projeto: mostrar que a V2 sabe lidar com scroll por coluna sem repetir a fragilidade de contexto observada na V1
- budget alvo:
  - `cabe` com custo controlado de `VSRAM` e coluna
  - zero estado sobrando apos transicao de cena
  - overlay em `WINDOW` como contrato obrigatorio
  - fallback declarado se a composicao exigir recuo estrutural
- resource_budget_model:
  - `scene_local_scope`: assets da torre/profundidade, dados de `VSCROLL_COLUMN`, overlay tecnico e estado de teardown
  - `rom_asset_cost`: `nao_medido`; `resources.res` ainda nao declara assets reais
  - `vram_resident_set`: tiles/mapas locais, fonte/overlay em `WINDOW`, sprite engine reservado por `SPR_initEx(768)` e dados de coluna/scroll necessarios
  - `load_time_dma_cost`: preload de tiles/mapas/paletas da cena permitido na entrada
  - `per_frame_dma_cost`: `nao_medido`; deve incluir custo de `VSRAM`/colunas e qualquer upload concorrente
  - `active_animation_window`: nenhum ciclo pesado aprovado ate laudo real; se houver sprite/graft, usar janela ativa
  - `scanline_sprite_pressure`: `nao_medido`; sprite grafts so entram com pior scanline auditado
  - `runtime_loading_model`: `scene_local_preload`
  - `fallback_plan`: reduzir numero de colunas, diminuir profundidade, simplificar foreground ou usar `compare_flat`
- riscos de VDP:
  - embaralhamento do texto por uso indevido de `BG_A`
  - `DMA_QUEUE` deixando lixo de scroll para a proxima cena
  - profundidade forte no editor, mas sem leitura espacial real em 320x224
  - mistura de prova de profundidade com pseudo-3D mais caro do que o slice precisa
- contrato de evidencia:
  - screenshot dedicada em BlastEm
  - `save.sram`
  - `visual_vdp_dump.bin`
  - captura da entrada na cena e da volta ao menu para provar teardown limpo
  - regressao deterministica com captura `overlay_off` e `overlay_on`
  - laudo de reset de scroll confirmando limpeza por CPU na saida quando aplicavel

## first_playable_slice

### Escopo

O primeiro slice obrigatorio da V2 e:

- front-end inicial curado
- 3 cenas benchmark
- evidência BlastEm como contrato obrigatorio
- regressao deterministica por cena
- budget por cena
- observacao de curadoria, ainda sem promocao automatica

### Cenas do slice

1. `scene_multiplane_showcase_v2`
2. `scene_water_fx_showcase_v2`
3. `scene_depth_tower_showcase_v2`

### O que o slice precisa provar

- o laboratorio ja nasce com identidade propria
- o menu nao e tela neutra; ele e parte do showcase
- cada uma das 3 cenas exercita uma classe diferente de solucao visual
- a automacao consegue navegar, capturar e amarrar evidencia por cena
- a documentacao e o runtime podem evoluir juntos sem colapso de contexto

### O que fica fora deste primeiro slice

- matriz completa de todas as cenas da V2
- claims de AAA total para o projeto inteiro
- canonizacao formal de aprendizados herdados da V1
- expansao para audio, boss labs ou efeitos mais raros antes do fechamento correto do slice inicial

### Criterio de aceite conceitual

O slice so deve abrir implementacao quando estiver claro que:

- o front-end tem papel de showcase e nao de placeholder
- as 3 cenas cobrem profundidade, FX de scroll e scroll especial com teardown
- cada cena podera ser julgada por visual, budget, regressao e evidencia
- a ordem de expansao futura nao depende de adivinhacao

## Roadmap Geral de Recursos

### Regra de leitura

Este roadmap organiza o que o agente ja demonstra hoje como proficiencia operacional no ecossistema, em ordem logica de implementacao.

Critério usado para entrar aqui:

- existe skill canonica ou contrato operacional explicito
- existe caso de V1, runtime materializado ou padrao tecnico rastreavel
- nao depende de inventar API nem de vender experimento como default

### Fase 0 - Fundacao, leitura e gate

- hierarquia de verdade do projeto
- questionario de abertura para `projeto_novo`, `reseed` ou `projeto_existente`
- `project_brief`, `core_loop_statement`, `feature_scope_map`, `scene_roadmap`, `first_playable_slice`, `front_end_profile`
- memoria operacional, changelog e manifesto estrutural

### Fase 1 - Pipeline visual base

- diagnostico de asset e triagem `erro_de_asset`, `erro_de_recurso_sgdk`, `erro_de_budget`, `erro_de_pipeline`
- traducao `basic` vs `elite` para VDP
- disciplina pixel-strict Mega Drive
- julgamento estetico e congelamento de direcao visual
- composicao multi-plano com `BG_A`, `BG_B`, foreground e `compare_flat` quando necessario

### Fase 2 - Front-end curado

- menu/title como showcase vivo e nao tela neutra
- hierarquia visual forte, item selecionado com feedback observavel
- `WINDOW` como plano fixo legitimo para HUD e overlay
- safe-area de texto e separacao entre leitura premium e leitura tecnica

### Fase 3 - Showcases de cena base

- cena multi-plano com parallax honesto
- sprite heroico ancorado por pivot consistente
- overlay seguro em `WINDOW`
- budget por cena e regressao deterministica

### Fase 4 - FX de scroll e profundidade

- `HSCROLL_LINE` para agua ou FX de banda controlada
- `VSCROLL_COLUMN` para profundidade por colunas
- teardown e reset deterministico de scroll-tables
- ownership explicito do callback/efeito e fallback declarado

### Fase 5 - Sprite e personagem

- sprite sheets com pivot estavel
- timing por VBlank
- economia de tiles por ciclo
- flip horizontal por hardware
- preparacao para boss articulation quando o caso pedir

### Fase 6 - Luz, paleta e raster controlado

- palette split / `H-Int` mid-frame com owner unico
- masked light em lab dedicado
- palette cycling quando o caso exigir vida perceptiva
- spotlight ou efeito localizado sem vender alpha blending inexistente

### Fase 7 - Boss, setpiece e articulacao

- boss kinematics com rigging/partes coordenadas
- leitura de weak point, telegraph e massa
- decisao entre sprites, plano dominante ou hibrido
- laudo de pior quadro antes de chamar de valido

### Fase 8 - Audio senior

- arquitetura XGM2
- ownership de canal
- coexistencia entre BGM, SFX, voz e ambiente
- `pause`, `resume`, `stop`, loop limpo e matriz de eventos
- plano formal de evidencia de audio em BlastEm

### Fase 9 - Integracao e prova

- build coerente com SGDK 2.11 real
- laudo de budget VDP antes de runtime final
- evidencia fresca em BlastEm vinculada a ROM vigente
- regressao por cena com captura reproduzivel
- memoria operacional atualizada sem inflar status

## Mapa de Proficiencia Atual

### Recursos graficos hoje tratados como proficiencia operacional

- fundacao de projeto, planejamento e classificacao de contexto
- traducao de arte para VDP com leitura `basic` vs `elite`
- composicao multi-plano e parallax entre `BG_A` e `BG_B`
- overlays seguros em `WINDOW`
- safe-area de texto e front-end curado
- animacao de sprite com pivot, timing e economia de VRAM
- `HSCROLL_LINE` para water FX e bandas vivas
- `VSCROLL_COLUMN` para profundidade com cleanup deterministico
- palette split / masked light em laboratorio dedicado
- budget VDP, VRAM, DMA, scanline pressure e recuos estruturais
- captura/evidencia em BlastEm com handshake em SRAM

### Recursos sonoros hoje tratados como proficiencia operacional

- arquitetura XGM2 por contrato
- ownership de canais
- integracao orientada a eventos
- `pause/resume` e loop-safe playback
- planejamento de prova de audio em emulador

### Recursos com proficiencia parcial, mas ainda nao default do roadmap inicial

- boss kinematics e forward kinematics em lab dedicado
- palette cycling como recurso de vida/estado
- front-end premium mais dramatico do que o necessario para o slice 1
- audio senior completo como cena propria, depois do fechamento visual inicial

## Trilha de Curadoria Futura

### O que ainda nao deve ser tratado como proficiencia consolidada

- `window alias` como politica geral de layout
- `hscroll slack reuse` como atalho padrao
- `SAT reuse` ou `sprite_midframe_sat_reuse` fora de benchmark dedicado
- `interlaced_448` fora de cena especial
- `software_affine_pseudo3d` como rota madura de producao
- `procedural_raster_glitch_suite` como efeito default do laboratorio
- `mutable_tile_decal_mutation` como sistema consolidado
- `cellular_microbuffer_sim` como tecnologia pronta

### Como esses itens devem entrar no futuro

- primeiro como caso explicitamente experimental
- depois como scene/lab dedicado com card formal e fallback
- depois com laudo de budget, build coerente e evidencia em BlastEm
- so apos validacao humana podem subir de `experimental` ou `advanced_pattern_candidate` para curadoria mais forte

### Regra de honestidade documental

- se a tecnica existe apenas como competencia declarada de skill, mas ainda nao tem prova madura suficiente no laboratorio vigente, ela fica em `curadoria_futura`
- se a tecnica ja foi exercitada em V1, mas ainda nao passou pelo ciclo correto de validacao na V2, ela entra como referencia herdada, nao como proficiencia final automaticamente transferida

## Dicionario Pedagogico

### `VDP`

- significado: e o chip de video do Mega Drive. Ele decide como planos, sprites, scroll, paletas e tabelas de video realmente aparecem na tela.
- exemplo pedagogico: quando o documento fala em `riscos de VDP`, ele quer dizer "riscos de a ideia visual nao caber ou quebrar no hardware real". Uma cena pode parecer boa num editor e ainda falhar no VDP por excesso de tiles, scroll mal resetado ou texto no plano errado.

### `BG_A`

- significado: e um dos dois planos principais de background. Em geral carrega a estrutura visual mais proxima ou mais importante da cena.
- exemplo pedagogico: numa floresta, `BG_A` pode carregar o chao, troncos e elementos que definem o palco principal da acao.

### `BG_B`

- significado: e o outro plano de background. Em geral carrega atmosfera, distancia, ceu, horizonte ou uma camada mais recuada da composicao.
- exemplo pedagogico: na mesma floresta, `BG_B` pode carregar ceu, neblina e montanhas distantes, deixando `BG_A` para a parte mais "jogavel" da imagem.

### `foreground`

- significado: elemento de frente da composicao, usado para dar profundidade ou oclusao. Nem sempre e um plano inteiro; pode ser detalhe controlado, sprite enxertado ou faixa composicional.
- exemplo pedagogico: galhos escuros passando na frente da camera podem funcionar como `foreground` para fazer a cena parecer mais profunda.

### `overlay`

- significado: camada de informacao visual por cima da cena, como labels, diagnostico, hints ou telemetria.
- exemplo pedagogico: texto mostrando nome da cena, modo atual ou estado do benchmark e um `overlay`.

### `WINDOW`

- significado: e o plano fixo do VDP usado para texto ou HUD sem sofrer com certos tipos de scroll do cenario.
- exemplo pedagogico: se a agua da cena usa scroll por linha e bagunca o texto quando ele fica em `BG_A`, mover o texto para `WINDOW` evita esse embaralhamento.

### `parallax`

- significado: efeito de profundidade em que camadas diferentes se movem em velocidades diferentes.
- exemplo pedagogico: se o fundo anda devagar e o chao anda mais rapido quando a camera se move, o olho percebe profundidade mesmo numa tela 2D.

### `HSCROLL_LINE`

- significado: modo em que o scroll horizontal pode mudar linha por linha da tela.
- exemplo pedagogico: para simular agua ondulando, cada faixa horizontal da agua pode se mover um pouco diferente, produzindo uma oscilacao viva.

### `VSCROLL_COLUMN`

- significado: modo em que o scroll vertical pode mudar coluna por coluna da tela.
- exemplo pedagogico: numa cena de torre ou deserto em profundidade, cada coluna pode subir ou descer um pouco diferente para sugerir massa e distancia.

### `scroll-table`

- significado: tabela de valores que o jogo envia ao VDP para dizer quanto cada linha ou coluna deve se mover.
- exemplo pedagogico: no water FX, a `scroll-table` e como uma partitura que diz "esta linha anda 1 pixel, a proxima 2, a outra volta 1", criando a onda.

### `teardown`

- significado: rotina de desmontagem e limpeza quando a cena termina.
- exemplo pedagogico: se a cena de profundidade usa `VSCROLL_COLUMN`, o `teardown` precisa zerar esse estado antes de voltar ao menu; senao o menu pode herdar lixo visual da cena anterior.

### `reset deterministico`

- significado: limpeza previsivel e sempre igual do estado tecnico da cena.
- exemplo pedagogico: entrar, sair e voltar para a mesma cena deve produzir o mesmo resultado visual. Se uma vez funciona e outra deixa "sujeira", o reset nao esta deterministico.

### `DMA`

- significado: mecanismo rapido de transferencia de dados para a memoria de video.
- exemplo pedagogico: trocar tiles animados do fundo durante o VBlank costuma usar `DMA`; se o volume for grande demais, o frame pode ficar pressionado.

### `DMA_QUEUE`

- significado: modo em que transferencias sao enfileiradas para acontecer depois, em vez de serem escritas de forma imediata por CPU.
- exemplo pedagogico: e util para performance, mas perigoso se a cena termina antes da fila ser drenada, porque o proximo estado pode receber escrita atrasada.

### `VBlank`

- significado: janela curta entre um quadro e outro em que o hardware aceita certas atualizacoes de video com mais seguranca.
- exemplo pedagogico: subir tiles, paletas ou tabelas importantes costuma ser mais seguro no `VBlank`; fora dele, a chance de artefato cresce.

### `VSRAM`

- significado: memoria usada pelo VDP para controlar scroll vertical.
- exemplo pedagogico: a cena com `VSCROLL_COLUMN` mexe em `VSRAM` para dizer quanto cada coluna sobe ou desce.

### `budget`

- significado: orcamento tecnico real da cena no hardware, incluindo VRAM, DMA, sprites, paletas, scroll e custo do pior quadro.
- exemplo pedagogico: uma cena bonita pode receber laudo `nao cabe` se o total de tiles, sprites e efeitos passar do que o Mega Drive aguenta com estabilidade.

### `budget alvo`

- significado: meta de custo que a cena precisa respeitar para ser considerada viavel.
- exemplo pedagogico: quando o arquivo diz que a cena precisa `caber` sem hack estrutural, isso define o teto esperado antes da implementacao.

### `cabe`, `cabe com recuo`, `nao cabe`

- significado:
  - `cabe`: a cena funciona dentro do hardware sem sacrificio relevante
  - `cabe com recuo`: a cena funciona se aceitar uma reducao ou ajuste
  - `nao cabe`: a arquitetura atual nao fecha no hardware
- exemplo pedagogico: uma cena pode ficar `cabe com recuo` se o fundo precisar perder detalhe, usar `compare_flat` ou reorganizar paleta para fechar a VRAM.

### `compare_flat`

- significado: prova honesta em um plano mais simples quando a versao multi-plano nao cabe em ROM real.
- exemplo pedagogico: se a curadoria offline ficou linda com duas camadas pesadas, mas o VDP estoura, o benchmark pode usar `compare_flat` sem fingir que o hardware suporta a composicao original inteira.

### `tiles`

- significado: pequenos blocos graficos, geralmente de 8x8 pixels, usados para construir cenarios, fontes e sprites.
- exemplo pedagogico: o Mega Drive nao desenha um fundo gigante como imagem continua; ele monta a cena a partir de muitos `tiles`.

### `tiles unicos`

- significado: quantidade de tiles que realmente sao diferentes entre si e, portanto, consomem espaco proprio.
- exemplo pedagogico: se cada pedaco do fundo for diferente, a cena explode em `tiles unicos` e pressiona a VRAM. Reuso e modularidade reduzem esse custo.

### `VRAM`

- significado: memoria de video onde vivem tiles, mapas e dados necessarios para a tela.
- exemplo pedagogico: quando falta `VRAM`, a cena pode corromper sprite, fundo ou tabela do VDP mesmo que o build compile sem erro.

### `scanline pressure`

- significado: pressao de sprites ou efeitos numa mesma linha horizontal da tela.
- exemplo pedagogico: se muitos sprites passam pela mesma altura ao mesmo tempo, pode surgir flicker ou perda de partes, mesmo que a tela pareca leve no geral.

### `pivot`

- significado: ponto de ancoragem usado para manter a estabilidade do sprite entre frames.
- exemplo pedagogico: num personagem andando, o pe pode servir de `pivot`; assim o corpo se move sem parecer flutuar ou tremer a cada frame.

### `palette split`

- significado: troca controlada de paleta em parte da tela, geralmente no meio do quadro.
- exemplo pedagogico: a parte de cima da tela pode usar uma paleta mais seca e a de baixo uma paleta mais fria para simular agua ou mudanca de atmosfera.

### `H-Int`

- significado: interrupcao horizontal usada para executar uma mudanca no meio do quadro, como split de paleta ou efeito raster.
- exemplo pedagogico: o `H-Int` pode disparar quando o feixe chega na linha da agua, trocando a paleta dali para baixo.

### `masked light`

- significado: tecnica de luz localizada ou spotlight sem alpha blending real, usando os recursos que o Mega Drive realmente oferece.
- exemplo pedagogico: em vez de iluminar a tela toda com transparencia moderna, a cena acende so a area do foco de luz e deixa o resto mais escuro.

### `palette cycling`

- significado: animacao feita trocando as cores da paleta ao longo do tempo, sem redesenhar todos os pixels.
- exemplo pedagogico: agua brilhando ou painel tecnologico pulsando podem ganhar vida apenas ciclando as cores certas.

### `boss kinematics`

- significado: estudo de movimento e articulacao de chefes ou entidades grandes.
- exemplo pedagogico: um boss com nucleo central e orbiters precisa de `boss kinematics` para que as partes parecam pertencer ao mesmo corpo e nao a objetos soltos.

### `rigging`

- significado: organizacao de partes articuladas para que um elemento grande possa se mover com coerencia.
- exemplo pedagogico: um braco mecanico pode ter base, cotovelo e garra; o `rigging` define como essas partes giram juntas.

### `telegraph`

- significado: sinal visual antecipado que avisa uma acao importante antes dela acontecer.
- exemplo pedagogico: antes de um golpe forte, o boss pode inclinar o corpo ou brilhar; isso e `telegraph`, porque prepara o jogador para reagir.

### `weak point`

- significado: ponto fraco visualmente legivel de um inimigo, boss ou setpiece.
- exemplo pedagogico: um olho brilhante ou nucleo exposto pode ser o `weak point` da luta.

### `XGM2`

- significado: sistema de audio usado no SGDK para musica e efeitos mais robustos dentro do Mega Drive.
- exemplo pedagogico: quando o roadmap fala em `audio XGM2 lab`, ele quer um laboratorio para provar musica, efeitos, pausas e loops dentro do driver correto, nao so "tocar uma faixa".

### `ownership de canal`

- significado: definicao clara de qual tipo de audio controla cada canal disponivel.
- exemplo pedagogico: se um canal e da musica e outro e do efeito critico, o sistema evita que um tiro corte a trilha inteira por acidente.

### `BGM`

- significado: musica de fundo.
- exemplo pedagogico: a trilha principal do menu ou da cena benchmark e a `BGM`.

### `SFX`

- significado: efeitos sonoros curtos de acao, impacto, UI ou ambiente.
- exemplo pedagogico: clique de menu, splash de agua ou impacto do boss sao `SFX`.

### `loop-safe playback`

- significado: reproducao em loop sem clique, corte abrupto ou reinicio perceptivelmente errado.
- exemplo pedagogico: uma musica de menu pode repetir infinitamente; se o jogador percebe um "tranco" toda vez que volta ao inicio, o loop nao esta seguro.

### `regressao deterministica`

- significado: capacidade de reproduzir sempre o mesmo caminho e a mesma captura de uma cena para verificar se algo mudou.
- exemplo pedagogico: o runner entra no menu, seleciona a cena 2, espera o mesmo tempo e captura a mesma prova; isso permite comparar resultados entre builds.

### `BlastEm`

- significado: emulador usado como gate principal de evidencia visual no workspace.
- exemplo pedagogico: uma cena so ganha prova forte quando roda no `BlastEm` com captura rastreavel da ROM vigente.

### `save.sram`

- significado: arquivo salvo com os dados persistentes que a ROM gravou em SRAM.
- exemplo pedagogico: ele pode guardar heartbeat e estado minimo de prova para mostrar que a cena realmente rodou no emulador.

### `visual_vdp_dump.bin`

- significado: dump binario do estado visual relevante do VDP usado como evidencia tecnica.
- exemplo pedagogico: ele serve como prova complementar de que os planos, paletas ou tabelas estavam naquele estado quando a captura foi feita.

### `captura com overlay off/on`

- significado: duas provas da mesma cena, uma limpa visualmente e outra com informacao tecnica ligada.
- exemplo pedagogico: `overlay_off` mostra a beleza da cena; `overlay_on` mostra diagnostico, labels ou telemetria para auditoria tecnica.
