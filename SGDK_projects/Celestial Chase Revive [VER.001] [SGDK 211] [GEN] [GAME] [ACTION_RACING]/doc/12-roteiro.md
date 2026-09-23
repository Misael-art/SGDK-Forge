# 12 - Roteiro - Celestial Chase Revive

## Status

Roteiro de producao para specs. Dialogos e textos estao prontos para virar string table, mas ainda nao foram testados em ROM.

## Tom

Urgente, luminoso, melancolico e heroico. A ameaca e colossal; a resposta do jogador e precisa, pequena e teimosa.

## Estrutura Geral

1. Abertura: o Farol-Matriz racha.
2. Catalizador: Lio pega o Nucleo Lumen.
3. Inicio da acao: a estrada acorda e a corrida comeca.
4. Evolucao: farois menores liberam upgrades e power-ups.
5. Desfecho: o Mestre Perseguidor se materializa e vira boss.
6. Final: Lio revive a rota celeste ou perde a luz.

## Cutscene Principal - `opening_catalyst_cutscene`

Formato: FSM de paineis, texto curto, fades seletivos, pan por scroll e stingers. Nao e video.

### Contrato de Texto

- Maximo de 2 linhas simultaneas.
- Maximo alvo: 26 caracteres por linha.
- Texto dramatico deve usar pausa por pontuacao.
- A/START acelera typewriter; pressionar depois do texto avanca.
- Nenhum texto pode cobrir rosto, Nucleo Lumen, estrada ou telegraph.

### FSM de Abertura

| Estado | Duracao | Painel | Texto | Movimento | Audio |
|---|---:|---|---|---|---|
| `OP_00_BLACK_STINGER` | 60 | preto | `THE SKY ROAD SLEPT.` | fade in lento | drone baixo |
| `OP_01_LIGHTHOUSE_WIDE` | 150 | Farol-Matriz em BG_B/BG_A | `UNTIL THE LAST BEACON CRACKED.` | pan vertical curto | sino FM |
| `OP_02_LIO_CLOSEUP` | 120 | close de Lio | `LIO, RUN.` | blink/reaction frame | voz sintetica curta opcional |
| `OP_03_CORE_INSERT` | 90 | Nucleo Lumen na mao | `CARRY THE LUMEN.` | palette pulse PAL2 | shimmer PSG |
| `OP_04_HART_SHADOW` | 150 | sombra do Mestre Perseguidor | `DO NOT LET IT REMEMBER YOUR NAME.` | shake 3 frames + flash | impacto grave |
| `OP_05_GATE_BREAK` | 120 | portao abre na estrada | `THE ROAD AWAKENS.` | hscroll/palette ramp | inicio da musica |
| `OP_06_CONTROL_HANDOFF` | 60 | Lio na primeira faixa | sem texto | letterbox recolhe | beat de largada |

### Storyboard Textual

1. Preto absoluto. Um ponto de luz respira.
2. O Farol-Matriz ocupa a tela, rachado de baixo para cima.
3. Lio surge em close-up, olhos iluminados por Lumen.
4. Maos pequenas seguram o nucleo; a paleta esquenta.
5. A silhueta do Mestre Perseguidor aparece como chifres no horizonte.
6. A camera desce para a estrada; linhas de fuga viram a pista jogavel.
7. Controle retorna sem corte brusco.

### Motion Beat Map

- `hold`: estados 0 e 1 usam pausa dramatica para escala.
- `blink_or_mouth`: Lio pisca no close; sem dublagem completa.
- `pan_or_scroll`: Farol e estrada usam pan por scroll.
- `reaction_frame`: Lio muda sobrancelha/olho quando ouve "RUN".
- `impact_motion`: gate break usa shake e flash curto.
- `stillness_justification`: core insert fica quase parado para leitura do objeto.

## Textos In-Game

### Title

- `CELESTIAL CHASE REVIVE`
- `START RUN`
- `UPGRADES`
- `RECORDS`
- `CREDITS`

### Cards de Fase

- Setor 1: `THE ROAD AWAKENS`
- Setor 2: `FOLLOW THE FALLING STARS`
- Setor 3: `THE GLASS BRIDGE SINGS`
- Setor 4: `SHADOWS HAVE HOOVES`
- Setor 5: `TURN AND FACE IT`

### Intermissao de Upgrade

- `A BEACON ANSWERS.`
- `CHOOSE ONE LIGHT.`

### Boss Approach

- `IT IS NO LONGER BEHIND YOU.`
- `IT IS THE ROAD.`

### Vitoria

- `THE FAROS LIVE AGAIN.`
- `THE CHASE BECAME A CONSTELLATION.`

### Falha

- `THE LIGHT WAS CAUGHT.`
- `RISE. RUN. RETURN.`

### Creditos

Pagina 1:

- `A MEGA DRIVE PROJECT`
- `CELESTIAL CHASE REVIVE`
- `VER.001 SGDK 2.11`

Pagina 2:

- `DESIGN`
- `GAME DESIGN`
- `SCENE DIRECTION`
- `TECHNICAL DESIGN`

Pagina 3:

- `ART AND AUDIO`
- `PIXEL ART`
- `CUTSCENE ART`
- `MUSIC AND SFX`

Pagina 4:

- `TOOLS`
- `SGDK 2.11`
- `BLASTEM VALIDATION REQUIRED`

Pagina 5:

- `THANK YOU`
- `RUN TOWARD THE LIGHT`

## Desfecho Final

O Mestre Perseguidor para de correr atras. Ele ocupa o horizonte, baixa os chifres e transforma a estrada em arena. A corrida continua em faixas, mas agora cada faixa tambem alinha weak points.

Sequencia:

1. Quebrar o primeiro chifre para reduzir ondas laterais.
2. Quebrar cascos para reduzir impactos de pista.
3. Carregar Pulse com Lumen expelido pelo boss.
4. Acertar o Nucleo Peitoral durante janela curta.
5. A estrada estabiliza e os farois acendem em cadeia.

## Regras de Escrita

- Nada de exposicao longa em gameplay ativo.
- O jogador deve entender pelo visual antes do texto.
- Nomes proprios aparecem pouco: Lio, Lumen, Mestre Perseguidor.
- Evitar humor quebrando tensao.
- Texto de tutorial fica no menu ou em cards curtos, nunca como debug.
- Creditos usam cards paginados com texto em caixa alta ate existir budget para nomes reais e charset expandido.
