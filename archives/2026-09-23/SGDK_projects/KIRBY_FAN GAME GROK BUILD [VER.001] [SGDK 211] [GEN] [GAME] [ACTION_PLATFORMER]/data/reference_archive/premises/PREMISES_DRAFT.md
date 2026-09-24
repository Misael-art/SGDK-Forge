# PREMISES DRAFT — extraídas do arquivo de referência (lab)

> Gerado automaticamente a partir de métricas. Revisão humana obrigatória antes de
> virar checklist de geração. **Fan/estudo:** rips convertidos podem ir ao res/; premissas também treinam geração original.

## Fonte

- Arquivo: `data/reference_archive/`
- Compare: `compare/ours_r6_vs_ref_kirby_panel.png`
- Métricas: `compare/metrics_v001.json`

## Personagem (Kirby)

| Premissa | Ref SNES (se ok) | Nosso R6 | Ação de geração |
|---|---|---|---|
| Tons de rosa no corpo (aprox) | 143 cores pink-like | 8 | Gerador deve manter **≥5** faixas (1–5 + outline) |
| Delta luminância p90−p10 | 46.7 | 175.1 | Alvo: delta ≥ 80 (volume legível a 32px) |
| Contorno escuro | presente nos rips | idx 6 | Sempre anel de contorno 1px |
| Pés contrastantes | castanho/vermelho | idx 7/8 | Nunca rosa do corpo nos pés |
| Olhos | alto contraste | 9/10 | Preto + brilho branco |
| Set de poses mínimo | idle, walk, jump, float, inhale, hurt | 8 frames R6 | Manter taxonomia do `kirby.c` |

## Cenário (Vegetable Valley NES)

- Estágios 2637–2640: estudar **densidade de tile** (grama, terra, arbusto) vs nosso R5.
- Premissa de tile: **não flat fill** — microdetalhe em ≥30% da área opaca de terra.
- Montanha: faces claras/escuras sólidas (já em R5); ref NES é mais “bloco”; ref SNES é alvo AAA.

## Pipeline MD (aprendizado de conversão)

1. Key color → index 0 (nunca corpo).
2. Reduzir cores **antes** de snap RGB333 (PALETTES.md).
3. Stamp 0..15 absoluto no PNG (L-011).
4. Sheet personagem: células uniformes, sem divisórias.
5. Comparar **métricas**, não bitmap do rip.

## Critério de sucesso do aprendizado

1. Geração original atinge pink_ramp ≥ ref e lum_delta ≥ 0.85× ref SNES (quando medido).
2. Critico cego: hesitação entre original e ref **painel de métricas** (não pixel-perfect).
3. Zero bytes de `raw/` em `res/` (hash gate).

## Próximo

- [ ] Revisão humana deste draft → `PREMISES.md` final
- [ ] Atualizar `build_kirby_procedural.py` com checklist de premissas
- [ ] Imagine prompts ancorados em premissas (sem “copy this sheet”)
- [ ] Critico cego R4: nosso gen vs SNES ref (métricas no relatório)
