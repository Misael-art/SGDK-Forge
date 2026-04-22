---
name: megadrive-vdp-budget-analyst
description: Analisa VRAM, DMA, sprites, paletas, scroll, scanline pressure, H-Int singleton budget, giant boss plane takeover e worst-frame cost para hardware real do Mega Drive.
---

# Mega Drive VDP Budget Analyst

Use esta skill antes de aprovar efeitos visuais, assets, transicoes ou mudancas de render.

## Verifique sempre

- VRAM total e tiles residentes
- teto real de tiles uteis antes da regiao de mapas do VDP
- DMA por VBlank
- sprites por scanline
- total de links de sprite
- uso de PAL0-PAL3
- H-Int unico por frame
- custo de line scroll e column scroll
- particao real entre background e sprite engine
- custo de enxerto de sprites para simular profundidade extra
- custo de animacao de tiles em VRAM por VBlank
- largura real do stage versus teto pratico do plano antes de streaming
- worst-frame budget quando a cena tiver dois lutadores, HUD e FX grandes
- separacao entre custo ROM, set residente em VRAM, DMA de preload e DMA por frame

## Decisao

Responda sempre em um destes formatos:

- `cabe`
- `cabe com recuo`
- `nao cabe`

Se responder `cabe com recuo`, explicite qual recuo desbloqueia a cena:

- reduzir tiles unicos do background
- reorganizar paletas em `3+1`
- ajustar reserva do sprite engine com `SPR_initEx(u16 vramSize)`
- mover parte da profundidade para `sprite grafts`
- promover a prova de ROM para `compare_flat`

## Resource Budget Semantics

Todo parecer deve separar limite fisico, residencia e custo por frame. Nao reprovar uma proposta so porque "o mundo inteiro nao cabe residente" antes de avaliar escopo local, preload, streaming e janela ativa.

Termos canonicos:

- `rom_asset_cost`: custo do asset compactado ou bruto em ROM; `FAST`, `BEST` e `NONE` mudam ROM/decompress/load behavior, nao o numero final de tiles descompactados que ocupam VRAM.
- `vram_resident_set`: tiles, fontes, sprites, mapas e tabelas que precisam estar simultaneamente residentes na cena atual.
- `load_time_dma_cost`: uploads feitos em boot, loading screen, troca de cena ou trecho sem gameplay responsivo; pode ser alto se houver tela/estado de carregamento honesto.
- `per_frame_dma_cost`: uploads por VBlank durante gameplay ou controle ativo; deve caber no pior quadro sem roubar uploads criticos.
- `active_animation_window`: subconjunto de frames/ciclos realmente necessario no intervalo atual; nao confundir sheet completa do personagem com residencia obrigatoria.
- `scene_local_scope`: assets permitidos para a cena/fase atual; assets de outra cena devem sair do budget residente.
- `scanline_sprite_pressure`: limite perceptivo e fisico de sprites por scanline; multiplexing/flicker e tradeoff declarado, nao mascara de overflow.

## Contrato Operacional

### Entrada minima

- `resources.res`
- dimensoes dos assets promovidos
- `build_output.log` quando existir
- configuracao real de `SPR_initEx`
- layout real de planos
- `ui_decision_card` quando houver HUD/UI formal
- `scene_transition_card` quando houver transicao formal
- `feedback_fx_decision_card`, `boss_setpiece_card`, `advanced_tilemap_design_card` ou `audio_architecture_card` quando houver espetaculo runtime formal

### Saida minima

- laudo deterministico `cabe`, `cabe com recuo` ou `nao cabe`
- numeros de VRAM usados no parecer
- separacao explicita entre `rom_asset_cost`, `vram_resident_set`, `load_time_dma_cost`, `per_frame_dma_cost`, `active_animation_window`, `scene_local_scope` e `scanline_sprite_pressure`
- `budget_decision` alinhado ao `ui_architecture_choice` quando houver UI formal
- `budget_decision` alinhado ao `continuity_model` quando houver transicao formal
- `budget_decision` alinhado aos cards de feedback FX, boss/setpiece, tilemap avancado e audio senior quando existirem
- `glyph_budget_class` alinhado ao `font_render_mode` quando houver anexo tipografico
- recuo explicito quando necessario

### Passa quando

