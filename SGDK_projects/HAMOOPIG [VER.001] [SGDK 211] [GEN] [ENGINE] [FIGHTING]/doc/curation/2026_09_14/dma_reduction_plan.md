# Plano de redução DMA NTSC — 2026-09-14

## Problema medido

O probe HPRB observou 10.064 bytes pendentes no pior quadro NTSC
(envelope aproximado: 7.782 B). PAL observou 7.984 B dentro do envelope de
aproximadamente 17 KiB. O limite não será “resolvido” truncando a fila, pois
isso deixaria tiles de lutador/efeito sem atualização e recriaria o bug gráfico.

## Ordem de implementação

1. Identificar o frame/estado que gera o pico, acrescentando apenas um marcador
   de pico ao HPRB (sem alterar a lógica de jogo). A sessão HPRB v2 localizou
   o DMA máximo no frame 3480, visualmente coincidente com o impacto grande/KO
   (`spr_spark3`); a sessão v3 de atribuição repetiu o pico em 1.790. O pico de
   scanline v2 foi no frame 3158.
2. Separar uploads de preload (entrada de luta/troca de personagem) dos uploads
   por quadro; manter os primeiros fora da janela de controle responsivo.
3. Para sprites de frame único (projétil, KO e poses terminais), carregar uma
   vez e desligar `SPR_FLAG_AUTO_TILE_UPLOAD` depois da confirmação do upload,
   preservando `SPR_FLAG_AUTO_VISIBILITY` e os índices de VRAM.
4. Para animações críticas, usar janela ativa de frames e fila limitada por
   VBlank; nunca atrasar hitbox, input, hitstop ou frame de impacto.
5. Rebuild canônico e nova captura NTSC/PAL; aceitar a mudança somente se o
   pior NTSC ficar abaixo de 7.782 B e os testes visuais de KO/especiais
   permanecerem limpos.

O primeiro candidato visual é comparar `spr_spark3` com uma versão streamada ou
um frame de impacto reduzido em uma cena de laboratório. Não substituir o
recurso diretamente no combate: o efeito é parte da leitura de impacto e a
troca precisa de vídeo comparativo, teste de hitstop e nova medição HPRB.

## Critério de recuo

Até o item 5, o estado oficial permanece `validado_budget=false` e
`cabe com recuo`. Qualquer artefato corrompido ou frame crítico atrasado rebaixa
a tentativa e restaura a ROM anterior. A sonda HPRB continua diagnóstica e não
é parte de uma alegação de desempenho por si só.

## Experimento controlado: `spr_spark2` (rejeitado)

- Variante compilada somente para laboratório com `HAMOOPIG_DMA_LAB_REDUCED=1`, trocando o `spr_spark3` do `SparkType==3` por `spr_spark2`.
- ROM experimental: `91591dac9c8689b10e87c202830d6a8b02b421f0427e23ea899a8b77b82a19de`.
- Captura: `out/emulator_evidence/visual_ko_20260914T002925Z/`; HPRB parcial: `out/logs/hprb_probe_report_20260914_spark_lab_partial.json`.
- Resultado: pico NTSC permaneceu em 10.064 B (frame 4.469), com 12 sprites por scanline; o FX não é o consumidor dominante. A leitura visual do impacto ficou menor. Variante rejeitada; o baseline funcional `ae6f5dab…` foi restaurado antes do build diagnóstico HPRB v3 `8544c31d…`.
- Aprendizado: instrumentar a composição de sprites/tiles do frame 4.469 e separar uploads de lutador, HUD e transição antes de nova redução.

## Atribuição HPRB v3 — sprites versus fila anterior

- ROM diagnóstica: `8544c31dc7ad4edb42dbdf84585499837c705c692ce90696f86180d4da5b8214`;
  captura `out/emulator_evidence/visual_ko_20260914T003949Z/`;
  relatório `out/logs/hprb_probe_report_20260914_attribution.json`.
- No mesmo cenário NTSC, o pico total foi 10.064 B (frame 1.790), com até
  7.176 B acrescentados por `SPR_update()` e até 5.536 B já pendentes antes
  dele. Os máximos são independentes por amostra, mas a contribuição de
  sprites é claramente o ramo prioritário.
- Próxima implementação: medir e reduzir uploads de frames de lutador
  (preload/janela ativa) preservando `SPR_FLAG_AUTO_VISIBILITY`; não alterar
  hitbox, hitstop ou ordem INPUT → cena → `SPR_update()` → VBlank.

## Atribuição no mesmo frame — HPRB v5

- Captura `visual_ko_20260914T012538Z`, ROM `e91823b7…`, relatório
  `out/logs/hprb_probe_report_20260914_peak_components.json`.
- No frame 4.469, o total de 10.064 B foi decomposto em 4.576 B já pendentes
  antes de `SPR_update()` e 5.488 B acrescentados pela atualização de sprites.
  O único delta de etapa observado foi a mensagem HUD (480 B); o restante é
  backlog acumulado de uploads de animação entre frames.
- Critério de implementação: reduzir a frequência/tamanho dos uploads de
  frames dos lutadores até que o backlog e o delta combinados fiquem abaixo de
  7.782 B NTSC. Truncar a fila continua proibido.

## Experimento: backpressure nativo do SGDK (rejeitado)

- Variante `HAMOOPIG_DMA_LAB_DELAYED_FRAME=1` removeu apenas o flag
  `SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE` dos sprites de lutador, permitindo
  que o motor adiasse frames quando `DMA_getMaxTransferSize()` fosse excedido.
- Captura `visual_ko_20260914T014412Z`, HPRB
  `out/logs/hprb_probe_report_20260914_delayed_lab.json`: 10.064 B no pico,
  com 4.576 B prévios + 5.488 B de `SPR_update()`, idêntico ao baseline.
  A rota atual não configura capacidade que acione esse backpressure.
- Variante rejeitada e macro restaurado para `0`; não houve alteração visual
  observada nem redução de DMA.

## Experimento: alongar ciclos neutros (rejeitado)

- Variante `HAMOOPIG_DMA_LAB_IDLE_SLOW=1` duplicou somente a duração dos
  estados idle, agachado e caminhada. Ataques, hitbox, hitstop e KO ficaram
  inalterados.
- Captura `visual_ko_20260914T015158Z`, HPRB
  `out/logs/hprb_probe_report_20260914_idle_slow_lab.json`: pico permaneceu
  10.064 B, com decomposição 4.576 + 5.488 B. Não atacou o frame crítico;
  variante rejeitada e macro restaurado para `0`.

## Experimento controlado: reutilização de estado (parcial/rejeitado)

- Variante `HAMOOPIG_DMA_LAB_REUSE_STATE_SPRITE=1` manteve o handle quando
  `PLAYER_STATE()` reentrava no mesmo estado, evitando `release/add` de idle,
  crouch e walk. Transições reais continuaram usando o caminho original.
- Captura NTSC `visual_ko_20260914T010324Z`, HPRB
  `out/logs/hprb_probe_report_20260914_reuse_lab.json`: delta de
  `SPR_update()` caiu de 7.176 B para 6.408 B, mas o pico total permaneceu
  10.064 B (fila prévia 5.536 B). HUD e KO permaneceram legíveis.
- Como o teto NTSC não foi pago, a variante não é promovida; macro foi
  restaurado para `0`. O resultado confirma que a próxima redução deve atuar
  na fila prévia e no carregamento de frames, não somente em reentradas.
