# 11 - Game Design Document - Celestial Chase First Playable

## Project Brief

`Celestial Chase` e uma perseguicao autoral em perspectiva forcada para Mega Drive. Um pequeno mensageiro celeste atravessa uma estrada astral em colapso enquanto um cervo-maquina monumental tenta alcanca-lo. O first playable entrega uma rodada curta, legivel e repetivel em que movimento lateral, salto e uso do `Celestial Pulse` transformam pressao visual em decisoes de jogo.

O projeto preserva os personagens source-baked aprovados e promove `APP_SCENE_CHASE` de benchmark automatico para first playable. A classificacao continua `LAB/TECHDEMO` ate aprovacao humana e promocao formal; o alvo desta iteracao e `vertical_slice_candidate`.

## Fantasia e Pilares

- **Fantasia:** sobreviver ao ultimo trecho de uma estrada celeste enquanto uma maquina ancestral cresce no horizonte.
- **Agency:** cada obstaculo oferece uma resposta clara por faixa, salto ou Pulse.
- **Pressao legivel:** proximidade do perseguidor e comunicada por HUD, escala visual, paleta e cadencia de ataques.
- **Espetaculo com consequencia:** shake, hitstop, poeira e transicoes de paleta correspondem a impacto, risco ou vantagem real.
- **Repetibilidade:** o slice dura 75 segundos em NTSC, oferece padroes deterministas com variacao de faixa e reinicia sem softlock.

## Core Loop Statement

`ler telegrafo -> escolher faixa ou saltar -> coletar energia -> usar Celestial Pulse para quebrar pressao -> sobreviver ate o portal -> repetir buscando melhor integridade`

Nos primeiros 30 segundos o jogador aprende a trocar de faixa, salta uma barreira baixa, coleta energia e percebe que erros aproximam o perseguidor.

## Kit do Jogador

- **Troca de faixa:** esquerda/direita move entre tres faixas discretas; uma troca tem compromisso curto e feedback de poeira.
- **Salto:** botao A; evita barreiras baixas e ataques rasantes, mas nao protege contra ameaca alta.
- **Celestial Pulse:** botao B quando o medidor esta cheio; limpa ameacas ativas, afasta o perseguidor e concede uma janela curta de seguranca.
- **Pause:** START congela regras, spawns e timers; START retoma.
- **Reinicio/menu:** resultado aceita A/START para reiniciar e B/MODE para menu.

## Regras Sistemicas

- O jogador possui tres pontos de integridade. Um impacto consome um ponto, aplica hitstop curto, shake, poeira e invulnerabilidade temporaria.
- O medidor Pulse recebe energia por coleta; quatro coletas completam o medidor e usar Pulse o zera.
- A pressao do perseguidor varia de 0 a 100. Ela cresce com o tempo e com dano; Pulse e a unica forma ativa de reduzi-la.
- Pressao 100 ou integridade 0 causa falha. Sobreviver ate o fim da fase de climax causa vitoria.
- Obstaculos nunca surgem sem telegrafo visual anterior. O padrao determinista respeita ao menos uma resposta valida.
- Nenhum input de debug fica disponivel no controle de entrega.

## Progressao do Slice

### Fase 1 - Introducao e Tutorial Invisivel, 0-20 s

- Ensina troca de faixa com coleta segura.
- Apresenta uma barreira baixa isolada e um ataque de faixa unica.
- Pressao cresce lentamente e o Pulse pode ser carregado uma vez.

### Fase 2 - Pressao Crescente, 20-50 s

- Combina barreira, ataque rasante e coleta em faixas diferentes.
- A cadencia aumenta e o perseguidor se aproxima quando o jogador erra.
- O Pulse passa de ferramenta opcional para recuperacao estrategica.

### Fase 3 - Climax e Escape, 50-75 s

- Alterna ondas curtas com uma respiracao antes do ataque final.
- O perseguidor executa impactos sincronizados com shake e poeira.
- O portal estabiliza ao final; integridade restante define a mensagem de resultado.

## Inimigos e Ameacas

