# R1-06 — notas de entrega

- Assinatura: Codex
- Papel: `palette_study`, `source_candidate`; nao sao assets de agua diretos para `res/`.
- `concept.png`: 1280x896, 39 cores; `above_below.png`: 1280x896, 41 cores; `distortion.png`: 1280x896, 37 cores. Todos sem alpha, dentro da grade RGB333; os tres `*_generated.png` preservam a procedencia.
- Decisoes: a linha d'agua foi mantida reta; luz submersa foi resolvida em clusters/dither, nunca alpha. O comparativo explicita a direcao cromatica e a prancha de distorcao mostra deslocamento horizontal por linha.
- Regra de derivacao proposta para implementar, ainda a validar contra o palette plan: para cada cor de superficie nao branca, mover G e B um degrau para cima quando possivel, mover R um degrau para baixo quando possivel e reduzir o valor maximo um degrau; branco de bolha/highlight permanece branco. O proximo modelo deve materializar uma tabela, nao usar operacao cega.
- Traducao futura: fixar `waterline_y`, duas faixas de paleta e tabela seno inteira; aplicar HScroll por linha por um unico owner. Feixes usam Highlight/dither, sem transparencia.
- Risco de tile 8x8: pedras e vegetacao submersas ainda tem textura em excesso, e o comparativo lado a lado precisa virar a mesma geometria modular, nao dois fundos independentes.
- Autocritica honesta: a linguagem de agua esta convincente offline, mas nao prova que a regra de paleta preserva todos os materiais nem que a tabela seno cabe no budget de H-Int; ambas as coisas exigem prova em ROM.
