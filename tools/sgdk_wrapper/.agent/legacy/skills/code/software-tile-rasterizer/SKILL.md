# software-tile-rasterizer

Use when a project proposes CPU-rendered pseudo-3D, polygon-like effects, raycast strips, pre-rendered video-style updates or any effect that rewrites tile graphics at runtime.

## Purpose

Make software rendering on a tile-based VDP explicit and bounded. The Mega Drive can fake effects by updating tile patterns, but the CPU, DMA and VRAM costs are severe.

## Required Inputs

- Target visual effect and resolution.
- Tile buffer dimensions.
- Update frequency.
- DMA upload plan.
- Gameplay relevance and fallback.

## Required Outputs

- Tile buffer layout.
- Dirty tile update plan.
- CPU and VBlank budget risk.
- Visual fallback if full-rate rendering fails.

## Hard Rules

- Do not describe CPU-rendered effects as native hardware scaling/rotation.
- Do not update large pattern regions every frame without a DMA budget.
- Do not mix gameplay-critical logic with unbounded software rendering loops.

## Pseudo-3D e software rendering candidato

Origem: itens de software 3D / pseudo-Mode 7 / rotozoom / wireframe / polígonos
simples / fullscreen rotation do lote `curation_batch_2026_06_16`, evidência
`E1_text`, expansão candidata. Reusa os contratos/saídas existentes (tile buffer
layout, dirty tile update plan, CPU/VBlank budget, visual fallback) e os
handoffs para `vram-streaming-dma-queue` e `megadrive-vdp-budget-analyst`; não
cria schema novo e não promete AAA/runtime.

- O Mega Drive **não tem Mode 7 nativo**. Toda escala/rotação de tela é truque de
  software por tile rewrite + DMA, nunca scaling/rotation de hardware.

### Padrões aceitos com restrição

- **Fake Mode 7** por line scroll, z-map ou tile rewrite: sempre nomear a técnica
  real usada (`line_scroll_floor`, `z_map_tile_rewrite`, `prerender_panels`); não
  vender como "Mode 7".
- **Rotozoom / fullscreen rotation**: apenas com buffer/tabela pré-computada,
  dirty tiles e budget de DMA por frame declarado.
- **Perspectiva de estrada estilo OutRun** via `HSCROLL_LINE`/`HSCROLL_TILE`
  pertence **primeiro** a `hscroll-linescroll-road-fx`; `software-tile-rasterizer`
  só entra se houver tile rewrite / CPU raster real.
- **Wireframe**: 3D em `fix16` → projeção 2D → raster de linhas em tile/pixel
  buffer.
- **Triângulos sólidos simples**: scanline fill para buffer pequeno, dirty tile
  map e upload por DMA.
- **Polygon-like effects** são aceitos como cena especial ou laboratório, nunca
  como default de engine.

### Budgets e blockers

- Toda técnica que reescreve tiles em runtime exige `per_frame_dma_budget_report`,
  `cpu_frame_budget_report` e reset/teardown declarados.
- Fullscreen rotation exige aprovação de `megadrive-vdp-budget-analyst` antes de
  produção.
- Polígonos 3D por software ficam como **P3/laboratório** até existir fixture
  local; não promover número (ex.: "200 tris/seg") sem benchmark local.
- Nenhum claim de runtime sem ROM/emulador; nenhum claim de VDP sem
  dump/telemetria quando aplicável.

### Anti-padrões

- chamar pseudo-Mode 7 de Mode 7 nativo;
- rasterizar a tela inteira sem medir DMA/CPU;
- prometer engine 3D genérica;
- usar `float`/`double`;
- usar `malloc`/`free`;
- sobrescrever tiles compartilhados sem dirty map e ownership.

### Skill deferida

- `software-polygon-renderer` permanece **deferred P3** e **não foi criada**;
  software-tile-rasterizer cobre pseudo-3D/polygon-like de forma bounded até
  existir fixture real que justifique uma skill separada.
- Produção real exige fixture, budget, ROM/emulador, evidência VDP/VRAM e code
  review.

## Handoff

- Use `vram-streaming-dma-queue` for uploads.
- Use `megadrive-vdp-budget-analyst` for budget validation.
- Use `hscroll-linescroll-road-fx` for line/tile scroll road perspective (owner).
- Use `aaa-pipeline-guardian` for advanced visual claims.