- **Celestial Boulder:** barreira baixa; exige salto ou troca de faixa.
- **Astral Brand:** ataque marcado no piso; exige sair da faixa antes da janela ativa.
- **Pursuer Pressure:** antagonista sistemico; nao colide como objeto comum, mas pune erros e fecha a rodada em 100 de pressao.

## Recompensas

- Coleta de energia aumenta Pulse em 25 pontos.
- Usar Pulse cheio limpa as ameacas ativas e reduz pressao em 28 pontos.
- Vitoria mostra integridade restante, Pulses usados e convite de reinicio imediato.

## Feature Scope Map

### Entra no Slice

- branding -> title/menu -> gameplay `APP_SCENE_CHASE` -> resultado -> reiniciar/menu;
- tres faixas, salto, Pulse, pause, integridade, pressao e resultado;
- tres fases de ritmo em 75 segundos NTSC, ajustadas por `targetFps`;
- obstaculos e ataques telegrafados;
- composicao em BG_B + BG_A, HUD de gameplay legivel e sprites source-baked aprovados;
- audio adaptativo e SFX funcionais nesta iteracao;
- evidencia BlastEm vinculada a ROM vigente.

### Entra Depois

- variacao procedural extensa;
- placar persistente em SRAM;
- segundo percurso e novos perseguidores;
- trilha XGM2 final com composicao externa aprovada;
- promocao do nome/classificacao para fora de `LAB/TECHDEMO`.

### Fora de Escopo

- fisica analogica de estrada ou claim de `road_physics`;
- runtime scaling continuo de sprites;
- boss modular completo;
- clone visual de IP existente;
- multiplayer, password ou save de progresso.

## Front-End Profile

- O title/menu comunica fantasia de livro celeste mecanico: ceu profundo, estrada luminosa e presenca distante do perseguidor.
- O idle usa pulso de paleta e movimento de planos; a selecao recebe flash curto e cue sonoro.
- O slice oferece uma opcao principal de inicio e exibe os controles no proprio menu.
- Texto e curto, de alto contraste e subordinado a composicao visual.
- Fundo morto, texto cru de template, neon sci-fi generico e instrucoes de desenvolvimento sao fora de tom.

## Scene Roadmap

1. `APP_SCENE_BRANDING`: logos curados, pulaveis.
2. `APP_SCENE_BOOT`: title card e transicao para menu.
3. `APP_SCENE_MENU`: escolha de jogar ou ler controles.
4. `APP_SCENE_CHASE`: first playable de 75 segundos.
5. `APP_SCENE_CHASE` em estado de resultado: vitoria/falha, reinicio ou menu.

## First Playable Slice

O first playable e uma rodada completa em `APP_SCENE_CHASE`. Ele passa quando o jogador consegue trocar de faixa, saltar, carregar/usar Pulse, receber dano, pausar, vencer, falhar, reiniciar e voltar ao menu sem softlock; todos os eventos precisam de feedback visual e sonoro observavel.

## Mapa e Secoes

O mapa e uma rota unica de tres faixas dividida em secoes temporais: introducao, pressao crescente e climax. Nao ha bifurcacao fisica nesta iteracao; a escolha espacial acontece a cada ameaca pela faixa esquerda, central ou direita.

## Tutorial Invisivel

- A primeira coleta nasce na faixa inicial.
- A segunda coleta nasce em faixa adjacente e introduz troca.
- A primeira barreira surge sozinha depois da primeira troca.
- O primeiro ataque de faixa unica evita a faixa atual por padrao, ensinando leitura antes de punir.
- O primeiro Pulse cheio recebe brilho e cue, sem caixa de texto intrusiva.

## Criterios de Qualidade

- leitura imediata de faixa, telegrafo e estado do Pulse em 320x224;
- nenhum elemento principal parecido com debug ou template;
- impacto sempre combina consequencia mecanica, hitstop, shake, poeira e cue;
- `over_budget_frames=0`, maximo de 20 sprites por scanline e 80 links SAT;
- arte critica preserva a direcao source-baked aprovada;
- nenhum status acima de `vertical_slice_candidate` sem BlastEm fresco e aprovacao humana.

