---
name: camera-system-sgdk
description: Use quando gameplay SGDK precisar de dead zone, look-ahead, bounds, room lock, parallax, screen shake, split-screen ou eixo Z com um owner unico de camera.
---

# Camera System SGDK

Trata camera como subsistema de gameplay, separado de coordenadas de mundo e
do carregamento visual.

## Contrato Operacional

### Entrada minima

- viewport e bounds do mundo
- alvo, eixos permitidos e velocidade
- dead zone, look-ahead e locks
- contratos de level design e parallax

### Saida minima

- `camera_behavior_contract`
- `camera_bounds_policy`
- `parallax_camera_contract` quando aplicavel
- fixtures de clamp, lock, shake e reset

### Passa quando

- mundo, camera e tela usam coordenadas distintas
- scroll final usa pixels inteiros
- bounds evitam revelar area invalida
- shake possui offset temporario e reset garantido
- room/boss lock possui entrada, saida e fallback

### Handoff para proxima etapa

- entregar offsets a `multi-plane-composition` e `sgdk-runtime-coder`
- entregar pior janela ativa a `megadrive-vdp-budget-analyst`

## Regras

- Atualizar camera uma vez por frame, depois da simulacao do alvo.
- Usar `fix16`/`fix32` apenas quando suavizacao exigir; escrever scroll inteiro.
- Look-ahead serve leitura do risco, nao antecipacao cosmetica.
- Parallax deriva da camera canonica; layers nao mantem cameras paralelas.

## Anti-padroes

- mover entidades para simular camera
- aplicar shake acumulativo
- misturar screen-space em colisao
- lock sem teardown
