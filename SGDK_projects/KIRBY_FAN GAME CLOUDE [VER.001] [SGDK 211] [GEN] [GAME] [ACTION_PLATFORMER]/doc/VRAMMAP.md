# VRAMMAP.md — Mapa dos 64 KB

> **Dono unico:** `systems/vram_budget.c`. Nenhum outro sistema aloca indice de
> tile. Ver [ARCHITECTURE.md](ARCHITECTURE.md) §6.1.
> **Status:** `documentado`. Enderecos de tabela ja `[VERIFICADO]` em runtime;
> alocacao por cena e `[NAO MEDIDO]` ate existir arte convertida.

---

## 1. O mapa completo — zero bytes nao contabilizados

`[VERIFICADO]` Enderecos default do SGDK 2.11 em `src/vdp.c:23-27`, plano 64x32,
H40. Confirmados em runtime pelo probe VLAB: `bg_a = 0xE000`, todas as tabelas
disjuntas, gate `vram_tables_disjoint` = pass.

| Faixa | Bytes | Conteudo | Tiles |
|---|---|---|---|
| `0x0000-0x01FF` | 512 | tiles de sistema do SGDK | 0-15 |
| `0x0200-0x7F7F` | **32128** | **tiles de fundo — nosso orcamento** | **16-1019** |
| `0x7F80-0xB3FF` | 13440 | regiao de sprite (`spriteVramSize`) | 1020-1439 |
| `0xB400-0xBFFF` | 3072 | fonte do SGDK (`FONT_LEN` 96) | 1440-1535 |
| `0xC000-0xCFFF` | 4096 | nametable BG_B | — |
| `0xD000-0xDFFF` | 4096 | nametable Window | — |
| `0xE000-0xEFFF` | 4096 | nametable BG_A | — |
| `0xF000-0xF3FF` | 1024 | tabela de HScroll (896 usados, 128 de sobra) | — |
| `0xF400-0xF7FF` | 1024 | sprite list (640 usados, 384 de sobra) | — |
| `0xF800-0xFFFF` | **2048** | **LIVRE** | — |
| **Total** | **65536** | | **1536** |

Soma conferida: 512 + 32128 + 13440 + 3072 + 4096 + 4096 + 4096 + 1024 + 1024 +
2048 = **65536**. Zero byte perdido.

### 1.0 Orcamento declarado — linha lida pelo gate

> **Total de tiles de fundo disponiveis: 1004 tiles**

Essa linha e o contrato que `tools/harness/gates.py` le no gate
`vram_tile_budget` (`_parse_vram_map`). Nao reformule sem rodar o gate depois:
o parser e por expressao regular e uma reescrita de prosa pode calar o gate sem
avisar. Se o numero mudar, mude aqui **e** confirme que o gate ainda casa.

### 1.1 Os 2 KB livres em `0xF800`

`[DECIDIDO]` Ficam **reservados e vazios**. Nao entram no orcamento de tile
porque nao sao contiguos com a area de tile — `TILE_SPACE` termina em `0xC000`.
Uso possivel no futuro: segundo buffer de HScroll para double-buffering da tabela
de parallax, se a medicao mostrar tearing. Ate lá, deliberadamente vazios.

### 1.2 Derivacao dos numeros `[VERIFICADO]`

De `inc/vdp.h:224-260` e `src/sprite_eng.c:157`:

```
VDP_MAPS_START = menor endereco de tabela = 0xC000
TILE_SPACE     = 0xC000 = 49152 bytes  ->  TILE_MAX_NUM = 1536 tiles
TILE_SYSTEM_INDEX 0, TILE_SYSTEM_LENGTH 16
FONT_LEN 96  ->  TILE_FONT_INDEX = 1536 - 96 = 1440
SPR_init() default spriteVramSize = 420  ->  regiao em 1020..1439
orcamento de fundo = 1440 - 420 - 16 = 1004 tiles
```

---

## 2. Tamanho de plano — a decisao e o que ela custa

`[DECIDIDO]` **64 x 32 tiles (512 x 256 px) para BG_A e BG_B.**

