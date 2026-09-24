# 11 - Game Design Document - Celestial Chase Revive

## Status

GDD em fundacao. Completo para orientar producao inicial, ainda nao validado por ROM.

## Visao

`Celestial Chase Revive` transforma a demo de corrida celeste em um jogo autoral de acao/corrida para Mega Drive. O jogador controla Lio, um mensageiro pequeno carregando o `Nucleo Lumen`, enquanto o Mestre Perseguidor atravessa planos do ceu para recuperar a luz roubada.

O jogo deve parecer rapido, dramatico e justo. A tela esta sempre viva, mas todo espetaculo precisa ter funcao: avisar perigo, abrir rota, alterar timing, comunicar upgrade ou preparar o boss.

## Tese Criativa

`Quanto mais luz voce carrega, mais a coisa te encontra.`

O Lumen nao e apenas moeda. E isca. Guardar Lumen aproxima o Mestre Perseguidor; gastar Pulse alivia o agora, mas atrasa upgrades. A perseguição precisa ser vista, ouvida e sentida desde o primeiro setor.

## Fantasia

Fugir por uma estrada astral em ruinas, reativar farois celestes e virar a perseguicao contra a entidade que estava caçando voce.

## Premissa Narrativa

O Farol-Matriz era o ultimo mecanismo capaz de manter abertas as estradas do ceu. Durante a cerimonia de reativacao, o selo que aprisionava o Mestre Perseguidor racha. Lio pega o Nucleo Lumen e dispara pela estrada antes que a entidade alcance a cidade suspensa.

Cada setor revive um farol menor. Cada farol concede uma tecnica nova ou fortalece uma existente. No fim, Lio nao apenas foge: ele usa os farois recuperados para forcar o Mestre Perseguidor a se materializar e enfrentar o jogador.

## Pilares de Design

1. Leitura antes de punicao.
2. Risco crescente sem caos ilegivel.
3. Upgrades com consequencia em decisoes de faixa, tempo e pressao.
4. Feedback audiovisual sincronizado com mecanica.
5. Boss final como culminacao da corrida, nao interrupcao.
6. Descoberta por setor: cada bioma muda uma regra jogavel.
7. Musica como telemetria emocional da fuga.

## Core Loop

`ler pista -> escolher faixa/salto/Pulse -> coletar Lumen -> sobreviver a pressao -> gastar ou guardar recurso -> receber upgrade -> encarar padrao mais agressivo`

## Loop de Sessao

1. Abertura ou menu.
2. Setor de corrida.
3. Intermissao de upgrade.
4. Setor com nova combinacao de risco.
5. Aproximacao do Mestre Perseguidor.
6. Boss final.
7. Resultado, ranking e creditos.

## Kit do Jogador

- Troca de faixa: tres faixas discretas no primeiro slice; compromisso curto de troca.
- Salto: evita barreiras baixas e ondas rasantes, mas nao atravessa marcas altas.
- Deslizamento Lumen: opcional para fase 2; baixa o perfil por uma janela curta.
- Celestial Pulse: limpa ameacas menores, reduz pressao e abre janela de recuperacao.
- Guard Shard: upgrade que converte um impacto em perda parcial de Lumen.
- Overdrive: upgrade tardio; aumenta velocidade e score, mas acelera padroes.

## Contratos Numericos e Executaveis

- Pista: `doc/track_data_format_contract.json`.
- Setor 1: `doc/sector_01_track_plan.json`.
- Colisao: `doc/collision_system_contract.json`.
- HUD: `doc/hud_layout_contract.json` e `doc/hud_wireframe.md`.
- Animacao: `doc/sprite_animation_contract.json`.
- Progressao/tuning: `doc/progression_tuning_tables.json`.
- Assets: `doc/asset_production_spec.json`.
- Boss: `doc/boss_attack_pattern_contract.json`.
- Pause/game over/continue: `doc/game_flow_contract.json`.
- Build: `doc/build_system_contract.json`.
- Creative cohesion: `doc/creative_cohesion_pass.md`.
- Presenca do perseguidor: `doc/pursuer_presence_contract.json`.
- Economia Lumen/Pressure: `doc/lumen_pressure_economy_contract.json`.
- Identidade mecanica por setor: `doc/sector_mechanic_identity_contract.json`.
- Setpiece assinatura: `doc/signature_setpiece_contract.json`.
- Audio reativo: `doc/reactive_music_gameplay_contract.json`.
- Replay/score: `doc/replayability_score_contract.json`.

