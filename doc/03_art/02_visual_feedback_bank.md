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
- heuristica_preventiva: usar `palette_strip`, `tileset_sheet` e auditoria de `H-Flip` como camada de review; preservar o ganho estrutural, mas reverter qualquer tratamento global que enfraqueça profundidade, material ou foco da composicao
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
- diagnostico_tecnico: o parser semantico viu densidade visual e classificou ruído incoerente como tiles reutilizaveis
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
