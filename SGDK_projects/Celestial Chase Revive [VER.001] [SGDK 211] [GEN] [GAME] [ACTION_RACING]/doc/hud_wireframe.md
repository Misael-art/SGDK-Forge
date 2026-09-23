# HUD Wireframe - Celestial Chase Revive

Status: `documentado`.

Resolucao alvo: `320x224`.

HUD runtime: `WINDOW` fixo no topo, `0..23px`. Gameplay comeca em `y=24`.

```text
0px   +--------------------------------------------------------------------------------+
      |                                                                                |
8px   |  [I][I][I]   LUM 000     PRS [################----------------]  PUL [####] FCS 00 |
      |                                                                                |
24px  +--------------------------------------------------------------------------------+
      |                                                                                |
      |                         PLAYFIELD / ROAD / SPRITES                             |
      |                                                                                |
224px +--------------------------------------------------------------------------------+
```

## Coordenadas

| Elemento | X | Y | W | H | Observacao |
|---|---:|---:|---:|---:|---|
| Integrity | 8 | 8 | 28 | 8 | 3 icones 8x8 com gaps de 2px |
| Lumen | 44 | 8 | 48 | 8 | `LUM` + 3 digitos |
| Pressure label/bar | 104 | 8 | 96 | 8 | `PRS` + barra 64px |
| Pulse label/bar | 208 | 8 | 56 | 8 | `PUL` + barra 32px |
| Focus | 272 | 8 | 40 | 8 | `FCS` + 2 digitos ou marcador |

## Regras

- Nada pode deslocar layout durante animacao.
- Texto usa fonte custom 8px; SGDK default e debug only.
- Pressure >= 80 usa flash de paleta em `PAL0_ui`, nao sprite extra.
- Boss troca `FCS` por 4 marcadores de weak point sem mudar o resto do HUD.
- HUD nao cobre telegraph, lane, Lio ou boss weak point.

## Pendencias

- Arte final do atlas.
- Captura BlastEm.
- `visual_delivery_gate_report.json`.
