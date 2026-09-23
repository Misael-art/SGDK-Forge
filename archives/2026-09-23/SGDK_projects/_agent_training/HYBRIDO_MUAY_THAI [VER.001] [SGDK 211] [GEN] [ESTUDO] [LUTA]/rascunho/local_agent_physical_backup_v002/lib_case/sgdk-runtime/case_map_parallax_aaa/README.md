# Case: MAP Parallax AAA

Caso canonico para cenario monumental com parallax por bandas, sem fingir terceiro plano.

Este case demonstra a rota segura para uma cena estilo horizonte profundo:

- BG_B recebe bandas de profundidade por line scroll.
- BG_A recebe o plano jogavel/foreground.
- WINDOW fica livre para HUD, salvo se outro contrato declarar uso.
- H-Scroll por linha e tratado como recurso caro, com owner unico e reset.

Status: `reference_case_pending_blastem_measurement`.

Enquanto nao houver ROM dedicada, screenshot e `runtime_metrics.json`, este case serve como padrao de arquitetura e contrato, nao como benchmark medido.

## Nao e

- Mode 7.
- Terceiro plano real.
- Prova de custo de pior quadro.
- Asset final de entrega.

