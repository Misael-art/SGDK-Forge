---
name: cutscene-cinematic-direction
description: Use quando a tarefa envolver abertura, cutscene, cena de contexto, dialogo cinematico, final, fake cinema, storyboard, retrato falante, painel narrativo, anime 90s ou narrativa visual em SGDK/Mega Drive. Esta skill transforma referencia cinematica em FSM, paineis, paletas, texto temporizado, budget por estado e evidencia em emulador.
---

# Cutscene Cinematic Direction

Esta skill existe para impedir que cutscene vire prompt solto, video mental ou tela estatica sem engenharia.

O alvo e linguagem 8/16-bit com qualidade de anime do inicio dos anos 90: composicao forte, retratos expressivos, paineis dramaticos, texto com ritmo, truques de paleta, fades seletivos, pans e holds. O alvo tecnico continua sendo Mega Drive / SGDK 2.11.

## Avaliacao honesta da capacidade atual

O agente ja consegue produzir cutscenes funcionais simples quando os assets existem e o runtime esta claro.

Ainda nao e confiavel para o alvo Phantasy Star IV, Valis III, Rondo of Blood, Tales of Phantasia, Snatcher ou Princess Minerva sem este contrato, porque o framework anterior espalhava pedacos da disciplina em texto expressivo, transicao, VDP e traducao de boards, mas nao obrigava:

- roteiro como maquina de estados
- storyboard/painel como asset de hardware
- budget por estado da cutscene
- timing de texto e pontuacao
- ownership de WINDOW, H-Int, CRAM e audio
- teardown ao sair
- evidencia visual especifica da cena

## Quando usar

Use esta skill para:

- abertura cinematica
- cena de contexto antes/depois de fase
- final
- dialogo com retrato, painel, balao ou texto dramatico
- storyboard board, cutscene board, manga panel ou anime close-up
- flashback, comunicador de piloto, briefing, epilogo
- qualquer cena onde imagem + texto + som carregam narrativa

## Nao use

- para transicao puramente mecanica sem narrativa: use `scene_transition_card`
- para HUD de gameplay sem narrativa: use `ui_decision_card`
- para converter uma imagem isolada sem plano de cena: use antes `art-translation-to-vdp`

## Contrato Operacional

### Entrada minima

- `doc/12-roteiro.md` ou `roteiro_scope`
- `doc/13-spec-cenas.md`
- `context_pack_manifest`
- `reference_profile`
- `scene_role=cutscene`
- `text_presentation_profile` quando houver fala, narracao ou corpo de texto

### Saida minima

- `cutscene_scene_contract`
- `cinematic_storyboard_contract`
- `cutscene_fsm_script`
- `cutscene_panel_layout`
- `cutscene_resource_plan`
- `cutscene_text_timing_map`
- `cutscene_teardown_plan`

### Passa quando

- a cena esta modelada como FSM
- paineis, texto, paletas, audio, FX e teardown tem owner
- o budget e medido por estado
- a evidencia aponta para a cutscene certa em BlastEm

### Handoff para proxima etapa

- entregar paineis para `art-translation-to-vdp`
- entregar resource plan para `megadrive-vdp-budget-analyst`
- entregar FSM e teardown para `sgdk-runtime-coder`

## Entradas obrigatorias

- `doc/12-roteiro.md` ou `roteiro_scope`
- `doc/13-spec-cenas.md`
- `context_pack_manifest`
- `reference_profile` com heranca declarada por jogo
- `scene_role=cutscene` no contrato de cena
- `text_presentation_profile` quando houver fala, narracao ou corpo de texto
- `audio_architecture_card` quando houver voz sintetica, stinger, musica, ambience ou SFX de texto
- `scene_transition_card` quando a cutscene entra ou sai de gameplay, menu ou fase

## Saidas obrigatorias

- `cutscene_scene_contract`
- `cinematic_storyboard_contract`
- `cutscene_fsm_script`
- `cutscene_storyboard_board`
- `cutscene_panel_layout`
- `cutscene_resource_plan`
- `cutscene_palette_script`
- `cutscene_text_timing_map`
- `cutscene_audio_cue_map`
- `cutscene_motion_beat_map`
- `cutscene_panel_animation_contract`
- `cutscene_teardown_plan`
- `cutscene_evidence_plan`

## Contrato de FSM

Cutscene nao e video. Cada momento da cena e um estado.

## Contrato machine-readable

Para `aaa_gate`, a cutscene precisa apontar
`doc/scene-contracts.json > cutscene_contract.cinematic_storyboard_contract`
para um JSON valido contra
`tools/sgdk_wrapper/schemas/cinematic_storyboard_contract.schema.json`.

