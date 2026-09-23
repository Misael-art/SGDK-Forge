# Phase 4 Asset Conversion Backlog

Status: `pipeline_backlog_only`

Este backlog cobre os rotulos citados no parecer agregado: `SNES->MD`,
`PC-98->MD`, `high-colour`, `color hacking` e `SFX prep`.

Eles ainda nao viraram cinco skills novas porque o thread nao traz detalhe
suficiente para definir contratos sem ambiguidade. Por enquanto, entram como
especializacoes candidatas de owners existentes.

## Mapeamento seguro atual

| Cluster | Owner atual | Artefato esperado antes de nova skill |
|---|---|---|
| SNES->MD | `art-translation-to-vdp` | case com source, paletas originais, perda aceitavel, proof MD |
| PC-98->MD | `art-translation-to-vdp` | case com aspect/crop, dithering, paleta, prova de leitura |
| high-colour -> MD | `art-conversion-pipeline` | palette reduction report, material ramps, perceptual comparison |
| color hacking | `megadrive-pixel-strict-rules` | CRAM/palette patch manifest, before/after, no palette collision |
| SFX prep | `xgm2-audio-director` | source format, target driver, channel ownership, priority policy |

## Regras de promocao futura

- Criar skill nova somente se houver ciclo operacional proprio.
- Se a tarefa for apenas traducao visual para VDP, aprimorar
  `art-translation-to-vdp`.
- Se a tarefa for apenas indexacao, PLTE, transparencia ou grade de cor,
  aprimorar `megadrive-pixel-strict-rules`.
- Se a tarefa for audio/SFX, usar `xgm2-audio-director` ou
  `z80-pcm-custom-driver` conforme o caso.
- Nao criar skill por nome de plataforma de origem sem fixture.

## Status honesto

`pipeline_backlog_only` significa que o agente reconhece potencial de valor,
mas nao possui evidencia suficiente para promover regra canonica detalhada.
