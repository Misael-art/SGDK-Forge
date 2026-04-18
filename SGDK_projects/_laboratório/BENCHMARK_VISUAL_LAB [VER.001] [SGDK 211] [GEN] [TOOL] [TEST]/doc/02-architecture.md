# 02 - Architecture

## Estrutura

- `src/main.c`: loop principal do laboratorio e seletor das provas
- `inc/game_vars.h`: enums do laboratorio e estado compartilhado
- `src/game_vars.c`: estado global do laboratorio
- `out/logs/validation_report.json`: consolidacao tecnica + eixo visual

## Camadas da validacao

1. `analyze_aesthetic.py` mede conformidade visual offline
2. `validate_resources.ps1` agrega o eixo visual ao relatorio canonico
3. `BENCHMARK_VISUAL_LAB` exibe a prova em ROM
4. BlastEm fecha o gate de observacao

## Provas fixas

### Silhouette Lab
- objetivo: provar leitura de sprite contra fundos distintos

### Layer Contrast Lab
- objetivo: provar separacao tonal entre BG_A, BG_B e plano critico

### Animation Readability Lab
- objetivo: provar que a leitura da forma sobrevive entre frames