| Opcao | Bytes/plano | A+B+Window | Tiles restantes p/ fundo |
|---|---|---|---|
| **64x32** | 4096 | 12288 | **1004** |
| 64x64 | 8192 | 20480 | 748 |
| 128x32 | 8192 | 20480 | 748 |

Trocar para 64x64 custa **256 tiles**, ou seja **25% do orcamento de fundo**.

**Por que 64x32 mesmo com o plano vertical de 256 px sendo apertado** (tela tem
224 px, sobram 32 px de folga): rolagem vertical exige refill de linha, e refill
e **CPU**, que e o recurso que temos sobrando — a medicao do template mostrou
`vblank_idle = 171` scanlines/frame. Tile e o recurso escasso. Trocar CPU
abundante por tile escasso e a direcao certa da troca.

Horizontalmente, 512 px de plano contra 320 px de tela deixam 192 px = 24 tiles
de margem para refill de coluna. Confortavel.

**Consequencia que o level design precisa respeitar:** sala mais alta que 256 px
exige refill de linha durante a rolagem. Isso e permitido, mas precisa constar
em [16-ldd.md](16-ldd.md) por sala.

---

## 3. Orcamento de DMA por frame

`[VERIFICADO]` De `sdk/sgdk-2.11/inc/dma.h:172,184`, documentacao do proprio SGDK:

> "VBlank period allows to transfer up to **7.2 KB on NTSC** system and **15 KB
> on PAL** system."

Esse e o teto duro. AGENTS.md: DMA **so** no VBlank, sem excecao.

### 3.1 Alocacao NTSC, 7372 bytes `[DECIDIDO]`

| Consumidor | Bytes/frame | % | Nota |
|---|---|---|---|
| Tabela de HScroll | 896 | 12.2% | **obrigatorio todo frame** — e o parallax |
| Sprite list (`SPR_update`) | 640 | 8.7% | 80 sprites x 8 B, pior caso |
| Paleta | 40 | 0.5% | troca submersa (32 B) + ciclo (8 B) |
| Tiles animados | 512 | 6.9% | 16 tiles/frame: cachoeira, agua |
| Refill de nametable | 64 | 0.9% | 1 coluna de 32 entradas x 2 B |
| Streaming de tile | 1024 | 13.9% | 32 tiles novos/frame |
| **Subtotal** | **3176** | **43.1%** | |
| **Folga** | **4196** | **56.9%** | |

**O orcamento fecha com folga de quase 57%.** Isso e projeto, nao medicao:
`[NAO MEDIDO]` ate existir cena real. Mas a folga e grande o bastante para
absorver erro de estimativa sem replanejar.

### 3.2 Regra de prioridade quando o orcamento apertar

Ordem de corte, em ordem inversa de importancia:

1. **streaming de tile** — reduzir para 16 tiles/frame, prefetch mais cedo
2. **tiles animados** — cachoeira a cada 8 frames em vez de 6
3. **refill de nametable** — espalhar por 2 frames

**Nunca cortar:** tabela de HScroll e sprite list. Cortar HScroll mata o
parallax, que e a identidade visual do projeto. Cortar sprite list faz sprite
desaparecer.

### 3.3 PAL

Com 15 KB, PAL tem o dobro do orcamento. `[DECIDIDO]` **Nao vamos usar essa
folga.** O jogo e autorado para caber em NTSC; PAL roda o mesmo conteudo com
folga maior. Usar a folga do PAL criaria conteudo que nao roda em NTSC.

---

## 4. Alocacao de tile por cena

`[NAO MEDIDO]` — todos os numeros abaixo sao **orcamento alvo**, nao medicao.
A medicao so existe depois da conversao de arte real. Orcamento: **1004 tiles**.

### 4.1 Tela de titulo

| Bloco | Tiles |
|---|---|
| Ceu noturno + campo de estrelas | 24 |
| Silhueta de colina + arvore | 60 |
| Logotipo | 120 |
| Texto de menu (fonte propria) | 40 |
| **Total** | **244** de 1004 |

Folga enorme. A tela de titulo e a cena mais barata do jogo e por isso e onde o
gradiente de ceu de 16-20 faixas pode ser mais ambicioso.