## Recursos

- Integridade: 3 pontos base.
- Pressao do Perseguidor: 0 a 100; em 100, falha ou entrada forçada em boss approach.
- Lumen: recurso de coleta usado para Pulse e upgrades, mas carregar Lumen demais aumenta Pressure.
- Foco: medidor temporario que recompensa sequencias sem erro.

## Regras Sistemicas

- A corrida sempre resolve em faixas discretas para manter leitura, colisao e sprite budget controlaveis.
- Toda ameaca precisa ter telegraph visual antes da zona de dano.
- Pressao do Perseguidor sobe com erros, tempo parado em faixa perigosa e coleta ignorada em rotas criticas.
- Pressao do Perseguidor tambem sobe por excesso de Lumen carregado.
- Pressao cai com Pulse bem usado, Beacon Key coletada e sequencias limpas.
- Upgrades nunca removem o risco principal; eles criam novas respostas para o mesmo risco.
- Cada setor precisa ter uma regra mecanica unica alem de velocidade e visual.
- A musica deve mudar densidade conforme Pressure, Lumen e fase do boss.
- O estado do jogo deve ser serializavel em SRAM sem depender de alocacao dinamica.
- Nenhum efeito visual entra se esconder hitbox, faixa segura, boss weak point ou UI vital.

## Progressao da Fase

Cada fase avanca em tres atos: leitura segura, combinacao de risco e assinatura setpiece. O primeiro ato apresenta a regra central do setor com baixa pressao. O segundo ato mistura a regra nova com obstaculos ja conhecidos. O terceiro ato usa camera, paleta, audio e spawn para criar um pico curto antes da intermissao ou do boss approach.

## Mapa de Secoes

| Secao | Papel | Regra Nova | Saida |
|---|---|---|---|
| 0 - Cutscene | catalizador | Nucleo Lumen roubado para sobreviver | corrida inicia |
| 1 - Farol Quebrado | onboarding | primeira presenca do perseguidor + Lumen grace | Pulse Core confirmado |
| 2 - Jardim de Meteoros | memoria espacial | meteoros caem e viram bloqueios temporarios | Drift Step |
| 3 - Ponte de Vidro Solar | ritmo e antecipacao | faixas somem/reaparecem em compasso | Guard Shard |
| 4 - Tunel de Sombra | reflexo audiovisual | telegraph curto com aviso por sombra/audio | Overdrive Gate |
| 5 - Coroa do Perseguidor | climax | boss em estrutura de corrida | final |

## Economia de Lumen sob Risco

Lumen possui quatro bandas:

- `0-19`: seguro.
- `20-39`: +1 Pressure por segundo.
- `40-59`: +2 Pressure por segundo.
- `60+`: +3 Pressure por segundo e cue audiovisual de excesso de luz.

Gastar Pulse custa 20 Lumen e reduz Pressure. Guardar Lumen compra upgrades, mas torna a fuga mais perigosa. O jogador deve sentir que cada orb e uma pergunta.

## Ritmo

O ritmo alterna segmentos de 20 a 40 segundos de decisao intensa com pausas diegeticas curtas de 6 a 12 segundos para upgrade, fala minima ou mudanca de paleta. A cadencia evita longos blocos de texto: a historia aparece como pressao, dano no cenario, mudanca musical e comportamento do perseguidor.

## Tutorial Invisivel

O ensino invisivel usa composicao de pista. O primeiro obstaculo de cada tipo aparece sozinho e com rota segura obvia. A segunda aparicao combina coleta opcional. A terceira cobra decisao sob pressao. Texto em tela so nomeia upgrade; nunca explica controle basico durante a corrida.

