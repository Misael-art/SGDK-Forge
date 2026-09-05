# Visual Feedback Bank

Este documento e a memoria viva da inteligencia visual do workspace.

Toda correcao visual recorrente deve entrar aqui antes de virar alteracao pontual de asset.

## Regra de uso

Fluxo obrigatorio:
1. Registrar o sintoma observado.
2. Traduzir para diagnostico tecnico.
3. Escrever a heuristica preventiva.
4. Relacionar as metricas afetadas.
5. Citar benchmark de referencia.
6. Definir o check em ROM no `BENCHMARK_VISUAL_LAB`.

Se uma correcao nao entrou aqui, ela ainda nao virou doutrina.

## Template canonico

```markdown
### [TITULO CURTO]

- sintoma:
- diagnostico_tecnico:
- heuristica_preventiva:
- metricas_afetadas:
  - palette_efficiency
  - tile_efficiency
  - detail_density_8x8
  - dithering_density
  - silhouette_readability
  - layer_separation
  - reuse_opportunity
- benchmark_referencia:
  - [jogo ou cena]
- check_em_rom:
```

### Fonte SGDK lendo a paleta da forja

- sintoma: o menu/boot depois da marca aparece com glifos distorcidos, cores de brasa ou ilegivel
- diagnostico_tecnico: `VDP_drawText` usa a paleta de texto corrente. Depois do branding, PAL0 e a rampa da forja; a fonte SGDK pinta o corpo do glifo com o indice 15 dessa paleta. Sem `VDP_setTextPalette` propria e sem WINDOW opaca, o texto herda fuligem e HSCROLL residual
- heuristica_preventiva: teardown da marca reseta scroll, S/H, H-Int e `VDP_setWindowOff`. O menu dono do front-end usa PAL3 so para texto, barra opaca no WINDOW e sombra 1px. Nunca desenhar menu de entrega em PAL0 de cena
- metricas_afetadas:
  - layer_separation
  - silhouette_readability
- benchmark_referencia:
  - Contra: title/options de Gunstar Heroes / Streets of Rage 2 — ouro ou branco com sombra sobre painel escuro
- check_em_rom: cena MENU apos F600 — FORGE legivel, opcoes ouro sobre barra, sem wave de HSCROLL

### Cortina de coluna que deveria levantar so o topo

- sintoma: o fogo da forja sobe, uma faixa preta corta a bigorna, e o "reveal" da coifa parece um void
- diagnostico_tecnico: `VSCROLL_COLUMN` desloca a coluna inteira do plano, nao uma janela de scanlines. 56px de lift puxam o piso para o palco e envolvem o topo (letterbox/coifa preta) por baixo, visivel nos pixels transparentes de BG_A
- heuristica_preventiva: se a intencao e revelar so o topo, use WINDOW (`VDP_setWindowVPos(FALSE, n)` diminuindo n) ou nao mova o plano. Nunca use scroll de coluna/linha como cortina local quando o mesmo plano carrega piso, fogo ou um objeto que precisa ficar travado
- metricas_afetadas:
  - layer_separation
  - silhouette_readability
- benchmark_referencia:
  - Contra: openings de Mega Drive que travam o set e carimbam o nome (Thunder Force IV, Gunstar Heroes)
- check_em_rom: ato 3 em F331 e F451 — fogo na mesma faixa do ato 2, bigorna sem costura preta

### Wipe de palco que apaga a cama da cena

- sintoma: o wordmark sai e leva a bigorna junto; fica um retangulo escuro atras do nome seguinte
- diagnostico_tecnico: `VDP_clearTileMapRect` na faixa compartilhada com o tilemap de props remove os tiles do objeto permanente. Index 0 no wordmark nao salva o que o wipe ja apagou
- heuristica_preventiva: elemento temporario sobre cama permanente sai por **restore** do tilemap original, nao por clear. Clear so e seguro onde o plano ja e transparente (parede acima de y=64 neste caso)
- metricas_afetadas:
  - layer_separation
  - silhouette_readability
- benchmark_referencia:
  - Contra: title cards de Streets of Rage 2 / Shinobi III — o cenario permanece, o nome e que entra e sai
- check_em_rom: F331 MISAEL com bigorna intacta; F451 MASTER com a mesma bigorna do F271

## Entradas iniciais

### Sprite Afundando no Fundo

- sintoma: o personagem some quando atravessa fundos com detalhe medio ou alto
- diagnostico_tecnico: a separacao tonal entre sprite e background esta insuficiente no contorno e na massa principal
- heuristica_preventiva: sprite critico precisa vencer o fundo com outline legivel, sombra interna organizada e valor medio diferente do plano atras
- metricas_afetadas:
  - silhouette_readability
  - layer_separation
- benchmark_referencia:
  - Shinobi III
  - Streets of Rage 3
- check_em_rom: validar em fundo claro, medio e escuro no `Silhouette Lab`

### Paleta Rica no Papel e Pobre na Tela

- sintoma: o asset usa varias cores mas continua parecendo chapado
- diagnostico_tecnico: a paleta gasta slots em tons proximos sem ampliar contraste util entre luz, base e sombra
- heuristica_preventiva: antes de adicionar cor, provar ganho de distancia tonal ou leitura material; se nao ganhar funcao, remover
- metricas_afetadas:
  - palette_efficiency
  - detail_density_8x8
- benchmark_referencia:
  - Monster World IV
- check_em_rom: comparar versao atual e versao reduzida no `Layer Contrast Lab`

### Quantizacao Cega Derrubando a Alma da Cena

- sintoma: a traducao "cabe" em 15 ou 16 cores, mas perde material, foco e personalidade
- diagnostico_tecnico: o pipeline delegou a decisao de paleta ao quantizador em vez de escolher manualmente quais rampas sobrevivem e quais tons podem ser fundidos
- heuristica_preventiva: usar quantizacao cega apenas como controle `basic`; a versao `elite` deve ter curadoria manual semantica de paleta, com escolha explicita de rampas compartilhadas e sacrificios de cor
- metricas_afetadas:
  - palette_efficiency
  - detail_density_8x8
  - reference_alignment
- benchmark_referencia:
  - 16-bit Ray Tracing - Castlevania: Symphony of the Night for Sega MegaDrive & Genesis - Dev Diary 9
- check_em_rom: validar em roster compartilhado ou cena multi-elemento se a paleta curada continua lendo material e foco melhor que a reducao cega

### Dithering Virando Ruido

- sintoma: a superficie parece suja em vez de texturizada
- diagnostico_tecnico: o padrao de dithering perdeu direcao tonal e comecou a operar como ruido de alta frequencia
- heuristica_preventiva: usar dithering apenas onde ele explica transicao de material ou atmosfera; se o olho nao entende o gradiente, limpar
- metricas_afetadas:
  - dithering_density
  - detail_density_8x8
- benchmark_referencia:
  - Earthworm Jim
  - Vectorman
- check_em_rom: alternar entre versao com e sem dithering no `Layer Contrast Lab`

### Cena Bonita, Planos Colados

- sintoma: a cena reduzida continua bonita, mas BG_A e BG_B parecem a mesma imagem com intensidade diferente
- diagnostico_tecnico: a traducao foi feita como compressao global da ilustracao, sem redistribuir contraste, detalhe e paleta por funcao de plano
- heuristica_preventiva: em `scene_slice`, o `basic` pode partir de uma compressao direta, mas o `elite` deve reatribuir profundidade; BG_B pede menor agressividade visual, menor densidade e atmosfera fria, enquanto BG_A deve carregar estrutura legivel sem repetir a leitura inteira do fundo
- metricas_afetadas:
  - layer_separation
  - palette_efficiency
  - detail_density_8x8
- benchmark_referencia:
  - verdant_forest_depth_scene
  - Shinobi III
- check_em_rom: alternar BG_A e BG_B isoladamente e verificar se cada plano ainda possui papel visual proprio

### Review de Tileset Nao Pode Matar a Cena

- sintoma: a sheet de tiles ficou mais limpa e organizada, mas a cena perdeu forca visual e o `elite` caiu
- diagnostico_tecnico: tecnicas de estruturacao de tileset foram aplicadas como transformacao estetica ampla, achatando contraste local, material e densidade util de detalhe
- heuristica_preventiva: usar `palette_strip`, `tileset_sheet` e auditoria de `H-Flip` como camada de review; preservar o ganho estrutural, mas reverter qualquer tratamento global que enfraqueca profundidade, material ou foco da composicao
- metricas_afetadas:
  - detail_density_8x8
  - layer_separation
  - reuse_opportunity
  - palette_efficiency
- benchmark_referencia:
  - verdant_forest_depth_scene
  - Earthworm Jim
- check_em_rom: comparar a versao estruturalmente otimizada com a elite anterior e confirmar que o plano heroico continua vencendo a leitura

### Orcando Contra 2048 Tiles Brutos

- sintoma: a cena parece caber no papel, mas corrompe quando promovida para ROM
- diagnostico_tecnico: o planejamento contou tiles brutos da VRAM e ignorou a faixa real tomada por mapas do VDP, fonte, tabelas e sprite engine
- heuristica_preventiva: nunca aprovar cena por caber em `2048` tiles teoricos; medir teto util real da configuracao e validar a particao entre background e sprite engine antes de promover para benchmark
- metricas_afetadas:
  - tile_efficiency
  - reuse_opportunity
  - layer_separation
- benchmark_referencia:
  - verdant_forest_depth_scene
  - How to Manage VRAM Limits for the Sega Genesis & Mega Drive
- check_em_rom: confirmar em BlastEm que a cena roda sem corrupcao e registrar tiles usados no bloco `VLAB`

### Mapa Grande Demais Para a Fase

- sintoma: a cena parece exigir truques agressivos de VRAM, mas o scroll real da fase usa so uma fracao do mapa configurado
- diagnostico_tecnico: o layout foi planejado com `plane size` maior do que a area jogavel realmente precisa, consumindo espaco de tabela sem ganho visual
- heuristica_preventiva: antes de propor alias de tabela ou reciclagem de blocos do VDP, testar `VDP_setPlaneSize(..)` e validar se a fase cabe num mapa menor sem perder scroll necessario
- metricas_afetadas:
  - tile_efficiency
  - reuse_opportunity
  - layer_separation
