# 00 - Project Brief - TAIKETSU ULTRA REBIRTH [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

Este documento e o contrato curto de intencao. Ele existe para impedir que o agente comece arte, codigo ou curadoria sem entender o tipo de trabalho.

## Contexto

- Tipo de trabalho: aaa_game
- Teto de promessa atual: vertical_slice; o destino E2E D0-D6 permanece declarado, sem promover ready_for_aaa
- Frase do projeto: Um duelo 2D de Mega Drive onde cada golpe disputa espaco, leitura e carga de especial ate a arena virar palco cinematografico.
- Publico alvo: jogadores de fighting games arcade e comunidade de desenvolvimento Mega Drive
- Plataforma alvo: Mega Drive / SGDK 2.11

## Pilares

Defina 3 a 5 pilares que guiam todas as decisoes.

- Pilar 1: combate fisico com frame data, hitstop e resposta legivel
- Pilar 2: identidade visual SNK 1996/SVC reinterpretada autoralmente em pixel nativo
- Pilar 3: cutscenes que movem retrato, corpo e camera ao mesmo tempo
- Pilar 4: ambicao maxima limitada por medicao real de VDP, VRAM, DMA e 60fps

## Escopo

### Dentro

- D0 fundacional: GDD, TDD, opt-in fighting e cobertura de capacidades
- D1 vertical slice: Jack contra Kairo Vant, stage Cinder Circuit, especial e uma CS-A/CS-D/CS-E
- D2-D6: roster, cutscenes, 30 dialogos ordenados, chefe desbloqueavel, audio final e pacote de aceitacao

### Fora

- online/rollback, tag team e arena 3D
- qualquer asset final nascido de primitivas procedurais ou sem aprovacao visual humana
- promocao `ready_for_aaa` antes do self-check de medicao 18/18 e dos gates humanos P1-P3

## Primeiro Resultado Valido

- Entrega minima desta abertura: D0 fechado com Q1; primeiro alvo jogavel: D1
- Evidencia minima: manifests validos, reports dos validators, ROM buildada pela Wine bridge e depois evidencia BlastEm selada pelo hash da ROM
- Criterio de sucesso: cada degrau fecha apenas com os artefatos e gates declarados no roadmap; status tecnico nunca e inferido de documento

## Riscos Principais

- Risco: seis lutadores excedem VRAM se residentes juntos
  Mitigacao: streaming por luta; somente os dois ativos residentes, medido por audit_tile_residency
- Risco: dois lutadores grandes excedem sprites por scanline
  Mitigacao: vdp_scanline_simulator antes da arte e fallback de efeitos sem flicker
- Risco: 30 dialogos explodem o escopo
  Mitigacao: produzir somente CS-E do D1 antes do fechamento P1; D4 fica bloqueado por degrau
- Risco: gap de medicao 17/18
  Mitigacao: manter teto honesto e bloquear ready_for_aaa

## Decisao de Abertura

- Data: 2026-09-05
- Decisor humano: convite E2E TAIKETSU ULTRA REBIRTH
- Decisao: create_new_project + aaa_game + opt-in fighting_2d_traditional
- Motivo: solicitacao explicita autoriza projeto novo, roster de 6, fighting 2D e loop em degraus com evidencia real
