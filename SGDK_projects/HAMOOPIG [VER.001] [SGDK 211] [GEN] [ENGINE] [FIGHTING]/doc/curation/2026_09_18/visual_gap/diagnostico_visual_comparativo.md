# HAMOOPIG — diagnóstico comparativo de qualidade

18 de setembro de 2026 · Oito referências fornecidas pelo usuário · Estado atual auditado por código, recursos e capturas persistidas.

## 1. Parecer

**O principal desnível está na direção de arte, na apresentação do combate e na especificidade das animações. A base técnica já contém boa parte dos sistemas citados, mas ainda não os transforma em uma experiência visual coesa.** Acrescentar sistemas indiscriminadamente ou aumentar todos os sprites não resolveria essa diferença.

Nas referências, cada tela comunica imediatamente quem luta, quanto resta de vida, qual recurso está disponível, o impacto de um golpe e em que fase está a partida. Retratos, barras, números, letreiros e efeitos possuem hierarquia e acabamento. O cenário oferece um lugar reconhecível, com materiais e profundidade, em vez de apenas preencher a tela.

Na captura atual do HAMOOPIG, há dois lutadores grandes, vida, relógio, round e hits. Porém, a vida não tem uma moldura que preserve a leitura da capacidade total, o especial parece outra barra de vida, faltam retratos, a tipografia varia entre sistemas e o cenário apresenta blocos de textura que disputam a atenção com os personagens. A seleção funciona como um painel de teste. Musgo ainda não possui o mesmo grau de clareza e acabamento dos lutadores importados.

O caminho recomendado é concluir **uma fatia de qualidade: dois lutadores completos, um cenário bem resolvido e toda a sequência seleção → round → combate → resultado → revanche**. Esse recorte deve estabelecer o padrão antes de multiplicar o elenco.

## 2. Escopo, fontes e limites

Foram vistas individualmente as oito imagens da pasta GAME. Elas foram copiadas sem edição para `rascunho/inputs/quality_reference_board_2026_09_18/`, dentro deste projeto; `reference_manifest.json` registra nomes originais e hashes. Seu uso é `quality_reference_only`: orientar julgamento e requisitos, sem importação de pixels para o jogo.

As capturas contêm molduras de Discord, vídeo e emuladores, com tamanhos e recortes diferentes. A comparação considera a área de jogo; não usa a largura do arquivo como resolução nativa. A informação de que pertencem à mesma família de engine vem do usuário: as imagens não comprovam, sozinhas, versão, plataforma ou arquitetura interna de todas as demonstrações.

**Imagem parada demonstra composição e uma pose. Não demonstra fluidez, FPS, transição temporal, parallax, qualidade de voz ou sincronismo.** Esses elementos entram como requisitos relatados pelo usuário ou hipóteses a verificar em vídeo/runtime. Nenhum efeito específico de VDP foi inferido apenas da aparência.

Base local: ROM `4c273bd5803913acbd62a55e6386f7c1e50e4d707cd14fd2fdd6c715ffa0ebbc`, memória operacional, fontes e recursos atuais. Foram vistas quatro capturas persistidas dessa rodada de ROM: `00_select.png`, `01_round.png`, `throw_only_result.png` do bundle `visual_ko_20260916T205914Z` e `01_title_initial.png` do bundle `title_return_20260916T212630Z`. **Não houve nova execução de emulador, avaliação de movimento ou audição nesta análise.**

O diagnóstico automático de arte encontrou **132 recursos ativos sem issues críticos nas verificações executadas** e nenhum bloqueio de build por esses recursos. Encontrou também 124 fontes em `/data`, das quais 116 exigem conversão e duas são inadequadas. Isso não significa 118 falhas no jogo: fontes fora do grafo ativo não bloqueiam o build. Tampouco o resultado técnico aprova estética, proveniência ou qualidade de animação. Há avisos de paleta que precisam de auditoria específica, sem conversão automática indiscriminada.

## 3. O que cada referência ensina

| ID / arquivo original | Evidência visível | Princípio a aplicar | O que não se pode concluir |
|---|---|---|---|
| R01 — 053901 | Lutadores de grande presença; efeito oval ocupa o centro; retratos e vida permanecem separados; avião e pessoas dão escala | Planejar a silhueta do golpe e reservar espaço para seu clímax sem apagar o HUD | Número de frames, colisão, custo DMA e estabilidade |
| R02 — 054019 | Retratos, nomes, relógio composto, barras de especial na base; água, vegetação e cascatas em planos perceptuais | Sistema visual completo e separação entre informação vital e recurso ofensivo | Água animada ou técnica de parallax |
| R03 — 054126 | Grade 4×4 com retratos, célula de interrogação, preview grande e título de seleção | Seleção como apresentação de elenco, com foco, identidade e expectativa | Que todas as 16 células representam personagens completos ou selecionáveis |
| R04 — 054159 | Árvore e lua funcionam como marcos; fundo azul frio contrasta com lutadores; interface compacta | Um cenário forte pode ter poucas massas dominantes e boa hierarquia | Efeito de iluminação em tempo real ou número de planos |
| R05 — 054410 | Letreiro “Round 2” grande, contornado, sobre o cenário; estrela e retratos permanecem legíveis | Abertura do round é um momento de apresentação, não apenas texto de estado | Duração, movimento do letreiro e voz do announcer |
| R06 — 054545 | Cenário mecânico com materiais reconhecíveis, profundidade e barras POW na base | Riqueza vem de materiais e estrutura, com faixas de informação reservadas | Viabilidade desse cenário no nosso orçamento ou como foi renderizado |
| R07 — 054631 | “RUSH 2 HITS”, número dominante, pose aérea e arco de golpe; vida e especial distinguíveis | Feedback deve explicar causa, consequência e progressão do combo | Janela real do combo, prioridade, cancel ou qualidade de interpolação |
| R08 — 054727 | “KO” ocupa o centro, contador de hits lateral, estrela e especial; golpe final ainda reconhecível | Resultado precisa de clímax e hierarquia sem apagar a ação decisiva | Hitstop, câmera lenta, voz ou reset correto |

R01–R08 correspondem aos arquivos `ref_01.png` a `ref_08.png` no manifesto. São referências de funções visuais distintas; misturar todas as suas estéticas numa única interface reproduziria justamente a inconsistência que precisamos corrigir.

## 4. Matriz: o que existe, o que falta e qual é a diferença