- benchmark_referencia:
  - BENCHMARK_VISUAL_LAB
  - How to Manage VRAM Limits for the Sega Genesis & Mega Drive
- check_em_rom: reduzir o tamanho do plano, recompilar a cena e confirmar em BlastEm que o scroll continua correto sem corrupcao de mapa

### Curadoria Offline Boa, Prova em ROM Pede Compare Flat

- sintoma: o `elite` offline vence com clareza, mas a promocao direta da composicao multi-plano para a ROM excede o teto pratico do fundo
- diagnostico_tecnico: a cena preservou profundidade e alma visual, mas a soma de tiles unicos de `BG_A + BG_B` ficou acima do budget util antes da regiao de mapas do VDP
- heuristica_preventiva: quando o laudo acusar `COMPARE_FLAT_CANDIDATE`, manter `original + basic + elite` como verdade de curadoria offline e usar `compare_flat` single-plane como prova honesta de benchmark, registrando a decisao como escolha de budget
- metricas_afetadas:
  - tile_efficiency
  - reuse_opportunity
  - layer_separation
- benchmark_referencia:
  - verdant_forest_depth_scene
  - BENCHMARK_VISUAL_LAB
- check_em_rom: comparar a curadoria offline com a versao `compare_flat` no BlastEm e confirmar ausencia de corrupcao sem esconder a fusao dos planos

### Sheet de Referencia Nao e Frame Jogavel

- sintoma: a IA ou o pipeline tenta traduzir para Mega Drive a sheet inteira de referencia, incluindo faixas de estudo, miniaturas, creditos ou blocos auxiliares
- diagnostico_tecnico: a fonte ainda nao foi decomposta em regiao util; o agente esta quantizando uma prancha editorial, nao um frame jogavel ou um conjunto real de layers
- heuristica_preventiva: antes de qualquer `basic` ou `elite`, identificar e isolar a area util da cena, os recortes de apoio e os elementos auxiliares; a traducao so pode operar sobre a regiao jogavel escolhida ou sobre layers explicitamente montados a partir dela
- metricas_afetadas:
  - palette_efficiency
  - silhouette_readability
  - reference_alignment
  - detail_density_8x8
- benchmark_referencia:
  - metal_slug_urban_sunset_scene
- check_em_rom: validar que a arte promovida para ROM nao carrega texto, quadros de referencia, bordas editoriais ou outros elementos que pertenciam apenas a sheet-fonte

### Animacao Sem Faixa Clara de Frames

- sintoma: o agente mistura poses, repete frames errados ou corta uma animacao no meio porque nao entendeu onde ela comeca e termina
- diagnostico_tecnico: a fonte era uma spritesheet ou board com multiplos blocos, mas faltou uma leitura semantica de ranges e agrupamentos de animacao
- heuristica_preventiva: antes de traduzir spritesheet, declarar `animation_ranges`, identificar blocos de idle/walk/attack e marcar quais frames sao apenas apoio editorial ou preview
- metricas_afetadas:
  - silhouette_readability
  - tile_efficiency
  - reuse_opportunity
- benchmark_referencia:
  - armand_compact_sprite_sheet
- check_em_rom: validar no benchmark de animacao se a ordem dos frames e a massa do movimento permanecem coerentes

### Sprite Sheet Sem Roteiro de Movimento

- sintoma: a IA gera poses bonitas isoladas, mas sem continuidade, pivot estavel ou cobertura dos estados jogaveis
- diagnostico_tecnico: o prompt pulou planejamento de animacao e pediu uma sheet completa antes de fixar model sheet, key poses, frame budget e contrato de escala
- heuristica_preventiva: antes de gerar personagem por IA, emitir `animation_state_plan`, `pose_roster`, `frame_budget_table` e `pivot_and_scale_contract`; gerar model sheet, key poses e strips por acao antes de montar a sheet final
- metricas_afetadas:
  - silhouette_readability
  - pose_continuity
  - volume_consistency
  - pivot_consistency
  - frame_flow_readability
  - gameplay_state_coverage
- benchmark_referencia:
  - Street Fighter Alpha 2
  - Streets of Rage 2
  - Mega Man X
- check_em_rom: validar contact sheet, pivot overlay e preview/GIF antes de qualquer promocao para `res/`

### Pose Sheet Confundida com Animacao

- sintoma: a IA gera uma prancha visualmente boa com idle, corrida, pulo, ataque e vitoria, mas cada quadro e uma acao diferente e nao uma sequencia temporal
- diagnostico_tecnico: o agente aceitou `key_pose_sheet` como se fosse `animation_strip`, sem `motion_phase_map` e sem delta entre frames adjacentes
- heuristica_preventiva: classificar toda imagem por `asset_kind`; `animation_strip` deve conter uma unica acao, fases temporais declaradas e `frame_delta_report`; prancha multi-acao so pode ser `accepted_key_pose_sheet`
- metricas_afetadas:
  - pose_continuity
  - volume_consistency
  - pivot_consistency
  - frame_flow_readability
  - adjacent_frame_delta
  - gameplay_state_coverage
- benchmark_referencia:
  - Street Fighter III
  - The King of Fighters 98
  - Disney's Aladdin
- check_em_rom: validar cada acao como strip isolada com preview animado antes de montar a sheet final

### Bloqueio Falso por Ferramenta de Imagem

- sintoma: o agente declara `blocked_image_tooling` mesmo quando o chat consegue renderizar imagem inline
- diagnostico_tecnico: o agente confundiu ausencia de tool callable/salvavel com ausencia de capacidade visual nativa
- heuristica_preventiva: antes de bloquear, emitir `tooling_capability_report`; se houver `native_chat_inline_generation`, continuar gerando inline e marcar `generated_inline_pending_persistence` ate salvar o arquivo
- metricas_afetadas:
  - reference_alignment
  - style_cohesion
  - asset_lineage_integrity
- benchmark_referencia:
  - imagegen built-in workflow
- check_em_rom: nao aplicavel antes da persistencia; validar filesystem antes de citar paths ou promover assets

### ROM Funcional com Fallback Visual

- sintoma: a ROM compila, roda e responde controle, mas usa asset procedural simplificado no lugar da arte premium aprovada
- diagnostico_tecnico: `local_author_pixel_rasterization` ou `procedural_renderer` foi promovido como fonte final, e o gate confundiu funcionamento tecnico com qualidade visual AAA
- heuristica_preventiva: asset critico so pode promover para `res/` com fonte premium persistida em `data/source_art/`, `premium_source_manifest`, lineage, `source_to_rom_visual_match >= 8` e benchmark declarado; `needs_review` e `perceptual_quality=nao_medido` bloqueiam entrega
- metricas_afetadas:
  - reference_alignment
  - style_cohesion
  - silhouette_readability
  - detail_density_8x8
  - layer_separation
  - asset_lineage_integrity
- benchmark_referencia:
  - HAMOOPIG KOF94 MINIMALIST
  - Street Fighter Alpha 2
  - The King of Fighters 98
- check_em_rom: comparar captura BlastEm da ROM vigente contra `data/source_art/` e contra o `benchmark_profile`; se `source_to_rom_visual_match < 8` ou `benchmark_match < benchmark_profile.required_match`, marcar `visual_gate_blocked`

### Ultimo Slot Visivel em Shadow/Highlight

- sintoma: um highlight de pele, metal ou olho continua "aceso" quando o sprite entra em sombra, quebrando o volume
- diagnostico_tecnico: o ultimo slot visivel da paleta do sprite foi usado por um tom critico numa cena com Shadow/Highlight, e esse slot nao reage do jeito esperado
- heuristica_preventiva: em qualquer cena com Shadow/Highlight incidindo sobre sprites, auditar o ultimo slot visivel da paleta; reservar para preto sacrificial, detalhe estavel ou emissivo intencional, nunca para highlight estrutural
- metricas_afetadas:
  - palette_efficiency
  - silhouette_readability
  - layer_separation
- benchmark_referencia:
  - SH_Slot_Audit_Lab
- check_em_rom: comparar a mesma sprite palette com highlight critico dentro e fora do slot auditado

### Controle Ingenuo Nao Ganha Credito de Pareamento

- sintoma: o `basic` continua marcando alto demais porque recebe `layer_separation` como se fosse uma composicao madura, mesmo sendo so um controle de traducao
- diagnostico_tecnico: o laudo tratou a variante de controle como layout intencional de `BG_A + BG_B`, inflando o score e escondendo o delta real entre erro e traducao
- heuristica_preventiva: so usar `paired_bg` no `basic` quando ele realmente representar uma composicao consciente de planos; controles ingenuos, sheets desmontadas ou crops errados devem ser avaliados sem esse credito
- metricas_afetadas:
  - layer_separation
  - reference_alignment
- benchmark_referencia:
  - metal_slug_urban_sunset_scene
- check_em_rom: validar que apenas a variante promovida como composicao real recebe comparacao de planos pareados

### BG_A Transparente Nao e Tile Morto

- sintoma: uma layer estrutural em `BG_A` recebe `OVER_EMPTY_TILES` mesmo quando os vazios sao justamente a janela semantica para o `BG_B` aparecer
- diagnostico_tecnico: o juiz tratou uma `scene_slice` multi-plano como se fosse um frame chapado independente, penalizando transparencia estrutural como desperdicio de VRAM
- heuristica_preventiva: em viewer ou cena multi-plano declarada por `paired_bg`, um `BG_A` com transparencia estrutural deve ser julgado pela composicao final; so marcar `OVER_EMPTY_TILES` quando o vazio nao fizer parte do recorte semantico da cena
- metricas_afetadas:
  - tile_efficiency
  - layer_separation
  - reference_alignment
- benchmark_referencia:
  - metal_slug_urban_sunset_scene
  - Shinobi III
