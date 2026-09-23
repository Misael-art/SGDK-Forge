# reference_archive — referência TSR para fan game de estudo

Política atual do projeto: **fan + estudo non-commercial**.
Rips convertidos **podem** ir para `res/` e para a ROM fan local.
Ver [LEGAL.md](LEGAL.md) e o plano
[`doc/plans/PARALLEL_TSR_REFERENCE_LEARNING_PLAN.md`](../../doc/plans/PARALLEL_TSR_REFERENCE_LEARNING_PLAN.md).

## Comandos

```bash
# Baixar curadoria Tier S
python3 tools/pipeline/tsr_fetch_curated.py

# Métricas + quantize lab + painel vs nosso sheet
python3 tools/pipeline/tsr_analyze_and_compare.py

# Instalar conversões no res/ (fan build) — quando o instalador existir
python3 tools/pipeline/tsr_install_to_res.py --role player
```

## Layout

| Path | Conteúdo |
|---|---|
| `catalog/` | Seleção humana |
| `raw/` | Downloads TSR |
| `versions/` | Snapshots (v001 raw, v003 quantized, …) |
| `compare/` | metrics + painéis |
| `premises/` | Premissas para geração e conversão |

## Proveniência

`MANIFEST.json` — `fan_study_allowed: true`, hashes, URLs.
