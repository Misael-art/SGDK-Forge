# Skill Promotion Candidates

Este arquivo lista candidatos locais que talvez merecam virar skill, workflow, regra, script ou `lib_case` canonico no futuro.

Nenhum item aqui esta promovido.

| Data | Classificacao | Candidato | Problema resolvido | Evidencia minima | Risco | Proxima revisao humana |
|---|---|---|---|---|---|---|
| 2026-08-18 | `promotion_candidate` | Patch em sgdk-runtime-coder: unpack IMAGE BEST e load-time | Impedir unpack APLIB no display; dest estatico; assar TILE_ATTR; DataRect+DMA | ROM e6437530/ceaa7028; d3/d4 cpu 160→83 | medio (API dest.tilemap) | Humano confirma texto da skill + teste de unpack |
| 2026-08-18 | `promotion_candidate` | Patch em emulator-vdp-evidence-curator: VLAB != beat | Screenshot e autoridade; frame_counter e degrau de 60; void escuro pode ser recusado e ainda ser evidencia | d2_reveal/d2_lock mesmo F151; d5_sky rejected | baixo | Humano aceita nota no selo |
| 2026-08-18 | `promotion_candidate` | Patch em shadow-highlight-scroll-fx: VSCROLL_COLUMN nao e cortina | Nao vender coluna como lift local da COIFA | pres4/pres6; memoria | baixo | Ja esta na doutrina; so explicitar o anti-padrao |


## Criterios minimos

- Deve ter sido usado com sucesso em contexto real do projeto.
- Deve reduzir erro recorrente, custo de producao ou ambiguidade.
- Deve ter limites declarados.
- Deve exigir revisao humana antes de qualquer mudanca canonica.
