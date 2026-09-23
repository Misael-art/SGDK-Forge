# 11 - Game Design Document - BLUE_CIRCUIT [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

## Project Brief

BLUE_CIRCUIT e um action platformer curto para Mega Drive em que uma tecnica de resgate atravessa uma subestacao automatizada tomada por energia instavel. O jogador corre, pula e atira pulsos de manutencao para limpar pequenos drones, abrir caminho e desligar um mini-boss de seguranca no fim da fase.

O projeto busca a sensacao de acao/plataforma 16-bit precisa sem copiar personagens, nomes, sprites, musica, UI, paleta, silhueta ou identidade visual de qualquer franquia existente. Benchmarks comerciais podem orientar tempo de resposta, densidade de tela e clareza de feedback, mas nunca servem como fonte visual, sonora ou de layout.

## Visao

A fantasia e "manutencao heroica dentro de um circuito gigante": corredores industriais azul-ciano, trilhas de cobre, alertas amber, vapor frio, paineis vivos e energia instavel que se comporta como obstaculo jogavel. A fase deve parecer pequena, densa e terminavel, com cada tela ensinando ou testando um unico risco.

O jogo nao e uma coletanea de sistemas. A primeira versao existe para provar um loop completo, curto e autoral: title, entrada na fase, inimigo comum, leitura de plataforma, mini-boss e tela de fim.

## Core Loop

1. Ler a proxima tela: plataforma, inimigo, tiro ou hazard.
2. Mover com intencao: correr, pular ou ajustar posicao.
3. Atirar para abrir janela de passagem ou remover ameaca.
4. Receber feedback imediato: hit spark, recuo visual, som curto e estado de inimigo.
5. Avancar para uma pressao levemente maior ate chegar ao mini-boss.

Nos primeiros 30 segundos, o jogador deve aprender que o disparo neutraliza drones, que pular exige leitura do chao e que energia azul clara indica risco.

## Feature Scope Map

### Entra no slice

- Title screen e press start.
- Player com correr, pular, cair, atirar e tomar dano.
- Projetil simples do jogador, limitado por pool estatico.
- Um inimigo comum: `line_sentry`, patrulha curta e tiro lento/telegraphed.
- Um mini-boss: `breaker_core`, arena simples, tres padroes curtos e vulnerabilidade apos ataque.
- Fase unica com secoes: tutorial de movimento, primeiro inimigo, plataforma curta, arena do mini-boss e fim.
- HUD minimo com vida do jogador e vida do mini-boss quando aplicavel.
- Tela de fim apos derrotar o mini-boss.

### Entra depois

- Variacao de inimigo.
- Checkpoint.
- Musica adaptativa.
- Efeitos de parallax ou palette cycling alem do minimo aprovado.

### Fora de escopo

- Dash, slide, wall jump, carga de tiro, armas alternadas, itens colecionaveis, multiplas fases, passwords, save e bosses modulares.

## Identidade de Front-End

- O primeiro frame deve comunicar circuito industrial energizado, nao ficcao generica.
- Title screen usa logotipo autoral `BLUE_CIRCUIT`, trilhas de placa e pulso eletrico sutil como idle.
- O press start deve responder com flash/pulse curto, sem menu complexo.
- Tela de fim usa a subestacao estabilizada e uma frase curta de encerramento.
- Fora de tom: robo azul humanoide derivativo, capacete/arm cannon reconhecivel, fonte generica como identidade final, fanfare parecida com IP existente.

## Ambicao Tecnica, Visual e Sonora

- `quality_promise`: vertical slice compacta, honesta e bem lida em Mega Drive, nao `ready_for_aaa` ate todas as evidencias existirem.
- `visual_direction`: industrial eletrico com azul/ciano como energia, amber como perigo, magenta/verde-lima como acentos; sprites pequenos mas expressivos, sem asset procedural como final.
- `sound_direction`: SFX curtos para tiro, hit, dano, jump e boss warning; BGM autoral futura com energia mecanica, nao derivativa.
- `gameplay_quality_bar`: input centralizado, colisao previsivel, tiro legivel, mini-boss telegraphed e nenhum dano surpresa.
- `hardware_strategy`: BG_B para fundo, BG_A para solidos/foreground, WINDOW para HUD quando aprovado, sprites para atores, pools estaticos, DMA apenas em VBlank e preload local por cena.

## Kit do Jogador

- Correr para esquerda/direita com aceleracao curta.
- Pular com altura controlavel e queda previsivel.
- Atirar pulso horizontal simples.
- Tomar dano com invencibilidade curta e knockback pequeno.
- Ler telegraph de inimigo e mini-boss antes de agir.