| Área | Estado observado no HAMOOPIG | Trabalho necessário | Prioridade |
|---|---|---|---|
| Escala dos lutadores | Sprites já grandes; Ken neutro declarado 64×96, Musgo 80×104 | Preservar presença e revisar proporções, pivôs e ocupação nos golpes | P1 |
| Animação específica | FSM e tabelas existem, mas muitos estados usam aliases genéricos | Autorar poses e timing que correspondam a movimento, guarda, dano, queda e vitória | P0 |
| Vida | Oito células por jogador, preenchimento amarelo e vazio transparente | Moldura, trilho vazio persistente, preenchimento fino e indicação de dano recente | P0 |
| Especial | Medidor funcional no BG_A, visual próximo da vida | Família própria, rótulo, estados de carga/pronto/consumo e feedback | P0 |
| Identidade do HUD | Nomes e vitórias representados por texto, asteriscos e pontos | Retratos, ícones de round e tipografia de identidade | P0 |
| Relógio | Atlas de dígitos e contagem existentes | Integrar moldura, contraste, alinhamento e alerta final | P1 |
| Hits | Contagem e exibição “HITS” implementadas | Número dominante, posição por atacante, entrada/saída e semântica de combo | P0 |
| ROUND/FIGHT/KO | Mensagens e estado de partida existem; KO também é símbolo fixo no topo | Letreiros próprios, coreografia e distinção entre rótulo fixo e evento de nocaute | P0 |
| Seleção | P1/P2, previews, confirmação e escolha de palco funcionam | Composição de elenco, retratos, cursores, confirmação visual e transição | P0 |
| Cenário | Duas definições residentes, uma camada cada; textura atual pouco hierarquizada | Reautoria modular, planos perceptuais, animação ambiental e tratamento de paleta | P0 |
| Câmera | Segue o ponto médio e acompanha altura de salto, com limites | Refinar enquadramento; implementar parallax separado se escolhido | P1 |
| Impacto | Há sparks/projéteis, hitpause, shake e sombras no código | Direção e verificação conjunta de pose, FX, som e resposta | P1 |
| Voz e música | PCM/SFX e BGM existem; três personagens compartilham mapa de SFX | Identidade sonora, announcer, prioridades, mix e escuta crítica | P1 |
| Título e retorno | Título, opções, fades e retorno implementados | Unificar linguagem com seleção/HUD e polir a passagem entre telas | P1 |
| Completude do jogo | Ciclo de luta parcial e matriz de probes | Uma partida completa validada antes de expansão e modos adicionais | P0 |

P0 = necessário para estabelecer o padrão do recorte; P1 = refinamento ou integração logo após. Prioridades não são uma estimativa de tempo nem prova de prontidão.

## 5. Diagnóstico por sistema

### 5.1 Personagens: presença já existe, especificidade ainda falta

Os lutadores atuais já ocupam uma fração importante da altura útil. A tabela declara 96 pixels de altura para Ken neutro e 104 para Musgo — aproximadamente 43% e 46% de uma tela de 224 linhas, respectivamente. São dimensões de célula, não medidas da silhueta visível. **Não há fundamento para aumentar todos os personagens como primeira correção.** Isso elevaria pressão de sprites e uploads, podendo diminuir o espaço para golpes e cenários.

A diferença mais concreta está em `inc/player_ken_table.h:143` e `inc/player_musgo_table.h:161`: conjuntos extensos de estados retornam a mesma animação. No Ken, estados 611/612 voltam ao neutro; diversos estados de dano/queda usam 550. Muitos ataques aéreos usam a sequência 300. No Musgo há vitória e queda específicas, mas ainda se repetem sequências em vários estados. Um alias pode ser deliberado; aqui, a quantidade e a abrangência exigem auditoria de cobertura visual por ação, antes de chamar o elenco de completo.

O resultado potencial é o personagem executar mecanicamente uma ação que sua pose não explica. A referência R07 é valiosa justamente porque a silhueta permite entender a ação naquele instante.

**Desenvolver:** ficha de poses por personagem; inventário estado → animação → frames → duração → pivot → janela de contato; poses próprias para deslocamento, salto, guarda alta/baixa, dano alto/baixo/aéreo, throw nos dois papéis, queda, aterrissagem, vitória e derrota. Um golpe não precisa de muitos frames por princípio: precisa de antecipação, ação e recuperação legíveis nos tempos corretos.

Para Musgo, resolver rosto, mãos, pés, volumes e espinhos em clusters nativos. A captura da seleção mostra mistura escura de verdes/marrons com contorno magenta aparente, dificultando separar anatomia e materiais. **O halo é um sintoma visual, não prova isolada de erro no índice transparente.** Comparar fonte, PNG indexado e ROM em fundo claro/escuro para distinguir franja de paleta, autoria do contorno e problema de conversão.

**Aceite:** mesma escala e apoio dos pés entre poses; nenhuma ação crítica depende de pose genérica incompatível; clipes em velocidade normal e quadro a quadro; revisão em tamanho de jogo, com o cenário real. Frames adiados pelo sprite engine não podem tornar o hitbox ilegível em relação à pose exibida.

### 5.2 Vida: modelagem correta ainda não produz leitura suficiente

`src/hud.c:249` converte energia de 0–96 em oito segmentos usando arredondamento para cima; cada degrau corresponde a 12 unidades, ou 12,5% da capacidade. Pequenos danos podem não alterar a barra imediatamente. `src/hud.c:255` oculta os segmentos vazios: perde-se a referência visual do comprimento máximo.

As referências preservam trilho, contorno e vazio. O jogador percebe o total disponível, a porção restante e, em algumas capturas, regiões de cor distintas. Uma imagem não demonstra que exista dano latente animado; esse é um requisito recomendado, não uma propriedade temporal comprovada das fotos.

**Desenvolver:** moldura externa contínua; trilho vazio persistente; preenchimento com resolução mais fina; camada de dano recente com duração autorada; espelhamento correto; contraste consistente sobre claro/escuro; zero e cheio inequívocos. Tiles parciais de uma célula podem permitir granularidade sem um sprite por pixel. Escolher atlas e residência antes de implementar.

**Aceite:** dano mínimo representativo altera a leitura; dano recente não altera a vida lógica; combo e KO preservam a sequência visual; barra de P2 esvazia no sentido correto; reset restaura todas as camadas.

### 5.3 Especial: precisa de vocabulário visual próprio

O medidor já existe (`src/hud.c:280`), mas usa a mesma família amarela e a região superior, logo abaixo da vida. Na captura, as duas informações se parecem demais. Nas referências R02/R06/R07, o recurso ofensivo está separado na base e possui rótulo e personalidade.

**Desenvolver:** família gráfica distinta, nome/ícone, estado vazio, carga parcial, pronto e consumo. A posição inferior é uma alternativa forte, mas depende do espaço dos pés e do palco: não deve cobrir a área de contato. Mudança de estado pode usar um pulso curto autorado, evitando cintilação contínua. O HUD consome eventos aceitos; não calcula ganho por overlap visual.

**Aceite:** jogador identifica vida e especial sem ler instruções; o estado pronto é reconhecível sem depender apenas da cor; gasto e reset são observáveis e não duplicados por hitpause.

### 5.4 Retratos, nomes, vitórias e relógio

As referências usam rostos como âncoras. Nosso HUD usa nomes e `*`/`.` (`src/hud.c:99–116`); não foi encontrado um retrato conectado nesse caminho. Portanto há uma implementação nova de retratos, enquanto nomes, vitórias e relógio pedem acabamento e integração.

**Desenvolver:** retrato pequeno autorado para cada lutador, moldura comum, variante/identificação consistente com a escolha, nomes com largura prevista e ícones de vitórias. Definir uma família para os dígitos. Integrar o símbolo KO fixo do topo ao design ou substituí-lo por um elemento menos ambíguo: o letreiro de nocaute deve ser claramente um evento.

Não colar miniaturas automáticas da sprite de corpo inteiro como retrato final. Retratos precisam de olhos, rosto e expressão legíveis na escala escolhida. Paleta e residência mudam entre seleção e combate; evitar fazer o HUD piscar quando a paleta do personagem muda por efeito.

### 5.5 Hits: contagem existe; dramatização e posição precisam amadurecer

