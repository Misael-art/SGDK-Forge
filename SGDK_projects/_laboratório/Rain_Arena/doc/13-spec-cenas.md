# 13 - Especificacao Tecnica por Cena — Rain_Arena

> Este documento define os limites tecnicos de cada cena.
> Nao altere sem ordem expressa do usuario.
> Toda mudanca de efeito visual deve respeitar estes budgets.

## Cena: Rain Arena - Slice de Chuva

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| VRAM (tiles) | 900 | 853 |
| DMA por frame | 1600 words | 800 tipico / 1488 pico |
| Sprites SAT | 80 | 40 |
| Paletas | 4 | 3 |
| Efeito dominante | scroll horizontal + troca de paleta | ativo |

### Observacoes

- 757 tiles artisticos entram via `bg_sky` e `bg_temple`; o sprite engine reserva mais 80 tiles para 40 gotas simultaneas.
- O pico de DMA acontece quando o flash de paleta coincide com frames de splash de 2 tiles.
- O eixo de audio desta cena fecha como silencio intencional: o slice nao declara recursos XGM/PCM/PSG nem chama rotinas de audio.
- O loop jogavel minimo usa HUD textual em `WINDOW` e reaproveita a cena existente sem introduzir arte nova nem ampliar a pressao de sprites.

