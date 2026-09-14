# Plano de evolução — HAMOOPIG como modelo de engine de luta

Data: 2026-09-14. Estado: **planejado**, sem implementação das novas melhorias nesta revisão.
Contexto: evolução de projeto existente, Mega Drive, SGDK 2.11, teto atual `prototype`.
Destinatários: agente implementador, revisor visual e responsável pelo projeto.
Registro executável de tarefas: `doc/engine/fighting_engine_roadmap.json`.

## Mensagem para encaminhamento

**Assunto: Plano de evolução e validação da engine HAMOOPIG para Mega Drive**

Olá!

A proposta é transformar o HAMOOPIG em uma base de jogos de luta organizada, configurável e fácil de continuar: combate com barra de especial e contador de combos, HUD transparente, velocidade consistente, dois cenários amplos e uma abertura que termina antes de apresentar o título e seu menu.

O trabalho será feito em etapas verificáveis. Um agente sem visão poderá implementar regras, integrações, conversões determinísticas e testes instrumentados. A qualidade de imagens, animações e transições ficará explicitamente pendente até ser examinada por um agente com visão ou por uma pessoa. Se o executor possuir visão e ferramentas de captura, poderá realizar essa revisão durante a implementação, mantendo as evidências e os limites de cada teste.

A ordem proposta começa pela medição e pelo controle do tempo, passa pelo gerenciamento de cenas e pelas regras de combate, e termina na arte, no segundo cenário e na validação integrada. O resultado esperado inclui ROM, código, configurações, manual de extensão e provas reproduzíveis.

Segue o plano técnico para execução. Os valores de balanceamento e a direção do segundo cenário abaixo são decisões propostas para a primeira versão; não são características já implementadas.

## 1. O que a revisão encontrou

Inspeção local em 2026-09-14: commit de referência `19eb8fae`; ROM encontrada em `out/rom.bin`:
`e2ca583341b3f0784442b765df67080ebb02cd015b8e06494c570464e65be0f4`.
Esse hash identifica o arquivo encontrado, não comprova que a ROM foi gerada de todo o código atual. Revalidar no início da execução.

| Superfície | Evidência local | Consequência para o plano |
|---|---|---|
| Especial | `energiaSP` existe; atualização EnergyType 2 em `src/player.c` e desenho em `src/hud.c` estão comentados | Recuperar o sistema com contrato, não apenas descomentar o desenho |
| Hits | `hitCounter` é incrementado em vítimas e zerado em certos estados | Não confundir contador legado com combo atribuído ao atacante |
| Relógio | `clock_digits_window.png`, 160×16, contém 1.635 pixels de índice 11 e nenhum de índice 0; HUD usa PAL1 | O fundo do atlas é opaco no sprite. Criar máscara correta preservando contornos |
| Tempo | `gLogicRate`, pausa e free-step existem; NTSC em modo 50 descarta ticks, inclusive processamento de input | Separar frequência de vídeo, lógica, input e ritmo de animação; medir antes de ajustar |
| Clock arcade | `ROUND_CLOCK_TICKS=38` | Um decremento do mostrador não representa hoje um segundo real |
| Abertura/menu | `src/title.c` mantém ambos em fases de `gRoom==1`; o menu ainda ocupa a imagem da abertura | A correção anterior não atende ao novo requisito de duas cenas com fade |
| Menu atual | START, OPTION, SFX, MUSIC, DEBUG, BACK; DEBUG inclui boxes, texto, perf, frame advantage, step, tick e H240 | Preservar funcionalidades recentes e validar todas, inclusive retorno de páginas grandes |
| Cena atual | `showdown.json`: 1.629 tiles de origem substituídos por 768 representantes, bloco de pixel 1, 14 cores opacas | A aproximação de tiles pode causar textura quadriculada mesmo sem escala 4× |
| Palco alternativo | Ramo `gBG_Choice==2` usa `gfx_bgb2` | Ramo existente não comprova um segundo cenário final |
| Documentação | GDD ainda contém placeholders; TDD/contratos citam owners e cenas que não correspondem integralmente ao runtime | Sanear documentação antes de usar seus números como contratos atuais |
| Medição | Histórico contém pico DMA 10.064 B e amostra curta posterior de 5.688 B, em ROMs diferentes | Não atribuir essas medidas à ROM encontrada nem concluir que o pior caso foi resolvido |

O agente desta revisão possui visão: examinou os assets atuais do cenário e relógio. Isso confirma inspeção dos arquivos fonte; **não houve nova execução de emulador nesta etapa de planejamento**. Os relatos históricos de fade/DMA não demonstram causalidade por si só; reproduzir e medir antes de registrar causa definitiva. Nenhuma prova em hardware físico foi feita aqui.

## 2. Promessa, escopo e critérios de produto

**Promessa:** modelo de engine de luta 1v1 com regras documentadas, funcionalidades opcionais e conteúdo substituível por dados.

**Loop central:** escolher lutadores e cenário → movimentar, atacar e defender → receber feedback de dano/combos/especial → resolver o round → revanche ou nova seleção.

**Primeira entrega integrada:** abertura separada, título e opções funcionais, uma luta com tempo medido, relógio transparente, especial e combos nos dois jogadores. O segundo cenário fecha a entrega seguinte.