`hud_combo_update` já escreve o total no BG_A (`src/hud.c:180`). Na captura atual, “2 HITS” aparece como texto espaçado na área baixa central; em R07/R08 o número domina e a palavra explica sua função.

**Desenvolver:** número grande com legenda menor, posição por atacante, duração curta legível, atualização sem reconstrução desnecessária e saída limpa. Definir a regra de encerramento do combo, a exclusão de guarda, a atribuição de projéteis e o tratamento de simultaneidade. A mesma identidade de evento deve alimentar dano, medidor, FX e contador.

**Aceite:** dois contatos do mesmo golpe persistente não viram dois hits; um multihit autorado vira; número não cobre rosto, projétil decisivo ou sinal de round; lados trocam corretamente. Comparar sequência completa, não só o frame em que o contador parece bonito.

### 5.6 ROUND, FIGHT, KO e resultado: o ciclo precisa de direção

O sistema já emite ROUND/FIGHT/KO/WINS/DRAW (`src/hud.c:455`). As referências R05/R08 mostram letreiros com volume, contraste e hierarquia. Não falta uma nova enumeração de estados; faltam arte de superfície e uma linha do tempo articulada com a luta.

**Desenvolver:** entradas e saídas dos letreiros; breve pausa de apresentação; sinal inequívoco de liberação do controle; clímax de KO; pose de vencedor; atualização de estrela; resultado e revanche. Associar voz apenas aos eventos corretos. Definir tempo em unidade explícita e comportamento PAL/NTSC, sem acelerar o jogo para acelerar o letreiro.

Em `src/hud.c:463–464`, as janelas atuais usam `gFrames` 180 e 300. Antes de alterar esses números, verificar a unidade e o percurso com o módulo de timing. Mais velocidade não é automaticamente melhor; a meta é antecipação e ritmo coerentes.

**Aceite:** nenhuma entrada de ataque vaza da seleção para o início; FIGHT termina quando o controle é liberado; KO não se repete; resultado representa o vencedor correto; DRAW e time-over têm apresentação própria; revanche não herda mensagem ou recurso da luta anterior.

### 5.7 Seleção: de configuração técnica a apresentação do elenco

`src/select.c:88–96` desenha instruções em texto sobre fundo preto; previews, dois cursores lógicos, confirmação e escolha de cenário já existem. R03 demonstra uma composição de seleção com escala de leitura, não a necessidade de copiar sua grade de 16 células.

**Desenvolver:** composição para o elenco realmente completo — três personagens podem ter três bons cards; cursores P1/P2 identificáveis; retratos; preview animado específico; nome; confirmação com pose/efeito; mudança de palco com pequena apresentação; desconfirmação e retorno claros. Deslocar comandos de depuração para uma tela própria.

Uma tela VS é uma extensão possível, não demonstrada nas oito imagens nem obrigatória para a primeira fatia. Deve entrar somente se sustentar a identidade e o ritmo aprovados no GDD.

**Aceite:** jogador escolhe sem ler um manual técnico; os dois jogadores podem selecionar o mesmo personagem com diferenciação clara; confirmação não duplica sons nem aloca sprites sem liberação; a entrada na luta preserva escolha, palco e paleta.

### 5.8 Cenário: a principal lacuna de arte de ambiente

A captura atual de SHOWDOWN mantém a composição geral de ponte, água e vegetação, mas converte grandes áreas em massas recortadas e padrões de alto contraste. Há disputa entre reflexos/chão e os pés; em partes, a textura parece ruído em vez de material. Isso é uma crítica à tradução visual observada, não prova de que 864 tiles sejam insuficientes para qualquer bom palco.

As referências oferecem diferentes soluções: R04 organiza a cena por árvore/lua; R02 por vegetação/cascata/reflexo; R06 por estruturas mecânicas. O objetivo é a clareza dessas decisões, não a soma de seus detalhes.

**Desenvolver:** uma planta do palco e pontos marcantes; kit de piso, estruturas e vegetação; bandas de contraste; área de luta legível; tratamento de bordas; paleta por material; módulos e repetições disfarçados por composição. Dither deve ajudar uma superfície ou rampa, não substituir desenho de volume.

Escolher um palco para retrabalho completo. Uma nova redução global de cores da mesma imagem pode manter o defeito estrutural. A reautoria deve começar na divisão de materiais e módulos, com comparação nativa antes do build.

### 5.9 Câmera, profundidade, animação e transição de cenário

Há câmera real: `src/graphics.c:237` segue o ponto médio dos lutadores, limita o deslocamento e acompanha saltos verticalmente. **Não é correto dizer que o palco não se move.**

Por outro lado, `src/stage.c:12` e `:30` declaram `layerCount=1` e carga residente; os parâmetros de parallax possuem `motionEnabled=FALSE`. O caminho de câmera observado escreve scroll global no BG_B. Isso não equivale a camadas independentes, animação de água/vegetação ou transição de iluminação.

**Desenvolver:** separar movimento de câmera, parallax e animação ambiental; escolher dois movimentos ambientais pertinentes ao palco, por exemplo água e folhagem; declarar fases e velocidades; definir uma transição perceptível entre apresentação e combate, ou entre rounds, se fizer parte da direção. O recorte inicial não precisa de todo tipo de efeito.

Uma implementação possível é BG_B para distância e BG_A para estrutura, compartilhando paleta quando isso preservar a leitura. Entretanto, BG_A hoje recebe mensagens, combo e especial: usar esse plano no cenário exige contrato de ocupação/restauração. WINDOW não é um terceiro plano livre independente de BG_A. Alternativas incluem faixas de scroll em um plano ou pequenos elementos em sprites, sempre medidos. A arquitetura deve nascer da composição escolhida.

**Aceite:** pés continuam presos ao chão; horizonte não acompanha o lutador como se estivesse colado nele; animação ambiental não rouba contraste dos golpes; mensagens não deixam buracos no cenário; não há costuras no extremo de câmera. Parâmetros declarados sem execução não contam como efeito implementado.

### 5.10 Impacto: integrar o que já existe

Há recursos `spr_spark*`, projéteis, sombras e hitpause. `src/physics.c:565` implementa shake durante hitpause; `src/main.c` possui caminho de slow motion de KO. Não se deve reimplementar esses sistemas sob a premissa de ausência.

**Desenvolver:** tabela de resposta por tipo/força de golpe; FX de contato com nascimento/pico/dissipação; diferenciação entre hit e guard; reação corporal; som; hitstop; eventual deslocamento de câmera. R01 define uma boa pergunta de teste: o golpe assinatura continua legível com os dois lutadores, cenário e HUD presentes?

O shake existente altera `P[i].x`. Avaliar se isso interfere em pushboxes/alcance: preferir separar deslocamento de apresentação da posição física quando o efeito não deve mover o lutador. Trata-se de risco de arquitetura, não de bug de gameplay comprovado nesta análise.

**Aceite:** força percebida combina com consequência; guarda não parece dano; FX não mascara o início do próximo golpe; nenhum flicker é usado para esconder excesso de sprites; nenhum ganho extra de combo ou especial nasce do efeito.

### 5.11 Áudio e vozes: já há reprodução, falta identidade comprovada

`res/sound.res` contém 17 recursos WAV e uma BGM XGM. `src/player.c:1092` despacha PCM em canais separados para P1/P2, e o mesmo ramo atende Ryo, Ken e Musgo. A BGM de luta observada no código é `bgm_ken_stage`, enquanto metadados de palco declaram nomes diferentes. Metadata musical não prova trilha distinta tocando.

