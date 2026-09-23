# Diagnostico: Kirby oco / transparente / amarelo

**Data:** 2026-08-08
**Status:** causa raiz **confirmada por forense de indices**
**Relaciona:** L-009, L-012; tese do operador sobre keying VDP

---

## 1. O que o hardware faz (Mega Drive VDP) — correto

No VDP, para **sprites** e tiles de plano, o **indice 0 de cada linha de paleta
(CRAM)** e o pixel **transparente**. O hardware nao desenha esse pixel; o que
aparece e o plano atras (ou a cor de backdrop se ambos forem transparentes).

Isso e independente de qual RGB esta gravado em CRAM[linha][0]. O RGB de
indice 0 so importa para a cor de fundo (backdrop) quando usado como tal; para
sprites, indice 0 = furo.

| Linha | Uso no projeto (doc/PALETTES.md) |
|---|---|
| PAL0 | ceu / montanha / colina |
| PAL1 | terreno |
| **PAL2** | **Kirby + inimigos** (`TILE_ATTR(PAL2, ...)`) |
| PAL3 | ability FX / S-H operators |

Runtime correto em `scene_stage.c`:

```c
PAL_setPalette(PAL2, spr_ph_kirby.palette->data, DMA);
SPR_addSprite(&spr_ph_kirby, ..., TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
```

**Nao** e (no nosso caso medido) ponteiro OAM na paleta errada. O sprite aponta
para PAL2. O furo e de **indice de pixel = 0 no tileset**, nao de linha de
paleta trocada.

---

## 2. Evidencia forense — o corpo virou Index 0

### Placeholder (funciona — rosa solido)

| Frame | idx0 no centro 12×12 | indices no centro |
|---|---|---|
| 0 | **0.0%** | 1, 2, 9 (rosa + olho) |
| 1–4 | **0.0%** | 1, 2, 9 |

Corpo = indices **1–4** (rosa). Indice 0 so no padding ao redor (~55% do
cell 32×32, normal).

### AI R2 / R2b (falha — oco / “amarelo”)

| Frame | idx0 no centro 12×12 | indices no centro |
|---|---|---|
| 0 | **80.6%** | 0, 2, 6, 9 |
| 2 | **86.8%** | 0, 6, 9 |
| 4 | **82.6%** | 0, 2, 3, 4, 6, 9 |

O **centro do personagem e ~80% indice 0**. Sobram contorno (6) e olhos (9).
No VDP isso e exatamente: silhueta + olhos, **interior transparente**, fundo
(H-int creme/amarelo da banda do ceu) visivel “por dentro”.

Isso **nao** e bug de emulador. E o VDP fazendo o que o tileset pediu.

### Preview PNG enganoso

O `kirby_sheet_r2b_x4.png` **parece** rosa no preview porque o PIL desenha
RGB da paleta (indices 1–4 quando existem). Mas nos frames idle o centro
continua majoritariamente 0. O olho humano ve manchas rosa na borda e assume
preenchimento; a medicao de indices desmente.

---

## 3. Mecanismo no nosso pipeline (bate com a tese)

### 3.1 Keying residual agressivo

A funcao `is_key` usada na conversao AI:

```
r>170 && g<150 && b>130 && |r-b|<130 && g+40 < r
```

Teste pontual:

| Cor | RGB | `is_key`? |
|---|---|---|
| Magenta de fundo | (255, 0, 255) | True (ok) |
| **Rosa base do corpo** | **(255, 146, 182)** | **True (BUG)** |
| Rosa claro | (255, 182, 219) | False |
| Contorno | (109, 36, 73) | False |

Na regiao de corpo da sheet AI bruta: **`is_key` acerta 72% dos pixels**.

Consequencia:

1. Pixels de pele rosa → classificados como “fundo”
2. Gravados como **indice 0**
3. VDP trata como transparente
4. Cenario / gradiente H-int (cremes da banda media) preenchem o furo →
   **Kirby “amarelo/transparente”**

Isso e o item **“Chave de Cor Mista”** da tese do operador, com um detalhe:
nao foi o rescomp fundindo dois RGBs iguais na paleta (nenhum idx 1–15 colide
com (255,0,255) nas sheets medidas). Foi o **classificador de transparencia**
que tratou rosa de corpo como se fosse a chave.

### 3.2 L-009 (caixa solida magenta)

Modo oposto: quantizacao sem idx0 suficiente (frames 4–5 com **0%**
transparente). Magenta de key virou cor **opaca** (idx 1 = (219,36,182)).
Hardware desenhou retangulo. Mesma familia de bug: **key mal isolada**.

### 3.3 Kirby amarelo por PAL errada?

Possivel em geral (OAM lendo PAL1/itens). **Nao e o que medimos aqui:**

- `TILE_ATTR(PAL2, ...)` consistente
- `PAL_setPalette(PAL2, spr_ph_kirby.palette->data, DMA)` na stage
- Captura “amarela” bate com **creme do H-int** (RGB ~255,255,146), nao com
  paleta de moeda/estrela

Amarelo observado = **fundo da cena atraves de pixels idx0**, nao swap de
sub-paleta.

---

## 4. Solucao (contrato de arte + pipeline)

### Regras duras

1. **Indice 0 = so transparencia.** Zero pixel de personagem em 0.
2. **Corpo em 1–15.** Rosa em 1–5, contorno 6, pe 7–8, olho 9, brilho 10.
3. **Chave de sheet distinta do personagem.** Preferir:
   - verde puro `(0, 255, 0)` se o personagem nao usa verde, **ou**
   - magenta `(255, 0, 255)` **somente** com match **exato** pos-snap RGB333,
     nunca com detector largo de “rosa choque”.
4. **Gate automatico por frame:** centro 12×12 com `idx0 < 5%` e
   `opaque > 35%`. Falha = recusa install na ROM.
5. **Nao confiar em preview visual** sem dump de indices.

### Procedimento de conversao (ordem)

1. Isolar personagem (flood a partir das bordas **somente** em cor de key
   exata, nao em rosa de pele).
2. Preencher buracos internos do silhueta (morph fill) **antes** de mapear.
3. Mapear corpo → indices 1–5 por luminancia na rampa PAL2.
4. Olhos/pes/contorno por regras geometricas, nunca por key.
5. Validar gate §4.
6. So entao copiar para `res/sprites/ph_kirby.png` e rebuild.

---

## 5. Veredito

| Hipotese do operador | Status no nosso projeto |
|---|---|
| Index 0 = transparencia de hardware | **Confirmado** (VDP) |
| Corpo mapeado para a chave → oco | **Confirmado** (centro 80% idx0) |
| Key mista fundo/personagem | **Confirmado** via `is_key` engolindo rosa base |
| Amarelo = paleta OAM errada | **Nao no nosso caso**; amarelo = H-int por tras do furo |
| Solucao: isolar key + corpo em 1–15 | **Adotada** |

Proximos passos de engenharia: reescrever conversor com key exata + gate de
centro; so entao reinstalar na ROM.