**Obrigatório nesta evolução:** todos os itens solicitados, opções ON/OFF com efeito real, dois cenários amplos, teste de todas as rotas do menu, manual e handoff por capacidade.

**Sugestões adicionais recomendadas:** treino com dummy, comandos documentados por lutador, input display, replay determinístico de QA, reset de configurações, registro de golpes e cenários por dados, builds normal/debug distintos. Entram em etapas próprias após a base.

**Backlog posterior:** SRAM de preferências, IA avançada, novos lutadores, cancels complexos, guard gauge e balanceamento competitivo aprofundado. Netplay/rollback e campanha narrativa não fazem parte desta entrega.

Identidade proposta: arcade de luta, logo HAMOOPIG legível, personagem preservado, paleta de acentos coerente com a fonte existente. Créditos a GameDevBoss/Daniel Moura na abertura e manual. Orientações de Rheo mantêm sua autoria própria. A referência comunitária é orientação técnica, não aprovação automática de assets ou implementação.

## 3. Contrato para agentes com e sem visão

Antes de começar, registrar capacidades reais, separadamente: executar shell/build; controlar emulador; ler RAM/VDP; capturar imagens; compreender imagens; interpretar vídeo; ouvir áudio. Capturar PNG não significa compreendê-lo; visão de imagens isoladas não comprova percepção temporal; analisar amplitude de WAV não equivale a escutar.

| Atividade | Sem visão pode concluir | Revisão adicional necessária |
|---|---|---|
| Vida, especial, combo, regras ON/OFF | Valores, transações, resets e testes do C real | Clareza do feedback durante a luta |
| Menus | Alcance dos itens, valores, input, transições, limites de cursor | Leitura, hierarquia, recorte e sobreposição |
| Transparência | Índices, máscara, tiles, CRAM e composição instrumental | Contorno íntegro e legibilidade em fundos diferentes |
| Cenários | Dimensão, paleta, hashes, tiles, câmera, residência e DMA | Cor, saturação, costuras, repetição, profundidade e relação com lutadores |
| Timing | Ticks, duração, atrasos, frame misses, reprodução de inputs | Sensação de peso, resposta e ritmo |
| Fade | Sequência de estados, CRAM e duração por frame | Continuidade visual, flashes, cortes e equilíbrio de ritmo |
| Áudio | Roteamento, driver, canais, silêncio/sinal e flags | Timbre, mix, cortes, distorção percebida e pertinência dos SFX |

Estados por eixo: `not_run`, `passed`, `failed`, `blocked_tooling`, `pending_visual_review`, `pending_audio_review`, `not_applicable` com justificativa. Ausência de visão bloqueia a aprovação visual, não o trabalho independente de lógica.

O executor sem visão deve:

1. Consumir atlas, máscaras e coordenadas declaradas; nunca inventar descrição do que a captura mostra.
2. Implementar e testar o contrato observável; produzir capturas mesmo sem interpretá-las.
3. Deixar arte nova como candidata. Se faltar fonte autoral, concluir loaders, manifesto e testes com fixture identificada; a entrega do cenário continua pendente.
4. Gerar handoff com hash da ROM, cenário/estado, região, opções, seed, inputs por tick, frames de interesse, métricas, arquivos e perguntas objetivas.
5. Usar `null` para resultados não medidos; não converter ausência de erros em aprovação.
6. Prosseguir pelos itens sem dependência da revisão pendente.
7. Receber a revisão, corrigir e recapturar. Toda alteração que afete a prova invalida a aprovação anterior daquele eixo.

Revisor com visão: comparar fonte, saída convertida e framebuffer da mesma ROM, além do vídeo. Informar defeito, frame, região da tela, impacto e critério de correção. Se o mesmo executor tiver visão nativa, pode executar esse protocolo; se o gate canônico exigir revisão independente para promoção, fornecer também esse parecer.

## 4. Arquitetura e ordem de execução

A numeração abaixo é a referência das tarefas no JSON. Módulos citados como **novos** são propostas, não arquivos existentes.

| ID | Entrega | Depende de | Saída verificável |
|---|---|---|---|
| P00 | Baseline, documentação e ferramentas confiáveis | — | Inventário, contratos e relatório inicial |
| P01 | Timing, input e separação de debug | P00 | Testes temporais + telemetria NTSC/PAL |
| P02 | Gerenciador de cenas e abertura separada | P01 | Roteiro de transições e prova de fade |
| P03 | Configurações e menu completo | P02 | Matriz item/valor/efeito/retorno |
| P04 | Eventos de combate e reset | P01 | Testes reais de colisão e dano |
| P05 | Barra e regras de especial | P04, P03 | Carga/consumo/ON/OFF simétricos |
| P06 | Contador de combos | P04, P03 | Hits confirmados, término e apresentação |
| P07 | HUD transparente e composição final | P05, P06 | Timer, vida, especial, hits e fonte integrados |
| P08 | Cenário Showdown revisado e renderer de estágios | P01, P07 | Comparação de arte + budget de câmera |
| P09 | Segundo cenário amplo | P08, P03 | Dois palcos selecionáveis e testados |
| P10 | QA integrada e revisão sensorial | P02–P09 | Matriz completa, evidências frescas, pendências explícitas |
| P11 | Modelo reutilizável e manual | P10 | Exemplo de extensão, manual e pacote verificável |