- check_em_rom: alternar entre a composicao completa e o `BG_A` isolado; se o vazio estiver servindo corretamente a leitura do `BG_B`, ele nao pode ser tratado como tile morto

### Camada Semantica Nao e Actor Sprite

- sintoma: destrocos, massas frontais ou arquitetura isolada recebem score ruim porque o laudo os julga como `sprite` compacto ou `bg_a` cheio, mesmo quando sao layers transparentes para remontagem
- diagnostico_tecnico: a decomposicao semantica foi feita, mas o manifesto usou o papel errado; o juiz penalizou vazio, bounding box e silhueta como se estivesse lendo um actor sprite ou um frame de fundo completo
- heuristica_preventiva: quando a fonte for desmontada em layers transparentes, usar `midground_layer` para massa estrutural entre `BG_B` e o plano jogavel e `foreground_layer` para frente composicional; reservar `sprite` para actor sprite real
- metricas_afetadas:
  - tile_efficiency
  - silhouette_readability
  - layer_separation
  - reference_alignment
- benchmark_referencia:
  - metal_slug_urban_sunset_scene
- check_em_rom: validar que a remontagem final preserva profundidade e que a camada isolada nao foi penalizada como se fosse frame de gameplay independente

### Quantizacao Nao Pode Matar o Alpha

- sintoma: uma camada isolada parece correta em memoria, mas depois da quantizacao volta como bloco opaco ou perde recortes importantes
- diagnostico_tecnico: a conversao de paleta remapeou pixels visiveis para a cor transparente ou descartou o canal alpha na ida e volta entre `RGBA` e `P`
- heuristica_preventiva: em qualquer traducao com layers transparentes, preservar explicitamente o alpha apos quantizacao e impedir que o slot transparente participe do remapeamento de pixels visiveis
- metricas_afetadas:
  - tile_efficiency
  - layer_separation
  - reference_alignment
- benchmark_referencia:
  - metal_slug_urban_sunset_scene
- check_em_rom: validar em painel humano e ROM que o ceu continua visivel atras da layer estrutural e que a massa frontal nao colapsou em buracos por erro de alpha

### Segmentacao Semantica Nao e Threshold de Cor

- sintoma: a ideia de separar `A/B/C` esta certa, mas as layers saem furadas, invadem a camada vizinha ou perdem o significado visual da cena
- diagnostico_tecnico: o pipeline tentou separar por cor, contraste ou borda sem entender o que era ceu, arquitetura, chao e massa frontal
- heuristica_preventiva: em `scene_slice`, primeiro decidir semanticamente o papel de cada regiao; so depois usar cor, luminancia e detalhe como pistas auxiliares para construir o matte
- metricas_afetadas:
  - reference_alignment
  - layer_separation
  - silhouette_readability
  - detail_density_8x8
- benchmark_referencia:
  - metal_slug_urban_sunset_scene
- check_em_rom: validar que a recomposicao preserva profundidade e que nenhuma layer foi "inventada" so por threshold de cor

### Quantizacao Tardia Preserva Estrutura

- sintoma: o pipeline ganha score local por layer, mas a cena recomposta perde gradiente, iluminacao, suavidade do ceu ou volume da arquitetura
- diagnostico_tecnico: a paleta foi reduzida cedo demais, antes da cena estar semanticamente separada e da recomposicao estar resolvida

### Prancha Editorial Nao e Cena

- sintoma: a IA tenta converter a prancha inteira como se todos os blocos fossem parte da cena final
- diagnostico_tecnico: faltou alfabetizacao semantica do `source`; preview, creditos, avatar, palette strip ou mockup foram tratados como regiao util
- heuristica_preventiva: antes de qualquer `basic`/`elite`, emitir `source inventory`, classificar layout e marcar explicitamente quais blocos sao `keep` e quais sao `drop`
- metricas_afetadas:
  - reference_alignment
  - layer_separation
  - detail_density_8x8
- benchmark_referencia:
  - metal_slug_urban_sunset_source_semantics
  - china_arena_stage_board_source_semantics
- check_em_rom: promover para ROM somente a cena recomposta a partir das regioes `keep`, nunca a prancha inteira

### Plano Principal Nao e Mascara Vazada

- sintoma: a arquitetura do plano principal vira um bloco furado, uma silhueta oca ou um recorte magro sem massa
- diagnostico_tecnico: o agente tratou `BG-A` como contorno isolado em vez de plano composicional principal com volume, chao e leitura estrutural
- heuristica_preventiva: quando o `source` indicar um plano principal inteiro, preservar massa e continuidade espacial; nao reduzir `BG-A` a mascara de fachada
- metricas_afetadas:
  - layer_separation
  - silhouette_readability
  - reference_alignment
- benchmark_referencia:
  - metal_slug_urban_sunset_source_semantics
- check_em_rom: validar que o plano principal mantem rua, edificacao e volume antes de qualquer foreground adicional

### Faixa Frontal Composicional Nao e Actor Sprite

- sintoma: o foreground composicional recebe julgamento de sprite compacto e acaba podado, esvaziado ou tratado como ruido
- diagnostico_tecnico: a skill confundiu massa frontal de cenario com actor sprite ou FX isolado
- heuristica_preventiva: strips frontais de composicao devem ser classificados como `scene_plane_foreground_composition` ou `foreground_layer`, nunca como `sprite` por default
- metricas_afetadas:
  - layer_separation
  - silhouette_readability
  - tile_efficiency
- benchmark_referencia:
  - metal_slug_urban_sunset_source_semantics
- check_em_rom: validar que a massa frontal ancora profundidade sem entrar na contagem mental de actor sprite

### Preview, Credito e Avatar Sao Ruido Semantico

- sintoma: mockups laterais, nome do autor, avatar ou mini previews aparecem na hipotese de cena ou contaminam o parsing
- diagnostico_tecnico: o agente viu similaridade visual e promoveu bloco editorial a regiao de cena
- heuristica_preventiva: `mockup_preview`, `author_credits`, `avatar_or_icon` e `metadata_block` devem ser inventariados como classes proprias e descartados por politica, salvo quando o caso explicitamente treinar esses blocos
- metricas_afetadas:
  - reference_alignment
  - detail_density_8x8
- benchmark_referencia:
  - metal_slug_urban_sunset_source_semantics
  - china_arena_stage_board_source_semantics
  - ryu_sprite_sheet_source_semantics
- check_em_rom: nenhum desses blocos pode aparecer em asset promovido para `res/` ou benchmark

### Remontagem Exige Quadro Espacial Comum

- sintoma: A, B e C ate parecem corretos isoladamente, mas nao encaixam quando recompostos
- diagnostico_tecnico: as regioes foram lidas sem respeitar um quadro espacial comum; cada bloco foi tratado como imagem solta
- heuristica_preventiva: toda hipotese de cena precisa declarar `composition_schema`, ordem de planos e `spatial_lock`; a remontagem deve acontecer sobre um mesmo quadro de referencia antes da quantizacao
- metricas_afetadas:
  - reference_alignment
  - layer_separation
  - tile_efficiency
- benchmark_referencia:
  - metal_slug_urban_sunset_source_semantics
- check_em_rom: a cena recomposta deve manter alinhamento entre ceu, plano principal e faixa frontal no recorte visivel da tela

### Stage Board Nao Aceita Sprite Strip Como Fundo

- sintoma: personagens repetidos ou strips de actor entram como parte do fundo so porque dividem a mesma prancha
- diagnostico_tecnico: a skill confundiu sheet auxiliar de elenco com bloco estrutural do stage
- heuristica_preventiva: em boards de background, strips de personagem devem ser `drop` por default; ceu, arquitetura e chao precisam ser extraidos por papel semantico, nao por proximidade visual
- metricas_afetadas:
  - reference_alignment
  - layer_separation
  - tile_efficiency
- benchmark_referencia:
  - china_arena_stage_board_source_semantics
- check_em_rom: nenhum actor strip pode contaminar BG_A/BG_B promovido para scene slice

### Palette Strip e Dado Auxiliar

- sintoma: a faixa de paleta aparece no painel como se fosse bloco de sprite ou parte do sheet jogavel
- diagnostico_tecnico: o parser semantico reconheceu a paleta, mas nao distinguiu dado auxiliar de frame util
- heuristica_preventiva: `palette_strip` deve entrar como `auxiliary_region`; e informacao para paleta, nao parte da animacao nem imagem comum
- metricas_afetadas:
  - reference_alignment
  - palette_efficiency
- benchmark_referencia:
  - ryu_sprite_sheet_source_semantics
- check_em_rom: a faixa de paleta nunca entra no atlas final de frames, mas pode orientar a paleta unica da animacao

### Sprite Sheet Precisa de Linhas de Animacao

- sintoma: a IA marca uma area unica de sprite sheet e ainda nao aprende onde comeca e termina cada sequencia
- diagnostico_tecnico: faltou ler a sheet como conjunto de bandas horizontais de animacao e preparar normalizacao por pivot
- heuristica_preventiva: em sprite sheets longas, emitir `animation_ranges` por linha util antes do recorte de frames; metadata e padding lateral nao podem contaminar essas bandas
- metricas_afetadas:
  - silhouette_readability
  - reuse_opportunity
  - tile_efficiency
- benchmark_referencia:
  - ryu_sprite_sheet_source_semantics
- check_em_rom: a preparacao da sheet deve permitir animacao sem tremor e sem mistura entre linhas

### Topo Glitchado E Regiao Morta

- sintoma: a IA trata uma faixa corrompida como cluster de tile valido
- diagnostico_tecnico: o parser semantico viu densidade visual e classificou ruido incoerente como tiles reutilizaveis
- heuristica_preventiva: em tile/object sheets com glitch evidente, a faixa corrompida deve virar `corrupted_region` e ser descartada inteira antes de separar tiles e objetos
- metricas_afetadas:
  - tile_efficiency
  - reference_alignment
- benchmark_referencia:
  - double_dragon_stage1_tileset_objects_source_semantics
- check_em_rom: nenhum tile vindo da faixa corrompida pode entrar em conversao ou atlas final

### Porta Animada Nao E Tile Simples