- o parecer consegue ser reconstruido por outra IA a partir dos mesmos numeros
- o laudo identifica claramente se o problema dominante e asset, recurso SGDK ou arquitetura
- o laudo nao confunde asset compactado em ROM com tiles residentes em VRAM
- o laudo nao confunde DMA de preload/loading com DMA por frame em gameplay
- o laudo considera scene-local loading, streaming e active animation window antes de concluir `nao cabe`
- quando houver UI formal, ownership e fallback nao contradizem o laudo
- quando houver transicao formal, `fx_ownership_map`, `teardown_reset_plan` e `fallback_plan` nao contradizem o laudo
- quando houver espetaculo runtime formal, pior quadro, scanline pressure, H-Int, CRAM, DMA, sprites, tile churn e audio ownership ficam auditados
- quando houver anexo tipografico, `glyph_manifest`, `charset_profile` e `fallback_font_plan` nao contradizem o laudo

### Handoff para proxima etapa

- entregar o laudo vigente para `sgdk-runtime-coder`
- bloquear runtime se o laudo nao existir ou estiver contradizendo codigo/docs
- quando houver UI formal, entregar o veredito junto do `ui_decision_card`
- quando houver transicao formal, entregar o veredito junto do `scene_transition_card`
- quando houver cards de espetaculo runtime, entregar veredito junto dos cards e do pior quadro

## Quando houver HUD/UI formal

- ler `ui_architecture_choice` antes de aprovar custo
- usar `budget_decision` como veredito oficial do card
- se a rota for `window_plane_static_hud`, auditar `WINDOW fixa + oclusao de BG_A`
- se a rota for `sprite_hud`, medir scanline pressure contra o pior quadro de gameplay
- se a rota for `raster_enhanced_ui`, exigir `fx_ownership_map`, reset simetrico e fallback honesto
- se houver anexo tipografico, ler `font_render_mode`, `charset_profile` e `glyph_budget_class` antes de aprovar custo
- `fixed_custom_hud_font`
  - auditar residency de tiles, custo de `WINDOW` e subset real de glifos
- `variable_width_tidytext`
  - auditar churn de tiles temporarios, DMA por update, cadence de redraw e reset do cache
- sem `glyph_manifest`, reprovar charset expandido ou compositor proporcional como rota canonica

## Quando houver transicao formal

- ler `continuity_model`, `player_control_policy`, `camera_motion_contract`, `fx_ownership_map`, `runtime_state_handoff`, `teardown_reset_plan` e `fallback_plan`
- usar `budget_decision` como veredito oficial do `scene_transition_card`
- `palette_fade_bridge`
  - auditar CRAM/audio fade e garantir que nao esteja mascarando uma transicao espacial que deveria ser planejada
- `spatial_scroll_bridge`
  - auditar mapa visivel, streaming, plane size, seam oculto e custo de camera no pior quadro
- `scripted_avatar_bridge`
  - auditar sprites, controle do jogador, colisao temporaria, camera scriptada e handoff de estado
- `tile_mask_mosaic_transition`
  - reprovar sem backup/restauro de tileset, budget de DMA, dirty region e fallback barato
- `raster_distortion_bridge`
  - reprovar sem owner unico de H-Int, reset de callback, custo de line scroll/VSRAM e prova de legibilidade
- `lighting_state_transition`
  - auditar CRAM, Shadow/Highlight, palette split, slots criticos e legibilidade de sprite/HUD
- `pseudo3d_perspective_bridge`
  - tratar como `advanced_tradeoff`; exigir budget proprio e fallback seguro
- sem `scene_transition_card`, reprovar transicao avancada como rota canonica

## Quando houver espetaculo runtime AAA

- ler `feedback_fx_decision_card`, `boss_setpiece_card`, `advanced_tilemap_design_card` e `audio_architecture_card` quando existirem
- usar `budget_decision` como veredito oficial de cada card
- `feedback_fx_decision_card`
  - auditar H-Int, CRAM, VSRAM, sprite particles, tile particles, camera shake e reset
  - medir se FX compete com HUD, jogador, projetil ou hitbox no pior quadro
- `boss_setpiece_card`
  - auditar boss + jogador + HUD + projeteis + FX no mesmo scanline budget
  - se houver `plane_takeover`, declarar perda de parallax e custo de tiles residentes
- `advanced_tilemap_design_card`
  - auditar metatile reuse, streaming boundary, dirty uploads, foreground priority e colisao visual
  - separar mundo total, janela visivel, resident set local e DMA de streaming
  - reprovar streaming sem seam budget e fallback
- `audio_architecture_card`
  - auditar ownership de canal, prioridade de SFX, ambience, stinger, pause/resume e custo de PCM
- sem card formal, reprovar tecnica avancada como rota canonica

## Tecnicas canonicas de extrapolacao segura

### Reparticao intencional de VRAM