Revisão visual pode acontecer a cada etapa, sem esperar P10. No primeiro ciclo, resolver P00–P04 e a causa do relógio; em seguida integrar especial/combos; depois finalizar palcos e fechar QA.

### P00 — Baseline e verdade operacional

- Ler AGENTS, memory bank, GDD, spec, TDD, manifests e índice de lições. Preservar alterações locais, incluindo menu debug/pausa/H240 recentes.
- Executar os guards e validadores metodológicos do workspace pelos wrappers disponíveis. Não recriar infraestrutura de build dentro do jogo.
- Registrar commit, dirty state, hash de fontes relevantes, ROM, toolchain efetiva, emulador/configuração, região e opções. Capturas antigas permanecem históricas.
- Atualizar GDD/brief de “porta direta” para modelo de engine extensível conforme este pedido; manter teto `prototype` até as provas.
- Reconciliar IDs de cena e retirar do contrato ativo referências herdadas a módulos inexistentes. Arquivar histórico sem apagá-lo.
- Rodar testes existentes; documentar a cobertura real. `test_title_menu_contract.py` atualmente busca tokens: não prova menu em execução.
- Auditar HPRB/decoder antes de confiar nos valores: schemas, tamanho/truncamento, endian, contagem saturada, sample count, atribuição ao mesmo frame, região e altura. O decoder atual não oferece `--self-check`; incluir fixtures positivas e negativas antes de usá-lo para aprovação. Corrigir tratamento de versões antigas quando campos não existirem.
- Separar fila DMA pendente, bytes efetivamente transferidos e backlog. Não usar limite genérico como medida do frame; PAL 224 e PAL 240 têm envelopes diferentes.

### P01 — Velocidade e input

Diagnosticar três causas separadas: velocidade do emulador/host, cadence do loop e duração das ações. Comparar caminhada, salto, startup/active/recovery de golpes, hitstop, intro de round e relógio. Não “corrigir” tudo trocando uma constante.

Proposta de contrato:

- Vídeo: H40 320×224, refresh nativo NTSC/PAL. H240 existente fica em debug e só se aplica a PAL e conteúdo com altura suficiente.
- Simulação normal: unidade de 60 ticks por segundo. NTSC normalmente 1 tick por VBlank; PAL usa acumulador inteiro e alterna 1/2 ticks conforme necessário para média de 60. Render/upload uma vez por frame de vídeo.
- Não multiplicar simplesmente física ou dano. Cada subpasso roda colisão, timers e transições coerentemente. Não reaplicar borda de input no segundo subpasso.
- Input amostrado a cada frame de vídeo, com bordas retidas até consumo lógico; toques em frames sem tick não podem desaparecer.
- Menus e fades usam tempo de apresentação, independente de slow motion/free-step da luta.
- Pausa congela luta, combo, especial e round; input de saída continua ativo. Hitstop congela somente os domínios definidos, preservando eventos únicos.
- Relógio padrão: um decremento a cada 60 ticks de luta ativa; opções 60/99/sem limite. Ritmo arcade legado de 38 ticks apenas no perfil de comparação/debug.
- Compatibilidade PAL: medir frame com dois ticks e áudio. Se exceder budget, registrar pendência e otimizar; não chamar 50 ticks de “60” nem promover PAL normalizado incompleto.
- Modos 50/60 atuais passam a ser opções de diagnóstico claramente identificadas; NORMAL sempre seleciona a política acima. Não apresentar um defeito de velocidade como opção do jogador.

Novos módulos propostos: `timing.c/.h`, adaptação de `input.c`, `main.c`, timers de HUD/FSM e probe. Tabelas de frame data preservam o baseline até teste objetivo indicar ajuste.

Aceite: replay com mesmas ações/seed termina com mesmo estado em simulação equivalente; 10 s de luta ativa correspondem a 600 ticks no teste determinístico, diferença de apresentação limitada a um frame. Medir emulador em cinco janelas de ao menos 10 s com áudio e cena pesada; reportar atraso e frame misses, sem confundir título da janela com FPS da ROM. Playtest de sensação permanece sensorial.

### P02 — Abertura, fade e título como cenas distintas

Novo `opening.c/.h`; `title.c/.h` passa a conter apenas título/opções. `main.c` delega a um gerenciador explícito (`scene.c/.h`, novo). Enumerar salas atuais antes de escolher novos valores; preservar compatibilidade dos probes.

Transição proposta:

`OPENING_FADE_IN → OPENING_HOLD → OPENING_FADE_OUT → TITLE_LOAD → TITLE_FADE_IN → TITLE_ACTIVE`