**Desenvolver:** lista de falas/sons por personagem; announcer para seleção, round, início, KO e resultado quando aprovado; sons de interface; identidade de golpes; temas/variações de palco; prioridades de interrupção; limite de simultaneidade e regra de repetição. Reutilização temporária de sons não deve virar identidade final por acidente.

Não há base para trocar o driver apenas para alcançar as fotos, que não contêm áudio. Primeiro medir e ouvir o caminho atual sob duas vozes, impacto, música e uploads. Se o driver não satisfizer o contrato, comparar alternativas com uma cena representativa.

**Aceite:** escuta crítica e gravação sem cortes indevidos ou distorção; falas compreensíveis; impacto audível sem encobrir tudo; KO não interrompido por SFX trivial; PAL/NTSC tratados; escolhas de conteúdo com proveniência própria. Detecção de sinal não substitui audição.

### 5.12 Identidade geral: escolher a linguagem que será repetida

A captura do título combina mascote estilizado, nome da engine, fundo azul geométrico e menu com letra de outra família. A luta usa atlas e fontes que remetem a outras referências; Musgo tem outro tratamento. Mesmo que cada componente funcione, o conjunto ainda comunica coleção de demonstrações.

**Desenvolver:** uma direção de interface, paleta de acentos, família de fontes, molduras, contornos, escalas de texto e regras de animação. Diferenciar marca da engine e identidade do jogo quando houver um produto definido. Manter o nome HAMOOPIG como engine não exige que toda a apresentação do jogo use a mesma mascote.

Não iniciar uma campanha de branding maior antes de fechar HUD/combate. O retorno mais imediato está naquilo que o jogador vê durante toda a luta.

## 6. Proposta inicial de composição — hipótese de trabalho

Esta planta é uma proposta para storyboard e medição, **não um contrato de asset aprovado** nem a reprodução do layout de uma referência. Coordenadas em uma área de jogo 320×224; a apresentação 4:3 deve ser conferida separadamente do arquivo bruto.

| Região | Proposta inicial | Restrição a testar |
|---|---|---|
| Retrato P1/P2 | 24×24 em x=8 e x=288, y=8 | Legibilidade facial e paleta compartilhada sem efeitos indesejados |
| Vida | Faixas de até 104 px em x=36 e x=180, região y=8–24 | Reservar bordas internas; preenchimento fino e dano recente |
| Relógio | Centro x=144–175, y=8–31 | Dois dígitos, moldura e contraste sem colisão com barras |
| Nome/vitórias | Faixa abaixo das barras, até y=40 | Texto mais longo e dois ícones não se sobrepõem |
| Combo | Área lateral temporária abaixo do HUD | Posição por atacante; não cobre rosto ou trajetória crítica |
| Especial | Faixas candidatas de até 96×12 perto da base | Não cobrir pés nem percepção de distância; ajustar piso antes de fixar |
| Round/KO | Área central transitória | Persiste o mínimo legível, sem alterar física ou mensagens de resultado |

O piso atual é 219 no mundo: simplesmente colocar duas barras no rodapé pode cobrir a luta. A altura útil, âncora dos pés e câmera precisam ser storyboardadas em conjunto antes de aprovar a posição inferior. Não mover física silenciosamente para encaixar a arte.

## 7. Orçamento para alcançar o visual

Não fechar qualidade visual medindo cada item isolado. A cena crítica deve reunir os dois maiores frames de luta previstos, FX principal, retratos/HUD, ambiente animado e áudio.

- **VRAM:** separar tiles de cenário, fontes, retratos, letreiros, lutadores, FX, mapas e tabelas. Contar residência simultânea; o elenco inteiro não precisa estar carregado na luta.
- **DMA:** registrar pior quadro de upload e frames visuais adiados. Preload do ROUND/KO pode ser preferível a carregar seu atlas no mesmo momento de um golpe grande, conforme orçamento.
- **Sprites:** medir total, quantidade por scanline e largura de sprites por scanline. Retratos e letreiros também entram, não apenas os lutadores.
- **Paletas:** o arranjo atual PAL0 cenário, PAL1 HUD, PAL2/PAL3 lutadores exige decidir onde entram retratos e FX. Não reduzir os cenários a uma camada por existir apenas um slot reservado ao fundo; planos podem compartilhar paletas.
- **CPU e áudio:** medir durante colisão, eventos, animação e efeitos simultâneos. Bytes na fila não são tempo de CPU.
- **Região:** buscar estabilidade na frequência de vídeo de cada modo suportado, com ritmo de gameplay consistente; não declarar 60 quadros de vídeo por segundo em PAL de 50 Hz.
- **Ambição medida:** experimentar o degrau seguinte de detalhe/efeitos antes de fixar teto. 864 tiles é uma escolha atual de residência, não o teto geral da qualidade artística ou do hardware.

Não há evidência nesta comparação de que SVP, FMV, pseudo-3D ou um coprocessador sejam pré-requisitos. São projetos técnicos diferentes. O ganho visível solicitado depende primeiro de pixel art, composição, animação, feedback e integração.

## 8. Plano de desenvolvimento por entregas

### M0 — Fixar uma direção e a cena representativa

**Entregas:** escolher dois lutadores e um palco; quadro de referência por função; storyboard de seleção, início, golpe comum, golpe assinatura, KO e revanche; matriz de ações/poses; layout HUD; inventário de paleta/VRAM e custo do próximo degrau. Atualizar GDD/spec somente para as escolhas aceitas.

**Aceite:** composição explica onde cada informação vive e como personagens/FX cabem. Elenco novo, novos modos e novos palcos ficam fora do primeiro recorte. Owner: direção de arte + design + budget.

### M1 — HUD e fluxo de partida com acabamento

**Entregas:** vida com vazio e dano recente, especial distinto, retratos, nomes/ícones de vitória, dígitos, combo e letreiros ROUND/FIGHT/KO. Reaproveitar a lógica existente; separar apresentação e dados de combate.

**Aceite:** sequência vida cheia → dano pequeno → combo → zero → vitória → revanche legível dos dois lados, sem resíduos de VRAM/paleta e com captura vinculada à ROM. Owner: UI/pixel art + runtime + QA.

### M2 — Dois lutadores com ações visualmente completas

**Entregas:** substituir aliases incompatíveis; poses, tempos e pivôs próprios; identificar cada frame crítico; reação e FX por categoria de golpe; um golpe assinatura por lutador. Se Musgo entrar, sua tradução nativa precisa ser resolvida, não apenas ampliada.

**Aceite:** idle, deslocamento, salto, guarda, dano, throw, queda, vitória e derrota distinguíveis em movimento; hitboxes sincronizadas; frame atrasado não destrói leitura. Owner: animação + combate.

### M3 — Um palco com materiais, profundidade e movimento

**Entregas:** reautoria modular; distribuição de contraste; duas animações ambientais autoradas; estratégia de profundidade; contrato de ocupação BG_A/HUD; teste de câmera e extremos. Streaming entra se a arquitetura escolhida exigir, com prova de misses e seams.

**Aceite:** palco reconhecível em tamanho de jogo; lutadores dominam a leitura; câmera/ambiente se distinguem; tilemap e overlays não se destroem. Owner: arte de ambiente + VDP/câmera.

