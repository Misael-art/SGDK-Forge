# R1-05 — notas de entrega

- Assinatura: Codex
- Papel: `tileset_concept`, `source_candidate`; a grade ilustrada nao substitui tiles validados em `res/`.
- `concept.png`: 1024x1024, 15 cores distintas, sem alpha; o PNG original de geracao foi mantido lado a lado.
- Decisoes: o catalogo separa topo de grama, massa de terra, cantos, slopes, decoracao, quebra, cachoeira e caverna. O contraste entre solido e fundo foi priorizado.
- Traducao futura: reconstruir em tiles reais 8x8, com tiles repetiveis testados por 3x3 automatico; extrair cada familia para seu proprio spec JSON e medir reuso/H-Flip.
- Risco de tile 8x8: a grade no concept e apenas guia e ha detalhes demais em alguns blocos; transcrever literalmente criaria tiles unicos e bordas desalinhadas.
- Autocritica honesta: a prancha explica o vocabulario, mas nao e uma prova matematica de tiling. O proximo modelo precisa gerar testes de borda e diferenciar colisao de decoracao no dado de fase.