- Entrada 0,3 s; hold 2 s após terminar a entrada; saída 0,25 s; entrada do título 0,25 s. Converter durações para frames da região com arredondamento definido.
- A/START durante hold solicita skip para fade-out; não confirma START no título. Durante fade, ignorar navegação e duplicação de confirmação.
- Carregar a composição do título com display protegido/preto, em lotes que caibam; terminar DMA antes do fade-in. O tempo de carga é medido e separado do fade.
- Usar um único owner de CRAM e uma transição assíncrona controlada por estado, sem fades concorrentes ou dependência de espera bloqueante no meio do dispatch.
- `Scene_request()` agenda a troca; commit ocorre em um limite único. Garantir exit/init exatamente uma vez e apenas um update de cena por tick.
- Inventariar e migrar TODAS as atribuições a `gRoom`, inclusive revanche e round reset. A convenção atual `gFrames=0/1` depende da ordem dos `if`; trocar para switch sem migrar isso quebra o fluxo.
- Limpar inputs consumidos sem apagar preferências. Invalidar caches/handles e restaurar scroll, WINDOW, altura, paletas, tiles e áudio no owner correto.
- Entrada de créditos nunca fica atrás do painel. Título possui arte/composição própria, não um retângulo sobre os créditos da abertura.

Seed de composição: canvas 320×224; margem segura 8 px; logo x16–304/y16–64; menu x24–184/y88–176; área do personagem x200–312/y72–208; rodapé y208–223. Opções abrem página própria, até seis linhas de 16 px com espaçamento de 8 px e paginação. Não forçar fonte 16×16 e nove itens no retângulo atual. Coordenadas são contrato inicial a verificar com arte.

Reutilizar identidade e atlas autorizado; extrair renderer de fonte compartilhado com HUD, com ownership de paleta/tiles por cena. Todo glyph necessário deve existir; textos do runtime inicialmente ASCII. Painel/cursor finais têm fonte/proveniência registrada. Não gerar personagem ou cenário final com primitivas.

Teste: boot, skip no início/fim do hold, botões mantidos, input simultâneo, intro OFF, fade OFF, reentrada no título e 100 ciclos sem leak. Capturar vídeo desde antes do fade até o título estável, com CRAM e estado instrumentados. OCR ou duas screenshots não certificam suavidade.

### P03 — Opções com semântica e persistência claras

Novo `GameConfig` em `config.c/.h`: defaults únicos, validação de valores, separação de flags visuais/regras e cópia `MatchRules` congelada no começo da partida. Preferências duram a sessão; SRAM fica para fase posterior. Opções visuais podem ser imediatas; regras e stage pool entram na próxima partida.

Menu principal: **START, OPTION**. START abre o fluxo existente de lutadores, seguido de seleção de cenário. P2 permanece ignorado no front-end; P2 joga normalmente na luta. Não adicionar botão inativo sem destino implementado.

OPTION abre páginas: **AUDIO, HUD, GAME, VIDEO, DEBUG, DEFAULTS, BACK**. Paginação e rótulos ajustados ao atlas. Tabela de strings e comprimento/caixa constituem contrato testável.

| Opção | Default proposto | Efeito quando OFF / alternativa | Momento |
|---|---|---|---|
| SFX | ON | Bloqueia novos SFX; encerra apenas PCM pertencentes aos SFX | Imediato |
| MUSIC | ON | Para BGM; ON retoma faixa da cena pela política documentada | Imediato |
| LIFE BAR | ON | Oculta barras; vida e KO continuam funcionando | Imediato |
| SPECIAL BAR | ON | Oculta barra; não altera regras de especial | Imediato |
| HIT COUNT | ON | Oculta feedback; contador/eventos continuam testáveis | Imediato |
| TIMER | ON | Oculta números; limite de tempo continua ativo | Imediato |
| TIMER BG | OFF | Fundo transparente; ON usa painel compacto de contraste | Imediato |
| SPECIAL RULES | ON | OFF: golpes configurados não exigem/cobram medidor; treino comparativo | Próxima partida |
| TIME LIMIT | 99 | 60, 99 ou OFF; OFF desativa time-over | Próxima partida |
| OPENING | ON | Pula abertura na próxima entrada/boot com config válida | Próxima entrada |
| FADE | ON | OFF: corte com carga protegida, sem flashes de recursos parciais | Próxima transição |
| STAGE COLOR | ENHANCED | ORIGINAL seleciona variante anterior identificada | Próxima carga |
| STAGE MOTION | ON | OFF desliga animação/parallax cosméticos; câmera básica continua | Próxima carga |
| STAGE 2 | ON | OFF retira o segundo cenário da seleção; primeiro permanece disponível | Próxima partida |
| DEBUG | OFF | Mestre oculta ferramentas; subitens existentes preservados | Conforme função |
| DEFAULTS | Ação | Restaura valores e limpa step/pausa/debug indevidos | Imediato/próxima partida |

Esses controles implementam “habilitar/desabilitar” sem oferecer uma opção de reintroduzir corrupção. A correção de timing, a separação de cenas e os limites do hardware são invariantes; modo LEGACY/50 e H240 são diagnóstico, não defaults de entrega. DEFAULTS não é um toggle. Não permitir excluir todos os cenários nem congelar o próprio menu com STEP.

UP/DOWN navega, LEFT/RIGHT escolhe explicitamente valor anterior/próximo, A/START confirma, B volta; um pressionamento gera uma ação. Prioridade determinística: B, confirmar, ajustar, navegar; opostos simultâneos neutralizam-se. Preservar cursor ao retornar; nenhuma cascata para outra página no mesmo input.

