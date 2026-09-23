---
name: input-system-sgdk
description: Use quando controle SGDK precisar de held, pressed, released, debounce, repeat, buffer, 6-button, 1P/2P ou multitap com leitura centralizada.
---

# Input System SGDK

Centraliza o hardware e entrega estados semanticos para cenas.

## APIs SGDK 2.11 verificadas

- `JOY_init`, `JOY_update`, `JOY_readJoypad`
- `JOY_getJoypadType`, `JOY_getPortType`, `JOY_setSupport`

`JOY_read`, `JOY_getPort` e `JOY_readAll` nao sao APIs de leitura validas.

## Contrato Operacional

### Entrada minima

- mapa de acoes e pads suportados
- politicas de held/pressed/released
- repeat, debounce e buffer
- reservas de botoes no game flow

### Saida minima

- `input_mapping_contract`
- `input_latency_contract`
- `multiplayer_input_plan` quando aplicavel
- snapshot de input por frame e fixtures

### Passa quando

- `JOY_update` ocorre uma vez por frame
- cenas consomem snapshot/acoes, nao leem hardware diretamente
- pressed/released derivam do frame anterior
- 6-button depende de deteccao real
- transicoes limpam buffers e locks

### Handoff para proxima etapa

- entregar API semantica a `scene-state-architect` e `sgdk-runtime-coder`
- entregar probes observaveis a `emulator-vdp-evidence-curator`

## Regras

- Inicializar suporte antes de assumir dispositivo especial.
- START respeita game flow; bind temporario nao pode contradizer pause/title.
- Input enviado pelo host so prova navegacao quando a ROM o observa.

## Anti-padroes

- polling espalhado por cenas
- inferir 6-button
- repetir press por contador local em cada menu
- manter input travado apos transicao
