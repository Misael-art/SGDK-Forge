# 16 - Level Design Document - BLUE_CIRCUIT [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

Use este documento quando o contexto envolver jogo completo, vertical slice ou
cena jogavel com mapa, progressao ou encounter design.

## 1. Escopo

- Cena/fase: `stage_01_blue_circuit`.
- Objetivo do jogador: atravessar a subestacao e desligar o `breaker_core`.
- Duracao alvo: 2 a 4 minutos no primeiro playable.
- Primeira acao memoravel: correr pelo `entry_conduit` com energia azul viva ao fundo.
- Ultima acao memoravel: derrotar o `breaker_core` e ver a subestacao estabilizar.

## 2. Mapa Logico

- Entrada: `entry_conduit`, chao seguro e leitura ampla.
- Golden path: entrada -> `sentry_lane` -> `charge_bridge` -> `breaker_core_arena`.
- Rotas opcionais: nenhuma no primeiro slice.
- Checkpoints: nenhum no primeiro slice.
- Saida: `exit_stabilized` apos derrota do mini-boss.

## 3. Ritmo

| Beat | Funcao | Intensidade | Mecanica exigida | Evidencia |
|---|---|---|---|---|
| 1 | tutorial de movimento no `entry_conduit` | baixa | correr/pular | storyboard gate |
| 2 | primeiro `line_sentry` | media | atirar e espacamento | model/sprite gates |
| 3 | `charge_bridge` | media | pulo com hazard amber | storyboard gate |
| 4 | `breaker_core_arena` | alta | telegraph, tiro e janela vulneravel | model/sprite gates |
| 5 | `exit_stabilized` | baixa | encerramento | storyboard gate |

## 4. Relacao Camera-Cenario

- Camera principal: side-view platform.
- Deadzone: horizontal curta ao redor do player.
- Lookahead: leve na direcao do movimento, apenas apos contrato de camera.
- Travamentos ou arenas: arena do `breaker_core` fecha bounds.
- Risco de leitura: fundos ciano nao podem engolir player, tiros ou hazards.

## 5. Tecnicas de Hardware

- Parallax: adiado; BG_B atmosferico e BG_A jogavel no primeiro slice.
- Raster/HScroll/VScroll: fora do primeiro slice salvo novo contrato/budget.
- Sprites e oclusao: player, `line_sentry`, projeteis e `breaker_core` por sprites.
- Paletas: cyan/blue energia, amber perigo, magenta weak point, lime status,
  neutros industriais.
- Budget: `nao_medido` ate conversao VDP.

## 6. Fallbacks

- Fallback visual: reduzir detalhe de fundo antes de reduzir legibilidade dos atores.
- Fallback tecnico: remover hit sparks, reduzir simultaneidade e manter preload local.
- Corte de escopo aceitavel: ending mais simples e arena menor; nao cortar o
  mini-boss do primeiro slice.
