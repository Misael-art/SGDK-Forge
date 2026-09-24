# 16 - LDD - Celestial Chase Revive

## Status

Level design especificado para producao inicial.

## Estrutura de Setores

Cada setor possui:

- introducao visual;
- padrao seguro;
- combinacao de risco;
- pickup tentador;
- mini-setpiece;
- transicao para upgrade ou proximo setor.

Cada setor tambem precisa de uma regra mecanica unica. Trocar apenas paleta, nome e velocidade nao basta para `aaa_game`.

## Formato de Dados de Pista

Contrato canonico: `doc/track_data_format_contract.json`.

Decisao: o jogo usa `lane_event_track`, nao matriz bruta de colisao por tile no primeiro slice.

Motivo:

- a corrida tem 3 faixas discretas;
- hazards, pickups e telegraphs precisam de timing deterministico;
- arte da estrada pode evoluir sem quebrar colisao;
- dados podem virar arrays `const` em C sem `malloc`.

Unidade de autoria:

- `track_step`: 16 frames NTSC;
- `lane_id`: 0 esquerda, 1 centro, 2 direita;
- `lane_mask`: bits por faixa;
- eventos possuem `telegraph_steps` e `active_steps`.

Setor 1 ja possui plano inicial em `doc/sector_01_track_plan.json`.

## Golden Path

1. Title.
2. Opening cutscene.
3. Setor 1: aprender troca, salto e Pulse.
4. Upgrade 1: escolher `Drift Step` ou `Guard Shard`.
5. Setor 2: meteoros e padroes diagonais.
6. Upgrade 2: escolher `Star Wake` ou reforco de Pulse.
7. Setor 3: ponte com rotas estreitas.
8. Setor 4: tunel de sombra com pressao alta.
9. Boss approach.
10. Final boss.
11. Resultado.

## Phase Rhythm Map

| Fase | Ritmo | Funcao |
|---|---|---|
| calm | coleta e leitura | ensinar sinal |
| pressure | padroes combinados | cobrar escolha |
| breath | 1 a 2 segundos | reset perceptivo |
| spike | setpiece/impacto | memorabilidade |
| reward | upgrade/luz | progressao |

## Identidade Mecanica por Setor

Contrato: `doc/sector_mechanic_identity_contract.json`.

| Setor | Identidade | Regra unica | Memoria desejada |
|---|---|---|---|
| 1 | primeira fuga real | perseguidor aparece no horizonte e Lumen ainda tem grace inicial | "a coisa esta vindo" |
| 2 | memoria espacial | meteoros caem e viram bloqueios temporarios | "lembro onde caiu" |
| 3 | ritmo da ponte | faixas de vidro somem/reaparecem em compasso | "preciso entrar no ritmo" |
| 4 | reflexo por sombra/audio | telegraph visual e mais curto, audio/sombra avisam antes | "ouvi antes de ver" |
| 5 | confronto | weakpoints transformam corrida em ataque | "virei a caca contra o cacador" |

## Setor 1 - Farol Quebrado

- Faixas: 3.
- Obstaculos: pedra baixa, marca astral, coleta Lumen.
- Novo sistema: Pulse.
- Regra unica: primeira presenca do Mestre Perseguidor em BG_B e grace temporario para Lumen pressure.
- Criterio: jogador deve entender que Pulse reduz pressao e que a perseguicao existe visualmente.

Dados iniciais:

- duracao: 96 `track_steps`, 1536 frames NTSC;
- velocidade: `320..512` em Q8.8 px/frame;
- eventos maximos ativos: 10;
- hazards simultaneos no primeiro slice: 6;
- pickups simultaneos no primeiro slice: 4.

Contratos:

- `doc/track_data_format_contract.json`
- `doc/sector_01_track_plan.json`
- `doc/collision_system_contract.json`
- `doc/entity_archetype_manifest.json`
- `doc/progression_tuning_tables.json`
- `doc/pursuer_presence_contract.json`
- `doc/lumen_pressure_economy_contract.json`

## Setor 2 - Jardim de Meteoros

- Obstaculos diagonais.
- Meteoros aterrissam e viram bloqueios persistentes por 3 a 5 `track_steps`.
- Pickups em faixas de risco.
- Introduz `Time Spark`.
- Criterio: jogador aprende a lembrar onde um meteoro caiu e decidir se gasta Pulse ou economiza para upgrade.

## Setor 3 - Ponte de Vidro Solar

- Pista estreita visualmente, ainda com 3 faixas logicas.
- Faixas somem/reaparecem em ritmo previsivel.
- Ataques de reflexo avisam antes de ficar ativos.
- Introduz `Comet Veil`.
- Criterio: upgrades mudam rota ideal.

Transicao para Setor 4: `shattered_lane_gauntlet`, definida em `doc/signature_setpiece_contract.json`.

## Setor 4 - Tunel de Sombra

- Pressao cresce mais rapido.
- Mestre Perseguidor ataca com cascos e ondas.
- Telegraph visual e mais curto, mas audio/sombra avisam antes.
- Menos texto, mais audio/visual.
- Criterio: preparar boss approach.

## Setor 5 - Coroa do Perseguidor

- Estrada vira arena de faixas.
- Weak points aparecem alinhados a faixas.
- Pulse passa de defensivo para ofensivo.
- O tema musical libera camadas completas por fase de boss.

## Replayability de Setor

Contrato: `doc/replayability_score_contract.json`.

Cada setor gera resultado com:

- tempo;
- porcentagem de Lumen coletado;
- dano tomado;
- Pressure maximo;
- estrelas.

O objetivo nao e bloquear progresso, mas dar motivo para repetir uma corrida curta.

## Reuso de Mecanicas

- Troca de faixa aparece em todos os setores.
- Salto responde a barreiras, ondas e ataques de casco.
- Pulse limpa ameacas, reduz pressao e abre boss window.
- Upgrades alteram timing, margem de erro e recompensa.

## Tutorial Invisivel

- Primeiro pickup na faixa inicial.
- Primeira troca sem perigo.
- Primeiro salto com telegraph longo.
- Primeiro dano seguido de Lumen suficiente para recuperar.
- Primeiro upgrade apos uma vitoria curta.

## Anti-Padroes

- Padrao sem resposta valida.
- Obstaculo surgindo sem telegraph.
- Coleta obrigatoria em rota injusta.
- Boss escondendo a faixa.
- FX que oculta Lio, HUD ou weak point.
