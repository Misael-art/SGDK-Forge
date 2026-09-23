# P4 — HUD de luta: roteiro, storyboard, medicao, orcamento e contrato de asset (2026-09-23)

Status: IMPLEMENTADO (2026-09-23). Aprovacoes humanas: arte SFA2 (Chok), paleta em slots da PAL0, barra estilo Street Fighter.

## 1. Roteiro (o que o HUD comunica)
Abertura: "ROUND n" -> "FIGHT!" (bloqueia controle). Luta: vida (amarelo, drena), especial (azul, enche),
tempo (99), retratos, vitorias de round, contador de hits junto a barra de quem faz o combo (ancora de
evento = mesmo sistema de acerto do P1). Fim: "K.O." / "TIME" / "DRAW", pose de vitoria. Super com fundo
de vitoria (730): HUD some (o proprio Ken declara `AssertSpecial nobardisplay`).

## 2. Storyboard (320x224, H40)
```
y 0-7   | [P1 nome]                          [P2 nome] |
y 8-15  |[face]====vida P1====  99  ====vida P2====[face]|
y 16-23 |      ##especial P1##       ##especial P2##   |
y 24-31 |  o o (vitorias)                   o o        |
y 32-39 |  12 HITS                                     |  <- lado de quem combou
meio    |          ROUND 1 / FIGHT! / K.O.             |  (sprites SFA2 grupo 30/90/95/96)
```

## 3. Medicao (host harness + BlastEm)
| medida | valor | fonte |
|---|---|---|
| lutadores nas linhas 0-39 | 7,4% dos ticks; ate 7 sprites HW ali | harness toprows (CPU x CPU, 36000 ticks) |
| HUD em sprites (2 vidas 128px + 2 especiais + tempo + 2 faces) | ~20 sprites nas mesmas linhas | estimativa por segmentos 32px |
| => pior caso sprites/scanline | 27 > 20 (estouro em ~7% dos ticks) | soma |
| HUD em tiles WINDOW | 0 sprites; DMA so quando valor muda (<= 40 palavras/quadro) | calculo |
| paleta de efeitos 15 -> 11 cores (4 para HUD) | erro medio 13,6 -> 23,6 (+74%) | k-means nos pixels FX do Ken |
| CPU atual (sem HUD novo) | 22,6% quadros acima do orcamento, pico 159% | ROM 38a67c94 |

## 4. Decisoes de transporte (recomendadas com base na medicao)
- Barras, tempo, textos fixos, retratos: **tiles no plano WINDOW** (linhas 0-4). Mesma arte de segmento,
  outro transporte; motivo registrado: sprites estourariam 20/linha quando o lutador pula.
- Mensagens grandes (ROUND/FIGHT/KO): **sprites** no meio da tela (so na intro/fim do round, sem luta ativa).
- Tecnica de barra (P4.1): **Street Fighter** (continua + fantasma de dano) recomendada: 1 tile de borda
  parcial por atualizacao (DMA minimo), leitura fina do dano; Fatal Fury (blocos) le em degraus de ~6% e
  exigiria o mesmo custo. Fantasma = mesma arte, cor clara via paleta.

## 5. Orcamento
- VRAM: fonte ~64 tiles, segmentos de barra ~8 tiles, retratos 2x(4x4)=32 tiles, ROUND/FIGHT/KO ~200 tiles
  (carregados so na intro/fim). Cabe entre corpos (fixos) e pool de sprites (600).
- Paleta: CONFLITO (ver decisao 2). PAL0=estagio (E4), PAL1/PAL2=lutadores, PAL3=efeitos.
- CPU: atualizacao do HUD por evento (so quando vida/tempo/combo muda), nao por quadro.

## 6. Contrato de asset (fontes externas, proveniencia obrigatoria)
| asset | fonte proposta | autor | status de licenca |
|---|---|---|---|
| segmento de vida/especial | recorte 8px de `fight.sff` 1,x / 10,x (SFA2 Lifebars) | Chok | a confirmar |
| fonte do tempo/combo | `Sfa2_time.fnt`, `Sfa2_combo.fnt` | Chok | a confirmar |
| retrato | `KenMastersADV.sff` 9000,0 (25x25) | Chok | uso local autorizado (Ken) |
| ROUND/FIGHT/KO | `fight.sff` grupos 30, 90, 95, 96 | Chok | a confirmar |
Nada desenhado por codigo. Todo simbolo entra em doc/asset_provenance_manifest.json.

## 7. Descoberta colateral
`sfa2_lifebars.zip` traz o `fightfx.sff/.air` padrao do MUGEN: supriria as faiscas comuns (sparkno 40)
e a anim de super comum (anim 100) hoje registradas como indisponiveis.

## 8. Resultado medido (implementacao)
- Transporte: tiles no WINDOW (linhas 0..6) + mensagens em sprites (partes <= 128 px, <= 16 sprites HW).
- Paleta: PAL0 slots 9..15 = 7 cores (o contrato estimava ~5): amarelo, vermelho, vermelho escuro, cinza,
  branco (cores REAIS da barra, conversao direta) + 2 azuis do especial. Estagio (E4) fica com 1..8.
  Mensagens/fontes usam a cor mais proxima dessas 7 (aproximacao declarada: ROUND/FIGHT perdem o degrade laranja).
- VRAM: 136 tiles de HUD + 16 do retrato (compartilhado P1=P2), apos corpos e fundo de super.
- CPU: 1a versao (varredura das 4 barras por quadro) = ~9% do quadro e 38,5% dos quadros acima do orcamento;
  versao por evento (so tiles entre borda antiga e nova) = ~3% do quadro; ROM b138fb35: 23,1% a 26,2%
  dos quadros acima do orcamento entre duas capturas (baseline sem HUD 22,6%; variacao entre capturas ~3 pp).
- Sprites por linha (pico medido): 10 (limite 20).
- Evidencia: out/mugenesis_evidence/p4_hud/blastem-linux-20260923T223739Z-1463769 (ROM b138fb35...).
- Efeito colateral: slot 15 da PAL0 (cor do texto do SGDK) agora e azul do HUD: texto de depuracao sai azul.
