# 06 - VDP Limit Extrapolation Techniques

## Objetivo

Registrar tecnicas que parecem "extrapolar" o VDP do Mega Drive, separando:

- tecnica canônica e segura
- tecnica avancada com trade-off
- quirk ou exploit que so pode entrar de forma opt-in

## Leitura resumida

### 1. Reparticao de VRAM

Fontes:

- `How to Manage VRAM Limits for the Sega Genesis & Mega Drive`
- `SPR_initEx(u16 vramSize)` em `sdk/sgdk-2.11/inc/sprite_eng.h`

Licao canônica:

- o limite util nao e o numero bruto de tiles da VRAM
- backgrounds grandes e imagens inteiras convertidas explodem tiles unicos
- o sprite engine automatico pode reservar VRAM demais para sprites quando o fundo e o problema principal

Regra:

- medir tiles unicos reais
- medir teto util antes da area de mapas do VDP
- ajustar `SPR_initEx` apenas quando a cena pedir isso

### 1.1 Plane size tuning

Fontes:

- `VDP_setPlaneSize(..)` em `sdk/sgdk-2.11/inc/vdp.h`
- organizacao de `planeWidth`, `planeHeight` e `regValues[0x10]` em `sdk/sgdk-2.11/src/vdp.c`

Licao canônica:

- reduzir o tamanho real de BG_A/BG_B e a primeira otimização estrutural legitima quando a fase nao usa toda a extensao do mapa
- antes de reciclar tabela, vale perguntar se o mapa foi simplesmente superdimensionado

Regra:

- categoria: `canonica_segura`
- usar antes de `window alias` ou `hscroll slack reuse`
- registrar no caso quando a fase adota mapa menor para recuperar espaco

### 2. Paleta 3+1

Fonte:

- `How to Manage VRAM Limits for the Sega Genesis & Mega Drive`

Licao canônica:

- reduzir um background de 4 para 3 paletas pode ser a decisao certa quando um foreground ou logo precisa de paleta propria

### 2.1 Curadoria manual de paleta

Fontes:

- `16-bit Ray Tracing - Castlevania: Symphony of the Night for Sega MegaDrive & Genesis - Dev Diary 9`

Licao canônica:

- a melhor traducao para Mega Drive raramente sai de uma reducao cega para 16 cores
- o salto real vem de decidir manualmente quais rampas sobrevivem, quais tons fundem e quais cores saem

Regra:

- categoria: `canonica_segura`
- `basic` pode usar quantizacao cega como controle
- `elite` deve preferir curadoria semantica de paleta quando material, roster compartilhado ou foco cromatico forem decisivos

### 3. Sprite graft para profundidade

Fonte:

- `Horse Level, Game Design & VDP Bugs`

Licao canônica:

- partes do meio-termo visual podem virar sprites para simular profundidade adicional e parallax extra
- isso nao cria uma terceira layer real; apenas desloca custo para o sistema de sprites

Regra:

- usar somente com validacao de scanline budget, total de sprites e risco de flicker

### 4. Quirk de sprite em X = -128

Fonte:

- `Horse Level, Game Design & VDP Bugs`

Licao canônica:

- existe um comportamento de hardware que pode mascarar ou fazer desaparecer outros sprites quando um sprite entra nessa faixa
- isso pode ser explorado, mas e uma tecnica de risco

Regra:

- default: proibido
- liberacao: apenas com intencao explicita, benchmark dedicado e memoria operacional atualizada

### 5. Window alias

Fontes:

- `VDP_setWindowAddress(..)` em `sdk/sgdk-2.11/inc/vdp.h`
- layout padrao do SGDK em `sdk/sgdk-2.11/src/vdp.c`

Licao canônica:

- a tabela da Window e configuravel; se a Window nao participa da cena, seu endereco pode virar candidato a alias
- isso nao significa que a tecnica seja segura por padrao no SGDK

Regra:

- categoria: `avancada_com_tradeoff`
- so usar quando a Window estiver realmente fora da cena
- bloquear se existir HUD, console, debug text ou qualquer escrita em `WINDOW`

### 6. H-Scroll slack reuse

Fontes:

- `VDP_setScrollingMode(..)` e `HSCROLL_PLANE` em `sdk/sgdk-2.11/inc/vdp.h`
- acessos da tabela em `sdk/sgdk-2.11/src/vdp_bg.c`

Licao canônica:

- em `HSCROLL_PLANE`, o uso da tabela de H-Scroll e menor do que em scroll por tile ou por linha
- o restante do bloco pode parecer reaproveitavel, mas essa tecnica e sensivel ao modo de scroll da cena

Regra:

- categoria: `avancada_com_tradeoff`
- so liberar quando a cena estiver travada em `HSCROLL_PLANE`
- invalidar automaticamente se a fase puder migrar para `HSCROLL_TILE` ou `HSCROLL_LINE`