### M4 — Seleção e áudio integrados

**Entregas:** apresentação do elenco real, cursores/confirmados, preview, palco; identidade sonora dos dois lutadores, announcer escolhido e mix; transição título/seleção/luta/resultado.

**Aceite:** percurso com controle normal, sem comandos de debug; som revisado sob cena pesada; retorno/revanche corretos. Owner: front-end + áudio + estados.

### M5 — Fechar a fatia, depois expandir

**Entregas:** partida completa, guard/hit/throw/projétil/multihit aplicáveis, KO/time-over/draw, ciclos de reset; pior quadro medido com áudio; BlastEm e artefatos exigidos; revisão visual, gameplay e áudio independentes.

**Aceite:** nenhum estado prometido apenas em metadata, nenhuma ação crítica com arte provisória, nenhuma dimensão de budget omitida e nenhum claim sustentado só por probe curto. A partir desse padrão, expandir o roster usando o mesmo contrato. Owner: QA e revisores de cada disciplina.

M2 e M3 podem avançar depois de M0 em frentes separadas se o orçamento comum estiver fechado. M5 depende de todas as anteriores. Não foram estimadas semanas: o custo depende principalmente da quantidade de poses novas, reautoria do palco e disponibilidade de arte/áudio.

## 9. Testes de aceitação que faltam às fotos

| Teste | O que observar | Evidência |
|---|---|---|
| HUD sobre claro/escuro | Vida/especial/retrato/relógio legíveis nos extremos da câmera | Capturas do mesmo SHA e vídeo curto |
| Dano mínimo e combo | Granularidade, dano recente, número de hits e atribuição | Input reproduzível + eventos + vídeo |
| Poses dos dois lados | Guarda, throw, dano aéreo, queda e vitória sem aliases incoerentes | Sheet/manifesto + clipe runtime |
| Golpe assinatura simultâneo | Leitura, upload, scanline, áudio e recuperação | Pior quadro correlacionado e captura |
| Seleção espelhada | Mesmo personagem, cursores e paletas distintos | Percurso P1/P2 sem injeção de estado |
| Ambiente e câmera | Sem seams, piso estável, HUD preservado no BG_A | Percurso pelos extremos e saltos |
| Round completo | ROUND/FIGHT/KO/resultado e input no tempo certo | Vídeo com áudio e estado rastreado |
| Reset prolongado | Sem vazamento de sprites, aliases ou jobs | Contagem de recursos antes/depois |
| Qualidade sensorial | Impacto, ritmo, vozes, mix e coerência estética | Revisão humana/independente registrada |

Os 33 testes de host aprovados na curadoria anterior continuam sendo evidência de seus contratos, não substitutos dessas avaliações. Esta rodada executou o diagnóstico de arte, sem repetir a suíte de código inalterado.

## 10. Decisão recomendada

O HAMOOPIG já permite buscar essa qualidade sem reiniciar a engine. O passo decisivo é transformar sua demonstração técnica em uma fatia com direção consistente. A primeira comparação após implementação deve colocar lado a lado **seleção, abertura, um golpe, um combo e KO**, e não apenas mais uma screenshot de personagens parados.

O avanço será verificável quando os sistemas existentes passarem a comunicar com a clareza das referências e quando o movimento/áudio confirmarem a promessa da imagem. Este laudo registra um diagnóstico e um plano; não promove assets, não altera runtime e não certifica equivalência de qualidade.

## Arquivos desta rodada

- `reference_manifest.json`: oito imagens locais e hashes.
- `comparison_board.html`: prancha de inspeção com referências e capturas do projeto, sem edição dos pixels.
- `art_diagnostic_report.json` e `art_diagnostic.log`: auditoria técnica de recursos ativos/fontes.
- `evidence_manifest.json`: hashes do código, recursos, ROM e capturas usados nesta análise.
- `development_backlog.json`: ações, prioridades, dependências e critérios de aceitação.

## 10. Addendum de confronto — 19 de setembro de 2026

Uma nova fatia foi executada e confrontada em 320×224 contra as funções visuais
das referências R01–R08. O resultado não é um claim AAA: é a atualização
observada do diagnóstico, vinculada à ROM
`723ba8c2b69555965800f5e09dccc5fa9d5f90ff7194d3d5d0c9a2a1c7498454`.

- O HUD agora apresenta retratos autorais, nomes, vitórias, relógio, vida com
  trilho, especial visualmente distinto e combo. `zero_1_result.png` mostra a
  hierarquia do KO com letreiro próprio e vencedor ainda legível.
- A seleção deixou de ser apenas painel técnico: cards P1/P2, preview grande,
  retratos, identidade, palco e confirmação dupla foram vistos no BlastEm.
- O BGB2 foi reautorado a partir de uma nova fonte original persistida; água,
  cais, vegetação, torre/lanterna e faixa de luta têm massas materiais mais
  legíveis. A tradução está medida, mas continua `compare_flat` em BG_B; não há
  evidência de parallax independente.
- A rota semântica mostrou o golpe assinatura de Ryo, projétil autoral, impacto
  e redução de vida. O KO/FX foi confrontado em imagem real, não inferido do
  código.
- Título, seleção, luta, resultado, revanche e retorno foram vinculados ao
  mesmo SHA em sessões BlastEm; a matriz P10 renovou 36/36 casos e passou a
  integridade de identidade.

O trabalho ainda não fecha todos os itens do diagnóstico. Permanecem como
trabalho obrigatório antes de promoção: aliases/cobertura completa de poses,
parallax multi-plano real ou justificativa visual final, pior quadro combinado
com áudio, CPU/jitter sustentados, escuta crítica, residência completa de tiles
carregados por C, higiene/proveniência pendente e revisão independente de
qualidade. Portanto o status correto continua `prototype_partial`, com
`growth_decision=revise_before_growth` e `ready_for_aaa=false`.

## 11. Addendum de terminais e confronto no SHA novo — 19 de setembro de 2026

Para atacar os aliases críticos, Ken recebeu uma vitória e uma derrota autorais.
As fontes e conversão estão em `data/source_art/ken/`; os sprites de pipeline
estão em `res/sprite/ken/victory_v1.png` e `res/sprite/ken/defeat_v1.png`.
O runtime liga 611/612 à vitória e 570/615 à derrota; Musgo também usa sua
derrota autoral em 615.

O build resultante tem SHA
`8ac1bda70511fbd395af9a3fa3f49ca356e39dec31254b8f336f96a0a405e506`. A prova
observada no BlastEm está em
`out/emulator_evidence/visual_ko_20260919T232926387580Z-3579731/zero_1_result.png`:
Ken aparece vencedor com punho levantado, KO ampliado, HUD e palco BGB2 na mesma
ROM. A captura inversa foi encerrada sem claim após não produzir dano.

Esta etapa reduz uma lacuna, mas não promove o projeto: P10, semântica, áudio e
bundle canônico anteriores estão stale em relação ao SHA novo; a entrega P2 por
teclado também precisa de correção/recaptura dedicada. O status correto permanece
`prototype_partial`, `revise_before_growth` e `ready_for_aaa=false`.

## 12. Renovação P10 e limite da recaptura semântica