Esse contrato unifica o storyboard em dados verificaveis:

- autoridade de roteiro/spec/contexto e tres referencias tecnicas;
- direcao cinematica, ferramentas de fake cinema e signature moment;
- FSM table-driven com estados, triggers, surfaces, paletas, texto, audio e teardown;
- budget por estado: VRAM residente, DMA de entrada, DMA por frame, glyph cache e sprite pressure;
- ownership de `WINDOW`, CRAM, scroll, audio e H-Int com reset/fallback;
- gate visual: fonte premium, aprovacao humana e `visual_delivery_gate_report`;
- plano de evidencia BlastEm: screenshot, SRAM, VDP dump, baseline e freshness.

`lint_scene_contract.ps1 -Mode aaa_gate` bloqueia:

- `SC107`: cutscene sem `cinematic_storyboard_contract`;
- `SC108`: contrato ausente, JSON invalido ou campos estruturais faltando;
- `SC109`: H-Int ativo sem owner, reset e fallback;
- `SC110`: `ready_for_aaa=true` sem fonte de producao e aprovacao humana.

Cada estado precisa declarar:

- `state_id`
- `narrative_purpose`
- `shot_type`: `establishing`, `portrait`, `reaction`, `object_insert`, `panel_hold`, `pan`, `flash`, `dialogue`, `transition`
- `entry_load`: assets, tiles, mapas, paletas e fonte carregados
- `render_surfaces`: `BG_B`, `BG_A`, `WINDOW`, sprites e prioridade
- `palette_domains`: PAL0-PAL3 e dono de cada dominio
- `text_block`: speaker, string id, limite de linhas, estilo e ancora
- `advance_trigger`: `WAIT_INPUT`, `WAIT_FRAMES`, `TEXT_DONE`, `AUDIO_CUE_DONE` ou combinacao declarada
- `duration_frames`
- `dynamic_fx`: palette cycle, fade seletivo, hscroll, H-Int, shake, blink, mouth, pan
- `motion_beats`: hold, blink, mouth, pan, shake, palette pulse, actor reaction ou stillness intencional
- `animation_link`: qual sprite/portrait/painel muda, quantos frames e qual regra de loop/retorno
- `audio_cue`
- `exit_teardown`

### FSM table-driven para runtime SGDK

Regra generalizada para handoff de cutscenes table-driven ao runtime SGDK.

Quando a cutscene tiver quatro ou mais beats, o handoff para runtime deve nascer
como tabela de estados/passos, nao como `update()` monolitico. O formato pode
variar, mas precisa carregar no minimo:

- frame inicial/final ou duracao por estado
- texto/string id e posicao/ancora
- trigger de avancar, skip ou completar typewriter
- callbacks ou IDs de `on_enter`/`on_exit`
- recursos/paleta/surface usados naquele estado
- teardown esperado antes do proximo estado

Isso reduz branching, facilita revisao temporal e impede que typewriter, skip,
fade e troca de painel fiquem misturados em uma cadeia de `if/else`.

## Direcao visual anime 90s

O resultado precisa parecer pixel art anime de 8/16-bit, nao filtro moderno.

Regras:

- olhos, sobrancelha, boca e silhueta do cabelo carregam emocao
- linework deve ser limpo, com clusters legiveis em 320x224
- pele, cabelo, tecido e metal usam rampas de 2 a 3 tons com hue-shift
- sombras sao temperatura e plano, nao cinza adicionado
- dithering so entra quando cria material ou gradiente controlado
- close-up precisa vencer em leitura nativa, nao so ampliado
- texto nunca briga com o rosto, foco dramatico ou painel principal
- evite pintura suave, blur, antialiasing sujo, olhos sem pixel intent e gradiente de IA

## Layout de paineis

Painel/manga layout e o default seguro.

Full-screen image e permitido, mas so com:

- `fullscreen_bitmap_justification`
- contagem de tiles e paletas
- plano de fallback para pan/crop/painel
- prova de que nao achatou a paleta nem matou a leitura

Board de cutscene deve usar `art-translation-to-vdp` com `translation_target=cutscene_board` e consultar `tools/sgdk_wrapper/.agent/lib_case/art-translation/case_cutscene_board`.

## Texto e ritmo

Texto cinematico e sistema de cena.

Obrigatorio:

- `glyph_manifest` com subset real
- `cutscene_text_timing_map` com velocidade base
- pausas por pontuacao:
  - virgula: pausa curta
  - ponto: pausa media
  - reticencias: pausa dramatica
  - quebra de linha: pausa de respiracao
- botao para acelerar/avancar sem quebrar FSM
- nenhuma chamada insegura de texto sem truncamento
- owner unico de `WINDOW` ou regiao de `BG_A` usada para dialogo

