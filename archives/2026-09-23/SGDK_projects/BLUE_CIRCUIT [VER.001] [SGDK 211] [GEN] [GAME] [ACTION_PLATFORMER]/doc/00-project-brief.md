# 00 - Project Brief - BLUE_CIRCUIT [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

## Contexto

- Tipo de trabalho: `aaa_game`
- Teto de promessa: `vertical_slice`
- Frase do projeto: um action platformer curto em que um tecnico de resgate atravessa uma subestacao viva, corre, pula e dispara pulsos para religar o nucleo Blue Circuit.
- Publico alvo: jogadores que gostam de acao/plataforma 16-bit responsiva, leitura limpa e desafio curto.
- Plataforma alvo: Mega Drive / SGDK 2.11
- Status operacional: `documentado`; runtime de entrega bloqueado ate fonte premium, aprovacao humana, conversao VDP, build canonico e evidencia BlastEm.

## Pilares

- Controle imediato: correr, pular e atirar devem responder em um frame logico previsivel, com input centralizado.
- Leitura antes de espetaculo: inimigos, tiros, plataformas e hazards precisam ser claros antes de receber qualquer FX.
- Identidade autoral: energia azul, manutencao industrial, placas de circuito, alertas amber e contrastes magenta/verde-lima; benchmark nenhum vira fonte visual, audio ou layout.
- Escopo curto e fechado: uma fase pequena, um heroi, um inimigo comum, um mini-boss, tela de titulo e tela de fim.
- Verdade de Mega Drive: sem `float`, sem heap no loop, sem API SGDK inventada, sem DMA fora do VBlank e sem declarar pronto sem BlastEm.

## Escopo

### Dentro

- Title screen com logo autoral, press start e feedback simples.
- Uma fase curta chamada `stage_01_blue_circuit`.
- Um personagem jogavel com correr, pular e atirar.
- Um inimigo comum com telegraph simples e comportamento repetivel.
- Um mini-boss simples com ataque telegraphed, vulnerabilidade clara e fim de fase.
- HUD minimo: vida do jogador, vida do mini-boss quando ativo e indicador simples de estado.
- Tela de fim com resultado da missao.

### Fora

- Dash, wall jump, charge shot, armas alternadas, password, save, loja, mapa, multiplas fases e multiplos bosses.
- Qualquer personagem, nome, sprite, musica, silhueta, paleta ou identidade visual protegida.
- Asset procedural, debug ou placeholder como arte final.
- Claims `ready_for_aaa`, release ou 60 FPS sem build e evidencia.

## Primeiro Resultado Valido

- Entrega minima: vertical slice curta, com title -> fase -> mini-boss -> fim.
- Evidencia minima: build canonico, `out/rom.bin`, `validation_report.json`, screenshot BlastEm, `save.sram`, `visual_vdp_dump.bin` quando o bloco visual canonico estiver ativo, freshness audit e memory/changelog sincronizados.
- Criterio de sucesso: o jogador consegue iniciar, atravessar a fase, derrotar o mini-boss e chegar ao fim em ROM observada no BlastEm, sem arte final bloqueada e sem drift de evidencia.

## Riscos Principais

- Risco: parecer derivativo demais de uma franquia conhecida.
  Mitigacao: usar referencias apenas para ritmo e qualidade; documentar identidade autoral e bloquear clone visual/audio.
- Risco: abrir runtime antes da arte e dos contratos.
  Mitigacao: manter `runtime_admission_report` bloqueado ate premium source + aprovacao humana + VDP conversion.
- Risco: escopo crescer por desejo de fluidez.
  Mitigacao: limitar o primeiro slice a correr, pular, atirar, um inimigo e um mini-boss simples.
- Risco: placeholders do template parecerem evidencia.
  Mitigacao: memory e changelog de 2026-06-25 invalidam qualquer hash/copied build herdado do template.

## Decisao de Abertura

- Data: 2026-06-25
- Decisor humano: usuario da sessao
- Decisao: `aaa_game` com teto `vertical_slice`
- Motivo: o pedido define um jogo jogavel curto com inicio, gameplay, fim e curadoria de arte, nao apenas um benchmark tecnico.