### 6.1 Shadow/Highlight ambiental

Fontes:

- `Animated background tiles & more! - Castlevania: SotN for Sega Mega Drive & Genesis - Dev Diary 18`

Licao canônica:

- Shadow/Highlight em background pode ser melhor do que overlay de sprite para beam, fog ou glow que precisam tocar cenario e personagem juntos
- isso cobra composicao mais rigida, mascara de tile e auditoria de slot da paleta do sprite

Regra:

- categoria: `avancada_com_tradeoff`
- exigir `palette_slot_audit`
- combinar com line scroll so quando o efeito realmente precisar fugir do 8x8 duro

### 6.2 Verdade de raster/paleta

Fontes:

- `Animated background tiles & more! - Castlevania: SotN for Sega Mega Drive & Genesis - Dev Diary 18`

Licao canônica:

- efeito raster ou palette split nao vira verdade por "parecer bom" em editor ou video
- BlastEm e gate minimo; hardware real e desejavel para tecnicas que dependem fortemente do timing

Regra:

- categoria: `canonica_segura`
- nao canonizar tecnica mid-frame sem prova em BlastEm

### 6.3 Background animado por VRAM

Fontes:

- `Animated background tiles & more! - Castlevania: SotN for Sega Mega Drive & Genesis - Dev Diary 18`

Licao canônica:

- decor animado muitas vezes deve sair do budget de sprite e entrar como troca de tiles em VRAM

Regra:

- categoria: `canonica_segura`
- medir DMA por VBlank antes de aprovar

### 6.4 Streaming de stage largo

Fontes:

- `REAL BOUT FATAL FURY SPECIAL MEGA DRIVE | ROLAGEM DE CENÁRIO E MAGIAS`

Licao canônica:

- cenario acima do teto pratico do plano precisa de streaming guiado pela camera

Regra:

- categoria: `canonica_segura`
- usar para stages largos, especialmente de luta

### 6.5 Worst-frame budget

Fontes:

- `REAL BOUT FATAL FURY SPECIAL MEGA DRIVE | ROLAGEM DE CENÁRIO E MAGIAS`
- `REAL BOUT FATAL FURY SPECIAL MEGA DRIVE | Burn Knuckle | Crack Shoot | Power Geyser | Rising tackle`

Licao canônica:

- port 1:1 de lutador/FX de Neo Geo para Mega Drive costuma explodir no pior quadro, nao no golpe isolado

Regra:

- categoria: `canonica_segura`
- medir sempre o quadro critico com dois lutadores, HUD e FX grandes

### 6.6 Borrowed FX ramp e alternancia temporal

Fontes:

- `REAL BOUT FATAL FURY SPECIAL MEGA DRIVE | Burn Knuckle | Crack Shoot | Power Geyser | Rising tackle`

Licao canônica:

- FX grande pode emprestar rampa do personagem ou alternar metades por frame para caber

Regra:

- categoria: `avancada_com_tradeoff`
- liberar so como fallback opt-in de budget

### 7. SAT reuse

Fontes:

- `SAT_MAX_SIZE` e cache da sprite list em `sdk/sgdk-2.11/inc/vdp_spr.h`
- sprite engine em `sdk/sgdk-2.11/inc/sprite_eng.h`

Licao canônica:

- menus, title screens e cutscenes com uso minimo de sprites podem permitir reutilizacao temporaria do espaco da SAT
- gameplay normal com sprite engine automatico nao deve assumir isso

Regra:

- categoria: `opt_in_de_cena_especial`
- restringir a menu, cutscene, title screen ou benchmark dedicado
- nunca vender isso como otimizacao padrao de gameplay

## Aplicacao no workspace

Estas tecnicas afetam diretamente:

- `megadrive-vdp-budget-analyst`
- `art-translation-to-vdp`
- `visual-excellence-standards`
- `BENCHMARK_VISUAL_LAB`

## Taxonomia final

- `canonica_segura`
  - `plane size tuning`
  - `SPR_initEx(u16 vramSize)` quando a medicao pedir
  - `3+1 palette split`
  - curadoria manual semantica de paleta
  - background animado por VRAM
  - gate de BlastEm para raster e palette split
  - streaming de tilemap para stage largo
  - worst-frame budget para luta e FX massivo
  - `compare_flat`
- `avancada_com_tradeoff`
  - `window alias`
  - `hscroll slack reuse`
  - `sprite graft`
  - Shadow/Highlight ambiental por background
  - `borrowed_fx_ramp`
  - alternancia temporal de FX gigante
- `opt_in_de_cena_especial`
  - `SAT reuse`
  - `X = -128` e quirks equivalentes

## Fontes

- https://www.youtube.com/watch?v=TQdLp0zOWXs
- https://www.youtube.com/watch?v=NqabGMow0VY
