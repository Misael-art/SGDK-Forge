# Estudo de referência — calibrar o teto na geração certa

**Data:** 2026-08-10 (v02)
**Fontes:** `49192_kirby.png` (Kirby's Adventure, NES), `52859_kirby.png` (Kirby Super
Star, SNES), `32130_kirby.png` (Nightmare in Dreamland, GBA) — já em disco no projeto
irmão GROK BUILD, catalogadas com `"ship_allowed": false`.

**Uso permitido:** `scale_density_timing_only`. A referência entrega **medida**. Não
entra em `res/`, não é traçada, não é fonte de geração. Um model sheet decalcado é
clone e reprova em `clone_risk_score` e na Trava 6 do `SGDK_GLOBAL`.

---

## 0. Correção da v01 — o erro que quase virou regra

A primeira versão deste estudo mediu **só o NES** e extraiu a regra *"corpo em 4 a 6
tons, nunca 9"*. O operador identificou o defeito antes que ela fosse canonizada:

> aquela não é economia elegante, é o **teto do NES** (3 cores + transparente)
> travestido de regra de arte. Canonizada, ensinaria o agente a mirar abaixo do
> hardware alvo e produzir gráficos fracos por regra.

Correto, e o dado confirma. **A regra foi retirada.** O achado sobre silhueta
sobrevive; o remédio que extraí dele não.

Lição de método: **referência de geração inferior serve para estudar leitura, nunca
para calibrar teto.** O Mega Drive tem 15 cores utilizáveis por paleta de sprite; o
NES tem 3. Medir o alvo contra o NES é escolher perder.

---

## 1. A medição que importa — tier de mesma geração

Célula única do sprite idle, fundo do sheet descontado:

| Fonte | Célula | **Tons de corpo** | Tier |
|---|---|---|---|
| NES Adventure | 24×24 | **5** | geração inferior — não é calibrador |
| **SNES Super Star** | **24×25** | **10** | **alvo** |
| P1 reprovado | 32×32 | 10 | — |
| Placeholder atual | 32×32 | 9 | — |

Rampa de pele medida no SNES, em pixels:

| RGB | Papel | px |
|---|---|---|
| `(248,160,232)` | degrau 1 — preenchimento sob a luz | **154** |
| `(240,112,224)` | degrau 2 — meio-tom | 64 |
| `(224,64,208)` | degrau 3 — sombra | 43 |
| `(192,16,176)` | degrau 4 — sombra profunda | 29 |
| `(112,0,88)` | degrau 5 — contato / oclusão | 25 |
| `(0,0,0)` | contorno | 79 |
| `(192,0,0)` / `(248,16,32)` | pé + brilho do pé | 14 / 4 |
| `(248,248,248)` | especular | 5 |

**Cinco degraus com queda monotônica de área.** Cada degrau ocupa menos que o anterior
— assinatura de rampa que descreve curvatura, não de paleta decorativa.

## 2. A conclusão que inverte as duas hipóteses anteriores

Já testei e descartei duas explicações para a reprovação do P1:

1. ~~"O corpo caiu no índice 0"~~ — falso. `sprite_solidity` aprova o P1 em 8/8 frames
   com `center_idx0 = 0,0%`.
2. ~~"Faltou economia tonal"~~ — falso, e invertido. O P1 tem **10 tons, exatamente o
   mesmo do SNES**.

O que resta, e que a comparação em `out/evidence/model_sheet_route/tier_comparison.png`
mostra diretamente:

> **Não é quantos tons. É se a rampa codifica uma direção de luz sobre uma esfera.**

| | SNES | P1 | Atual |
|---|---|---|---|
| Direção de luz identificável | **sim**, superior-esquerda | não | não |
| Rim highlight | sim | mancha pálida sem função | listra vertical sem função |
| Terminador acompanha curvatura | sim | não | não |
| Sombra de contato na base | sim | não | não |
| Pé | pequeno, saturado, com brilho | enorme, escuro, domina | minúsculo, solto |
| Olho | oval com especular | oval pequena, alta | **retângulo** |

O SNES e o P1 gastam o mesmo orçamento cromático. O SNES compra volume com ele; o P1
compra manchas.

## 3. Regras para o nosso design — derivadas do tier correto

| # | Regra | Vem de |
|---|---|---|
| R1 | **Direção de luz única e declarada** (superior-esquerda). Mancha clara que não decorre dela é defeito, não brilho | §2 |
| R2 | Rampa de pele de **5 degraus**, queda monotônica de área | §1 |
| R3 | Alvo de **10 a 12 tons** no personagem, dentro dos 15 de PAL2. **Não reduzir por economia** | §1 |
| R4 | Contorno escuro fechado em 100% da silhueta, slot dedicado | NES e SNES concordam |
| R5 | Razão corpo : pé ≥ 3:1; pé saturado e pequeno, com 1 px de brilho | §2 |
| R6 | Olho oval vertical com especular, nunca retângulo | §2 |
| R7 | Sombra de contato na base, para assentar no chão | §2 |
| R8 | Nenhuma forma interna sem referente anatômico declarado | §2 |

Orçamento: 11 slots de PAL2 usados, 4 livres. Cabe com folga.

## 4. Limites honestos

- Mediu pose estática. Timing, espaçamento e continuidade de pose seguem sem medida.
- O SNES tem mais paletas simultâneas que o MD; a rampa é transferível, o **número de
  materiais coexistindo em cena não é**. Isso é trabalho do budget analyst.
- Os 5 degraus são **especificação, não cores escolhidas**. Precisam ser autorados no
  lattice RGB333 (passos de 36) e verificados contra o teto de 58 cores.
- Nada aqui substitui aprovação humana do model sheet (Trava 3).