### Criterios de Qualidade Visual

A direcao de arte passa quando heroi, perseguidor, faixa segura, telegrafo, coleta e HUD permanecem legiveis em um quadro; a barra visual exige profundidade clara entre BG_B, BG_A, WINDOW e sprites sem parecer tela de debug.

### Ambicao Tecnica

A ambicao tecnica e sustentar 60 FPS NTSC com duas tabelas de line scroll, pool estatico de sprites, XGM2, zero heap no loop e DMA enfileirado apenas para o VBlank. O recuo oficial remove line scroll e alonga animacoes antes de aumentar residencia.

### Tecnicas Escolhidas

As tecnicas escolhidas usam `registry_id` documentado no manifesto: `line_scrolling`, `pseudo3d_road_stack`, `camera_scroll_management`, `hitstop_camera_shake_feedback`, `window_plane_static_hud`, `dma_transfer_safety` e `palette_state_transitions`.

### Direcao Sonora

A direcao sonora usa um pulso musical original em loop, cues curtos de movimento/coleta e eventos prioritarios para dano, Pulse, vitoria e falha. A identidade musical cresce por cadencia de pressao sem substituir a leitura mecanica.

## Technical, Visual and Audio Ambition

- **Tecnica:** 60 FPS NTSC, inteiros/fix16, pools estaticos, DMA seguro, ownership unico de VBlank/H-Int/WINDOW/audio.
- **Visual:** atmosfera e estrada em planos separados, scroll por plano/linha quando o budget permitir, transicoes de paleta por fase e feedback de impacto.
- **Audio:** estados `intro`, `pressure`, `climax`, `victory` e `failure`; SFX prioritarios para impacto, Pulse e perigo.
- **Gameplay:** rodada justa, legivel e repetivel com ao menos uma resposta valida por ameaca.

## Technique Selection Seed

| Registry ID | Funcao | Owner | Budget/Evidencia | Fallback |
|---|---|---|---|---|
| `line_scrolling` | dar velocidade e deformacao controlada a estrada | scene runtime + VDP budget | linhas atualizadas no VBlank; runtime metrics | scroll por plano |
| `pseudo3d_road_stack` | organizar faixas e profundidade sem claim de Mode 7 | level design + runtime | BG_A e padroes de ameaca | estrada estatica em perspectiva |
| `camera_scroll_management` | comunicar pressao e impacto | runtime | offsets pequenos; teardown em resultado | scroll por plano zerado |
| `hitstop_camera_shake_feedback` | confirmar dano, Pulse e golpe do perseguidor | player/rules runtime | hitstop <= 6 frames; shake <= 5 frames | palette flash + poeira |
| `window_plane_static_hud` | manter integridade, Pulse e pressao legiveis | HUD runtime | faixa superior compacta | HUD em BG_A sem scroll |
| `dma_transfer_safety` | impedir upload inseguro durante gameplay | app/runtime | fila SGDK e VBlank | preload de cena |
| `palette_state_transitions` | diferenciar as tres fases | scene runtime | poucas entradas CRAM por tick | paleta fixa aprovada |

`prerendered_sprite_scaling` fica adiado: os strips aprovados nao oferecem os estagios necessarios sem nova aprovacao visual.

## Route Decision Record

- `context_type`: projeto_existente_promovendo_cena
- `dominant_route`: scene_architecture
- `first_skill`: planning/game-design-planning
- `first_tool`: contratos canonicos + assets source-baked aprovados
- `resource_loading_model`: scene_local_preload
- `asset_strategy`: preservar sprites aprovados; promover composicao split v007 somente apos budget
- `evidence_required`: contracts audit, build, res graph, runtime metrics, regression, screenshot BlastEm, SRAM e VDP dump da mesma ROM
- `forbidden_shortcuts_until_evidence`: sem debug final, sem fallback procedural como arte final, sem claim AAA, sem aprovacao humana fabricada
