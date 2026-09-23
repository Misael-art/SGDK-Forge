# 15 - Technical Design Document - BLUE_CIRCUIT [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

O TDD descreve como o jogo sera construido. Ele nao substitui o GDD; traduz as escolhas de design em arquitetura, memoria, VDP, audio, input e validacao.

## 1. Contexto Tecnico

- Contexto do projeto: `aaa_game`
- Teto de entrega tecnica: `vertical_slice`
- Hardware alvo: Mega Drive
- SDK: SGDK 2.11
- Regiao alvo: NTSC 60 Hz e compatibilidade PAL 50 Hz observada no BlastEm.
- Status: `technical_ready_creative_blocked`; existe runtime jogavel medido,
  mas os gates criativos, hardware real e release continuam abertos.

## 2. Arquitetura

- Modelo de cenas: FSM simples com `title_screen`, `stage_01_blue_circuit` e `ending_screen`.
- Estrutura de modulos prevista: `src/core`, `src/scenes`, `src/system`, `src/game`, `inc/**`, `res/**`.
- Estado global permitido: estado da aplicacao, input snapshot, pools estaticos de atores/projeteis, camera e HUD.
- Buffers estaticos: actor pool, projectile pool, collision probes, tile query cache pequeno e runtime probe.
- Proibicoes: sem `float`, sem `double`, sem `malloc/free`, sem API SGDK inventada, sem DMA fora de VBlank.

## 3. Sistemas

### Input

- Owner: `src/system/input.c`.
- APIs SGDK 2.11 permitidas: `JOY_init`, `JOY_update`, `JOY_readJoypad`, `JOY_getJoypadType`, `JOY_getPortType`, `JOY_setSupport`.
- Politica: `JOY_update` uma vez por frame; cenas consomem acoes semanticas, nao hardware direto.
- Mapeamento inicial:
  - D-Pad esquerda/direita: correr.
  - Button A ou C: pular.
  - Button B: atirar.
  - START: iniciar title; pausa fica fora do primeiro slice.
- Estados: held, pressed, released derivados do frame anterior.
- Buffer: limpar pressed/released na troca de cena.

### Gameplay

- Sistemas core: player controller, projectile pool, enemy pool, mini-boss FSM, tile collision, camera e HUD.
- Sistemas secundarios: runtime probe e debug overlay apenas quando o build de QA exigir.
- Pool inicial:
  - player: 1
  - inimigos comuns simultaneos: ate 4
  - mini-boss: 1
  - projeteis do jogador: ate 3
  - projeteis inimigos: ate 4
  - particulas/hit sparks: ate 6, somente apos budget visual
- Ordem de update: input -> player intent -> physics/collision -> actors -> projectiles -> camera -> HUD/render queues.

### Colisao

- Owner: modulo futuro `src/game/collision.c`.
- Coordenadas: world-space em pixels; velocidade e subpixel em `fix16`.
- Solidos: metatiles 16x16 com flags de material; nao derivar solidez de cor/paleta.
- Primeiro slice: solido, vazio, hazard simples. Sem slopes e sem one-way ate contrato especifico.
- Resolucao: eixo X depois eixo Y, probes separados para pe, cabeca e laterais.
- Dominios separados: solid box, hurtbox, hitbox e pushbox.

### Camera

- Owner: modulo futuro `src/game/camera.c`.
- Modelo: side-view platform, scroll inteiro final.
- Dead zone: pequena zona horizontal ao redor do player.
- Look-ahead: apenas para leitura de risco, sem mover entidades para simular camera.
- Bounds: clamp no retangulo da fase para nao revelar area invalida.
- Shake: fora do primeiro slice, exceto se o mini-boss receber card/budget futuro.
- Registry: `camera_scroll_management` com tags `CAMERA_MANAGEMENT`, `CAMERA_DEADZONE`, `CAMERA_LOOKAHEAD`, `INTEGER_RENDER_SNAP`.

### Entidades

- Owner: modulo futuro `src/game/entity.c`.
- Modelo: arrays fixos e archetypes com callbacks simples.
- Archetypes iniciais: `player`, `line_sentry`, `player_shot`, `enemy_shot`, `breaker_core`.
- Spawn: falha explicita quando o pool estiver cheio; sem spawn silencioso.
- Mini-boss: single body FSM, nao modular.

### Render e VDP