- Nao orce contra `2048` tiles brutos como se todos fossem livres para arte.
- Orcar contra a faixa realmente util depois de BG_A, BG_B, window, hscroll, sprite table, fonte e sprite engine.
- Se o background legitimo pede mais tiles unicos do que a particao padrao comporta, preferir `SPR_initEx(u16 vramSize)` a aceitar corrupcao silenciosa.
- Se uma cena so estoura porque o projeto inteiro foi contado como residente, recortar por `scene_local_scope` antes de reduzir a ambicao visual.

**Formula de budget (SGDK 2.11):**
```
maps_addr = endereco mais baixo entre BGB, BGA, Window, SAT, HScroll tables
TILE_MAX_NUM = maps_addr / 32
User tiles = TILE_MAX_NUM - TILE_SYSTEM_LENGTH(16) - FONT_LEN(96) - SPR_initEx(N)
BG_A max = User tiles - BG_B tiles

Configs comuns (maps_addr = 0xC000 em todas):
  64x32 + SPR_initEx(128): user = 1296, com BG_B(242) → BG_A max = 1054
  64x32 + SPR_initEx(420): user =  948, com BG_B(242) → BG_A max =  706
  32x32 + SPR_initEx(128): user = 1296, com BG_B(242) → BG_A max = 1054
```
**OBRIGATORIO: calcular tile count com `rescomp` (IMAGE ou TILESET) ANTES de integrar arte.**

### `Plane size tuning`

- O VDP nao exige sempre o maior mapa possivel para BG_A e BG_B.
- Se a fase nao precisa de toda a extensao vertical ou horizontal, reduzir `VDP_setPlaneSize(..)` e uma forma limpa de recuperar espaco de tabela.
- Isso e tecnica canônica e segura quando o tamanho menor cobre o scroll real da cena.
- Em SGDK, trate isso como primeira resposta estrutural antes de hacks mais agressivos.

### Paleta `3+1`

- Se um foreground importante precisa de identidade propria, considere fundo em 3 paletas e reserve 1 para o elemento de frente.
- Isso melhora composicao sem fingir que o VDP ficou maior.

### `Sprite grafts` para profundidade

- O Mega Drive nao ganha terceira layer real.
- Mas elementos intermediarios podem virar sprites auxiliares para simular profundidade adicional.
- So e canônico se passar em sprites por scanline, total de sprites na tela, custo de VRAM e ausencia de flicker.

### `compare_flat` para prova em ROM

- Se um comparativo multi-plano e didatico offline, mas estoura o budget real em ROM, a prova em emulador pode usar `compare_flat` single-plane.
- Isso e aceitavel quando a memoria operacional registra a decisao e a curadoria offline preserva `original + basic + elite`.

### Animacao de background via VRAM

- Antes de aprovar sprite decorativo so para "animar o fundo", medir se a troca de tiles em VRAM resolve o mesmo efeito com menos pressao de scanline.
- Isso move custo de SAT/sprites para DMA/VBlank e residency de tiles.
- E tecnica `canonica_segura` quando:
  - a troca cabe no VBlank
  - os tiles animados sao residentes ou streamados com seguranca
  - o efeito nao compete com uploads mais criticos do frame

### Streaming de tilemap para stage largo

- Cena acima do teto pratico do plano nao deve depender de wrap acidental.
- Se o stage passar de ~512 px no arranjo do plano usado, tratar streaming guiado pela camera como resposta canônica.
- Medir:
  - bytes por coluna ou bloco
  - tolerancia de velocidade da camera
  - risco de seam

### Streaming de animacao e janela ativa

- Sheet completa de personagem nao precisa estar inteira residente se o runtime usa janela ativa, SGDK auto VRAM alloc ou streaming manual validado.
- Medir:
  - frames residentes no pior estado de gameplay
  - tiles unicos do ciclo ativo
  - DMA de troca de frame quando houver upload dinamico
  - fallback para reduzir frames, cadence ou variacao se o pior quadro estourar
- Multiplexing ou flicker controlado so pode entrar para efeito nao-critico; nunca para heroi, hitbox, golpe-chave ou leitura essencial.

### Gate de verdade para raster e paleta

- Efeito raster ou palette split que so "parece bom no editor" nao existe ainda.
- BlastEm e o minimo de gate.
- Se a cena depender fortemente do comportamento mid-frame, pedir tambem prova em hardware real quando possivel.

## Tecnicas avancadas com gate forte

### `Window alias`

