# 00 — Project Brief — KIRBY_FAN GAME GROK BUILD

| Campo | Valor |
|---|---|
| Nome | KIRBY_FAN GAME GROK BUILD [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER] |
| Genero | ACTION_PLATFORMER |
| Plataforma | SEGA Mega Drive / Genesis (SGDK 2.11) |
| Tipo | **Estudo + fan game non-commercial** (reimaginacao de Kirby's Adventure, NES) |
| ROM | ≤ 4 MB, sem mapper — fan/estudo, nao marketplace |
| Alvo visual | Alien Soldier / Gunstar Heroes / Dynamite Headdy / SoR2 / Demons of Asteborg |
| Assets | Original **e/ou** referencia TSR convertida (ver `data/reference_archive/LEGAL.md`) |

## Uma frase

Reimaginar **Kirby's Adventure** no Mega Drive entregando o que o NES tentava
(gradientes, profundidade, cor por regiao) com o vocabulario real do VDP:
line-scroll, H-int, Shadow/Highlight, YM2612 e 60 fps estaveis.

## Pilares

1. **Verbo central = inalar.** Vortex com Shadow/Highlight, hit-stop, PCM punch.
2. **Dream Land exuberante.** Minimo 4 camadas de parallax, ceu dinamico, raster.
3. **Arcade feel.** Knockback em `fix16`, smear, screen shake, flash de impacto.
4. **Boss multi-articulado.** Whispy Woods com dezenas de sprites encadeados.
5. **Gates = lei.** Cores, sprites/scanline, VRAM, DMA, frametime — sempre PASS.

## Escopo VER.001 (fatia vertical)

```
TITULO → VEGETABLE VALLEY 1 → 2 → 3 → BOSS (Whispy Woods) → GAME OVER / CONTINUE
```

- 5 copy abilities: FIRE, BEAM, CUTTER, STONE, SWORD
- ~12 tipos de inimigo (5 dao copy)
- Arte: original e/ou referencia TSR convertida (fan/estudo); trilha no espirito da OST
- Plano grafico paralelo: `doc/plans/PARALLEL_TSR_REFERENCE_LEARNING_PLAN.md`

## Fora de escopo VER.001

Mundos 2–7, mini-games, museu, save/password, 2P, Meta Knight, Nightmare,
distribuicao comercial / marketplace / monetizacao.

## Nota legal (regra de engenharia)

Kirby e IP da Nintendo/HAL Laboratory. Este projeto:

- e **estudo + fan game non-commercial** (sem marketplace, ads, IAP, venda);
- **pode** usar referencia / sheets do Spriters Resource **convertidos** para MD
  (`data/reference_archive/`, credito em MANIFEST) — ver LEGAL.md;
- **nao** reivindica ownership da IP;
- se virar comercial no futuro, rips saem e sobra so arte original/licenciada.

## Relacao com o irmao CLOUDE

O projeto CLOUDE validou FASE 1 + harness neste host. GROK BUILD herda a
**arquitetura medida** e a telemetria VLAB, mas e um arvore isolada: contratos,
arte, scores e evidencia vivem aqui. A meta de GROK e empurrar a qualidade
visual/sonora para o teto AAA do brief (geracao de assets + loop critico).

## Criterio de "pronto" da fatia

| Item | Medicao |
|---|---|
| Loop jogavel | playtest scriptado cobre 100% dos estados do jogador |
| Gates hardware | `tools/harness/gates.py` PASS em todas as cenas |
| BlastEm | bundles `sealed` por cena em `out/evidence/` |
| Arte | quantizada RGB 3-3-3, ≤16 cores/paleta, 0 ilegais |
| ROM | `out/rom.bin` ≤ 4 MB, roda em hardware via flashcart |