- sintoma: sequencia de porta e tratada como cluster generico de tiles e perde ordem, pivot ou papel de objeto
- diagnostico_tecnico: faltou distinguir objeto animado de tile reutilizavel
- heuristica_preventiva: sequencias progressivas como portas devem ser classificadas como `object_animation_sequence`; parede base e overlay de dano devem ficar em grupos separados
- metricas_afetadas:
  - tile_efficiency
  - reuse_opportunity
  - reference_alignment
- benchmark_referencia:
  - double_dragon_stage1_tileset_objects_source_semantics
- check_em_rom: a porta deve sair pronta para sprite animado ou troca de tile, sem contaminar o tileset base da parede
- heuristica_preventiva: para `elite`, manter layers em RGBA de alta fidelidade durante extracao, matte e recomposicao; quantizar so no estagio final da entrega de layer ou da prova de hardware
- metricas_afetadas:
  - palette_efficiency
  - detail_density_8x8
  - layer_separation
  - reference_alignment
- benchmark_referencia:
  - metal_slug_urban_sunset_scene
- check_em_rom: comparar a mesma cena com quantizacao precoce versus quantizacao tardia e validar qual preserva melhor o horizonte, os highlights e a leitura estrutural

### Profundidade por Enxerto de Sprite

- sintoma: BG_A e BG_B nao entregam profundidade suficiente, mas um terceiro plano real nao existe
- diagnostico_tecnico: a composicao precisa de elementos intermediarios com scroll proprio e leitura separada do fundo
- heuristica_preventiva: promover apenas detalhes selecionados para sprites auxiliares quando isso aumentar profundidade sem estourar scanline budget; tratar como composicao de hardware, nao como gambiarra visual
- metricas_afetadas:
  - layer_separation
  - silhouette_readability
  - reuse_opportunity
- benchmark_referencia:
  - Shinobi III
  - Horse Level, Game Design & VDP Bugs
- check_em_rom: validar com contador de sprites por scanline e confirmar ausencia de flicker em BlastEm

### X Igual a -128 e Faixa Proibida

- sintoma: sprites desaparecem ou mascaram outros sem que o limite visivel pareca excedido
- diagnostico_tecnico: um sprite entrou na faixa off-screen associada ao bug de mascaramento do VDP em `X = -128` nas coordenadas praticas do SGDK
- heuristica_preventiva: tratar `X = -128` como area proibida por padrao; so explorar esse comportamento em benchmark ou efeito deliberado com memoria operacional explicita
- metricas_afetadas:
  - silhouette_readability
  - layer_separation
- benchmark_referencia:
  - Horse Level, Game Design & VDP Bugs
- check_em_rom: mover o sprite para fora da faixa proibida e comparar imediatamente o resultado em BlastEm

### Sprite Sheet Com Spill Entre Bandas

- sintoma: um frame de animacao carrega parte do sprite da linha vizinha no topo ou na base
- diagnostico_tecnico: o agrupamento por componente usou overlap bruto e deixou um sprite alto contaminar a sequencia adjacente
- heuristica_preventiva: recorte por frame precisa respeitar a faixa semantica da banda; componentes com centro fora da banda so entram quando a parte visivel dentro da banda for dominante
- metricas_afetadas:
  - reference_alignment
  - silhouette_readability
  - reuse_opportunity
- benchmark_referencia:
  - ryu_sprite_sheet_source_semantics
- check_em_rom: qualquer frame com puxada vertical indevida deve ser bloqueado antes de virar atlas ou metadata de animacao

### Buraco Interno De Cor-Chave Merece Auditoria

- sintoma: vao entre pernas, braco e tronco ou espaco interno de silhueta sai preenchido quando o source sugeria transparencia util
- diagnostico_tecnico: o export removeu apenas background conectado a borda e ignorou ilhas internas de cor-chave enclausurada
- heuristica_preventiva: o laudo pre-entrega deve apontar `internal key-hole alpha` como oportunidade; em sprites e objetos, comparar source e frame exportado antes de decidir manter ou remover a ilha interna
- metricas_afetadas:
  - silhouette_readability
  - reference_alignment
- benchmark_referencia:
  - ryu_sprite_sheet_source_semantics
- check_em_rom: validar se a abertura interna melhora leitura sem destruir detalhe legitimo do sprite

### Drop Grande Nao Pode Sumir Sem Rastro

- sintoma: a IA descarta uma regiao grande e o avaliador humano nao consegue mais revisar se a decisao foi correta
- diagnostico_tecnico: o pipeline removeu o bloco sem preservar evidencia visual de descarte
- heuristica_preventiva: toda `drop region` grande deve ser exportada em `drops/` e listada em `delivery_findings`
- metricas_afetadas:
  - reference_alignment
  - layer_separation
- benchmark_referencia:
  - china_arena_stage_board_source_semantics
- check_em_rom: confirmar que a regiao dropada era editorial ou nao jogavel, e nao foreground util perdido

### Shared Canvas De Review Precisa de Tight Preview

- sintoma: layer de cena parece "vazia" ou com buracos quando aberta isoladamente no explorer
- diagnostico_tecnico: a exportacao em canvas comum manteve alpha fora da area util, mas o laudo nao explicou isso nem mostrou preview recortado
- heuristica_preventiva: scene layers exportadas para review estrutural devem vir com nota explicita de `shared_canvas` e `tight preview`
- metricas_afetadas:
  - layer_separation
  - reference_alignment
- benchmark_referencia:
  - metal_slug_urban_sunset_source_semantics
- check_em_rom: antes da promocao para tilemap real, confirmar se o alpha do review e apenas matte estrutural ou se existe perda visual verdadeira

### Proof Offline Correto Ainda Pode Falhar em ROM

- sintoma: a curadoria offline parece resolvida, mas a versao integrada no laboratorio ou na ROM aparece corrompida, opaca ou estruturalmente diferente
- diagnostico_tecnico: o pipeline confundiu validacao estetica com promocao de runtime; a arte estava correta para review humano, mas a cadeia `asset -> recurso SGDK -> VRAM -> emulador` ainda nao estava segura
- heuristica_preventiva: toda promocao de `scene_slice` precisa passar por triagem de quatro classes antes de virar prova canonica: `asset`, `flags do recurso`, `budget de tiles` e `pipeline de build`; o primeiro acerto visual nao encerra o diagnostico
- metricas_afetadas:
  - reference_alignment
  - layer_separation
  - tile_efficiency
- benchmark_referencia:
  - sunny_land
  - BENCHMARK_VISUAL_LAB
- check_em_rom: recompilar, abrir no BlastEm e confirmar que a leitura final da ROM coincide com a prova offline e nao apenas com o preview RGBA

### Flags de IMAGE Podem Sabotar Cena Valida

- sintoma: a imagem parece SGDK-valida no papel, mas a promocao para ROM explode tiles, perde reuse e degrada a cena sem que o asset bruto pareca quebrado
- diagnostico_tecnico: a linha `IMAGE` foi declarada com configuracao conservadora demais para uma cena grande, desativando compressao e otimizacao de tiles onde a promocao precisava justamente de deduplicacao estrutural
- heuristica_preventiva: em backgrounds de cena, nunca tratar `IMAGE` como mera referencia de arquivo; revisar a politica de compressao e otimizacao antes da build final e desconfiar de `NONE NONE` em imagens grandes promovidas para benchmark
- metricas_afetadas:
  - tile_efficiency
  - reuse_opportunity
  - layer_separation
- benchmark_referencia:
  - sunny_land
  - BENCHMARK_VISUAL_LAB
- check_em_rom: alternar entre a configuracao antiga e a configuracao otimizada do mesmo `IMAGE` e registrar no BlastEm se a cena mantem leitura sem corrupcao

### Transparencia Indexada E Pre-Requisito, Nao Diagnostico Final

- sintoma: o time corrige alpha, a cena melhora, mas a promocao em ROM continua divergindo do esperado
- diagnostico_tecnico: em layers que dependem de alpha estrutural, a representacao indexada correta e um pre-flight obrigatorio da cadeia SGDK; ainda assim, o problema real pode continuar em integracao de recurso, reuse de tiles ou robustez do pipeline
- heuristica_preventiva: quando uma layer transparente falhar, corrigir primeiro a representacao indexada com slot transparente isolado e depois continuar a triagem; nunca encerrar o diagnostico apenas porque o alpha voltou a aparecer, e nunca promover esse passo sozinho a causa raiz final sem prova adicional em ROM
- metricas_afetadas:
  - reference_alignment
  - layer_separation
  - tile_efficiency
- benchmark_referencia:
  - sunny_land
  - metal_slug_urban_sunset_scene
- check_em_rom: apos restaurar a transparencia, repetir a validacao estrutural e confirmar se a ROM final tambem recuperou composicao, custo e estabilidade

### Cena Heroica Merece Rotas Congeladas, Nao Aleatoriedade

- sintoma: cada iteracao da mesma cena volta com ceu, atmosfera e linguagem material diferentes, mesmo quando a geometria base continua igual
- diagnostico_tecnico: o pipeline nao registrou uma exploracao controlada de alternativas nem congelou uma direcao visual apos a escolha; a IA reabriu a direcao de arte do zero em vez de iterar dentro de um contrato
- heuristica_preventiva: em cenas heroicas ou muito atmosfericas, permitir no maximo 3 rotas fortes dentro do mesmo `shared_canvas_contract`, comparar as rotas com a mesma regua de leitura/budget e registrar a escolhida em `route_decision_record` antes de prosseguir para budget final e runtime
- metricas_afetadas:
  - layer_separation
  - palette_efficiency
  - dithering_density
  - reference_alignment
- benchmark_referencia:
  - metal_slug_urban_sunset_scene
  - Streets of Rage 3
- check_em_rom: confirmar no BlastEm que a rota congelada continua legivel, coerente com o resto do projeto e nao foi substituida por outra linguagem cromatica em iteracoes futuras

### Desafiante Bonito Nao Derruba Incumbente Sozinho