- O VDP permite reposicionar a tabela da Window; em teoria ela pode apontar para a mesma regiao de outro plano quando a Window nao estiver sendo usada.
- Isso so entra como tecnica avancada quando:
  - a Window estiver realmente fora da cena
  - nao houver HUD, console, texto de debug ou rotina escrevendo em `WINDOW`
  - a decisao estiver registrada na memoria operacional
- Em SGDK, isso nao e default seguro porque o ecossistema assume layout classico e pode usar `WINDOW` em fluxos auxiliares.

### `H-Scroll slack reuse`

- Em modo `HSCROLL_PLANE`, a tabela de H-Scroll consumida em runtime e menor do que nos modos por tile ou por linha.
- O espaco restante pode parecer reutilizavel, mas isso so e aceitavel quando:
  - a cena estiver travada em `HSCROLL_PLANE`
  - nao houver transicao futura para `HSCROLL_TILE` ou `HSCROLL_LINE`
  - a prova em BlastEm confirmar que nada alem do trecho inicial esta sendo lido
- Trate como tecnica de cena fechada, nao como politica geral de layout.

### Shadow/Highlight ambiental por background

- Beam, fog, smoke ou glow que precisam atravessar fundo e sprite juntos podem justificar Shadow/Highlight de background.
- Isso alivia sprite pressure, mas passa a cobrar:
  - tilemask
  - composicao de planos
  - auditoria de slot de paleta do sprite
  - custo de line scroll se a mascara precisar fugir do 8x8 duro
- Tratar como `avancada_com_tradeoff`.

### Worst-frame budget

- Em jogo de luta, boss fight ou FX massivo, nao orcar por frame "bonito" isolado.
- Orcar pelo pior quadro:
  - dois personagens
  - HUD
  - golpe ou magia
  - hit spark e sub-FX
- Port 1:1 de Neo Geo ou arcade pesado deve ser considerado suspeito ate passar nesse orçamento.

## Tecnicas opt-in de cena especial

### `SAT reuse`

- A Sprite Attribute Table pode parecer reaproveitavel em titulo, menu ou cutscene com poucos sprites.
- Isso nao entra como comportamento padrao do agente.
- So liberar quando:
  - a cena nao depender do sprite engine automatico naquele momento
  - houver controle explicito do ciclo de vida da SAT
  - a tecnica estiver restrita a menu, title screen, cutscene ou benchmark dedicado
  - a evidencia em emulador confirmar ausencia de conflito com sprites futuros

## Taxonomia operacional

- `canonica_segura`
  - `plane size tuning`
  - `SPR_initEx(u16 vramSize)` quando a medicao pedir
  - `3+1 palette split`
  - `compare_flat` como prova honesta de ROM
- `avancada_com_tradeoff`
  - `window alias`
  - `hscroll slack reuse`
  - `sprite grafts`
  - Shadow/Highlight ambiental por background
  - alternancia temporal de FX gigante
- `opt_in_de_cena_especial`
  - `SAT reuse`
  - quirks e exploits de sprite

## Senior Competencies

Esta skill deve ser tratada como dona do budget senior de hardware:

- `scanline pressure`
  - 20 sprites por scanline como verdade de pior quadro
- `H-Int arbitration`
  - uma familia de callback por cena, com owner explicito
- `H-Int singleton budget`
  - uma familia de efeitos por frame, nunca duas assumidas por inercia
- `DMA leakage`
  - custo real por VBlank, inclusive no quadro mais pesado
- `window occupancy / BG_A occlusion`
  - custo real de usar `WINDOW` como HUD e o quanto de `BG_A` fica sacrificado
- `interlaced shimmer budget`
  - medir ganho real de layout versus tremor visual e custo de leitura
- `sprite multiplexing tradeoff`
  - diferenciar alternancia temporal de reuso real de SAT
- `SAT rewrite risk`
  - medir corrupcao potencial, competicao com H-Int e fragilidade de timing
- `giant boss plane takeover`
  - custo e beneficio de mover chefes gigantes para `BG_A/BG_B`
- `worst-frame budgeting`
  - dois personagens, HUD, FX e uploads concorrendo no mesmo quadro
- `shadow/highlight slot audit`
  - risco de operador em slot critico de paleta
- `masked lighting budget`
  - medir custo real de pool emissivo, scanline pressure e perda de leitura em spotlight movel
- `procedural glitch readability budget`
  - garantir que rasgo, flash ou corrupcao de HUD continuem servindo gameplay
- `mutable tile pool budget`
  - quantos tiles unicos uma sala pode sujar sem estourar residency
- `dirty upload discipline`
  - uploads de mutacao local precisam caber no pior quadro
