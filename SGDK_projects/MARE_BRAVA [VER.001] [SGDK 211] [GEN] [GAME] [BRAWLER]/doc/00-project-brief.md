# 00 - Project Brief - MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]

Este documento e o contrato curto de intencao. Ele existe para impedir que o agente comece arte, codigo ou curadoria sem entender o tipo de trabalho.

## Contexto

- Tipo de trabalho: aaa_game
- Teto de promessa: vertical_slice
- Frase do projeto: belt scroller brasileiro onde cada golpe tem peso de maré e o cais é arma (ring-out na água), disputando com Streets of Rage 2 em game feel.
- Publico alvo: jogador de beat'em up 16-bit que já esgotou os clássicos e quer identidade nova com a mesma barra de qualidade.
- Plataforma alvo: Mega Drive / SGDK 2.11

## Pilares

- Pilar 1: peso de maré no combate (hitstop, knockback, ring-out costeiro)
- Pilar 2: crowd sempre legível (silhuetas, telegraphs, máximo 4 inimigos ativos)
- Pilar 3: identidade brasileira autoral (muay thai de vila, percussão FM, calor litorâneo)
- Pilar 4: evidência antes de promessa (nada é "pronto" sem BlastEm a 60fps)

## Escopo

### Dentro

- First playable slice CAIS_01: 1 heroína (TAÍNA), 2 arquétipos de inimigo, 1 onda de 3 grupos, ring-out, pickup, HUD, FSM completo (branding/title/gameplay/fim), XGM2

### Fora

- Co-op, boss, armas de chão, fases 2+, cutscenes além de painéis estáticos, qualquer conteúdo de IP protegida

## Primeiro Resultado Valido

- Entrega minima: first playable slice (CAIS_01) rodando no BlastEm
- Evidencia minima: screenshot dedicada BlastEm + save.sram MDRT + validation_report limpo + runtime_metrics com 60fps
- Criterio de sucesso: completar a onda com combo + gerenciamento de espaço, ring-out funcional e legível, 60fps estáveis

## Riscos Principais

- Risco: arte IA não atingir consistência de sprite sheet (estados coerentes entre frames)
  Mitigacao: gerar por estado com referência fixa de personagem; aprovação humana antes de conversão; fallback para reduzir estados do slice
- Risco: pressão de sprites por scanline com 4 inimigos de 44-56px na mesma faixa
  Mitigacao: laudo megadrive-vdp-budget-analyst antes do runtime; trava de 4 ativos; espaçamento por wave manager
- Risco: toolchain Linux/Wine nova neste host quebrar em edge case
  Mitigacao: loop provado com SMOKE_TEST em 2026-07-03; receita documentada na memória do agente; fallback = host Windows original

## Decisao de Abertura

- Data: 2026-07-03
- Decisor humano: Misael (resposta explícita no menu de sessão)
- Decisao: aaa_game, novo projeto, especialização brawler_belt_scroll
- Motivo: usuário escolheu criar novo jogo com opt-in de gênero do registry ativo; workspace tem base de treino de luta (HYBRIDO_MUAY_THAI) reaproveitável em conhecimento