- sintoma: uma rota alternativa parece mais bonita em comparativo isolado, mas na solucao real do projeto nao supera o metodo padrao ja consolidado
- diagnostico_tecnico: o julgamento comparou um desafiante flat ou uma imagem isolada contra um incumbente multi-plano fora de contexto, premiando impacto visual bruto e ignorando aderencia ao source, reuse e honestidade de promocao para ROM
- heuristica_preventiva: quando existir metodo padrao incumbente, toda rota desafiante deve vencer em dois niveis antes de substituir o default: `perceptual win` e `system win`; se nao vencer nos dois, a rota fica arquivada como alternativa e o padrao permanece
- metricas_afetadas:
  - reference_alignment
  - layer_separation
  - reuse_opportunity
  - silhouette_readability
- benchmark_referencia:
  - metal_slug_urban_sunset_scene
  - Streets of Rage 3
- check_em_rom: comparar o incumbente composto e o desafiante no mesmo enquadramento, medir tiles unicos e confirmar em BlastEm se o desafiante realmente supera o metodo padrao em leitura e custo

### Flat Anime Pode Ser Solucao, Nao Regressao

- sintoma: uma rota mais chapada, em filosofia de anime background ou cel-shading, parece simplificada demais a primeira vista e corre risco de ser descartada so por abrir mao de degrades ricos
- diagnostico_tecnico: o julgamento confundiu riqueza material com excesso de transicao tonal e ignorou que o Mega Drive premia massas claras, sombra dirigida e reuse estrutural
- heuristica_preventiva: uma rota `anime_style` e valida quando transforma textura em blocos de cor dirigidos, melhora leitura de massa, reduz tiles unicos e preserva a fantasia-base da cena; se vencer em leitura e sistema, pode subir para rota elite mesmo sem imitar o gradiente do source
- metricas_afetadas:
  - palette_efficiency
  - silhouette_readability
  - reuse_opportunity
  - reference_alignment
- benchmark_referencia:
  - metal_slug_urban_sunset_scene
  - Monster World IV
  - Streets of Rage 3
- check_em_rom: comparar a rota chapada com o incumbente no mesmo enquadramento, medir tiles unicos, confirmar se a leitura continua rica em 320x224 e exigir congelamento humano explicito antes de trocar a filosofia de pintura do projeto

### Anime Background Nao E Posterize Duro

- sintoma: o agente entende "anime" como contorno bruto, posterizacao agressiva e ceu chapado generico, produzindo uma cena dura, pobre em traco e distante da referencia humana aprovada
- diagnostico_tecnico: a traducao confundiu `anime background` com `cel shading simplificado`; ela apagou a inteligencia do linework, perdeu a direcao tonal da noite e trocou rampas ilustrativas por blocos arbitrarios
- heuristica_preventiva: quando a referencia aprovada for um fundo de anime, preservar estes pilares antes de reduzir budget:
  - linework fino e desenhado, nao contorno pesado indiscriminado
  - rampas controladas de material, especialmente em tijolo, telhado, metal e pedra
  - ceu como campo tonal elegante, nao so uma chapa azul qualquer
  - janelas quentes como contraponto narrativo
  - flattening cirurgico apenas onde ele ajuda reuse e leitura
- metricas_afetadas:
  - reference_alignment
  - palette_efficiency
  - silhouette_readability
  - reuse_opportunity
- benchmark_referencia:
  - Gemini urban anime background study
  - Streets of Rage 3
  - Shinobi III
- check_em_rom: provar a rota de anime em composicao multi-plano; se o look aprovado pelo humano so existir na imagem full-flat e desmoronar ao separar BG_A/BG_B, a rota ainda nao esta pronta

### Anime Guiado Pede Pipeline por Etapas

- sintoma: o agente tenta achar o look anime final diretamente na conversao para SGDK e perde controle sobre o que veio do traco, o que veio da massa de cor e o que veio da paleta
- diagnostico_tecnico: sem separar `line art`, `recolor de superficies` e `promocao SGDK`, a iteracao mistura decisoes demais e fica dificil corrigir cor sem destruir desenho, ou corrigir budget sem destruir atmosfera
- heuristica_preventiva: quando o alvo for fundo anime controlado, seguir um pipeline guiado:
  1. `scene crop` aderente ao framing final
  2. `anime style` como board de linguagem
  3. `line art only` como contrato de desenho
  4. `recolor broad surfaces` com paleta explicita
  5. `promocao SGDK` com split `BG_A/BG_B`, reforco seletivo de traco e budget review
- metricas_afetadas:
  - reference_alignment
  - palette_efficiency
  - reuse_opportunity
  - layer_separation
- benchmark_referencia:
  - metal_slug_urban_sunset_scene
  - anime guided route study
- check_em_rom: a cor final da cena so pode ser considerada madura se a etapa de `recolor broad surfaces` continuar bonita depois do split para `BG_A/BG_B` e ainda couber no budget real

### Line-First Fecha o Anime no Mega

- sintoma: mesmo com line art correto, a promocao para Mega Drive continua com linhas turvas ou micro-variacao demais porque o traco e a cor ainda estao competindo no mesmo passo
- diagnostico_tecnico: o pipeline reaplica line art e recolor ao mesmo tempo; o resultado preserva contorno demais onde so precisava de contrato estrutural e gera tiles unicos desnecessarios
- heuristica_preventiva: em fundo anime para Mega Drive, transformar o line art em `block mask` e `display mask`:
  1. `block mask` delimita regioes de pintura
  2. `display mask` preserva apenas os tracos que realmente precisam aparecer
  3. a cor deve ser preenchida por regiao e so depois receber o traco seletivo
- metricas_afetadas:
  - tile_efficiency
  - reuse_opportunity
  - silhouette_readability
  - reference_alignment
- benchmark_referencia:
  - metal_slug_urban_sunset_scene
  - anime line-first route study
- check_em_rom: validar se a versao `balanced` ou `cohesive` continua com linhas firmes em BlastEm sem reintroduzir ruido de microtraco nem estourar o teto pratico de tiles

### Benchmark Recolor Virando Clone

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: o asset parece "novo" so porque trocou cores, mas mantem silhueta, pose, proporcao, stage layout ou leitura estrutural do benchmark
- diagnostico_tecnico: o benchmark foi usado como fonte visual implicita em vez de referencia tecnica de escala, densidade, timing, presenca, budget e qualidade
- heuristica_preventiva: asset critico autoral precisa de `source_validity_report`, `authoriality_gate_report` e `clone_risk_report`; `benchmark_similarity_index` acima do limite declarado pelo `benchmark_profile` bloqueia promocao para `res/`
- metricas_afetadas:
  - reference_alignment
  - style_cohesion
  - silhouette_readability
  - palette_efficiency
- benchmark_referencia:
  - HAMOOPIG KOF94 MINIMALIST
  - Street Fighter Alpha 2
  - The King of Fighters 98
- check_em_rom: comparar a captura BlastEm contra a fonte autoral e o benchmark; se a semelhanca estrutural vencer a autoria, marcar `visual_gate_blocked`

### Gi Branco Muddy Sem Hue-Shifting

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: o gi branco vira cinza sujo, perde volume ou parece recolor mecanico sem material
- diagnostico_tecnico: a paleta de tecido claro nao declarou rampas frias de sombra, highlights quentes/limpos nem distancia tonal minima por slot
- heuristica_preventiva: sprite heroico com gi branco exige `white_material_palette_contract` antes de conversao, com sombras azul/roxo, highlights limpos/quentes e funcao por slot; `PALETTE_WASTE` bloqueia entrega
- metricas_afetadas:
  - palette_efficiency
  - silhouette_readability
  - detail_density_8x8
  - dithering_density
- benchmark_referencia:
  - Streets of Rage 3
  - Shinobi III
  - Monster World IV
- check_em_rom: validar em fundo claro, medio e escuro se o gi ainda le tecido, volume e separacao sem virar mancha cinza

### ROM Funcional Mas Sem Autoria Visual

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: a ROM compila, roda e responde, mas personagem, HUD ou stage parecem placeholders, debug lab ou clone sem linguagem propria
- diagnostico_tecnico: o pipeline promoveu funcionalidade tecnica antes de passar `source_validity`, `authoriality_gate` e status `elite_ready`
- heuristica_preventiva: build + BlastEm nao reduzem exigencia visual; asset critico precisa de fonte premium autoral, manifesto completo, `clone_risk_score` dentro do limite declarado, `source_to_rom_visual_match >= 8` e nenhum blocker visual
- metricas_afetadas:
  - style_cohesion
  - reference_alignment
  - silhouette_readability
  - layer_separation
- benchmark_referencia:
  - HAMOOPIG KOF94 MINIMALIST
  - Streets of Rage 3
  - Gunstar Heroes
- check_em_rom: se `validation_report.blocking_statuses` contiver `visual_gate_blocked`, o closeout fica `blocked` mesmo com ROM bootando

### Budget Pass Nao E Visual Pass

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: a cena e defendida como suficiente porque cabe em VRAM/DMA, apesar de sprite, cenario ou HUD parecerem pobres
- diagnostico_tecnico: o laudo de budget foi usado para substituir julgamento estetico e mascarar falta de densidade, autoria, paleta manual ou hierarquia visual
- heuristica_preventiva: separar `budget_pass` de `visual_pass`; se o runtime cabe com folga, o budget nao pode justificar empobrecimento visual, e o asset volta para visual gate
- metricas_afetadas:
  - palette_efficiency
  - detail_density_8x8
  - layer_separation
  - style_cohesion
- benchmark_referencia:
  - Contra Hard Corps
  - Gunstar Heroes
  - Streets of Rage 3
- check_em_rom: revisar captura BlastEm em 320x224 e exigir `visual_delivery_gate_report` limpo antes de qualquer status `pronto`