## Upgrades

### Pulse Core

Desbloqueia `Celestial Pulse`. E obrigatorio e aparece depois do catalizador.

Funcao: ensinar recuperacao ativa.

### Drift Step

Reduz o tempo de troca de faixa e permite micro-ajuste durante salto.

Funcao: aumentar agency sem criar movimento analogico caro.

### Guard Shard

Primeiro impacto com Lumen suficiente consome recurso em vez de integridade.

Funcao: transformar coleta em seguro de risco.

### Star Wake

Deixa trilha curta que atrai pick-ups proximos.

Funcao: incentivar linhas de corrida agressivas.

### Overdrive Gate

Ativa modo de alto risco: velocidade maior, score maior e pressao visual mais intensa.

Funcao: opcao de maestria e ponte para boss final.

## Power-Ups de Pista

- Lumen Orb: recurso basico.
- Comet Veil: invulnerabilidade curta, sem dano ao boss.
- Time Spark: reduz pressao por poucos segundos.
- Echo Double: afterimage funcional que captura um hit leve; tecnica visual so entra se budget permitir.
- Beacon Key: item de setor que libera upgrade ou abre atalho.

## Estrutura de Campanha

### Setor 1 - Farol Quebrado

Funcao: ensinar faixa, salto, Pulse, pressao e a primeira presenca visual do Mestre Perseguidor.

### Setor 2 - Jardim de Meteoros

Funcao: introduzir meteoros que aterrissam e viram obstaculos persistentes por poucos steps.

### Setor 3 - Ponte de Vidro Solar

Funcao: introduzir faixas de vidro que somem e retornam em ritmo previsivel.

### Setor 4 - Tunel de Sombra

Funcao: pressao maxima, telegraph curto, aviso por sombra/audio e uso de upgrades.

### Setor 5 - Coroa do Perseguidor

Funcao: boss approach e confronto final.

## Mestre Perseguidor

O Mestre Perseguidor comeca como presenca de fundo e termina como boss. Ele possui tres funcoes:

- pressao sistemica durante a corrida;
- ataque setpiece durante transicoes de setor;
- boss final com weak points.

Ele deve ser visivel desde o Setor 1. A silhueta cresce em BG_B, o motivo sonoro entra por Pressure e sombras/cascos passam a antecipar hazards. A barra `PRS` informa, mas a tela deve contar primeiro.

Weak points planejados:

- Chifres: quebram telegraph de ondas amplas.
- Cascos: reduzem ataques de impacto na pista.
- Nucleo Peitoral: encerra a luta apos os farois revividos.

## Boss Final

O boss final preserva a estrutura de corrida:

- jogador ainda ocupa faixas;
- ataques chegam pela estrada;
- weak points aparecem em janelas de alinhamento;
- Pulse vira ferramenta ofensiva quando carregado por Lumen do boss;
- o cenario reage ao dano com paleta, tremor e abertura de rota.

## Momento Assinatura

`shattered_lane_gauntlet`: na transicao Setor 3 -> 4, o Mestre Perseguidor golpeia a estrada, quebra duas das tres faixas e deixa o jogador preso a uma faixa segura por 3 segundos enquanto destrocos caem ao redor. O momento deve ser simples de implementar por `lane_mask`, mas forte o bastante para ser lembrado.

## Replay e Maestria

Cada setor pode conceder ate 3 estrelas por desempenho:

- porcentagem de Lumen coletado;
- dano tomado;
- Pressure maximo;
- tempo alvo.

Recompensas planejadas: lore shards, concept art e modificadores de dificuldade. SRAM e obrigatoria antes de qualquer unlock persistente.

## Criterios de Qualidade Visual

- Lio, faixa segura, ameaca, coleta e UI devem ser legiveis em um frame.
- O Mestre Perseguidor deve parecer monumental sem cobrir telegraphs.
- A estrada precisa parecer profunda sem prometer Mode 7.
- Cutscene deve usar composicao de anime 90s: paineis fortes, foco no rosto/objeto, texto ritmado e movimento minimo dirigido.
- HUD nao pode parecer debug.