- Planos usados:
  - BG_B: fundo do circuito, parallax futuro bloqueado ate arte/budget.
  - BG_A: tiles solidos/foreground.
  - WINDOW: HUD minimo quando o contrato de UI estiver aprovado.
  - Sprites: player, inimigo, projeteis, mini-boss e hit sparks.
- Tecnicas escolhidas com registry ID/tag: `camera_scroll_management`; efeitos visuais avancados continuam adiados.
- Budget VRAM: `nao_medido`; depende de source premium e conversao VDP.
- Budget DMA por frame da cena 3: pico medido de 1 entrada/40 bytes antes do VBlank.
- Budget sprites/SAT da cena 3: pico medido de 4 sprites ativos e 3 por scanline.
- Fallbacks: reduzir tiles de fundo, reduzir inimigos simultaneos, remover hit sparks, simplificar HUD.

### Audio

- Driver: XGM2 previsto, pendente de audio design.
- Canais e prioridade: BGM autoral futura; SFX de jump, shot, hit, damage, boss warning e boss defeat.
- Politica: SFX de gameplay vence detalhe cosmetico.
- Estado atual: nenhuma musica ou SFX final aprovada para o jogo.

### Save / Persistencia

- Escopo: nenhum save de jogador.
- SRAM: permitida apenas para runtime probe/evidencia quando o wrapper exigir.
- Probe MDRT: buffer estatico de 900 amostras; alvo regional de 900 quadros
  NTSC ou 750 PAL; exportacao para SRAM somente quando a janela termina.
- A captura so recebe `capture_status=ok` quando a contagem planejada e
  `probe_window_complete` concordam. Captura parcial permanece `partial`.

## 4. Contratos de Cena

Cada cena deve aparecer em `doc/13-spec-cenas.md` e declarar:

- `scene_id`
- owner de input, render, camera, HUD e teardown
- budget previsto ou `nao_medido`
- fallback
- evidencia esperada

## 5. Riscos Tecnicos

| Risco | Impacto | Mitigacao | Evidencia |
|---|---|---|---|
| Runtime antes de asset premium | placeholder vira falso progresso | bloquear `runtime_admission_report` ate fonte/aprovacao/conversao | visual_delivery_gate_report |
| Colisao improvisada | gameplay inconsistente | fixtures de canto, teto, parede, queda e dano antes do codigo | collision_topology_report futuro |
| Input espalhado | transicoes e pause instaveis | input snapshot central | input_mapping_contract futuro |
| Mini-boss crescer | escopo explode | single body FSM, tres padroes maximos | GDD/spec cenas |
| Budget desconhecido | ROM compila mas nao prova entrega | VDP budget analyst depois da arte | scene_budget_report |

## 6. Validacao

- Build canonico: `build.bat` via wrapper central, somente depois de contratos e fonte visual.
- BlastEm: obrigatorio para promover qualquer runtime.
- Freshness audit: obrigatorio depois de qualquer ROM/captura.
- Scene closeout: obrigatorio ao fechar title, stage ou end.
- QA: seguir `doc/14-plano-de-provas-qa.md`.

### Pre-runtime human gates

- Gate 1 - Storyboard precisa ser aprovado antes de bloquear model sheet como fonte.
- Gate 2 - Model sheet precisa ser aprovado antes de spritesheet virar fonte de
  conversao.
- Gate 3 - Spritesheet precisa ser aprovado antes de qualquer VDP conversion
  final, `res/` promotion ou runtime com asset critico.
- Os candidatos atuais ficam em `data/source_art/**` e sao `review_candidate`,
  nao arte final.

## 7. Plano de TDD Incremental

Nenhuma fatia deve entrar em runtime sem teste/fixture ou criterio vermelho equivalente.

1. Input contract: fixture de pressed/held/released e limpeza em troca de cena.
2. Collision fixtures: chao, parede, teto, queda, hazard e dano.
3. Projectile pool: limite de projeteis, despawn e hit confirmado.
4. Enemy FSM: `line_sentry` patrulha, telegraph e dano.
5. Mini-boss FSM: ataques previsiveis, janela vulneravel e fim de fase.
6. Scene flow: title -> stage -> end com teardown de input/HUD/camera.
7. Build/validation: wrapper central, validation report e BlastEm.

## 8. Atualizacao

Mudanca de arquitetura, tecnica, cena, budget ou pipeline exige atualizar:

- `doc/10-memory-bank.md`
- `doc/changelog/changelog.md`
- `doc/13-spec-cenas.md`
- `doc/technique_usage_manifest.json`