Aceite por item: valor mostrado coincide com config e efeito real; ON→OFF→ON; BACK/B; extremos; key held; P2; DEFAULTS; boot; título→luta→revanche→seleção. Para DEBUG validar BBOX/HBOX/TEXT/PERF/FRAMEADV/FREESTEP/TICK/H240 e respectivas dependências. Áudio OFF deve impedir também chamadas diretas fora de `FUNCAO_PLAY_SND`; auditar todos os produtores.

### P04 — Eventos de combate e reset

Novo `CombatEvent` contém atacante, defensor, instância de ataque/projétil, hit index, tick, dano, guard/hit/throw e resultado. Produzir evento no caminho real que resolve colisão; consumir para vida, medidor, combo, som e efeitos.

Um overlap durando vários frames não é vários hits. Multihit só emite novamente quando o contrato do golpe autorizar outro hit index. Tratar projétil persistente, troca simultânea, chip, KO, throw e invulnerabilidade. Resolver eventos do tick em ordem declarada para não favorecer P1.

Não duplicar regras com novos contadores em paralelo ao legado. Fazer migração pequena e comparar resultados de dano existentes. Reset de round limpa ataques, projéteis, combos, medidor conforme regra, hitstop e referências; preserva config, roster e placar autorizado.

Teste do C real: hit único por overlap, multihit legítimo, whiff, defesa, chip, dano letal, troca simultânea e novo round. Usar relógio/eventos falsos apenas como dependências; não reescrever a fórmula sob teste em Python e chamar isso validação do runtime.

### P05 — Especial

Versão inicial proposta: medidor por jogador 0..32, inicia zerado por round, sem carry entre rounds nesta fase. Campo e intermediário impedem overflow/underflow.

Balanceamento inicial em dados: hit confirmado dá +4 ao atacante e +2 ao defensor; bloqueio dá +1 ao atacante; whiff não dá carga. Atualizar uma vez por evento. KO fecha a sequência; não ganhar repetidamente durante animação de derrota.

Selecionar e documentar um golpe já existente por lutador como `metered_special`, custo 32, sem inventar animação final. Mapear comando e estado real de Ryo/Ken/Musgo em tabela. Demais golpes continuam sem custo salvo regra explícita. Debitar somente quando a FSM aceita iniciar o golpe; input inválido/interrompido antes da aceitação não cobra; interrupção posterior não devolve. Política sem autopreenchimento/rage oculto; auditar trechos legados de rage.

SPECIAL RULES OFF libera o golpe configurado sem custo e mantém o medidor inativo em zero; SPECIAL BAR OFF só oculta a apresentação. Se regra OFF, exibir FREE quando barra visível.

Renderer: pequenas células compartilhadas em VRAM, no rodapé, em duas áreas espelhadas. Proposta x8..135 e x184..311, y208..215 em 224 linhas. Transferir padrões compartilhados uma vez; alterar só células/frames necessários. Preenchimento parcial deve distinguir valores próximos; cheio/zero exatos.

Compartilhar tiles não é multiplexação por scanline: economiza padrões de VRAM, mas cada sprite continua custando SAT e pixels por linha. Se o alocador mover o tile owner, atualizar aliases ou usar reserva fixa explícita; manter instâncias vivas não prova que o bloco não se moveu.

Aceite: 0,1,31,32; saturação; custo insuficiente/exato; P1/P2; eventos duplicados; pause/hitstop; KO/reset; regra OFF e HUD OFF. Revisão visual: barra não esconde pés/sombra, cheio legível sem flash excessivo e esvaziamento simétrico.

### P06 — Contador de hits/combos

Definir combo como hits confirmados do mesmo atacante sem o defensor recuperar oportunidade de agir; a janela de hitstun/juggle/throw deve estar em dados. Bloqueios não incrementam combo; contatos após recuperação iniciam nova sequência.

Estado por atacante: `combo_hits`, `combo_damage`, `combo_active`, `display_until`. Campo legado da vítima não é a fonte única. Exibir a partir de 2 hits; manter resultado por 60 ticks de apresentação após término; zerar no próximo round. Contagem interna saturada em u16; display 99+ se exceder 99.

Hitstop não duplica evento; projétil mantém autoria; throw conta uma vez ou usa hits autorados; KO preserva a contagem final antes do reset. Definir troca simultânea sem apagar prematuramente o combo oposto. Contador de treino “hits totais” é separado e rotulado.

Posição inicial: abaixo das barras de vida, longe do relógio e das mensagens centrais; no máximo três dígitos/símbolo e HITS. Somente redisplay quando mudar.

Aceite: hit isolado, combo de 2/3 hits, intervalo após recuperação, guard, multihit, projétil, throw, troca simultânea, morte e reset, P1/P2 e display OFF. Revisão visual/temporal: leitura e tempo de permanência, sem esconder ação.

### P07 — HUD e transparência