A ROM
`8ac1bda70511fbd395af9a3fa3f49ca356e39dec31254b8f336f96a0a405e506` foi
confrontada novamente pela matriz P10. O resultado foi `36/36
pending_visual_review`, `0 failed`, com máximos de 48 sprites VDP, 12 sprites
por scanline e 8176 bytes DMA enfileirados; isso comprova execução e vínculo de
bundles, não aprovação estética automática. A recaptura semântica em
`out/emulator_evidence/visual_ko_20260920T001624972891Z-3780703/` não gerou
SRAM/HSEM e os quadros finais ficaram com overlay de pausa/debug, portanto
especial, guard e throw continuam sem evidência semântica/visual válida. O
diagnóstico permanece `prototype_partial_current_sha` e
`revise_before_growth`.

Uma segunda recaptura corrigiu o fallback do harness para START exclusivo do P2 e removeu o overlay de pausa/debug: `out/emulator_evidence/visual_ko_20260920T002156365973Z-3833796/`. Ainda assim, ela não gerou SRAM/HSEM nem um quadro inequívoco do projétil; a lacuna de especial/guard/throw continua aberta.

As telas de título, opções e retorno foram recapturadas no SHA atual em `out/emulator_evidence/title_return_20260920T002445Z/`; a rota está registrada, mas a qualidade final de todas as telas ainda requer revisão independente.

A seleção P2 foi recapturada com Ryo/P1 e Ken/P2 em `out/emulator_evidence/visual_ko_20260920T002637710025Z-3870542/selected_final.png`; o cursor por teclado agora aparece no personagem solicitado. A lacuna específica foi reduzida, mas confirmação dupla, mirror-match e revisão tipográfica continuam abertas.

## 13. Prova visual do golpe assinatura — 20 de setembro de 2026

A rota isolada de especial foi repetida no BlastEm com teclado real, sem injeção
de SRAM ou estado de combate, usando a ROM SHA
`8ac1bda70511fbd395af9a3fa3f49ca356e39dec31254b8f336f96a0a405e506`. O bundle
é `out/emulator_evidence/visual_ko_20260920T033026169476Z-462317/`.

O quadro `special_only_p1_try0_4.png` mostra Ryo emitindo um projétil laranja
autoral contra Musgo, com leitura simultânea de palco, retratos, barras de vida,
barra de especial e relógio. O HSEM do mesmo bundle mede 204 frames de projétil
para P1; o HPRB mede 3 eventos de projétil e 3 hits, com pico de 7424 B DMA,
48 sprites VDP e 12 sprites por scanline, todos dentro dos limites nominais.

Isso fecha apenas o subitem especial/projétil da resposta de impacto. A mesma
captura mede `guard_frames_p1=0`, `guard_frames_p2=0`, `throw_frames_p1=0`,
`throw_frames_p2=0`, `combat_total_guards=0` e `combat_total_throws=0`.
Portanto guarda, agarrão, hitstop, cobertura de golpes, áudio e revisão sensorial
de todas as telas continuam obrigatórios. O status não muda: `prototype_partial_current_sha`,
`growth_decision=revise_before_growth`, `ready_for_aaa=false`.

## 17. Fatia visual recapturada após HUD/seleção — 20 de setembro de 2026

A ROM final desta etapa é `7431b4eed0b5d03039fa8dcb395509d562ae3e79f6308f59a2a2955ec6e3a08d`.
Na seleção, `out/emulator_evidence/visual_ko_20260920T051451465479Z-902783/selected_final.png`
mostra BGB2 autoral como fundo, cards P1/P2, retratos/silhuetas, VS, estágio e comandos legíveis.

No combate, o trilho de vida passou a ser uma unidade de três tiles autorais em BG_A,
com pontas espelhadas no P2. O HPRB final mede `7424/7782 B` DMA, `48` sprites VDP
e `12/20` sprites por scanline. O especial aparece em
`out/emulator_evidence/visual_ko_20260920T051517794165Z-904309/special_only_p1_try0_2.png`;
HSEM mede 203 frames de projétil P1 e HPRB mede 3 projéteis/3 hits. A guarda aparece em
`out/emulator_evidence/visual_ko_20260920T052509378538Z-947249/guard_only_04.png`,
com 1 guard e 0 hits no HPRB.

Título e opções foram recapturados no SHA final em
`out/emulator_evidence/title_return_20260920T053318Z/`; `options_scene_page.png`
mostra `OPTIONS 3` e seus controles. KO, revanche, throw, áudio, P10 e revisão
independente continuam sem fechamento no SHA final. O throw também foi validado em
`out/emulator_evidence/visual_ko_20260920T054131172698Z-1018183/throw_only_contact_4.png`
com `2 HITS` e HPRB 2 throws/2 hits. O bundle KO
`out/emulator_evidence/visual_ko_20260920T053546652798Z-1001707/` mostra `KO`
autoral em `zero_1_settle.png` e `PLAYER 1 WINS` em `after_combat.png`; HPRB
mede 2 KO/41 hits, 7424 B DMA, 66 sprites VDP e 12 sprites/scanline. O status
permanece `prototype_partial_current_sha`, `growth_decision=revise_before_growth` e
`ready_for_aaa=false`.

## 24. Contraste de Musgo recapturado no SHA 3c82c14b

O conversor `data/source_art/musgo/convert_musgo.py` passou a usar uma rampa
de gameplay verde/oliva com highlights separados, mantendo o snap compatível
com o Mega Drive. A silhueta de Musgo agora separa melhor de água, raízes e
doca na seleção e na luta.

O build canônico gerou a ROM
`3c82c14b3c959098f09b57de7a387147b970eb42fabb1bf8af986c20e46938f9`.
As evidências são `out/emulator_evidence/visual_ko_20260921T023824721736Z-1156410/`
(seleção) e `out/emulator_evidence/visual_ko_20260921T023408630615Z-1134439/`
(combate/resultado/revanche). HCAD confirmou 6.060/6.060 commits totais e
5.049/5.049 na luta; a janela observou 58,8–61,1 FPS.

É correção de legibilidade, não fechamento de paridade: combo/impactos comuns,
hierarquia de SP/ROUND/FIGHT, grade completa de elenco, palco multi-plano,
escuta humana, performance sustentada e revisão independente continuam abertos.

### Sound Test same-ROM — d9334271

`out/emulator_evidence/sound_test_20260921T021855Z/` confirmou a rota real
`TITLE -> OPTIONS -> SOUND TEST -> PLAY -> loop -> STOP` na mesma ROM. O WAV
isolado tem 48 kHz estéreo, 18,15 s, pico PCM 3865, RMS -25,68 dBFS e zero
clipping; `audio_signal_report.json` classifica apenas
`signal_and_route_present`. A escuta humana de timbre, emenda do loop,
balanço e mascaramento com SFX continua deliberadamente pendente.

## 22. Faixa de elenco e recaptura do SHA d9334271

Para atacar diretamente o gap de seleção, a tela passou a carregar uma faixa
real de elenco com três retratos derivados de fontes autorais persistidas:
`data/source_art/select/roster_icons_v01.png` e
`res/sprite/select/roster_icons.png`. Cada identidade ocupa um frame 24x24 com
moldura própria e PAL0 compartilhada; o recurso foi aceito pelo ResComp como
três frames/27 tiles, e a captura BlastEm é
`out/emulator_evidence/visual_ko_20260921T020818911985Z-993126/00_select.png`.

