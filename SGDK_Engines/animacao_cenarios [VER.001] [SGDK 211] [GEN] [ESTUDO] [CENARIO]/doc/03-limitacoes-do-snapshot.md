# Limitacoes do Snapshot

Este pacote nao e buildavel sozinho porque faltam:

- `cenarios_res.h`
- definicoes de imagens `gfx_bgb1` ate `gfx_bgb7`
- assets `.png` correspondentes

## Por que ainda vale a pena manter

- a logica de animacao continua valiosa para estudo
- o codigo e pequeno o bastante para ser relido por iniciantes
- o wrapper agora responde sem erro enganoso e deixa claro que se trata de
  uma referencia, nao de uma ROM pronta