### 4.2 Fase 1 — Vegetable Valley

| Bloco | Paleta | Tiles |
|---|---|---|
| Ceu (faixas + nuvens) | PAL0 | 40 |
| Montanhas distantes | PAL0 | 80 |
| Colinas + arvores | PAL0 | 160 |
| Topo de grama + quinas | PAL1 | 48 |
| Corpo de terra (3 variacoes) | PAL1 | 40 |
| Encostas 45 graus | PAL1 | 32 |
| Decoracao (pedra, flor, cogumelo) | PAL1 | 40 |
| Cachoeira (3 quadros de ciclo) | PAL1 | 24 |
| Bloco destrutivel | PAL1 | 8 |
| Primeiro plano (camada 5) | PAL1 | 40 |
| HUD (Window) | PAL2 | 60 |
| **Total residente** | | **572** de 1004 |
| **Livre para streaming por sala** | | **432** |

Deriva direto do `r1-05` aprovado, que entregou exatamente esse vocabulario.

### 4.3 Fase 2 — Lago

| Bloco | Tiles |
|---|---|
| Ceu + nuvens | 40 |
| Montanhas distantes | 64 |
| Vegetacao de margem | 80 |
| Terreno + pedras arredondadas | 120 |
| Superficie de agua (ciclo) | 32 |
| Cenario submerso (pedras, algas) | 140 |
| Bolhas + feixes de luz | 24 |
| HUD | 60 |
| **Total residente** | **560** de 1004 |

A fase 2 e a mais caterizada em tile porque o cenario submerso e um segundo
vocabulario completo. `r1-06` avisou disso: "pedras e vegetacao submersas ainda
tem textura em excesso". **Risco real de estouro aqui** — mitigacao em §6.

### 4.4 Fase 3 — Caverna

| Bloco | Tiles |
|---|---|
| Fundo de caverna (padrao repetivel) | 48 |
| Estalactites / formacoes | 80 |
| Terreno de rocha | 120 |
| Cristal / neon (ciclo) | 32 |
| Plataformas moveis | 40 |
| HUD | 60 |
| **Total residente** | **380** de 1004 |

A mais barata das tres fases. Caverna repete padrao com agressividade, e por isso
e onde o holofote com Shadow/Highlight pode gastar mais.

### 4.5 Arena do boss — Whispy Woods

| Bloco | Paleta | Tiles |
|---|---|---|
| Tronco (BG_A, nao sprite) | PAL3 | 120 |
| Copa de folhagem (padrao repetivel) | PAL3 | 64 |
| Chao da arena | PAL1 | 48 |
| Fundo (ceu + arvores) | PAL0 | 100 |
| HUD + barra de vida do boss | PAL2 | 72 |
| **Total residente** | | **404** de 1004 |

Os galhos, o rosto, a maca e a rajada sao **sprite**, nao tile — vem do orcamento
de 420 tiles da regiao de sprite, nao daqui. Cabe: 58 sprites de 80 no orcamento
de ARCHITECTURE.md §5.1.

---

## 5. Streaming de tile por sala

`[DECIDIDO]` Fundo de fase = **tiles residentes** (sempre em VRAM, §4) +
**tiles de sala** (carregados na transicao).

- residente: vocabulario de terreno, ceu, HUD. Nunca sai.
- de sala: decoracao especifica, gimmick, inimigo exclusivo. Troca na transicao.

Refill de coluna durante rolagem horizontal:

```
BG_A e 64x32. Rolando, cruza-se uma coluna a cada 8 px de scroll.
A 2 px/frame -> 1 coluna a cada 4 frames.
Custo por coluna: 32 entradas x 2 B = 64 bytes de nametable.
Se os tiles daquela coluna forem novos: + 28 tiles x 32 B = 896 bytes.
```

`[DECIDIDO]` **Tile novo nunca chega no frame em que e preciso.** Prefetch de 2
colunas de antecedencia, amortizado. Isso mantem o pico de DMA em 1024 bytes/frame
(§3.1) em vez de 896 num unico frame de borda.