## Regras Sistemicas

- O estado do jogo sempre separa mundo, camera e tela.
- Input de hardware vira snapshot semantico antes de qualquer cena consumir acoes.
- Colisao solida, hurtbox, hitbox e pushbox sao dominios separados.
- Dano so ocorre quando ataque e hurtbox se encontram depois do telegraph.
- Toda transicao de cena limpa input buffers, camera, HUD e pools temporarios.

## Progressao Da Fase

A fase avanca em linha curta: entrada segura, primeiro inimigo, combinacao de plataforma/tiro, arena do mini-boss e encerramento. Nao ha backtracking, senha, save ou segunda rota no primeiro slice.

## Mapa E Secoes

- `entry_conduit`: tela de leitura ampla para correr e pular.
- `sentry_lane`: primeira ameaca comum, com espaco para aprender tiro.
- `charge_bridge`: pequena secao de plataforma com hazard eletrico.
- `breaker_core_arena`: arena fechada do mini-boss.
- `exit_stabilized`: transicao para tela de fim.

## Ritmo

O pacing alterna calma e pressao: 1 tela de movimento, 1 tela de inimigo, 1 tela de combinacao e 1 pico final. Cada secao deve caber em poucos segundos e nunca empilhar dois ensinamentos novos ao mesmo tempo.

## Tutorial Invisivel

O jogo deve ensinar sem texto: o primeiro buraco vem sem inimigo, o primeiro inimigo vem em chao plano, o primeiro hazard vem antes do mini-boss, e o mini-boss repete seu padrao antes de punir agressivamente.

## Climax

O climax do slice e o `breaker_core`: uma arena curta em que o nucleo anuncia o ataque, fecha a janela de seguranca e depois abre uma vulnerabilidade clara. O momento assinatura so recebe blackout, flash ou screen shake se budget e contratos aprovarem.

## Criterios De Qualidade Visual

- Player, inimigo, tiro e hazard precisam ler em 320x224 sem depender de texto.
- Paleta nao pode ser apenas azul; amber, magenta e verde-lima entram como funcao de perigo, energia ou contraste.
- Background nao pode competir com hitboxes.
- Title screen nao pode usar fonte generica como identidade final.
- Qualidade visual final exige source premium, aprovacao humana, conversao VDP, visual gate limpo e BlastEm.

## Gates Humanos De Direcao Visual

O humano validara somente tres marcos criativos. Todo o restante sera tratado
como validacao tecnica do pipeline.

1. `gate_1_storyboard`: aprova a leitura completa do slice em seis beats:
   title, entrada, `line_sentry`, `charge_bridge`, `breaker_core` e fim.
2. `gate_2_model_sheet`: aprova a identidade autoral do player, inimigo comum e
   mini-boss, incluindo silhueta, materiais, paleta e ausencia de clone visual.
3. `gate_3_spritesheet`: aprova a folha de animacao candidata antes de qualquer
   conversao VDP, promocao para `res/` ou integracao runtime.

Os candidatos atuais estao registrados em `doc/contracts/human_visual_gate_plan.json`.
Eles podem orientar review, mas continuam `awaiting_human_validation`.

## Ambicao Tecnica

A barra tecnica e conservadora: SGDK 2.11, preload local por cena, camera side-view com snap inteiro, pools estaticos, DMA seguro em VBlank e nenhum efeito global sem owner e teardown.

## Direcao Sonora

A direcao sonora deve comunicar manutencao eletrica sob pressao: pulso curto para tiro, click limpo para hit, ruido seco para dano, alerta distinto para mini-boss e stinger simples na derrota do `breaker_core`. Nenhum som final esta aprovado; musica e SFX precisam ser autorais, validados em `.res`, auditados por `audio_validation_report.json` e confirmados no BlastEm antes de qualquer claim `audio=ok`.

## Tecnicas Escolhidas

A primeira tecnica catalogada selecionada e `camera_scroll_management`, porque a fase precisa de dead zone, look-ahead leve, bounds e integer snap. Ela esta `documentada`, sem runtime ou budget aprovado. H-Int, line scroll, palette cycling de gameplay, streaming e boss setpiece ficam adiados.

| Cena/sistema | Registry id | Tags | Funcao no jogo | Papel visual/sonoro | Owner skills | Budget/evidencia esperada | Fallback |
|---|---|---|---|---|---|---|---|
| `stage_01_blue_circuit` | camera_scroll_management | CAMERA_MANAGEMENT, CAMERA_DEADZONE, CAMERA_LOOKAHEAD, INTEGER_RENDER_SNAP | manter leitura de risco e evitar area invalida | camera discreta e estavel em side-view | camera-system-sgdk, scene-state-architect, sgdk-runtime-coder, megadrive-vdp-budget-analyst | camera_behavior_contract, build, validation, BlastEm, runtime metrics | camera fixa por setor |