A recaptura integral da mesma ROM é
`out/emulator_evidence/visual_ko_20260921T020916512873Z-996433/`. Ela observou
59,7–61,1 FPS, dois KOs, resultado e revanche. O SRAM HCAD foi decodificado em
`hcad_cadence_report.json`: 7.980 frames de vídeo, 7.980 ticks lógicos e
7.980 commits de apresentação; na luta, 7.071/7.071/7.071, com os dois
invariantes verdadeiros.

O avanço melhora a leitura da seleção, mas não equivale à prancha de referência:
o elenco ainda tem três identidades, não uma grade completa; HUD, palco,
FX/KO e tipografia continuam abaixo do alvo; escuta humana, barra viva,
performance sustentada e revisão independente seguem abertas. Status honesto:
`prototype_partial_current_sha`, `growth_decision=revise_before_growth`,
`ready_for_aaa=false`.

## 23. Probes visuais adicionais no SHA d9334271

- Especial/projétil: `out/emulator_evidence/visual_ko_20260921T022432657376Z-1075427/`;
  `special_only_p1_try1_12.png` mostra o projétil autoral em contato.
- Agarrão: `out/emulator_evidence/visual_ko_20260921T022629512075Z-1087290/`;
  o roteiro real foi executado, mas o bundle declara apenas probe visual.
- Guarda: `out/emulator_evidence/visual_ko_20260921T022712721078Z-1091012/`;
  `guard_only_06.png` mostra a defesa em cena, também sem claim automático de
  aprovação. Os manifests preservam explicitamente essa limitação.

## 16. Recaptura same-ROM após câmera de impacto — 20 de setembro de 2026

A ROM vigente foi reconstruída com câmera de impacto determinística, limitada a
eventos de combate aceitos e sem mover HUD ou alterar física. O SHA atual é
`640c3223ec5b674af237e7ed31895540c5b7e7e5e6d4acce2376345b5f06cf90`.

O especial foi recapturado em
`out/emulator_evidence/visual_ko_20260920T041415021491Z-688336/`; o frame
`special_only_p1_try0_2.png` mostra o projétil laranja autoral de Ryo em voo,
com HUD, retratos, palco e Musgo legíveis. HSEM mede 117 frames de projétil e
HPRB mede 2 projéteis no mesmo SHA.

O agarrão foi recapturado em
`out/emulator_evidence/visual_ko_20260920T041830157874Z-704017/`; o frame
`throw_only_contact_4.png` mostra Musgo suspenso, Ryo em recuperação, impacto
de contato e `2 HITS`. HSEM mede 68 frames de throw P1; HPRB mede 2 throws e
2 hits, com `7424 B` DMA, 48 sprites VDP e 12 sprites por scanline.

A guarda continua válida na sessão
`out/emulator_evidence/visual_ko_20260920T040520275634Z-656638/`; o quadro
`guard_only_05.png` mostra o impacto com sparks sem redução de vida. O código de
evento solicita tremor apenas para hit, guarda e throw aceitos. Isso é avanço
de resposta, não fechamento da fatia: telas completas, hitstop perceptível,
áudio, aliases/poses, pior quadro e revisão independente continuam abertos.
Capturas anteriores de título, seleção, KO, áudio e P10 devem ser recapturadas
na ROM `640c3223` antes de qualquer closeout único.

O status permanece `prototype_partial_current_sha`, com
`growth_decision=revise_before_growth` e `ready_for_aaa=false`.

## 14. Prova visual do agarrão — 20 de setembro de 2026

A rota `--throw-only` foi corrigida para impedir o fallback de START que abria o
painel de debug e repetida com teclado real no BlastEm. O bundle válido é
`out/emulator_evidence/visual_ko_20260920T034410560385Z-533030/`, ainda no SHA
`8ac1bda70511fbd395af9a3fa3f49ca356e39dec31254b8f336f96a0a405e506`.

O quadro `throw_only_contact_4.png` mostra o contato do agarrão: Musgo está
suspenso, Ryo está na recuperação e o letreiro `2 HITS` permanece legível sobre
o BGB2 e o HUD. HSEM mede 68 frames de throw P1 e HPRB mede 2 eventos de throw,
2 hits, 7424 B DMA, 48 sprites VDP e 12 sprites por scanline.

O bundle anterior dessa rota, com `PAUSE/DEBUG`, foi descartado e não sustenta
qualquer claim. Guarda ainda não foi exercitada com sucesso: a prova atual mede
zero frames/eventos de guarda. Permanecem também hitstop, cobertura integral de
golpes/poses, áudio, pior quadro combinado e revisão sensorial de todas as telas.

## 15. Prova visual de guarda — 20 de setembro de 2026

A rota dedicada foi ajustada para lançar o projétil antes de P2 pressionar o
recuo; assim o defensor não abandona a distância natural antes do contato. O
bundle válido é `out/emulator_evidence/visual_ko_20260920T035134604414Z-571565/`,
no mesmo SHA da ROM.

O frame `guard_only_06.png` mostra o contato com sparks no defensor e sem
redução visual de vida. HSEM mede 76 frames de guarda P2 e 36 frames de
projétil P1; HPRB mede 1 evento de guarda, 1 projétil e 0 hits, com 7424 B DMA,
61 sprites VDP no pico do probe e 12 sprites por scanline.

Com isso, a resposta de impacto tem provas same-ROM para especial/projétil,
guarda e agarrão. Isso não encerra a fatia: hitstop, cobertura integral de
golpes/poses, áudio, pior quadro combinado e revisão sensorial de todas as telas
continuam abertos. O status permanece `prototype_partial_current_sha`,
`growth_decision=revise_before_growth`, `ready_for_aaa=false`.

## 17. Delta confrontado com as referências — SHA 8e7a34dc

Esta atualização não trata intenção como entrega. A ROM foi recompilada pelo
wrapper canônico e confrontada em BlastEm nas capturas same-ROM:

- seleção: `out/emulator_evidence/visual_ko_20260920T224941749302Z-331917/`;
- seleção + combate BGB2: `out/emulator_evidence/visual_ko_20260920T230426778949Z-380612/`;
- Sound Test e áudio isolado: `out/emulator_evidence/sound_test_20260920T231117Z/`.

O delta visual efetivamente integrado é:

1. seleção com superfície autoral traduzida, VS central e molduras laterais,
   usando 204 tiles na faixa 655..858, separada da reserva de sprites;
2. BGB2 com reuso regional preservador de material, 857 tiles contra orçamento
   medido de 864, eliminando os maiores mosaicos retangulares observados no
   diagnóstico original;
3. HUD de combate com chassis azul/dourado, retratos, nomes, relógio e especial
   em `WINDOW` full-screen, sem escrever transientes no BG_A;
4. `Forge Crystal` autoral no Sound Test e na luta, com rota PLAY/loop/STOP
   observada, sinal estéreo 48 kHz e zero clipping no relatório objetivo.

O frame de combate registra 60,2 fps e mostra os nomes, `SP`, life bars e palco
sem corrupção estrutural. Ainda não é paridade final com as referências: combo
dominante, KO/letreiro em sequência completa, todas as poses/FX, partida,
revanche, escuta humana e revisão independente continuam gates abertos. O
status correto é `prototype_partial_current_sha`; `ready_for_aaa=false`.

### Fechamento da tentativa de partida longa no mesmo SHA