- `cellular microbuffer envelope`
  - regiao maxima, cadence do solver e custo de dirty tiles antes de a tecnica deixar de caber

Regra:

- esta skill responde se a tecnica `cabe`, `cabe com recuo` ou `nao cabe`
- ela deve sempre explicitar o recuo necessario
- nenhuma tecnica de scene special effect pode ser aprovada sem esse parecer
- `interlaced_448` pode entrar no core roadmap, mas o parecer default continua `special_scene_only`

## Quirks e exploits do VDP

- Quirk de hardware nunca entra como comportamento padrao do agente.
- So use com intencao declarada, benchmark dedicado e evidencia em BlastEm.

### X = -128 em coordenadas praticas

- Em fluxos SGDK, colocar sprite na faixa off-screen equivalente a `X = -128` pode causar desaparecimento ou mascaramento de outros sprites.
- Por padrao, trate essa faixa como proibida.
- So liberar se o exploit for deliberado e documentado.

## Alertas classicos

- alpha blending real nao existe
- terceira camada de background nao existe
- DMA fora de VBlank exige justificativa forte
- compressao `.res` reduz custo de ROM e pode alterar tempo de load, mas nao reduz o custo final do tile descompactado quando residente em VRAM
- shadow/highlight tem regras de prioridade e custo de paleta
- imagem inteira convertida em tilemap quase sempre explode tiles unicos
- **paleta PNG inflada (>16 entradas PLTE) causa corrupcao silenciosa**: o rescomp usa indices brutos da paleta para gerar tiles; dois pixeis com a mesma cor RGB mas indices diferentes no PNG produzem tiles "unicos" falsos, inflando o tileset sem motivo visual. Verificar SEMPRE byte 24 (bitDepth<=4) e contagem de entradas PLTE (<=16) antes de qualquer trabalho de recursos. Uma imagem com 11 cores unicas mas 256 entradas de paleta e um problema critico
- **VRAM overflow por excesso de tiles unicos e SILENCIOSO**: a ROM compila sem erros mas os tiles invadem sprite VRAM, fonte e nametables do VDP, causando corrupcao total. NUNCA assumir "2048 tiles disponiveis". O budget real depende de `maps_addr` (endereco mais baixo de tabela VDP no VRAM). Para SGDK 2.11 com planos 64x32 OU 32x32: `maps_addr = 0xC000`, `TILE_MAX_NUM = 1536`, user tiles = 1536 - 16(sys) - 96(font) - SPR_initEx. **Calcular ANTES de buildar: BG_B_tiles + BG_A_tiles <= TILE_MAX_NUM - 16 - 96 - SPR_initEx.**
- **maps_addr = 0xC000 para AMBOS 32x32 e 64x32 no SGDK 2.11** — mudar `VDP_setPlaneSize()` NAO aumenta tile space porque BGB nametable fica em 0xC000 em ambos os casos
- **Arte com >80% tiles unicos e incompativel com cenarios largos** — panoramas detalhadas (como cityscapes) facilmente geram 2.8 tiles unicos por pixel-coluna. Para cenas > 320px, exigir ratio de tiles unicos <= 60% OU streaming de segmentos
- `SPR_init()` automatico nao e neutro para cenas pesadas de background
- `VDP_setPlaneSize(..)` costuma ser a primeira otimização estrutural legitima antes de alias ou reciclagem de tabela, mas NAO aumenta tile space no SGDK 2.11
- `window alias` e `hscroll slack reuse` podem funcionar, mas quebram facil se a cena ou o modo de scroll mudarem
- `SAT reuse` so faz sentido em telas especiais; em gameplay normal tende a conflitar com o sprite engine
- `sprite graft` sem medicao de scanline budget vira flicker, nao profundidade
- sprite decorativo demais para "animar fundo" costuma ser pior do que tile animation via DMA
- efeito raster ou palette split sem BlastEm nao deve subir de status
- stage acima do teto do plano pede streaming de tilemap guiado pela camera
- frame critico de luta precisa ser orcado como conjunto; nao por personagem isolado

## Escada forense obrigatoria

1. header PNG / PLTE
2. `rescomp` raw tiles
3. separar `rom_asset_cost`, `vram_resident_set`, `load_time_dma_cost`, `per_frame_dma_cost`, `active_animation_window`, `scene_local_scope` e `scanline_sprite_pressure`
4. formula real de VRAM
5. decisao de arquitetura
6. BlastEm

Se a analise saltar esta ordem, o parecer ainda nao esta maduro.

