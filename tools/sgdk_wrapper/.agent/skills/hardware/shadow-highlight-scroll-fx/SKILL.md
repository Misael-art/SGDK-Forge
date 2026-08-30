---
name: shadow-highlight-scroll-fx
description: Use quando uma cena Mega Drive precisar de Shadow/Highlight, HSCROLL_LINE/TILE, VSCROLL_COLUMN, palette cycling, H-Int ou raster FX.
---

# Shadow Highlight Scroll FX

Owner unico de efeitos VDP de scroll, luz e raster. Substitui aliases separados
de line-scroll e raster-palette.

## Contrato Operacional

### Entrada minima

- efeito e funcao de gameplay/narrativa
- planos, paletas e scanlines afetados
- camera, cadence e pior quadro
- owners concorrentes de H-Int/CRAM

### Saida minima

- `scroll_fx_contract`
- `raster_fx_ownership_map`
- palette/scroll tables e teardown
- budget, fallback e plano de evidencia

### Passa quando

- existe um owner de H-Int por cena
- `HSCROLL_LINE`, `HSCROLL_TILE` e `VSCROLL_COLUMN` sao usados com semantica correta
- CRAM e prioridade preservam jogador e HUD
- tabelas e updates cabem no pior quadro
- desligar o efeito possui fallback visual aceitavel

### Handoff para proxima etapa

- entregar tabelas a `sgdk-runtime-coder`
- entregar custo a `megadrive-vdp-budget-analyst`
- entregar prova a `emulator-vdp-evidence-curator`

## Regras

- H-Int/raster e arquitetura de cena, nao decoracao solta.
- Gradiente suave real nao existe; usar rampas, dither ou troca de paleta medida.
- Mid-frame exige screenshot e dump/telemetria apropriada.
- `VSCROLL_COLUMN` nao substitui parallax horizontal.

## Anti-padroes

- dois callbacks H-Int independentes
- line scroll sobre silhueta sem bandas autoradas
- palette swap sem reset
- efeito sem relacao com gameplay ou pulso narrativo
