# Shadow Dancer Revisitado - conversao SGDK 2.11

## Contexto

- Tipo de trabalho: technical_demo / engine conversion
- Teto de promessa: technical_demo
- Frase do projeto: adaptar a base tecnica do beat 'em up Shadow Dancer para um runtime SGDK 2.11 auditavel.
- Plataforma alvo: Mega Drive, SGDK 2.11, 320x224 H40
- Genero do projeto: beat 'em up; o slice atual cobre mapa, locomoção e base de colisão, não o combate completo.

## Pilares

- mapa grande com memoria residente limitada;
- movimento em fixed-point e colisao dentro dos limites do mapa;
- DMA agendado para VBlank e loop deterministico;
- documentacao e claims menores que a evidencia disponivel.

## Escopo atual

Dentro: quatro mapas, tileset nao comprimido, cache virtual de 576 tiles, player, gravidade, pulo, camera com dead zone, input 1P e validacao de recursos.

Fora nesta conversão: inimigos, combate, HUD final, audio, saves, title screen, multiplayer, arte nova e release comercial.

## Primeiro resultado valido

- Entrega minima: build SGDK 2.11 da copia em `SGDK_projects`.
- Evidencia minima: `out/logs/validation_report.json` e, depois, captura BlastEm vinculada ao hash da ROM.
- Criterio de sucesso: build sem API legada, sem malloc/free no runtime, sem DMA imediato no callback e sem blockers de recurso.

## Riscos

- A fila DMA pode estourar em scroll agressivo; medir em NTSC e registrar fallback.
- O mapa de colisao legado possui semantica compacta; validar contato em BlastEm antes de alterar a fisica.
- Os PNGs tem avisos de quantizacao 9-bit; o estado atual e placeholder, nao visual final.

## Decisao de abertura

- Data: 2026-09-21
- Decisor: agente, por inferencia do pedido de conversao
- Decisao: technical_demo
- Motivo: o material original e uma engine/experimento de mapa virtual e nao contem escopo de jogo completo.