- Criar máscara de fundo do atlas do relógio a partir da fonte/contrato. Remapear os pixels de fundo ao índice 0, preservando contornos escuros do glyph. Não trocar “todo RGB preto” cegamente.
- Testar cada dígito 0..9 em ambos os lados e transições 10→09→00. TIMER BG OFF não escreve preenchimento opaco por trás.
- Manter vida 0..96 correta, P2 espelhado, zero integral; separar vida real, easing e eventual trilha de dano.
- Renderer de fonte compartilhado entre HUD/título; catálogo completo de strings e custo por cena. Não trocar PAL2/PAL3 dos lutadores para mostrar texto.
- Emitir `doc/ui_pixel_surface_contract.json` com atlas hash, grid, índices de cor/transparência, máscaras, posições, prioridades, custos e ownership. Fonte, moldura e cursor têm proveniência explícita.
- Medir HUD + lutadores + sparks + especiais na mesma scanline. Barras de especial abaixo e combo acima ajudam a distribuir carga, mas isso não substitui a medição.
- Evitar painel preto permanente de largura inteira; opções de contraste são compactas e intencionais.

Aceite sem visão: diferenças de pixel fora da máscara zero; glyph preservado; limites de tela; spans VRAM sem overlap; flags e sprites coerentes. Aceite visual: fundos claro/escuro dos dois palcos, câmera nos extremos, salto no topo, KO e avisos de round.

### P08 — Cenário atual, cor e arquitetura de estágios

Objetivo visual: recuperar detalhe, verdes/azuis e separação entre árvores, água e pedra; reduzir repetição quadrada sem apagar formas. Referência primária local `rascunho/showdown_native_crop_preview.png`; fonte histórica e contrato em `doc/art/showdown/`.

Consultar também as versões melhores do laboratório do workspace
`SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/`.
Inventariar os candidatos e copiar as fontes/configurações relevantes para o rascunho
deste projeto com hashes antes de usá-las no pipeline. Comparar o mesmo recorte/câmera;
não assumir que uma versão anterior “melhor” caiba no orçamento atual.

Comparar separadamente: fonte → quantização para CRAM → redução de tiles → composição na ROM. Aumentar saturação global não restaura detalhe perdido. Medir erro por região, costuras de tiles, repetição e número de cores; tais métricas detectam degradação, mas não aprovam arte.

**Decisão inicial de rota: adaptar o baseline de streaming guiado pela câmera.** Fazer diagnóstico de ocupação por janelas antes da conversão final:

1. Medir tiles únicos visíveis em cada posição da câmera e numa margem de preload.
2. Avaliar mapa com tileset residente e reutilização exata; alternativa de cache de padrões por blocos quando o conjunto não cabe.
3. Distinguir streaming de tilemap de streaming de padrões: MAP não resolve automaticamente um tileset grande demais.
4. Emitir orçamento conjunto de planos, tabelas VDP, HUD, font, sprites dinâmicos e buffers RAM. Reservas antigas 768/420 não são metas universais.
5. Primeira composição pode continuar flat BG_B se passar o visual. BG_A para camada secundária exige owner compartilhado com mensagens do HUD ou migração desses textos; WINDOW não é terceiro plano independente.
6. Um upload de coluna pode concorrer com golpe grande, especial e PCM. Medir essa interseção e preload antes da borda; nunca exibir tile faltante enquanto “a fila alcança”.
7. Medir o próximo degrau de cache/painel/qualidade; registrar por que o candidato final foi escolhido. Não promover o mais leve só por compilar.

Paletas iniciais: PAL0 cenário, PAL1 HUD, PAL2 P1, PAL3 P2. Mais cor no cenário exige redistribuição com prova dos demais consumidores; não assumir paleta livre.

Novos `StageDefinition` e `stage.c/.h`: ID, dimensões, piso, limites de luta, câmera, paletas, layers, parallax, animações, loading model, BGM, custo e proveniência. `init.c` carrega a definição selecionada, não fórmulas específicas do nome do cenário.

Viewport 320×224; manter escala atual de Ryo/Ken/Musgo. Palco atual 512×256: travel horizontal 192; vertical até 32 no modo 224 e até 16 no modo 240. Calcular limites por dimensão/altura, inclusive intermediários assinados. Velocidade de câmera não altera posição mundial nem física do lutador.

Aceite: extremos esquerdo/direito/topo/baixo, saltos, reversão de câmera e fronteiras do cache sem dado não inicializado, costura ou invasão de VRAM. Revisão visual obrigatória da cor, textura, profundidade e legibilidade dos três lutadores.

### P09 — Segundo cenário amplo

Usar o mesmo StageDefinition/loader. Proposta autoral inicial: **cais de pântano do Musgo**, plataformas de madeira/pedra e água ao fundo, para diferenciar do parque. Isso é direção proposta; não há asset final identificado nesta revisão.

