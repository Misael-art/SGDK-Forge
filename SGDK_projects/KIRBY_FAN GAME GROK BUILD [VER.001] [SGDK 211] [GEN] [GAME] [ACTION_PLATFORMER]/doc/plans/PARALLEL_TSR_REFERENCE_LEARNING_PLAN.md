# Plano paralelo — Aprendizado gráfico via Spriters Resource → fan build + geração AAA

**Status:** `ativo` · atualizado 2026-08-08
**Natureza do projeto:** **estudo + fan game non-commercial** (sem barreiras internas a rips convertidos).
**Trilha A (referência):** TSR → conversão MD → `res/` → ROM fan de estudo.
**Trilha B (aprendizado/geração):** métricas → premissas → arte original → bater qualidade AAA.

---

## 0. Premissas legais e de projeto (fan / estudo)

| Fonte | Regra |
|---|---|
| Projeto README | Fan **non-commercial** / estudo; **não** marketplace, ads, IAP, venda |
| Spriters Resource ToU | Uso OK em non-commercial / unpublished; **proibido em comercial** |
| Copyright Nintendo/HAL | IP permanece com os titulares; fan não reivindica ownership |
| Política interna (2026-08-08) | Rips convertidos **podem** ir a `res/` e à ROM **fan de estudo** com crédito em `MANIFEST.json` |

**Fluxo permitido (sem barreira interna)**

```
TSR rip
  → convert/quantize MD
  → (A) instalar em res/ → ROM fan estudo
  → (B) métricas + premissas → geração ORIGINAL → res/ (quando maduro)
```

**Fluxo proibido**

```
ROM/comercial / marketplace / ads / monetização com rips
reupload de sheets brutos sem crédito TSR
```

`fan_study_allowed=true` no manifesto do arquivo. Se o projeto virar comercial, reverter para só original (LEGAL.md §5).

---

## 1. Objetivo de aprendizado

Aprender, com evidência mensurável, **o que** um cartucho AAA (e o NES/SNES canônico do Kirby) faz em:

1. **Personagem** — volume esférico, rampa de rosa, pés, olhos, contorno, set de poses
2. **Inimigos / boss** — silhueta legível a 16–32px, 3+ tons
3. **Tiles / estágio** — Vegetable Valley: grama, terra, montanha, céu
4. **Pipeline MD** — RGB333, 4bpp, index 0, paletas absolutas, scanline budget

Quando as premissas estiverem estáveis, treinar o pipeline de **geração** (procedural + Imagine) para bater as **mesmas métricas** sem copiar pixels de rip.

---

## 2. Curadoria — melhores assets (v1)

Seleção por **relevância para Vegetable Valley MD** + qualidade do sheet + densidade de poses.

### Tier S — obrigatório v1

| ID | Jogo | Nome | Por quê |
|---|---|---|---|
| 49192 | NES Kirby’s Adventure | Kirby | Origem do fan game; set completo de poses |
| 49202 | NES Adventure | Enemies | Waddle Dee etc. — inimigos do loop |
| 49193 | NES Adventure | Whispy Woods | Boss já no código |
| 2637–2640 | NES Adventure | Vegetable Valley 1–4 | Tiles/estágio do world 1 |
| 2635 | NES Adventure | World 01 Vegetable Valley | Mapa/overview de referência |
| 52859 | SNES Super Star | Kirby | **Âncora AAA 16-bit** de volume/poses |
| 32130 | GBA Nightmare in Dream Land | Kirby | Remake colorido limpo; rampa moderna |

### Tier A — v1.1 (depois do S)

| Foco | Exemplos |
|---|---|
| Abilities SNES/GBA | Beam, Sword, Fire (volume + FX) |
| Super Star stages | Green greens / pastoral BG |
| Dream Land 3 | Silhuetas 16-bit densas |
| Palettes sheets | Super Star / Mirror palettes |

**Excluídos de v1:** customs/edited, Mass Attack (estilo 3D-ish), Smash customs.

---

## 3. Layout de pastas (arquivo versionado)

```
data/reference_archive/
  LEGAL.md                          # ToU + copyright + fan_study_allowed
  MANIFEST.json                     # ids, urls, hashes, tier, versões
  catalog/selection_v1.json         # curadoria humana
  raw/
    nes_kirby_adventure/
      49192_kirby.png
      49202_enemies.png
      ...
    snes_kirby_super_star/
      52859_kirby.png
    gba_nightmare_dreamland/
      32130_kirby.png
  versions/
    v001_raw/                       # snapshot imutável pós-download
    v002_cropped/                   # após crop de células
    v003_md_quantized/              # RGB333 + 4bpp absolute
    v004_md_sheet_32/               # sheet 8×32 alinhado ao anim table
  compare/
    ours_r6_vs_ref_snes.png
    metrics_v00N.json
  premises/
    PREMISES.md                     # regras extraídas (treino de geração)
    palette_ramps.json
    pose_taxonomy.json
  lab_rom/                          # builds fan (fan_study_allowed)
```

