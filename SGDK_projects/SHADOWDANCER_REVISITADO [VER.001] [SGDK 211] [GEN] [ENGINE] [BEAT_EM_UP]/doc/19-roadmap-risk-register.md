# Roadmap e riscos

## Marco 1 - conversao SGDK 2.11

Codigo, recursos e documentacao migrados; build pendente nesta sessao.

## Marco 2 - prova de runtime

BlastEm, input roteirizado, camera, colisao e fila DMA observados.

## Riscos

- fila DMA acima do limite NTSC: reduzir janela ou espacamento de scroll;
- semantica do mapa de colisao diferente do esperado: criar fixture antes de alterar regras;
- sprite legado maior que o budget de hardware: medir antes de trocar o .res;
- arte sem refinamento visual: manter acceptance_status placeholder.

