# 00 - Project Brief - Celestial Chase Revive

## Status

`documentado`. Este brief abre a producao do Revive; nao existe ROM, build, BlastEm ou budget medido do Revive.

## Frase de Produto

`Celestial Chase Revive` e um jogo de acao/corrida para Mega Drive em que um mensageiro celeste foge por uma estrada astral em colapso, revive os Faros do Ceu com upgrades e enfrenta o Mestre Perseguidor no limiar do ultimo portal.

## Decisoes Criativas

- Heroi: `Lio`, mensageiro celeste pequeno, rapido e vulneravel.
- Catalizador: o Farol-Matriz e quebrado durante a cerimonia de reativacao dos ceus.
- Antagonista: `Mestre Perseguidor`, uma entidade cervo-maquina ancestral que cresce de sombra distante para boss setpiece.
- Objeto dramatico: `Nucleo Lumen`, a carga que mantem viva a rota de fuga e alimenta upgrades.
- Fantasia jogavel: velocidade, leitura de faixa, risco crescente, recuperacao ativa e confronto final.

## Pilares

- Velocidade legivel: todo efeito de velocidade precisa melhorar a leitura de rota, perigo ou recompensa.
- Espetaculo com consequencia: shake, flash, hitstop, parallax e audio alteram risco, timing ou decisao.
- Evolucao em corrida: upgrades nao sao menu decorativo; cada um muda como o jogador responde a pressao.
- Boss como persecucao transformada: o final nao vira outro jogo, ele converte a pressao da corrida em duelo de weak points.
- Mega Drive honesto: sem Mode 7, sem alpha real, sem heap no loop, sem DMA fora de VBlank.

## Escopo do Vertical Slice

Entra no primeiro slice:

- abertura curta do catalizador em FSM de cutscene;
- title/menu com identidade propria;
- corrida inicial com tres faixas, salto, Pulse, pressao e coleta;
- uma tela de upgrade simples apos o primeiro setor;
- prototipo de boss approach sem final completo;
- plano de evidencia BlastEm.

Fica para marcos posteriores:

- campanha completa de 5 setores;
- boss final completo em multiplas fases;
- persistencia SRAM final;
- assets premium finais de todos os personagens;
- release/legal/marketing.

## Referencia Herdada do Benchmark

O benchmark provou que a familia visual de corrida celeste pode rodar com:

- BG_A/B separados;
- line scroll para velocidade;
- sprites grandes source-baked;
- evidencia BlastEm e VDP dump;
- blockers visuais honestos.

O Revive herda apenas a disciplina de budget e gate. Nao herda arte final, caminhos absolutos, status AAA ou aprovacao perceptual.