### Campanha Procedural Disfarcada De AAA

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: a campanha possui ROMs que compilam e abrem no BlastEm, mas a tela e dominada por texto, ASCII, nomes de efeitos, padroes verdes/azuis e um avatar minimo sem arte de cena autoral
- diagnostico_tecnico: o agente otimizou para satisfazer checks de presenca e contagem, reutilizando template procedural e fallback generico no lugar de implementar a intencao visual/mecanica de cada eixo
- heuristica_preventiva: em campanha multi-ROM, rodar `audit_effect_campaign_semantics.ps1`; reprovar `mass_generic_procedural_fallback`, `generic_debug_text_panel`, `generic_lab_resource_set`, `canonical_180_identity_unverified` e `ready_for_aaa_with_unproven_report`
- metricas_afetadas:
  - style_cohesion
  - reference_alignment
  - layer_separation
  - silhouette_readability
  - detail_density_8x8
- benchmark_referencia:
  - Gunstar Heroes
  - Contra Hard Corps
  - Streets of Rage 3
- check_em_rom: confirmar em BlastEm que cada ROM tem arte de cena, gameplay signal, assets auditaveis, `visual_delivery_gate_report`, `freshness_audit_report`, `scene_closeout_gate_report` e auditoria semantica limpos; painel procedural so pode ser `lab_not_delivery`

### Referencia Visual Virando Prompt De Copia

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: o prompt de arte usa nome de jogo, estudio, IP ou artista como comando direto de estilo e o resultado tenta copiar silhueta, composicao ou identidade visual em vez de herdar tecnica
- diagnostico_tecnico: a referencia foi tratada como fonte autoral e nao como benchmark de line weight, paleta, densidade, staging, material, timing ou leitura em 320x224
- heuristica_preventiva: prompts e briefs devem traduzir referencias para linguagem tecnica observavel; nomes de jogos e obras ficam como `inspiration_only` ou benchmark, nunca como instrucao de copia para asset critico
- metricas_afetadas:
  - reference_alignment
  - style_cohesion
  - silhouette_readability
  - palette_efficiency
- benchmark_referencia:
  - Sonic The Hedgehog 2
  - Shinobi III
  - Streets of Rage 3
- check_em_rom: comparar captura BlastEm contra o `master_style_manifest`; se o asset parecer clone de benchmark em vez de cena autoral, marcar `visual_gate_blocked` e exigir novo `authoriality_gate_report`

### Halo De Assinatura Apagando O Monograma

- status: candidate_until_SMOKE_TEST_branding_v3_proof
- sintoma: a cena autoral tem brilho e movimento, mas o selo pessoal vira um orbe generico; as letras do monograma desaparecem antes que o leitor reconheca a assinatura
- diagnostico_tecnico: o sprite de halo possui miolo opaco e recebe precedencia na SAT, cobrindo a silhueta informativa do monograma
- heuristica_preventiva: halo de marca deve ser vazado no centro, ter densidade maior na periferia e ficar atras do sprite de assinatura; o monograma precisa vencer em contraste e leitura antes de qualquer glow
- metricas_afetadas:
  - silhouette_readability
  - layer_separation
  - style_cohesion
  - detail_density_8x8
- benchmark_referencia:
  - publisher marks de 16-bit
  - selos metalicos autorais
- check_em_rom: capturar a fase autor em BlastEm e confirmar que `MO` e reconhecivel antes do nome completo; se o primeiro substantivo visual ainda for "bola de luz", manter `visual_gate_blocked`

### Sprite Lavado Por Rampa Sem Funcao

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: personagem grande ou sprite heroico compila, mas parece palido,
  sem volume, sem impacto e com cores "lavadas" depois da conversao
- diagnostico_tecnico: a quantizacao tratou cor como distancia RGB, nao como
  rampa de material; highlights, base, shadow e dark shadow nao foram
  escolhidos semanticamente
- heuristica_preventiva: sprite critico precisa de `material_color_ramp_plan`;
  cada material deve declarar quais tons sobrevivem, onde ha hue shift e qual
  cor tem funcao de outline externo ou separacao interna
- metricas_afetadas:
  - palette_efficiency
  - detail_density_8x8
  - silhouette_readability
- benchmark_referencia:
  - Streets of Rage 3
  - Contra Hard Corps
  - Vectorman
- check_em_rom: revisar o sprite em 320x224 contra fundo claro e escuro; se o
  volume depender de zoom, manter `visual_gate_blocked`

### Fake Pixel Art Em Sprite Gerado

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: sprite parece pixel art reduzido, mas em detalhe possui blur,
  anti-aliasing, halos, microcores ou bordas fracionarias
- diagnostico_tecnico: source IA/high-res foi aceito sem
  `fake_pixel_art_rejection`, downscale nearest-neighbor/redesenho nativo,
  PLTE limpa e snap para grade 9-bits
- heuristica_preventiva: todo sprite vindo de IA ou mockup passa por
  `fake_pixel_art_rejection`, `pixel_perfect_animation_pass` quando animado e
  `sprite_artifact_report` antes de `res/`
- metricas_afetadas:
  - palette_efficiency
  - silhouette_readability
  - tile_efficiency
- benchmark_referencia:
  - Sonic 3
  - Shinobi III
  - Monster World IV
- check_em_rom: se a captura BlastEm mostrar halo, tremor de borda ou matte
  residual, reabrir o source e bloquear a promocao visual

### Ilhas E Objetos Fora Da Celula Do Personagem

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: ha pixels, pedaços de roupa, FX, sombras ou residuos fora do corpo
  do personagem dentro da celula da strip
- diagnostico_tecnico: slicing aceitou fragmentos de celula vizinha, chroma
  matte residual ou FX baked-in como se fosse parte do personagem
- heuristica_preventiva: cada strip critica precisa de
  `sprite_artifact_report`, `line_cleaning_report` e `cluster_motion_review`;
  FX de impacto deve ser asset separado quando tiver funcao de gameplay
- metricas_afetadas:
  - silhouette_readability
  - tile_efficiency
  - reuse_opportunity
- benchmark_referencia:
  - Streets of Rage 3
  - Gunstar Heroes
  - Contra Hard Corps
- check_em_rom: alternar frames em BlastEm e confirmar que nenhuma ilha pulsa,
  cobre hitbox, entra em SAT como sprite invisivel ou consome tile sem leitura

### Color Blocking Sem Lineart Limpa

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: personagem parece ter boas cores, mas roupa, cabelo, anatomia ou
  contorno ficam tortos, serrilhados ou confusos em 320x224
- diagnostico_tecnico: a arte pulou `lineart_blocking_1px` e tentou resolver
  forma com saturacao, sombra ou highlights depois do color blocking
- heuristica_preventiva: personagem critico precisa de lineart 1px hard-edge em
  uma unica cor escura temporaria antes de paleta final; limpar degraus,
  double corners, pixels orfaos e diagonais antes de color blocking
- metricas_afetadas:
  - silhouette_readability
  - detail_density_8x8
  - palette_efficiency
  - style_cohesion
- benchmark_referencia:
  - Streets of Rage 3
  - Shinobi III
  - The King of Fighters 98
- check_em_rom: validar o mesmo personagem contra fundo claro e escuro; se a
  forma so fica boa por causa de cor/shading, manter `visual_gate_blocked`

### Rotacao Sem Volume Rastreado

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: personagem parece mudar de corpo quando vira para 3/4, perfil,
  costas ou close-up; membros e acessorios flutuam entre angulos
- diagnostico_tecnico: a sheet foi desenhada por pose isolada sem
  `turnaround_tracking_contract`, linhas de articulacao e volumes 3D
- heuristica_preventiva: personagem com rotacao, direcoes multiplas ou angulo
  cinematico precisa declarar tracking lines, volume primitives, foreshortening
  e policy de pivot/hurtbox antes de key poses e strips
- metricas_afetadas:
  - silhouette_readability
  - volume_consistency
  - pivot_consistency
  - style_cohesion
- benchmark_referencia:
  - Streets of Rage 3
  - Shinobi III
  - Monster World IV
- check_em_rom: alternar direcoes e confirmar em 320x224 que cabeca, ombros,
  cintura, joelhos, pes, pivot e hurtbox permanecem coerentes

### Movimento Sem Gravidade Ou Peso

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: pulo, queda, aterrissagem, corrida ou golpe parecem leves demais,
  lineares ou sem impacto fisico
- diagnostico_tecnico: a animacao nao declarou `motion_physics_contract`; faltam
  centro de massa, contato de solo, arcos, gravity beat e inercia secundaria
- heuristica_preventiva: locomocao, pulo, ataque, dano e boss premium devem
  declarar key poses, center_of_mass_curve, gravity_and_contact_model,
  arc_path_map e secondary_motion_order antes do polimento final
- metricas_afetadas:
  - timing_feel
  - frame_flow_readability
  - volume_consistency
  - silhouette_readability
- benchmark_referencia:
  - Sonic 3
  - Earthworm Jim
  - Streets of Rage 3
- check_em_rom: capturar motion GIF e BlastEm; se o corpo nao acumula energia,
  nao cai, nao comprime ou nao paga inercia, manter `visual_gate_blocked`

### Estado Que Estala Sem Transicao

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: personagem sai de ataque, queda, dano ou cutscene direto para idle,
  causando snap visual e perda de game feel
- diagnostico_tecnico: runtime e sheet nao possuem
  `state_transition_motion_contract`; faltam bridge frames, recovery ou regra de
  cancel/retorno
- heuristica_preventiva: toda promocao de sheet jogavel precisa mapear
  from_state, to_state, trigger, bridge_frames, momentum_policy e return_rule
  antes de integrar `SPR_setAnim`/`SPR_setFrame`
- metricas_afetadas:
  - frame_flow_readability
  - timing_feel
  - pivot_consistency
  - gameplay_state_coverage
- benchmark_referencia:
  - Shinobi III
  - Streets of Rage 3
  - Comix Zone
- check_em_rom: validar em controle real no BlastEm que ataque, landing, hurt e
  cutscene retornam com recovery e sem troca brusca de escala ou ground_y

### Cutscene Com Painel Morto

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: cutscene possui imagem bonita e texto, mas parece parada, sem ritmo,
  sem reacao e sem vida em 320x224
- diagnostico_tecnico: faltou `cutscene_motion_beat_map`; hold, pan, blink,
  mouth, reaction, impact motion ou stillness_justification nao foram declarados