A rota longa foi executada com teclado real em
`out/emulator_evidence/visual_ko_20260920T232720289830Z-454619/` (Ryo/P1
contra Musgo/P2) e manteve 59,9–61,1 fps. Ela observou reset de round quando a
vida caiu de 1060 para 164 pixels, mas o harness perdeu contato após o reset;
`terminal_probe` e `terminal_capture` ficaram nulos. O bundle não sustenta claim
de KO/resultado. A variante espelho Musgo/Musgo, em
`out/emulator_evidence/visual_ko_20260920T232009718656Z-433578/`, também mostrou
resets e revanche visual, mas sem estado terminal inequívoco. Essas sessões são
diagnóstico de estabilidade e não substituem a prova dedicada de KO.

## 18. Prova same-ROM de KO, resultado e revanche — SHA 5a99b076

A ROM vigente é `5a99b076be3ae96a382a07676e62b3b8f16d8de59b109a3fd8a886c8dd7d0d1f`.
O bundle BlastEm é
`out/emulator_evidence/visual_ko_20260920T235500737537Z-543800/` e contém:

- `ko_result_round_1.png` e `ko_result_round_2.png`: o atlas autoral mostra
  `KO`, o combo `RUSH 21 HITS`, os retratos, HUD e BGB2 sem os mosaicos falsos;
- `after_match_result.png`: `PLAYER 1 WINS` após duas vitórias;
- `rematch_round.png`: entrada A retorna à luta e mostra `ROUND 1` com saúde
  restaurada;
- `hprb_probe_report.json`: 3.750 frames, `combat_total_ko=2`, DMA máximo
  `7424/7782 B`, `50/80` links VDP e `13/20` sprites por scanline;
- `hsem_probe_report.json`: amostras de distância/ataque e estados finais do
  mesmo ROM. O HPRB é a contraprova pós-sessão; SRAM não foi usada como canal de
  controle ao vivo.

O Sound Test foi recapturado no mesmo SHA em
`out/emulator_evidence/sound_test_20260920T235813Z/`: `Forge Crystal`, PLAY,
loop e STOP observados; WAV estéreo 48 kHz, 17,05 s, sinal presente e zero
clipping. A escuta humana de timbre, loop, balanço e mascaramento continua
pendente, então isso prova integridade de sinal/rota, não “som cristalino” como
juízo subjetivo.

O avanço fecha a prova de partida/revanche e a integridade objetiva de áudio,
mas não promove paridade visual final: a barra viva ainda não tem laudo passado,
a revisão independente art/gameplay/audio está apenas planejada, a validação
geral permanece stale/não limpa e a reautoria multi-plano do palco ainda é
inferior à prancha de referência. Status: `prototype_partial_current_sha`,
`growth_decision=revise_before_growth`, `ready_for_aaa=false`.

## 19. Recaptura musical e combate com Forge Crystal v2 — SHA 24262999

A ROM vigente passou a ser
`24262999f2390f14fe131ba3508e70ea348db024bd30cae43edc44082faad958` após a
reautoria reproduzível de `Forge Crystal`. O compositor versionado
`data/source_audio/build_forge_crystal_v2.py` substitui o pipeline fantasma
`psg_score.py` e gera oito compassos/768 frames NTSC com quatro funções PSG:
lead, baixo, contraponto cristalino e percussão de ruído.

O Sound Test foi recapturado em `out/emulator_evidence/sound_test_20260921T002424Z/`.
A tela confirmou `SOUND TEST / FORGE CRYSTAL`, a rota PLAY/loop/STOP foi real e o
WAV isolado passou a ter 3290 valores PCM distintos, 48 kHz estéreo, 17,05 s,
pico 3865, RMS -25,67 dBFS e zero clipping. A luta foi recapturada em
`out/emulator_evidence/visual_ko_20260921T002700587260Z-640941/` com 88,25 s de
vídeo/áudio, dois KOs, 42 hits e a mesma faixa tocando no contexto de SFX.

O envelope VDP do combate continua `cabe`: 7424/7782 B DMA, 48/80 links VDP e
13/20 sprites por scanline. O VLAB, porém, mede pico de CPU 152%, jitter 10 e
pico de inicialização 1645%; performance sustentada/60 fps permanece bloqueada.
Também não há aprovação auditiva humana, revisão independente atual ou barra
viva passada. Status honesto: `prototype_partial_current_sha`,
`growth_decision=revise_before_growth`, `ready_for_aaa=false`.

## 20. Eventos de combate e match same-ROM após correção causal — SHA b6f7cd64

Após a correção dos estados de throw e do harness, a ROM vigente é
`b6f7cd649f829c21555883014721992b04261f0c32b34a620538d0548be7cc88`.
O alcance de contato foi ajustado de 60–65 px para 105 px na hitbox autoral,
porque a separação física deixa os lutadores em 100 px; o comando continua
limitado a `throwDistance <= 100`.

Provas same-ROM isoladas, todas com HPRB/HSEM e decisão VDP `cabe`:

- throw: `visual_ko_20260921T004209197732Z-684636/`, 2 throws e 64 frames de
  estado de throw;
- special/projectile: `visual_ko_20260921T005155291248Z-716150/`, 3 projectiles
  e 204 frames de fireball, com FX visível no contact sheet;
- guard: `visual_ko_20260921T005412979207Z-723566/`, 1 guard e 77 frames de
  defesa, sem dano confirmado.

O match completo renovado em
`visual_ko_20260921T005523892270Z-727484/` registrou 2 KOs, 42 hits, resultado
e rematch real, com 87,6 s de áudio isolado. O Sound Test renovado em
`sound_test_20260921T005842Z/` confirmou PLAY/loop/STOP na mesma ROM.

Isso fecha cobertura funcional de evento, mas não fecha qualidade comparável à
prancha: o VLAB ainda marca performance sustentada como não provada, a escuta
humana e a revisão independente continuam pendentes, a barra viva não tem
laudo passado e HUD/seleção/KO/palco ainda estão abaixo da referência em
hierarquia visual. Claim permanece `prototype_partial_current_sha`.

## 21. Instrumentação de cadência e recaptura same-ROM — SHA edc9a23f

O build canônico após a instrumentação de runtime gerou a ROM
`edc9a23ff103bc1a7db6182f6f13d95567a464428eb7bdafc2db624ad53df427`.
O ledger HCAD foi capturado no BlastEm em
`out/emulator_evidence/visual_ko_20260921T012445543185Z-809087/hcad_cadence_report.json`.

Na janela NTSC de 7.260 frames, a ROM registrou 7.260 commits de apresentação,
7.260 ticks lógicos, zero frames sem lógica, 7.260 frames de um tick e zero
frames de dois ticks. Na subjanela de luta foram 6.353 frames, 6.353 ticks e
6.353 commits. Os invariantes do decoder passaram. Isso remove a hipótese de
um frame de apresentação perdido nessa rota normal; não prova ainda a rota PAL,
free-step ou o desempenho sustentado da cena com áudio.

O mesmo bundle confrontado visualmente mantém o diagnóstico anterior: a seleção
continua abaixo da prancha por apresentar dois cards em vez de um roster completo,
o HUD continua compacto, e BGB2 ainda é uma composição compare-flat sem um
segundo plano independente. O HCAD é avanço técnico real e não altera o claim:
`prototype_partial_current_sha`, `growth_decision=revise_before_growth`,
`ready_for_aaa=false`.
