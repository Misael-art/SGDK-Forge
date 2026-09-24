# P1 A1 — ph_kirby.png

- Entrega: `source_candidate`; ainda nao promovida para `res/`.
- Dimensao: 256x32; 8 frames de 32x32.
- Cores reais: 10 visiveis + chave magenta.
- Gate tecnico: PASS; RGB333, PAL2 e meio-tom entre 9.91% e 10.08% por frame.
- Gate de artefato v2: PASS; 8/8 frames, zero clipping, ilhas, drift, falha de contato ou delta invalido.
- Silhueta FLOAT vs IDLE: PASS; diferenca simetrica/union = 0.123311, acima do piso 0.12.
- O que melhorou: corrida tem contato/passagem/oposto, salto recolhe os pes, FLOAT rompe a silhueta com duas protuberancias e INHALE usa boca grande e inclinacao traseira.
- Do que nao gostei: a variacao de squash do torso na corrida ainda e conservadora; precisa ser julgada a 60 fps dentro do BlastEm antes de promocao.
