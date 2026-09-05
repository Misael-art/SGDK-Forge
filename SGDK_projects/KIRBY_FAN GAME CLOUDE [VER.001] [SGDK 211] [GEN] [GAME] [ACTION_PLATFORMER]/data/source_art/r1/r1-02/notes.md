# R1-02 — notas de entrega

- Assinatura: Codex
- Papel: `layer_study`, `source_candidate`; nenhum dos dois PNGs e asset de fundo para `res/`.
- `concept.png`: 1280x896, 41 cores distintas; `layers.png`: 1280x896, 39 cores distintas. Ambos foram normalizados sem alpha para RGB333 e mantem os originais C2PA em `*_generated.png`.
- Decisoes: a cena composta prioriza rota jogavel e profundidade por valor. A prancha de camadas e propositalmente separada em faixas independentes; a identificacao e visual, sem texto de runtime.
- Ceu: o prompt pediu 12 faixas; a proxima etapa deve contar as faixas no PNG e fixar uma tabela de raster antes de converter. Nao inferir que uma faixa visual equivale a uma interrupcao final.
- Traducao futura: preservar o mesmo canvas/ancora por camada; separar semanticamente ceu, montanhas, colinas, terreno e oclusao frontal. A cachoeira exige budget/DMA proprio se animada.
- Risco de tile 8x8: a cena inteira tem detalhes organicos demais para conversao direta; converter por vocabulario modular e medir tiles unicos por camada, nunca por `IMAGE` da imagem completa.
- Autocritica honesta: a separacao de planos esta forte, mas ainda precisa de medicao real em escala de cinza e de um contrato de scroll; a faixa HUD nao deve ser aceita apenas por impressao visual.
