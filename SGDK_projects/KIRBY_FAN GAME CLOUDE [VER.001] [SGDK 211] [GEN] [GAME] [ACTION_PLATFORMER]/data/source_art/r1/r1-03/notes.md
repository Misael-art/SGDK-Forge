# R1-03 — notas de entrega

- Assinatura: Codex
- Papel: `concept_art`, `source_candidate`; nao e boss final nem prova de articulacao em ROM.
- `concept.png` foi normalizado para 1024x1024, 15 cores distintas, sem alpha; `concept_generated.png` preserva a origem.
- Decisoes: a leitura favorece tronco central e rosto grande; o galho foi pedido em sete modulos isolados e em tres curvaturas, enquanto a copa foi tratada como vocabulario repetivel em vez de sprite unico.
- Traducao futura: redesenhar cada segmento em bbox/pivot declarados, marcar os sete encaixes e provar FK/curvaturas no emulador. A copa deve ir para BG/tilemap, nao para OAM.
- Risco de tile 8x8: a textura de casca e os clusters de folha devem ser simplificados para evitar explodir tiles unicos; nenhum detalhe pode atravessar uma junta de galho.
- Autocritica honesta: a folha comunica bem a ideia modular, mas ainda nao prova que os pivots das tres curvaturas encaixam no runtime; isso precisa de contrato geometrico, nao de inspeção visual.
