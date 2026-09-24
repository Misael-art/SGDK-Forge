# P2 — Calibracao das rampas de roupa (Ken) — 2026-09-23

## Achado de medicao (antes de ajustar)
A premissa "cores saturadas demais pouco" nao se confirmou: a saturacao HSV das roupas em uso ja era 1,00.
O defeito real era **brilho baixo** (turquesa: topo V 0,85, mediana 0,56), **degrau colapsado** na
quantizacao 3 bits/canal (vermelho: 5 tons distintos de 6) e **pouco contraste contra o fundo escuro**.

## Alvos (definidos antes do ajuste; revisados para serem justos entre matizes)
- T1 croma: saturacao nao cai mais que 0,05 (acromaticas isentas).
- T2 brilho: degrau mais claro no nivel maximo do VDP (V >= 0,98) e mediana V >= 0,60.
- T3 rampa: 6 degraus distintos no VDP, luma estritamente crescente.
- T4 contraste: mediana deltaE76 (CIELAB) >= 40 contra o fundo atual (#202838).
- Luma absoluta foi descartada como alvo: vermelho puro no maximo tem luma 0,30 (injusto por matiz).

## Metodo (`convert-char --vivid-clothing`, converters/sprites.py::vivid_ramp)
Slots de roupa = slots do corpo que variam entre os 12 .act (6 slots). Degrau mais escuro e ancora
(faixa/sombra profunda, intacto). Demais degraus recebem nivel maximo 7-(n-1-r) nos 8 niveis/canal do
VDP com canais escalados proporcionalmente (matiz/saturacao preservados). So aplica onde melhora;
acromaticas (preto/branco) mantem a intencao de design.

| variante | aplicada | V topo/mediana | deltaE vs fundo | degraus |
|---|---|---|---|---|
| black | nao | 0.42/0.28 -> 0.42/0.28 | 18.6 -> 18.6 | 6 -> 6 |
| blue | nao | 0.99/0.85 -> 0.99/0.85 | 57.1 -> 57.1 | 6 -> 6 |
| blue2 | nao | 0.99/0.85 -> 0.99/0.85 | 61.6 -> 61.6 | 6 -> 6 |
| gold | nao | 0.85/0.56 -> 0.85/0.56 | 73.4 -> 73.4 | 6 -> 6 |
| green | sim | 0.99/0.71 -> 0.99/0.71 | 96.9 -> 96.9 | 6 -> 6 |
| green2 | sim | 0.99/0.71 -> 0.99/0.71 | 74.7 -> 74.7 | 6 -> 6 |
| orange | nao | 0.99/0.99 -> 0.99/0.99 | 91.9 -> 91.9 | 6 -> 6 |
| purple | sim | 0.85/0.71 -> 0.99/0.71 | 66.4 -> 70.0 | 5 -> 6 |
| red | sim | 0.99/0.71 -> 0.99/0.85 | 89.8 -> 96.8 | 5 -> 6 |
| turquoise | sim | 0.85/0.56 -> 0.99/0.71 | 50.2 -> 63.4 | 6 -> 6 |
| white | nao | 0.99/0.85 -> 0.99/0.85 | 69.2 -> 69.2 | 6 -> 6 |
| yellow | nao | 0.99/0.99 -> 0.99/0.99 | 107.5 -> 107.5 | 6 -> 6 |

Em uso na luta: P1 = turquoise, P2 = red.

## Palavras CRAM finais (slot 0..15, 0x0BGR)
- turquoise: 0x000, 0x68C, 0x0AE, 0x6CE, 0x8CE, 0xAEE, 0x68C, 0x220, 0x006, 0x660, 0x880, 0x468, 0xAA0, 0xCC0, 0xEE0, 0x000
- red: 0x000, 0x68C, 0x0AE, 0x6CE, 0x8CE, 0xAEE, 0x68C, 0x006, 0x006, 0x008, 0x00A, 0x468, 0x00C, 0x04C, 0x06E, 0x000

## Evidencia
- Antes: ROM 38a67c94..., sessao out/mugenesis_evidence/e3_ken/blastem-linux-20260923T184826Z-675868
- Depois: ROM 5690eafe..., sessao out/mugenesis_evidence/p2_saturation/blastem-linux-20260923T221128Z-1382705/ (before_after.png lado a lado; fora do Git: arte de terceiros)
- Desempenho inalterado (so dados de CRAM): 22,6% dos quadros acima do orcamento.

## Dependencias
T4 foi medido contra o fundo PROVISORIO. Remedir quando o estagio (E4), o HUD (P4) e Shadow/Highlight (P5)
entrarem: S/H escurece/clareia a paleta inteira e muda o contraste percebido.