---

## 6. Alavancas para recuperar VRAM

Ordem de custo/beneficio. Cada uma tem um preco declarado.

| # | Alavanca | Ganho | O que quebra |
|---|---|---|---|
| 1 | Recuperar a fonte do SGDK (`FONT_LEN` 96) | **+96 tiles** | `VDP_drawText` para de funcionar. Perde-se o HUD de debug e o overlay de diagnostico. **Fazer so no build de release.** |
| 2 | Reduzir `spriteVramSize` de 420 para 384 | +36 tiles | Menos tile simultaneo de sprite. Testar contra a cena do boss (58 sprites) antes. |
| 3 | Aumentar reuso de tile no fundo distante | +40 a 80 tiles | Fundo mais repetitivo. Aceitavel em camada 2, ruim em camada 4. |
| 4 | Padrao repetivel maior para caverna | +30 tiles | Menos variedade visual. |
| 5 | Aumentar `spriteVramSize` (alavanca inversa) | -N tiles de fundo | Necessario se o boss estourar a regiao de sprite. |

`[DECIDIDO]` **A alavanca 1 esta reservada para a fase 2**, que e a de maior
risco (§4.3). Se a fase 2 estourar, recuperar a fonte resolve 96 dos tiles antes
de tocar em arte.

**Nenhuma alavanca deve ser acionada por precaucao.** Acionar so contra medicao
de estouro real, e registrar no changelog.

---

## 7. Gates — contrato para `gates.py`

O probe VLAB ja exporta `VDP_getBGAAddress`, `BGBAddress`, `WindowAddress`,
`SpriteListAddress`, `HScrollTableAddress`, `PlaneWidth`, `PlaneHeight`. Isso
basta para V1-V4.

| # | Gate | Regra | Estado |
|---|---|---|---|
| V1 | Tabelas em faixa valida | cada tabela dentro de `0x0000-0xFFFF` e alinhada | **implementado** |
| V2 | Tabelas disjuntas | zero sobreposicao entre as 5 tabelas | **implementado** |
| V3 | Tabelas fora da area de tile | toda tabela `>= 0xC000` | **implementado** |
| V4 | Tamanho de plano | `PlaneWidth == 64 && PlaneHeight == 32` | **IMPLEMENTAR** — pega regressao de plano silenciosa |
| V5 | Orcamento de tile por cena | tiles declarados <= 1004 | **em `warn` — este doc desbloqueia** |
| V6 | Pico de DMA por frame | <= 7372 bytes NTSC | **IMPLEMENTAR** — exige contador no probe |

V5 estava em `warn` porque este arquivo nao existia. **Agora existe.** O gate
pode passar a ler a tabela de §4 e comparar com o uso real.

V6 e a dependencia mais importante que falta: **o probe nao conta bytes de DMA.**
Sem isso, o orcamento de §3 e planilha, nao medicao. Trabalho de probe.

---

## 8. Criterio de pronto do subsistema de VRAM

- [ ] V1-V4 passando em toda cena
- [ ] uso de tile medido por cena <= tabela de §4 — V5
- [ ] pico de DMA medido <= 7372 B/frame — V6, **exige instrumentar o probe**
- [ ] zero estouro de VRAM em 600 frames de playtest scriptado
- [ ] `[NAO MEDIDO]` custo real em scanlines de montar a tabela de HScroll
      (orcamento de ARCHITECTURE.md §3: <= 8 scanlines/frame)
- [ ] transicao de sala sem pico de DMA acima do teto

---

## 9. Changelog

| Data | Mudanca |
|---|---|
| 2026-07-29 | v1. Mapa de 64 KB byte-exato, soma conferida em 65536, zero byte nao contabilizado. Plano travado em 64x32 com justificativa de troca (CPU abundante por tile escasso). Orcamento de DMA `[VERIFICADO]` em 7.2 KB NTSC / 15 KB PAL via `dma.h:172`. Alocacao alvo de tile para 5 cenas. 5 alavancas de recuperacao com preco declarado. 6 gates especificados, 3 implementados; V5 desbloqueado por este arquivo. |