- Fonte externa autorada/gerada por ferramenta de imagem ou artista, persistida com prompt/origem/hash. Executor sem visão pode preparar contrato e integrar candidato, mas não aprovar o resultado.
- Tamanho alvo 768×256; mínimo de aceitação 512×256, com largura pelo menos igual ao palco atual e scroll real. Meça 1024×256 como próximo degrau antes de fechar a escolha; largura em ROM não implica carregar tudo na VRAM.
- Piso plano coerente com o sistema de luta existente, sem introduzir plataformas físicas nesta etapa.
- Plano distante com movimento sutil e foreground controlado se budget permitir; STAGE MOTION OFF preserva cenário completo estático e câmera. Evitar cenário “amplo” que seja só a mesma tela duplicada.
- Seleção após lutadores: PARK / DOCK e BACK, fonte local legível e miniaturas autoradas se houver orçamento. Stage 2 OFF remove DOCK e resolve seleção anterior para PARK na próxima partida.
- Rematch preserva cenário; nova seleção permite trocar. BGM por StageDefinition e respeito às flags. Nenhuma troca de estado deve herdar tiles/paletas/scroll do palco anterior.
- Os dois stages ocupam ROM, mas só o stage ativo possui recursos de cena residentes.

Aceite: repetir toda a regressão de luta/KO/reset nos dois cenários, áudio por cena, paleta do roster, 100 trocas de palco e câmera nos extremos. Fonte nova sem review mantém P09 parcialmente concluído, mesmo que o loader passe.

## 5. Plano de testes e evidências (P10)

**Matriz mínima:** três lutadores × três adversários × dois cenários × duas regiões = 36 combinações ordenadas. Em todas: boot/entrada, movimento, salto, golpe, vida, timer e encerramento básico. P1/P2, mirrors e paletas alternativas têm cobertura explícita.

Adicionar sequências determinísticas: KO de cada lado, time-over desigual, empate, multihit, projéteis simultâneos, especial aceito/negado, KO durante combo, revanche, seleção e reset. Definir inputs por tick lógico e registrar sua apresentação por frame; o mesmo input script por tempo de parede não garante equivalência.

Configurações: defaults, tudo visual OFF, tudo ON e combinações aos pares. Testar exaustivamente interações perigosas: HUD × regras; timer display × limite; intro × fade; áudio × pausa; região × timing × H240; debug mestre × subitens; segundo palco × seleção. Não declarar todos os conjuntos testados por cobertura pairwise.

Performance:

- Relatar frames/ticks, skipped/missed VBlanks, CPU/pior tempo quando instrumento permitir, DMA enviado/pendente/backlog, sprites ativos, links SAT, sprites por linha e pixels por linha.
- H40 tem limite de 80 entradas, 20 sprites/linha e 320 pixels de sprite/linha. Contar largura processada, inclusive área transparente; não basta contar pixels visíveis.
- Recalcular envelope de VBlank pela região/altura e rota real de transferências; thresholds hardcoded dos relatórios antigos não são certificação.
- Worst cases: dois lutadores grandes em ataque/salto + sparks + projéteis + barra cheia + combo + scroll na fronteira + áudio ativo.
- Partida prolongada por região e 100 ciclos de cena/reset para detectar leaks, stale handles e fragmentação. Falha de alocação é erro de teste, não sprite “opcional”.
- Baseline com instrumentos e build normal separados; medir custo da sonda. Nenhum cheat de QA nem probe pode substituir o caminho real do gameplay.

Áudio: captura isolada por emulador; ligar/desligar SFX/MUSIC independentemente; validar entrada/saída, duas fontes de SFX simultâneas, pausa e troca de BGM. Sinal RMS/peak é prova elétrica; revisão auditiva fecha o mix.

Cada bundle novo em `out/emulator_evidence/<session_id>/` contém ROM hash, toolchain/config, input script, seed, manifest, screenshots, vídeo da transição e combate, áudio isolado, SRAM/probe e dumps VDP quando exigidos. Nunca sobrescrever capturas de ROM anterior; cache visual não é aprovação de novo binário.

Não usar screenshot de boot para afirmar combate, vídeo mudo para afirmar áudio, ou nome da janela para afirmar FPS do loop. Ferramentas de captura/controlador devem ser verificadas no host atual, inclusive compatibilidade X11/Wayland e instância correta.

## 6. Ferramentas existentes e lacunas

Caminhos abaixo relativos ao projeto, salvo os explicitamente relativos ao workspace. Conferir assinatura/ajuda antes de executar.

| Existe hoje | Uso real |
|---|---|
| `tests/test_health_contract.py` | Regressão de saúde; ampliar conforme eventos |
| `tests/test_timeover_contract.py` | Time-over; adaptar à nova unidade temporal |
| `tests/test_stage_palette.py` | Paleta/asset de referência; não prova estética |
| `tests/test_title_menu_contract.py` | Smoke por tokens; substituir/complementar por execução do C |
| `tests/capture_visual_ko.py` | Captura/input existente; inspecionar adequação a novas cenas |
| `tests/analyze_hprb_probe.py` | Decoder existente, com self-check ainda a implementar |
| `tests/audit_captured_audio_signal.py` | Sinal de áudio; não escuta. Tem `--self-check` (silêncio, RMS conhecido, clipping, entrada vazia) |
| workspace: `tools/sgdk_wrapper/build_sgdk_wine_bridge.sh` | Build canônico |
| workspace: `tools/sgdk_wrapper/capture_blastem_evidence_linux.sh` | Captura canônica |
| workspace: `tools/sgdk_wrapper/finalize_emulator_evidence.ps1` | Selo de evidências; respeitar requisitos reais |
| workspace: `tools/sgdk_wrapper/scene_contract_compiler.ps1` | Reconciliar contratos com cenas reais |