- heuristica_preventiva: cutscene AAA deve tratar cada painel como estado de
  FSM com beat de movimento, budget por estado, texto temporizado, audio cue e
  teardown simetrico
- metricas_afetadas:
  - silhouette_readability
  - style_cohesion
  - layer_separation
  - frame_flow_readability
- benchmark_referencia:
  - Phantasy Star IV
  - Valis III
  - Snatcher
- check_em_rom: capturar a cutscene no BlastEm; se nao ha beat visual nem
  justificativa dramatica para quietude, manter no maximo `needs_review`

### Escala De Personagem Alterada Tarde

- status: candidate_until_BENCHMARK_VISUAL_LAB_proof
- sintoma: personagem parece bom isolado, mas camera, hitbox, FOV, pivot ou
  custo de animacao ficam incoerentes depois que a sheet ja comecou
- diagnostico_tecnico: a escala foi tratada como resize visual, nao como
  `visual_dna_manifest.scale_contract` travado antes de model sheet, key poses
  e strips
- heuristica_preventiva: personagem novo precisa declarar `scale_class`,
  bbox em multiplos de 8, FOV, hitbox, workload, integer-pixel motion e
  `scale_lock_status=locked` antes de key poses aprovadas
- metricas_afetadas:
  - scale_lock_integrity
  - scale_gameplay_fit
  - pivot_consistency
  - tile_efficiency
- benchmark_referencia:
  - Sonic 3
  - Monster World IV
  - Streets of Rage 3
- check_em_rom: validar o personagem em cena com camera e colisao; se a escala
  precisar mudar depois de key poses, reabrir planejamento em vez de aplicar
  resize silencioso

### Health Bar Sem Sistema De Dano Latente

- status: candidate_until_UI_PIXEL_SURFACE_LAB_proof
- sintoma: barra de vida parece apenas um retangulo colorido; o jogador nao
  percebe claramente quanto dano acabou de receber
- diagnostico_tecnico: faltou `ui_pixel_surface_contract`; a UI nao declarou
  container, buffer de dano latente, fill ativo, drenagem por pixels inteiros,
  threshold critico e feedback low HP
- heuristica_preventiva: health bar de acao deve ter moldura/outline, buffer
  atrasado, fill hard-edge sem AA, drain em 1 ou 2 px, critical threshold e
  evidencia de leitura nativa antes de runtime final
- metricas_afetadas:
  - ui_readability
  - attention_profile
  - gameplay_feedback_latency
  - pixel_grid_integrity
- benchmark_referencia:
  - Sonic 3
  - Streets of Rage 3
  - Contra Hard Corps
- check_em_rom: causar dano em BlastEm e confirmar que fill ativo, buffer,
  flash critico e audio/feedback nao tremem, nao escalam fracionado e nao
  escondem gameplay

### Logo Ou Fonte Generica Como Identidade Final

- status: candidate_until_BRAND_IDENTITY_LAB_proof
- sintoma: title screen, logo, press-start ou menu principal parecem prototipo,
  fonte padrao, texto desenhado em cima da cena ou marca sem personalidade
- diagnostico_tecnico: faltou `brand_identity_manifest`; o agente tratou
  tipografia e logo como overlay funcional, nao como sistema de leitura,
  genero, tom, escala e runtime VDP
- heuristica_preventiva: front-end autoral precisa declarar logo, fonte display,
  fonte de corpo/HUD, teste de silhueta, monocromatico, thumbnail, fundo
  dinamico, metafora de gameplay legivel, fallback estatico e budget antes de
  promover asset ou runtime
- metricas_afetadas:
  - thumbnail_readability
  - silhouette_readability
  - style_cohesion
  - product_identity
- benchmark_referencia:
  - Contra Hard Corps
  - Sonic 3
  - Streets of Rage 3
- check_em_rom: validar title/menu no BlastEm; se a leitura depende de fonte
  generica, efeito decorativo, escala grande ou fundo limpo, manter
  `visual_gate_blocked`

### Jogo Correto Mas Sem Momento Assinatura

- status: candidate_until_CREATIVE_DIRECTOR_RADAR_proof
- sintoma: o projeto compila, roda, possui arte/sons funcionais e documentos,
  mas ainda parece benchmark, prototipo ou jogo generico sem promessa memoravel
- diagnostico_tecnico: faltou `creative_director_radar`; o agente validou
  conformidade tecnica, mas nao comparou mecanica, level design, audio, visual,
  front-end e game feel contra uma promessa autoral e eixos de benchmark
- heuristica_preventiva: projeto novo, reseed, vertical slice ou claim AAA deve
  declarar promessa em uma frase, 5 eixos de benchmark, 3 pilares assinatura,
  5 gaps/propostas priorizadas, cena assinatura, docs alvo, owner skill,
  evidencia e fallback antes de promover producao
- metricas_afetadas:
  - product_identity
  - gameplay_signature
  - audio_identity
  - visual_identity
  - first_10_seconds_readability
- benchmark_referencia:
  - Street Fighter II Turbo
  - Chrono Trigger
  - Streets of Rage 2
  - Gunstar Heroes
  - Super Metroid
- check_em_rom: validar no BlastEm se o primeiro contato, a primeira acao e a
  cena assinatura provam a promessa do projeto; se a ROM apenas demonstra
  sistemas corretos, rebaixar claim ou emitir `signature_gap`

### Arte Correta Mas Traco Generico

- status: candidate_until_AUTHORIAL_LINE_CONTRACT_proof
- sintoma: a imagem parece competente, limpa e "arcade", mas os personagens,
  props, HUD ou cenario poderiam pertencer a qualquer outro jogo; falta uma
  assinatura de desenho observavel em rosto, maos, silhueta, roupa, materiais e
  landmarks.
- diagnostico_tecnico: o prompt declarou genero, era ou benchmark de qualidade,
  mas nao declarou `authorial_line_contract`; o agente otimizou para uma media
  visual do dataset em vez de uma gramatica de traco do projeto.
- heuristica_preventiva: antes de gerar ou aceitar asset critico, exigir
  contrato de traco autoral com pelo menos: `line_signature`,
  `silhouette_hooks`, `face_grammar`, `hand_foot_grammar`,
  `costume_asymmetry`, `material_marks`, `environment_marks` e lista do que
  seria considerado generico. Sem isso, bloquear com
  `authorial_line_contract_missing` ou `generic_prompt_style_blocker`.
- metricas_afetadas:
  - style_cohesion
  - product_identity
  - silhouette_readability
  - detail_density_8x8
  - material_readability
- benchmark_referencia:
  - Comix Zone
  - Streets of Rage 3
  - Shinobi III
- check_em_rom: reduzir o asset para escala nativa em um fundo claro, medio e
  escuro; se o jogador nao reconhece a obra pelo traco, silhueta e material sem
  ler texto ou manifesto, manter `visual_gate_blocked`.

### Stage Visivel Mas Achatado E Opaco

- status: candidate_until_MUGEN_SFF_SHOWDOWN_rework_proof
- sintoma: stage importado aparece no BlastEm, sem matte magenta, mas a cena
  fica plana, com camera de laboratorio e cores opacas apesar de fonte vibrante
- diagnostico_tecnico: o agente confundiu conformance mecanica com qualidade
  visual; deltas de parallax foram achatados em um unico plano, `zoffset` e
  `verticalfollow` nao viraram contrato de camera de luta, e a paleta usou
  nearest-color/remap massivo sem medir vitalidade cromatica
- heuristica_preventiva: stage com camera X/Y e camadas importadas precisa de
  `camera_motion_contract`, `parallax_layer_contract` e
  `palette_vitality_check` antes de qualquer claim visual; `pass_with_degradation`
  fica no maximo como evidencia de laboratorio
- metricas_afetadas:
  - layer_separation
  - color_vibrancy
  - camera_composition
  - source_to_rom_visual_match
  - perceptual_quality
- benchmark_referencia:
  - palcos arcade 2D com parallax multi-plano
  - jogos de luta 16-bit com chao ancorado e camera legivel
- check_em_rom: comparar source viewport, export preview e screenshot BlastEm;
  se a cena perdeu planos, chao, materiais ou temperatura de cor, bloquear como
  `flattened_mugen_parallax`, `fighting_stage_camera_contract_missing` ou
  `palette_vibrancy_lost`

### Polimento Do Erro Em Sprite Sheet Derivada

- status: rejected_until_VISUAL_SOURCE_OF_TRUTH_proof
- sintoma: o agente tenta "melhorar", "refinar", "upscalear" ou usar img2img em
  sprite sheet parcial/reprovada, preservando blocagem ruim, perda de identidade,
  drift de cabelo/roupa/material e falso senso de progresso
- diagnostico_tecnico: faltou contrato `visual_source_of_truth`; um report
  `passed` de fidelidade tecnica foi interpretado como permissao de fonte
  artistica, mesmo com `human_visual_review_missing_for_aaa`,
  `visual_vdp_dump_missing` ou `visual_gate_blocked`
- heuristica_preventiva: sheet reprovada/parcial vira
  `obsolete_for_generation_source`; a proxima geracao deve nascer do model
  sheet aprovado/travado, `visual_dna_manifest`, brief de direcao,
  `art_gameplay_direction_gate`, lineart 1 px por estado e key poses aprovadas
- metricas_afetadas:
  - source_lineage_integrity
  - model_sheet_to_sprite_fidelity
  - identity_continuity
  - animation_charisma
  - ready_for_aaa
- benchmark_referencia:
  - lutadores 16-bit com silhueta, rosto e roupa consistentes entre estados
  - sprites de luta com key poses redesenhadas em grid nativo
- check_em_rom: se faltam revisao humana, `visual_vdp_dump.bin`, metrics 60fps
  ou leitura visual AAA, manter `runtime_candidate_not_source`; rode
  `validate_visual_source_of_truth.ps1` e bloqueie qualquer uso como `source`,
  `baseline`, `reference_for_generation`, `img2img_base`, `generation_source`
  ou `image_reference`

