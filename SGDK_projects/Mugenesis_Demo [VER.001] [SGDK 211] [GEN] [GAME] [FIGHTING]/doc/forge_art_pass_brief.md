# Passe de arte — `img_logo_engine_v2` (o FORGE)

Asset: `res/branding/logo_engine_224x64.png`, `PAL1` (`BRAND_V2_PAL_METAL`), plano A em
`LOGO_X0=48, LOGO_Y0=64`. E o logo que os 56 estilhacos montam em F203 — o momento de
assinatura da cena inteira.

O runtime esta correto. A montagem funciona, o pouso funciona, a varredura especular funciona.
**O que falta e separacao de luma contra o fundo, e nao codigo.**

---

## O que foi medido

`audit_luma_floor.py`, piso 34 (um degrau de componente do Mega Drive):

| | |
|---|---|
| cobertura de tinta | 61% do canvas (8777 de 14336 px) |
| luma media do fundo na regiao | **49,2** |
| **massa de tinta perdida sob o piso** | **46%** |
| massa com realce legivel | 31% |

Por indice:

| idx | rgb | luma | contraste | massa | |
|---|---|---|---|---|---|
| 2 | (0,34,68) | 27,7 | **−21,5** | **24,9%** | sob o piso |
| 4 | (34,68,102) | 61,7 | **+12,5** | **18,8%** | sob o piso |
| 3 | (0,34,102) | 31,6 | **−17,6** | **2,3%** | sob o piso |
| 9 | (136,102,0) | 100,5 | +51,4 | 23,3% | ouro, le bem |
| 15 | (0,0,0) | 0,0 | −49,2 | 20,1% | contorno, le bem |
| 13 | (204,170,170) | 180,2 | +131,0 | 4,5% | |
| 1, 5, 6, 10, 11 | — | — | — | 5,9% no total | |

Por faixa horizontal — **a perda e toda na metade de cima**:

| faixa y | tinta | sob o piso |
|---|---|---|
| 0..8 | 947 | **67%** |
| 8..16 | 1476 | **80%** |
| 16..24 | 1029 | **61%** |
| 24..32 | 1281 | **71%** |
| 32..40 | 1160 | 26% |
| 40..48 | 1048 | 8% |
| 48..56 | 1051 | 11% |
| 56..64 | 785 | 24% |

A metade de baixo, onde mora o ouro, le. A metade de cima, onde mora o aco, dissolve.

---

## A causa raiz nao e sutil: e a mesma tinta

Comparando as paletas dos PNGs:

| | logo_engine | forge_bg_b | forge_bg_a_props | |
|---|---|---|---|---|
| idx 4 | (34,68,102) | (34,68,102) | (34,68,102) | **identico** |
| idx 5 | (68,102,136) | (68,102,136) | (68,102,136) | **identico** |
| idx 2 | (0,34,68) | — | — | igual ao idx 3 dos fundos |

**43,7% do FORGE esta pintado com as cores exatas do cenario.** Nao e contraste baixo por
escolha estetica: e a mesma cor. Um objeto pintado com a tinta do fundo desaparece no fundo, e o
gate so colocou numero numa coisa que a rampa ja garantia.

---

## E o conserto e livre — a restricao que causou isso nao existe

```c
#define BRAND_V2_PAL_FORGE    PAL0  /* ambiente */
#define BRAND_V2_PAL_METAL    PAL1  /* logo engine */
```

O FORGE e **dono do PAL1 inteiro**. O cenario vive no PAL0. Mexer em `PAL1[2]`, `[3]`, `[4]`
**nao toca no fundo**, nao afeta nenhum outro asset e nao custa VRAM.

Havia motivo para reaproveitar a rampa do cenario se a paleta fosse compartilhada. Ela nao e.

E tem mais folga na mesa. O logo declara 15 cores e **nunca pinta quatro delas**:

| idx | rgb | luma | uso |
|---|---|---|---|
| 7 | (136,170,204) | 163,7 | **0%** |
| 8 | (170,204,238) | 197,7 | **0%** |
| 12 | (238,204,34) | 194,8 | **0%** |
| 14 | (204,204,204) | 204,0 | **0%** |

O topo claro da rampa de aco **ja esta declarado e nunca foi pintado**. O idx 6 (luma 129,7)
aparece em 0,3%. A peca tem para onde subir e ficou embaixo.

---

## Parte da culpa e da direcao, de novo

`branding_v2_art_direction.md` pediu o FORGE como aco frio contra a forja quente, e o contraste
de **matiz** foi entregue: azul contra laranja funciona. O que a direcao nao disse foi que
matiz nao substitui luma — dois tons podem ser opostos na roda de cor e ter o mesmo brilho, e o
Mega Drive nao ajuda a separar o que voce nao separou.

Mesmo erro do PRESENTS, eixo diferente: la foi "leve" sem piso, aqui foi "frio" sem piso.
A partir de agora todo adjetivo de direcao carrega numero — e a secao 36 do `SGDK_GLOBAL.md`.

---

## O que precisa ser verdade quando voltar

Nao vou desenhar a peca. O que o gate vai medir:

1. **Massa de tinta sob o piso ≤ 33%.** Hoje 46%. Piso = 34 de luma contra fundo em 49,2.
2. **Massa de realce ≥ 20%** (contraste positivo acima do piso). Hoje 31%, ja passa — nao
   regrida.
3. **Papel de indice preservado.** `PAL1[13,14]` continua sendo folga de highlight: e por ali
   que a varredura especular passa, e o runtime depende disso. Valor hex e semente sua; papel do
   indice e contrato.
4. **Nenhum indice do FORGE identico a um indice do fundo** na familia de aco.

O caminho mais curto e afastar `PAL1[2,3,4]` do 49,2 do fundo e usar o topo da rampa que ja esta
declarado — mas a decisao e sua. Se voce achar que a leitura melhor sai por outro caminho e o
resultado passar nos quatro pontos acima, **a direcao e que estava errada e eu corrijo o brief.**

## Como verificar antes de entregar

```bash
python3 tools/sgdk_wrapper/audit_luma_floor.py --root tools/sgdk_wrapper/modelo
```

Alvo: `logo_engine_224x64.png` sem `finding`. Os outros tres assets ja passam
(`presents_text` 0% perdida, `logo_author` 0%, `logo_project` 0%) — **nao regrida nenhum deles.**

Restricoes de sempre: PNG indexado, index 0 transparente, 15 cores visiveis, componentes so em
degraus de 34 (0,34,68,102,136,170,204,238 — nibble par, o resto nao existe no CRAM de 9 bits),
canvas 224x64, alinhado a 8 px.