Versionamento: cada passo de pipeline grava em `versions/vNNN_*` + entrada em `MANIFEST.json` (sha256, data, ferramenta).

---

## 4. Pipeline de conversão e comparação

| Etapa | Script | Entrada | Saída | Gate |
|---|---|---|---|---|
| D1 Download | `tools/pipeline/tsr_fetch_curated.py` | catalog | `raw/` + hashes | HTTP 200, size > 0 |
| D2 Catalog | idem | raw | MANIFEST | ids batem com selection |
| C1 Inspect | `tools/pipeline/tsr_analyze_sheet.py` | raw | cell size, #cores, lum | report JSON |
| C2 Quantize | `tools/pipeline/tsr_to_md_lab.py` | raw | v003 RGB333 | 0 ilegais lattice |
| C3 Align | idem | v003 | v004 sheet 256×32 (Kirby) | center idx0 < 5% |
| M1 Metrics | `tools/pipeline/tsr_compare_to_ours.py` | v004 vs ph_kirby / R6 | SSIM-proxy, rampa, poses | score table |
| M2 Panel | idem | — | compare/*.png | visual |
| P1 Premises | humano + script | metrics | premises/* | checklist |
| G1 Generate | build_kirby_procedural / Imagine | premises | original sheet | gates R6+ |
| S1 Fan ROM | convertidos e/ou original | res/ | `out/rom.bin` fan | gates PASS + `fan_study_allowed` |

**Métricas de aprendizado**

- Contagem de tons de rosa no corpo (alvo AAA: ≥5 incluindo outline)
- Luminância highlight vs core shadow (delta)
- Proporção pé/corpo, olho/rosto
- Número de poses distintas no set idle/run/jump/float/inhale
- Para tiles: % área com microdetalhe vs flat fill

Rips convertidos **podem** ser a base do fan ROM enquanto o gerador original
amadurece; o aprendizado continua medindo gap ref vs nosso.

---

## 5. Como isso treina a geração AAA

1. **Premissas** viram checklist do gerador e prompts Imagine.
2. Cada geração nova é **comparada** às métricas do ref.
3. Enquanto isso, fan ROM pode usar **ref convertida** (estudo sem barreira).
4. Quando geração original ≥ ref em métricas + crítico hesita, promove original.

```
ref_metrics ──► premises ──► generator ──► gen_metrics
     │               ▲                         │
     └──► res/ fan   └──── gap analysis ◄──────┘
```

---

## 6. Fases de execução

| Fase | Entrega | Done quando |
|---|---|---|
| **P0** | Plano + LEGAL + pastas + catalog v1 | docs no repo |
| **P1** | Download Tier S + MANIFEST hashes | 100% files + sha256 |
| **P2** | Quantize + compare vs R6 | painel + metrics JSON |
| **P3** | Premises v1 | PREMISES.md |
| **P4** | Instalar convertidos em `res/` + fan ROM gates PASS | harness verde |
| **P5** | Generator original bate premises | critic + métricas |
| **P6** | (Opcional) mix ref+original por asset | melhor score visual |

---

## 7. Relação com a trilha principal

| Trilha principal | Trilha referência |
|---|---|
| Loop jogável + gates | Sheets canônicos NES/SNES/GBA |
| R6 procedural atual | Ref ensina teto de volume e poses |
| Critico ~7.1 | Critico vs **ref** + Celestial |
| Fan ROM non-commercial | Pode incluir rips convertidos com crédito |

---

## 8. Riscos

| Risco | Mitigação |
|---|---|
| Vazamento para uso comercial | LEGAL + README: marketplace proibido |
| Dependência de site TSR offline | Archive local v001_raw imutável |
| Escopo infinito de 592 assets | Tier S fechado; A só após P3 |
| Qualidade MD (key/palette) | Gates idx0 + RGB333 em toda instalação |

---

## 9. Próxima ação

1. ~~Criar árvore + LEGAL + catalog~~
2. ~~Baixar Tier S~~
3. ~~Analyze + panel~~
4. **Instalar convertidos em res/ (Kirby → sheet 8×32)**
5. Rebuild fan ROM + gates
6. Premises finais + gerador

*Plano paralelo v1.1 — fan/estudo sem barreira interna.*