## Movimento cinematico minimo

Cutscene AAA nao precisa animar tudo, mas precisa dirigir o tempo. Cada estado
declara `cutscene_motion_beat_map`:

- `hold`: pausa intencional com duracao e motivo dramatico;
- `blink_or_mouth`: retrato vivo quando rosto estiver legivel;
- `pan_or_scroll`: movimento de camera por scroll quando o painel pedir escala;
- `reaction_frame`: pequena mudanca de expressao, mao, ombro ou silhueta;
- `impact_motion`: shake, flash, speed line ou palette pulse separado;
- `stillness_justification`: quando o quadro parado e escolha dramatica, nao falta de plano.

Blockers:

- `dead_panel_cutscene`
- `portrait_static_without_justification`
- `cutscene_motion_beat_missing`
- `motion_steals_text_readability`
- `cutscene_return_state_dirty`

## Truques de hardware permitidos

Use truques para sugerir cinema com pouco movimento:

- pan horizontal ou vertical por scroll
- blink/mouth frames em retrato
- special cut-in de golpe: gameplay pausado por poucos frames, rosto ou busto em tiles grandes, speed lines/palette flash separados e retorno de estado limpo
- palette cycling para agua, neon, energia, alerta e brilho
- fade seletivo por paleta
- camera shake curto em revelacao ou impacto
- H-Int/raster apenas com owner unico, budget e reset simetrico
- Shadow/Highlight apenas quando houver `palette_slot_audit`

H-Int nao e tempero. E callback global. Sem owner e teardown, a cena fica bloqueada.

Special cut-in nao e video nem sprite gigante em gameplay ativo. Ele exige
estado proprio na FSM, `cutscene_resource_plan`, budget por estado, owner de
paleta/texto/audio e teardown simetrico antes de voltar ao jogo.

## Budget por estado

O budget nao e da cutscene inteira como se tudo estivesse residente.

Cada estado precisa declarar:

- `vram_resident_set`
- `load_time_dma_cost`
- `per_frame_dma_cost`
- `palette_domains`
- `glyph_cache`
- `sprite_pressure`
- `state_teardown`

Se um estado depende do estado anterior, isso precisa estar em `state_handoff`. Conteudo herdado por acidente nao conta.

## Evidencia

Cutscene so fecha gate com:

- `scene_contract` com `scene_role=cutscene`
- screenshot dedicada da cutscene no BlastEm
- `runtime_metrics.scene_id` correspondente
- baseline comparativo para validacao visual AAA
- `visual_vdp_dump.bin` em entrega AAA ou quando houver suspeita visual
- `freshness_audit_report` sem stale

## Passa quando

- existe FSM de cutscene antes do runtime
- `cinematic_storyboard_contract` existe e valida antes de qualquer claim AAA
- todos os estados possuem assets, texto, trigger, FX, audio e teardown declarados
- todos os estados narrativos AAA possuem `cutscene_motion_beat_map` ou `stillness_justification`
- retrato falante/close-up com rosto legivel possui blink, mouth, reaction frame ou justificativa de silencio visual
- paineis, retratos e texto possuem budget por estado
- full-screen foi justificado ou substituido por painel/pan
- texto tem cadence e controle de avanco
- `WINDOW`, H-Int, CRAM, scroll e audio possuem owner unico
- a cena foi vista rodando em BlastEm com evidencia da cena correta

## Handoff

- para `art-translation-to-vdp`: storyboard board, close-ups, panels e source images
- para `multi-plane-composition`: layout de BG_B, BG_A, WINDOW e sprites
- para `megadrive-vdp-budget-analyst`: resource plan por estado
- para `sgdk-runtime-coder`: FSM, timing, audio, teardown e evidencia esperada

## Anti-padroes

- prompt de imagem sem `cutscene_scene_contract`
- cutscene AAA sem `cinematic_storyboard_contract`
- usar uma ilustracao fullscreen gigante como ROM final sem budget
- texto parado sobre imagem morta sem ritmo, som ou composicao
- painel morto sem `cutscene_motion_beat_map` ou `stillness_justification`
- retrato falante sem blink/mouth/reaction quando o rosto e grande o bastante para ler
- importar expectativa de PC Engine CD, SNES ou Sega CD como se fosse capacidade SGDK automatica
- H-Int sem owner
- fade preto generico para toda emocao
- cutscene que nao sabe como sai para a proxima cena
- chamar de anime 90s uma imagem moderna suavizada e borrada
- cutscene com muitos beats codificada como `update()` crescente sem tabela de
  estados, sem `on_enter`/`on_exit` e sem teardown por passo