## Ambicao Tecnica

- 60 FPS NTSC como alvo.
- Inteiros/fix16/fix32, sem float/double em gameplay.
- Pools estaticos.
- DMA seguro no VBlank.
- Line scroll e palette transitions com owner unico.
- Cena de cutscene como FSM formal.
- Boss setpiece com budget de scanline antes de runtime.

## Tecnicas Escolhidas

As tecnicas escolhidas estao registradas em `doc/technique_usage_manifest.json` e sincronizadas com `doc/13-spec-cenas.md`, `doc/10-memory-bank.md` e `doc/changelog/changelog.md`.

| Registry ID | Uso no jogo | Fallback |
|---|---|---|
| `dma_transfer_safety` | uploads de tiles, sprites e paletas em janela segura | cortar variantes visuais |
| `line_scrolling` | estrada pseudo-3D e instabilidade do perseguuidor | scroll por blocos |
| `pseudo3d_road_stack` | sensacao de profundidade da corrida | estrada mais plana |
| `camera_scroll_management` | leitura de velocidade e setpieces | camera fixa por setor |
| `hitstop_camera_shake_feedback` | impacto sem perder leitura | flash de paleta curto |
| `window_plane_static_hud` | HUD estavel sobre corrida | HUD em BG_A reservado |
| `palette_state_transitions` | mudanca emocional e dano no mundo | troca simples por setor |
| `prerendered_sprite_scaling` | presenca monumental do boss | fewer scale frames |
| `xgm2_audio_architecture` | musica e SFX coordenados | XGM2 simplificado |
| `save_sram_checksum_redundancy` | progresso e evidencia operacional | senha curta ou sem save |

## Direcao Sonora

A direcao sonora combina baixo FM pulsante, arpejos brilhantes e PSG usado como sinal de perigo. A identidade musical deve separar tres estados: fuga limpa, pressao do Perseguidor e overdrive. SFX de coleta ficam curtos e agudos; impacto usa camada grave controlada para nao mascarar telegraphs. A cutscene inicial usa poucos eventos sonoros marcantes: rachadura do selo, pulso do Nucleo Lumen e entrada do tema de corrida.

Musica tambem e feedback jogavel: Pressure baixo usa FM limpo; Pressure medio adiciona PSG percussivo; Pressure alto adiciona densidade agressiva e DAC opcional; boss libera camadas completas por fase.

## Fora de Escopo Inicial

- Multiplayer.
- Fisica analogica completa de veiculo.
- Scaling continuo por hardware inexistente.
- Alpha blending real.
- Persistencia complexa alem de upgrades/highscore.
- Qualquer tecnica `LABORATORIO` como requisito de entrega.

## Criterio do Primeiro Slice

O primeiro slice passa apenas quando:

- title/menu entra e sai corretamente;
- logo possui contrato de identidade e leitura nativa planejada;
- fonte custom de front-end/HUD/cutscene esta registrada e SGDK default fica restrita a debug;
- creditos possuem rota de menu, contrato e retorno ao title;
- track data do `SECTOR_01` existe e compila para arrays estaticos;
- colisao possui hitboxes, layers, resposta e fixtures;
- HUD possui wireframe pixel e coordenadas fixas;
- Lio possui contrato de animacao e alinhamento com hitbox;
- tabela de tuning inicial existe para velocidade, pressao, spawn e upgrades;
- boss possui padroes de ataque e weakpoints documentados;
- build usa wrapper central e declara arquivos minimos do runtime seed;
- abertura curta roda como FSM;
- corrida inicial permite faixa, salto, Pulse e dano;
- uma intermissao de upgrade aparece;
- ROM builda;
- BlastEm confirma boot e cena correta;
- screenshot, `save.sram` e `visual_vdp_dump.bin` existem;
- validadores nao possuem blockers tecnicos;
- memoria e changelog estao sincronizados.