**A criar**, conforme a etapa: testes de timing/input/C de cenas, config/menu, eventos de combate, medidor, combos, máscaras de HUD e StageDefinition; probe ampliado; manifesto de evidência e handoff visual. Preferir `tests/` se permitido pelo manifesto local, migrando testes de rascunho com referências atualizadas. Nenhuma dessas ferramentas novas deve ser citada como existente antes da implementação.

APIs locais SGDK 2.11 são a autoridade. Fontes primárias complementares: [paletas/fades](https://github.com/Stephane-D/SGDK/blob/master/inc/pal.h), [MAP e scrolling](https://stephane-d.github.io/SGDK/map_8h.html), [tutorial de backgrounds](https://github.com/Stephane-D/SGDK/wiki/Tuto-background). Conferir diferenças de versão antes de copiar exemplos. MAP atualiza tilemaps via fila DMA; preload e residência dos padrões precisam de planejamento próprio.

## 7. Modelo amigável e completo (P11)

Para transformar correções em uma engine que outro desenvolvedor consiga usar:

- `engine_quickstart.md`: dependências, wrapper, build/run e diagnóstico de falha; executar o passo a passo em cópia isolada.
- `engine_extension_guide.md`: registrar lutador, golpes, hitboxes/hurtboxes/pivôs, custos de especial, cenário, BGM e HUD. Exemplo mínimo integrado e compilável.
- `controls_and_options.md`: comandos reais, navegação, pausa, defaults e o que cada OFF muda. Validar controles de 3/6 botões conforme suporte declarado; não prometer seis ataques em pad de três botões sem mapeamento implementado.
- Tabelas por dados para FighterDefinition/MoveDefinition/StageDefinition; pools estáticos e ownership claros. Extrair progressivamente do monólito, sem reescrever toda a FSM de uma vez.
- Perfis NORMAL e DEBUG; frame-step, tick e H240 visíveis como ferramentas, sem vazamento acidental para build normal. Erros de configuração rejeitados com mensagem útil.
- Modo treino recomendado: dummy parado/defendendo, refill opcional de vida/especial, input display, reset de posição e frame advantage. Esse modo é extensão própria e não critério implícito para encerrar as correções solicitadas.
- Registro de assets/áudio e créditos exportável com o template. Manter fontes de estudo de arcade identificadas; a redistribuição como pacote exige resolver as permissões das fontes, sem inventar licença.
- Build reproduzível, testes em lote pelo wrapper, ROM identificada por versão/hash e matriz de compatibilidade. Hardware físico só recebe status aprovado depois de teste próprio.

## 8. Documentos que a implementação deve atualizar

`doc/11-gdd.md`, `doc/15-tdd.md`, `doc/03-arquitetura.md`, `doc/13-spec-cenas.md`, `doc/scene-contracts.json`, `doc/scene-regression.json`, `doc/07-budget-vram-dma.md`, `doc/14-plano-de-provas-qa.md`, `doc/17-audio-design.md`, `doc/technique_usage_manifest.json`, `doc/asset_provenance_manifest.json`, manifests de contexto/metodologia quando necessário, `doc/10-memory-bank.md` e `doc/changelog/changelog.md`.

Seeds deste plano: briefing/loop/escopo (§2); identidade e cutscene de abertura sem diálogo (§2/P02); escala/câmera (§P08); UI (§P07); mecânicas (§P04–P06); arquitetura/timing/pools (§P01–P04); arenas (§P08–P09); roster preservado Ryo/Ken/Musgo sem novos inimigos; áudio por cena (§P03/P09/P10); runtime/CI/manual (§5–7). Música adaptativa e narrativa longa ficam fora desta fase.

Formalizar brand/UI/transition cards antes de arte/runtime final. Mapear técnicas a IDs existentes no registry, sem inventar IDs. Estratégia inicial: preload local para front-end/HUD, streaming de mapas/cache avaliado por câmera para cenários, janelas de animação para sprites. Arte nova começa por diagnóstico/tradução autoral; núcleo começa por timing e eventos. Evidência decide a rota.

Lições novas vão para JSON local em `doc/curation/`, com sintoma, reprodução, causa comprovada ou hipótese, correção, teste preventivo, hash e limitações. Não promover regra ao framework por causa de uma captura ou por mera sugestão do plano.

## 9. Critério de encerramento

Para cada P00–P11, registrar separadamente código integrado, build, testes, execução instrumental no emulador, revisão visual, revisão auditiva, budget e documentação.

A engine só será descrita como “modelo completo validado nesta versão” quando todos os itens obrigatórios tiverem os eixos aplicáveis aprovados, o manual tiver sido reproduzido e a ROM final corresponder às evidências. Enquanto faltar visão, áudio, fonte de arte ou budget, a entrega deve dizer exatamente: **o que funciona, o que foi medido e o que ainda precisa de revisão**.

Primeiro passo do executor: P00, medir timing/identidade da ROM atual e reproduzir os defeitos. Não usar o relato anterior de “transição corrigida” como aceite da separação de telas solicitada agora.
