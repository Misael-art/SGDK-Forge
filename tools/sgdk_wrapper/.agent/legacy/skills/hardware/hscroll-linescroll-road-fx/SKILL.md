# hscroll-linescroll-road-fx

Use when a scene promises road curves, pseudo-3D floors, water waves, heat haze, line scroll parallax or any per-line horizontal distortion.

## Purpose

Convert line-scroll spectacle into a SGDK/VDP plan that can fit HScroll table updates, camera behavior and DMA/VBlank constraints.

## Required Inputs

- Target display mode and visible height.
- Plane ownership.
- HScroll mode: plane, tile row or line.
- Camera motion and effect timeline.
- Interaction requirements with sprites and collision.

## Required Outputs

- HScroll table ownership and update timing.
- Formula or lookup table for line offsets.
- Plane and priority constraints.
- Update route: precomputed HScroll table, VBlank upload, H-Int split, or
  bounded per-frame recompute.
- Runtime fallback if the line-scroll budget is too expensive.

## Hard Rules

- Do not call an effect "Mode 7" unless it is explicitly framed as pseudo-3D line scroll or software rendering.
- Do not animate every line without a budget.
- Do not tie collision directly to distorted pixels unless a gameplay-space mapping exists.
- Do not describe HBlank magic without a real owner. If the effect relies on
  H-Int/HBlank timing, declare the interrupt owner, scanline targets, reset path
  and fallback.
- Prefer a table-driven HScroll plan when it can express the effect; per-line
  CPU/interrupt work is a last resort and needs budget evidence.
- The art must be authored for bands/scanlines. Line offsets applied to arbitrary
  art can tear silhouettes and readability.

## Candidate Curation Note

Source: attached White_Pointer-style transcript summary reviewed on 2026-06-17,
`E1_text`. The retained improvement is the distinction between perceptual
"HBlank trick" language and an implementable SGDK plan: table ownership,
scanline ownership, update cadence, reset and gameplay-space mapping.

## Curadoria candidata: traducao raster NES -> Mega Drive

Origem: transcricao anexada em 2026-06-17 sobre parallax no NES e aplicacao no
Mega Drive, evidencia `E1_text`. Absorver apenas como regra operacional
candidata; nao promove runtime, budget, ROM ou qualidade final.

### O que aproveitar

- Conteudo de NES/Sprite 0/MMC3 serve como analogia historica, nao como tecnica
  operacional do Mega Drive. Traduzir sempre para VDP: `HSCROLL_LINE`,
  `HSCROLL_TILE`, `WINDOW`, H-Int ou plano separado.
- Parallax por bandas rigidas deve declarar `scanline_band_map`: linha inicial,
  linha final, plano dono, ratio de scroll, prioridade visual e costura entre
  bandas.
- Estrada/piso pseudo-3D deve declarar `horizon_line`, curva de ratio por linha
  (formula ou LUT), range minimo/maximo, sinal do offset, camera source e
  fallback para scroll por banda/tile se a tabela por linha nao couber.
- Agua, calor, nevoa e distorcao otica precisam de tabela autorada para a arte;
  nao aplicar offsets de linha em arte arbitraria que rasgue silhueta ou HUD.
- Quando o efeito usa `VDP_setHorizontalScrollLine`, declarar tamanho da tabela,
  metodo de transferencia, janela de update e conflito com outros sistemas que
  tambem escrevem HScroll.

### Rejeicoes desta fonte

- Nao copiar busy-wait/Sprite 0/MMC3 como padrao mental para Mega Drive.
- Nao chamar a tecnica de "camadas infinitas"; line scroll cria variacao dentro
  de plano, nao planos independentes reais.
- Nao prometer estrada 3D perfeita por gradiente linear simples; a curva precisa
  ser ajustada a arte, camera, velocidade e leitura de gameplay.
- Nao copiar demo com input/debug/texto para producao; input, camera e HUD tem
  skills donas.

## Handoff

- Use `shadow-highlight-scroll-fx` when Shadow/Highlight is part of the same scene.
- Use `vram-streaming-dma-queue` for animated tiles in the effect area.
- Use `aaa-pipeline-guardian` for AAA scene claims.