### Tecnicas rejeitadas ou adiadas

| Registry id | Decisao | Motivo | Condicao para reconsiderar |
|---|---|---|---|
| h_int_raster_fx | adiada | nao e necessario para provar o loop curto | art direction aprovada, budget VDP e funcao de gameplay clara |
| tilemap_streaming | adiada | fase pequena pode usar preload local | mapa maior ou pressao real de VRAM |
| modular_boss | rejeitada nesta versao | mini-boss simples nao tem partes independentes | novo GDD/TDD aprovando boss modular e budget |

## Mecanicas Core

- Movimento horizontal: aceleracao curta e velocidade maxima previsivel.
- Pulo: gravidade em `fix16`, corte de altura se soltar o botao e colisao separada por eixo.
- Tiro: projetil horizontal simples, limite baixo de simultaneos e feedback claro no impacto.
- Dano: invencibilidade curta, knockback pequeno e reset seguro em queda.
- Mini-boss: ataques telegraphed, janela vulneravel e derrota encerra a fase.

## Progressao

- `title_screen`: comunica identidade e inicia o jogo.
- `stage_01_blue_circuit`: uma fase pequena com quatro secoes jogaveis.
- `breaker_core_arena`: ultima secao da fase, sem nova cena de runtime.
- `ending_screen`: confirma estabilizacao do circuito e fecha o slice.

## Regras e Limites

- O jogador nunca deve ser atingido por um ataque sem telegraph visual ou posicao previsivel.
- O inimigo comum deve morrer com poucos tiros e ensinar spacing.
- O mini-boss deve usar poucos padroes, repetir claramente e nao exigir decoracao longa.
- A fase deve caber em uma sessao curta; sem backtracking.
- Todo material visual final exige source premium local, hash, licenca/autoria e aprovacao humana.

## First Playable Slice

- Primeira entrega jogavel: title -> fase unica -> mini-boss -> fim.
- Sistemas a provar: input snapshot, colisao tile-based, camera side-view, pools de atores/projeteis, HUD minimo, scene transition e runtime probe.
- Criterio minimo: o loop existe somente quando rodar no BlastEm com evidencia fresca e sem visual gate bloqueado.

## Route Decision Record

- `context_type`: `projeto_novo`
- `dominant_route`: `planning`
- `first_skill`: `art/art-asset-diagnostic` apos aprovacao da direcao e fonte premium; runtime so entra depois do gate visual.
- `first_tool`: `tools/sgdk_wrapper/validate_project_context.ps1`
- `resource_loading_model`: `scene_local_preload`
- `asset_strategy`: `mixed`
- `evidence_required`: context/methodology/hygiene reports, visual delivery gate, build, validation, BlastEm screenshot/SRAM/VDP dump quando aplicavel.
- `forbidden_shortcuts_until_evidence`: runtime final, asset procedural final, clone visual, API SGDK nao verificada, DMA fora de VBlank, ready_for_aaa.

## Escopo Atual

- Fase em producao: candidatos visuais dos tres gates humanos.
- Fora desta fase ate aprovacao humana: conversao VDP final, promocao de arte
  para `res/`, codigo jogavel de entrega, build de entrega e evidencia de emulador.

## Cenas de Front-End

- `title_screen`: profile_kind `front_end_profile`, owner de input/press start e teardown antes da fase.
- `ending_screen`: profile_kind `front_end_profile`, sem salvar estado, retorno futuro ao title em backlog.

## Vibe Playable Birth Route

- `visual_route_required=true`
- `critical_asset_default_status=blocked_no_premium_source`
- `runtime_evidence_default_status=missing`
- `human_approval_required=true`
- `blastem_required_for_delivery=true`

## Coesao Criativa Pre-runtime

- Ameaca: a subestacao automatizada tenta isolar o intruso com drones e descargas.
- Risco sistemico: energia instavel transforma plataformas e arenas em leitura de timing.
- Identidade mecanica por setor: movimento limpo primeiro, tiro contra sentry depois, mini-boss como leitura de telegraph.
- Momento assinatura: o `breaker_core` apaga a luz da arena por um pulso curto antes do ataque principal, se aprovado por budget e arte.
- Audio como feedback: jump, shot, hit, damage e boss warning precisam ser distinguiveis.
- Replay hook: fase curta com tempo de conclusao e dano recebido como meta futura, nao no slice inicial.