### Teste Funcional Nao Atinge Densidade Comercial

- status: candidate_until_MARE_BRAVA_visual_v02_rom_proof
- sintoma: a animacao funciona e o personagem aparece no cenario, mas a imagem
  ainda parece um teste tecnico quando comparada aos melhores jogos comerciais
  do Mega Drive: paleta curta sem riqueza perceptiva, sprite simples, fundo
  basico e iluminacao sem resposta temporal
- diagnostico_tecnico: os quatro eixos visuais foram tratados isoladamente; a
  paleta ainda nao organiza rampas por material e temperatura, o sprite nao
  preserva densidade de clusters da fonte autoral, BG_A e BG_B nao constroem
  profundidade suficiente por silhuetas/parallax e a luz permanece apenas
  pintada, sem estado de gameplay ou variacao controlada
- heuristica_preventiva: depois da prova de movimento, exigir um passe conjunto
  de `material_color_ramp_plan`, detalhe por clusters 8x8, separacao de planos,
  parallax por bandas e luz/espuma/pulso com owner, budget e fallback; no Mega
  Drive, substituir a ideia de "gradiente suave" por rampas discretas, dithering
  funcional, palette cycling e raster FX somente quando houver contrato
- metricas_afetadas:
  - palette_efficiency
  - detail_density_8x8
  - silhouette_readability
  - layer_separation
  - material_readability
  - style_cohesion
- benchmark_referencia:
  - Streets of Rage 3: volume dos lutadores, materiais e profundidade de palco
  - Sonic the Hedgehog 3: palette cycling, parallax e riqueza cromatica
  - Shinobi III: silhueta, atmosfera e efeitos subordinados ao gameplay
- check_em_rom: comparar antes/depois na mesma resolucao nativa e no mesmo
  enquadramento, vinculados ao hash da ROM; capturar idle e movimento no
  BlastEm, auditar VDP/paletas e confirmar que o fundo/FX nao rouba a leitura do
  lutador nem quebra o budget de 60 fps

### Efeito Tecnico Forte Sobre Composicao Generica

- status: candidate_until_MARE_BRAVA_cais01_v04_rom_proof
- sintoma: parallax, line scroll, palette cycling, particulas e iluminacao
  funcionam, mas ceu, skyline, piso e props parecem elementos colados ou
  genericos quando comparados com a fonte autoral aprovada
- diagnostico_tecnico: o passe de efeitos alterou a macrocomposicao antes de
  congelar massas, landmarks e marcas de material; primitivas procedurais
  substituíram nuvens horizontais, silhueta industrial compacta, agrupamento de
  caixotes, rede, ferragens e irregularidade da madeira presentes nas fontes
  selecionadas
- heuristica_preventiva: antes de adicionar FX, registrar uma matriz de fonte
  por regiao e congelar macrogeometria, hierarquia de massas, faixa jogavel,
  landmarks e material marks; o passe tecnico pode animar, separar ou iluminar
  essas formas, mas nao redesenha a composicao sem novo gate humano
- metricas_afetadas:
  - style_cohesion
  - reference_alignment
  - layer_separation
  - detail_density_8x8
  - material_readability
  - gameplay_readability
- benchmark_referencia:
  - fontes autorais aprovadas do projeto para desenho e composicao
  - Streets of Rage 2/3 apenas para contraste, leitura e densidade
  - Sonic the Hedgehog 2 apenas para bandas de agua e parallax
- check_em_rom: comparar no mesmo enquadramento a fonte de direcao, o passe
  basico, o passe de efeitos e a captura BlastEm; confirmar que as nuvens,
  silhueta industrial, grupo de caixotes, rede, poste e textura de madeira
  continuam reconheciveis e que nenhum FX desloca ou apaga a faixa de luta

### Matte Granulado Aprovado Como Sprite Nativo

- status: rejected_until_BORDER_CONNECTED_MATTE_proof
- sintoma: o sprite passa modo P, 4 bpp, index 0 e grade VDP, mas traz retangulo
  claro, halo verde/cinza ou graos ao redor da silhueta
- diagnostico_tecnico: fundo foi inferido por threshold global de brilho/croma;
  LANCZOS/bilinear criou cores intermediarias; o snap VDP ainda converteu
  indices diferentes para o mesmo RGB, inflando identidade de tile
- heuristica_preventiva: quando alpha nao for confiavel, extrair apenas fundo
  compativel conectado as bordas, emitir `foreground_matte_report`, binarizar
  alpha antes do resize, usar NEAREST no caminho nativo e compactar aliases de
  paleta depois do snap; light/dark/chroma sao evidencias do mesmo hash
- metricas_afetadas:
  - silhouette_readability
  - edge_cleanliness
  - palette_efficiency
  - tile_identity_integrity
  - source_to_native_fidelity
- benchmark_referencia:
  - sprites comerciais de luta/brawler com recorte duro e leitura limpa em 1x
- check_em_rom: inspecionar 1x em fundo claro, escuro e cor-chave, depois no
  BlastEm; qualquer franja que altere silhueta ou consuma tiles bloqueia visual

### Metasprite Vertical Contado Como Pressao Horizontal

- status: rejected_until_HARDWARE_CELL_SCANLINE_proof
- sintoma: uma escala mais alta e descartada porque o total de celulas do
  metasprite e somado em todas as scanlines do personagem
- diagnostico_tecnico: celulas empilhadas em Y foram tratadas como se estivessem
  simultaneamente na mesma linha, fabricando overflow de links
- heuristica_preventiva: decompor cada objeto em celulas VDP de no maximo 32x32
  (ou consumir `hardware_cells` reais) e acumular cada celula apenas no seu
  intervalo Y; medir separadamente total de links, links/linha e pixels/linha
- metricas_afetadas:
  - sprite_links_total
  - sprites_per_scanline
  - sprite_pixels_per_scanline
  - scale_decision_integrity
- check_em_rom: confirmar a decomposicao do runtime e medir a pior composicao;
  estimativa corrigida reabre o gate, mas nao substitui evidencia BlastEm

### Cor De Roupa Vazando Para Pele

- status: candidate_until_MARE_BRAVA_material_topology_rom_proof
- sintoma: a roupa principal perde uma borda clara e sua cor aparece na barriga,
  braco, axila ou outra area de pele; o sprite parece sujo, o contorno interno
  enfraquece e o volume de roupa/corpo fica ambiguo em 1x
- diagnostico_tecnico: o pipeline usou regiao anatomica ampla, posicao, matiz ou
  luminancia para colorir (`torso`, `arms_or_guard`) sem um mapa independente de
  propriedade de materiais. A mesma heuristica atravessou top, pele e wraps; AA
  entre materiais mascarou a perda de topologia
- heuristica_preventiva: depois do color blocking e antes do shading, exigir
  `material_region_contract` com um proprietario por pixel, indices exclusivos
  por material, outline compartilhado declarado e fronteiras criticas. Borda
  dura de 1 px e o default; sombra da roupa fica do lado da roupa e sombra da
  pele do lado da pele. Feedback local corrige primeiro a fronteira principal,
  depois membros/acessorios, preservando pose e silhueta da candidata em rework
- metricas_afetadas:
  - material_readability
  - palette_efficiency
  - detail_density_8x8
  - silhouette_readability
  - style_cohesion
- benchmark_referencia:
  - Streets of Rage 3: separacao de pele, roupa e outline em lutadores pequenos
  - Shinobi III: bordas duras e rampas com funcao em escala nativa
  - Monster World IV: economia cromatica sem contaminar materiais adjacentes
- check_em_rom: comparar fonte, candidato anterior e material-clean no mesmo
  enquadramento 320x224. Em fundo claro, escuro e no palco real, barriga/bracos
  devem permanecer pele, roupa deve manter sua silhueta e nenhum pixel de AA
  cruzado pode piscar ou dissolver a fronteira durante a animacao

## 2026-09-01 — source sanitation + causal route portfolio

Escopo: raster high-res que precisa virar sprite nativa. Evidencia inicial:
caso humano full-body em baixa resolucao; priors nao sao universais.

### Fonte contaminada confundida com anatomia

- sintoma: sombra de chao, poeira, fumaça, nuvem, particula, floor line,
  checkerboard ou texto sobrevivem como pe, roupa, cabelo ou contorno
- diagnostico_tecnico: a imagem entrou como `translation_source` sem
  saneamento semantico; alpha/matte nao resolve oclusao de identidade
- heuristica_preventiva: executar `forge-art source-audit`; manter a fonte
  contaminada apenas no papel de referencia seguro e obter uma pose limpa
- metricas_afetadas: `silhouette_readability`, `style_cohesion`,
  `material_readability_under_vdp_limits`
- check_em_rom: nao aplicavel antes da autoria nativa; gate fecha na fonte

### Rotulo de filtro sem causalidade

- sintoma: candidato chamado Lanczos/Mitchell, mas os pixels nasceram de
  spans, mascaras ou coordenadas hardcoded
- diagnostico_tecnico: o underlay foi apenas hash/metadata; nao participou do
  caminho causal do output
- heuristica_preventiva: `route_shootout_report` liga source hash, matte hash,
  backend/versao/algoritmo/parametros e output hash; redraw posterior usa
  `native_reauthoring_over_<route>_guide`
- metricas_afetadas: lineage, `style_cohesion`, `silhouette_readability`
- check_em_rom: proibido promover; volta ao shootout/autoria

### Falso challenger

- sintoma: BASIC/ELITE ou A/B diferem por recolor/near-duplicate sem hipotese
  visual distinta
- diagnostico_tecnico: delta numerico substituiu julgamento de identidade
- heuristica_preventiva: painel fixa source/crop/matte/target/anchor, alerta
  near-duplicates e nunca escolhe vencedor automaticamente
- metricas_afetadas: `silhouette_readability`, `detail_density_8x8`,
  `style_cohesion`
- check_em_rom: gate humano nao abre se todas as rotas ja falham identidade

Autoridades: `art/native-sprite-production/references/source-route-triage-protocol.md`
e `tools/sgdk_wrapper/forge_art/route_prior_registry.json`.
