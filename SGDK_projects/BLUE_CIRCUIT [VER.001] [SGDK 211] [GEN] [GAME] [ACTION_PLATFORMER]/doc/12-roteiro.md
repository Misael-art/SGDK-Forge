# 12 - Roteiro Narrativo - BLUE_CIRCUIT [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

> Use este documento quando o projeto tiver historia, dialogos ou encontros narrativos.
> Se nao houver narrativa, mantenha como placeholder.

## Roteiro Scope

- Textos formais neste slice: title, HUD tecnico minimo e ending.
- O storyboard conta a narrativa visual sem briefing longo: entrar na
  subestacao, neutralizar drones, atravessar energia instavel e desligar o
  nucleo `breaker_core`.
- Dialogo, cutscene longa, retratos falantes e lore ficam fora do primeiro
  slice.

## Tom geral

- Tom: urgente, tecnico e esperancoso.
- O personagem age como resgate/manutencao, nao como soldado ou mascote derivativo.
- A ameaca e uma subestacao automatizada em isolamento, nao um vilao falante.

## Estrutura de encontros

- `title_screen`: apresenta a subestacao e a marca autoral `BLUE_CIRCUIT`.
- `entry_conduit`: mostra que o personagem esta entrando para resolver uma falha.
- `sentry_lane`: o drone `line_sentry` comunica seguranca automatizada ativa.
- `charge_bridge`: o hazard amber comunica energia instavel e timing de pulo.
- `breaker_core_arena`: o nucleo de seguranca vira o pico de leitura e combate.
- `ending_screen`: a subestacao estabiliza e fecha a missao.

## Dialogos por cena

### Title screen

- **Speaker:** sistema visual
- **Texto:** `BLUE_CIRCUIT` / `PRESS START`

### Ending screen

- **Speaker:** sistema visual
- **Texto:** `SUBSTATION STABILIZED` / `MISSION COMPLETE`

## Regras de escrita

- Maximo 2 linhas por tela textual.
- Sem dialogo durante gameplay no primeiro slice.
- Sem termos de franquias, nomes protegidos ou referencias diretas a jogos
  existentes.
- Texto final precisa caber em fonte legivel no Mega Drive e passar por QA de
  leitura em 320x224.
