# R1-01 — notas de entrega

- Assinatura: Codex
- Papel: `concept_art`, `source_candidate`; nao e sprite, sheet de animacao nem asset para `res/`.
- Arquivos: `concept_generated.png` preserva a origem do gerador; `concept.png` e a derivacao normalizada para 1024x768, sem alpha e com 10 cores distintas.
- Paleta final exata: `#000000`, `#242449`, `#6d2449`, `#922424`, `#db4949`, `#db6d92`, `#ff00ff`, `#ff9292`, `#ffb6b6`, `#ffffff`. A chave magenta e `#ff00ff`; os tres rosas e os demais tons obrigatorios do pedido foram preservados.
- Decisoes: a organizacao visual, os turnarounds e as silhuetas foram priorizados sobre acabamento. Os rotulos foram tratados apenas como auxilio de leitura da prancha, nunca como texto de jogo.
- Traducao futura: recortar e redesenhar em grade nativa 28x28 por estado; extrair primeiro a silhueta, depois olhos, pes e boca. Nao fazer downscale direto desta prancha.
- Risco de tile 8x8: as poses com bochechas infladas e boca aberta comprimem detalhes faciais demais; o recorte manual tera de preservar contraste de olhos/boca em poucos clusters.
- Autocritica honesta: a prancha ainda e mais limpa como concept sheet do que como model sheet de producao; precisa de pivots, bboxes e key poses aprovadas antes de qualquer sprite sheet.
