# Suzaku Castle: medicao, rota e gates de producao

Estado em 2026-09-25: **pre-producao medida; asset e runtime pendentes**. Este
documento nao aprova o cenario, o audio ou a ROM. A fonte privada permanece em
`rascunho/entrada_bruta/ssf2_01_ryu.zip` (SHA-256
`d781b8d53d8b35789ed18985b7ad7ab9db977d220d9940b132999ed92323fb96`).
Nao redistribuir os pixels derivados sem decisao de proveniencia/licenca.

## Planta e comportamento da fonte

- MUGEN `localcoord=320,240`; alvo Mega Drive H40=320x224. O recorte vertical
  provisorio e de 16 px. Confirmar linha dos pes e areas do HUD no storyboard
  antes de fixar o recorte.
- Camera MUGEN: `boundleft=-224`, `boundright=224`, curso de 448 px.
- Fundo: ceu/nuvens, castelo e muro; frente: telhados ornamentais e piso.
  Os deltas reais por camada sao 0, .470982, .537946, .671875, .792410 e
  1.102678; ceu tem velocidade horizontal -.25. A fonte tambem declara uma
  camada animada `BG 5`, ainda nao portada. O composite de medicao usa apenas
  dois deltas aproximados (.43/.67); ele **nao** implementa o parallax original.
- O benchmark visual para o primeiro quadro e o centro do castelo, com
  telhado/floor em primeiro plano. A camera deve ser testada nos dois cantos,
  inversao de lado, saltos, push e super; o HUD permanece estavel.

### Storyboard numerico inicial (a confirmar na ROM)

| Elemento | Coordenada/intervalo em pixels | Responsabilidade |
| --- | --- | --- |
| viewport H40 | x=0..319, y=0..223 | 4:3, sem escala 5/6 |
| WINDOW HUD | y=0..55 | nao acompanha camera nem shake |
| area de combate | y=56..207 | personagem, projeteis, telhados e muralha |
| barra de power | y=208..223 | HUD em BG_A cobre o palco |
| linha dos pes runtime | y=200 | confirmar contato com o piso na arte final |
| mundo alvo Suzaku | x=0..767 | 320 + curso de camera 448 |
| camera inicial | x=224 | centro da fonte, castelo como ancora |
| Ken inicial P1/P2 | x=314/454 | 70 px a cada lado do centro do mundo |
| camera limite | x=0..448 | evitar amostra fora da arte nos cantos |

O runtime atual ainda declara mundo de 640 px, camera inicial 160 e clamp
de 4 px/quadro. Logo a tabela acima e contrato de implementacao proposto,
nao comportamento ja observado. Um mundo de 768 muda espaco de luta e
distancia para comandos; exigir replay de push/corners antes de prometer
paridade. A passagem de seis deltas MUGEN para dois planos VDP precisa de
decisao artistica por faixas, por exemplo ceu/castelo/muro em BG_B e
telhado/piso em BG_A com scroll por linha apenas se a tabela e o DMA couberem.
Nao somar os deltas como se fossem camadas hardware independentes.

## Medicao reproduzivel e resultado

O comando `mugen2sgdk_forge stage-candidate` verifica o hash da fonte por
relatorio, preserva sete palavras da PAL0 do HUD, escolhe oito palavras para
o palco e gera vistas indexadas 4bpp em
`rascunho/processado/stage_takeover/v1/`. `candidate_report.json` guarda
paleta, larguras, camadas, SHA dos PNGs, custo por vista e camera. O relatorio
deve ser lido antes de qualquer copia para `res/`.

| Recurso | Medido | Limite/implicacao |
| --- | ---: | --- |
| BG_B composto | 520 px; 689 tiles com H/V flip | cobre todo o curso .43 |
| BG_A composto | 624 px; 679 tiles com H/V flip | cobre todo o curso .67 |
| Uniao da arte dos dois planos | 1.366 tiles | 920 acima da regiao de 446 |
| Uniao simultaneamente visivel, camera 0..448 | 697..845 tiles | ainda acima de 446 |
| Pixels visiveis recoloridos | 55,7% atras; 69,0% frente | paleta e candidata tecnica, nao aprovada visualmente |
| VRAM com sprite pool 600 | 174 tiles livres; 446 com emprestimo bgfx | `fight_vram` da ROM principal `20034654...` |

Como controle, uma vista central achatada 320x224 foi compilada com
ResComp 3.95 (`IMAGE ... BEST`) dentro de `rascunho/`: **719 tiles reais**
(23.008 bytes descompactados), tilemap 2.240 bytes, dados comprimidos do
tileset 7.291 bytes. O controle continua 273 tiles acima da capacidade atual
de 446, elimina o parallax e nao foi vinculado ao jogo. Em 64x32, mesmo se
houvesse espaco agregado, o cenario precisaria de particionamento porque
as reservas de bgfx e a area livre ficam separadas pelos recursos do HUD.

Contagem de tiles usa equivalencia exata e H/V flip; ela **nao** equivale ao
ResComp nem ao custo de DMA. O empréstimo dos 272 tiles de bgfx exige ocultar o
palco durante o super, restaurar ambos planos e a PAL0 no fim, e provar que a
restauracao cabe no VBlank sem pausa perceptivel. Reduzir o sprite pool a 384
daria 662 tiles com empréstimo, mas essa configuracao nao foi aprovada: efeitos
e super precisam provar o pico real de VRAM e scanline. `CramConsumer` disciplina
escritas e restauracao da paleta; nao aumenta a CRAM nem a VRAM.

O mapa BG_A de 624 px tambem excede a largura de 512 px de um plano 64x32.
Mudar para 128 colunas altera a ocupacao das tabelas de plano e invalida o
orcamento atual; essa rota precisa de nova medicao da configuracao VDP. Um
streamer em 64x32 precisaria atualizar colunas e os seus tiles em movimentos
de camera, com contrato de DMA e controle de residencia. Alem disso, o super
atual desenha BG_B enquanto BG_A fica por cima: esconder/restaurar apenas
BG_B deixaria telhado e piso do palco sobre o efeito. Os dois planos precisam
de uma transicao explicita e de teste visual.

A primeira tentativa mediu uma largura fixa de 512 px e subcontou a borda
direita (1.236 tiles). O conversor foi corrigido para derivar largura de
`320 + camera_span*delta` por plano; a prova atual e 1.366. Teste de regressao
fixa 520/624 px. Reducao automatica agressiva para 452 tiles foi inspecionada
em 1x e perdeu material de telhado/piso; ficou em `rascunho` como experimento
rejeitado. A composicao central mostra a direcao, nao um asset final.

Um experimento posterior reutilizou diretamente um modulo de piso de 32 px
da fonte e reduziu a vista central achatada de 719 para 531 tiles; retirar a
continuidade do telhado fora da esquerda baixou para 519. A imagem 1x
`modular_reveal.png` ficou visivelmente repetitiva no piso e perdeu parte da
profundidade, alem de ainda exceder 446. Rejeitada como cenario final. O
resultado demonstra que repetir um crop autoral pode baixar VRAM, mas a
aceitacao depende de redesenho de textura/ritmo e da cena viva.

## Sonda de residencia do sprite pool (2026-09-25)

A ROM test-only `37fd9eb8...44ac11` foi executada no BlastEm com dois Ken em
potencia maxima, P2 AI ativo e pool `SPR_initEx=600`; nenhum cenario foi
carregado. Telemetria SRAM registrou 2.941 amostras, minimo de 247 tiles
livres, maior bloco livre contiguo de 72 tiles, pico de 11 sprites ativos e
zero falhas de alocacao. Relatorio hash-bound:
`doc/mugen/vram_residency_probe_2026_09_25.json`.

Esse ensaio prova que contar apenas tiles livres mascara fragmentacao: 247
livres nao equivalem a um bloco de 247. Nao autoriza reduzir o pool para
acomodar arte, porque o teste nao carregou stage, tinha audio dummy e nao
incluiu toda a carga de gameplay/audio. O titulo do BlastEm mostrou 59,9 fps
num snapshot; 116/1200 quadros medidos excederam o budget e a alegacao de
cadencia sustentada permanece sem prova. A proxima comparacao precisa usar
capturas pareadas com o mesmo estado, mesma instrumentacao e audio habilitado,
incluindo cenario e a maior combinacao de FX.

O registro de arquitetura `doc/mugen/stage_architecture_record_2026_09_25.json`
mantem as tres familias em aberto. Dois planos residentes continuam acima do
budget estimado; streaming ainda nao tem contrato DMA nem implementacao; a
vista flat de 719 tiles excede a capacidade e a variacao de piso de 32 px
continua rejeitada. A proxima arte de staging deve preservar mais variacao
autoral do piso e melhorar a traducao de paleta antes de se medir novamente.
Nenhuma rota, paleta ou asset foi promovido.

## Rota de implementacao

1. Fixar storyboard em pixels: horizonte, pes, faixa WINDOW/HUD, castelo,
   bordas e evento ambiental. Confrontar com screenshots de fonte e com 320x224
   no tamanho real; registrar as escolhas de paleta por material.
2. Extrair modulos autorais da fonte (nuvens, torre, muro repetivel, telhados,
   piso) e redesenhar/editar os detalhes que precisam repetir. O conversor
   apenas indexa, compoe e mede; nao fabrica arte final por primitivas nem
   esmaga a fonte por k-means. Preservar fontes e hashes no `rascunho/`.
3. Medir tres rotas em ROM de teste com a mesma cena pesada: (a) dois planos
   residentes com modulos repetidos; (b) duas janelas com streaming de tiles
   em fronteiras de camera e contrato de DMA; (c) single-plane `compare_flat`
   como controle tecnico. Para cada uma registrar tiles ResComp, pool de sprite
   efetivamente livre, DMA por transicao, pixels/sprites por scanline, perda
   visual 1x e estabilidade. Escolher pela prova, nao por premissa.
4. O plano escolhido deve suportar PAL0 compartilhada com o HUD durante o
   combate normal e emprestimo bgfx durante o super. Preservar `PAL0[0]` e
   confirmar que todos os consumidores de `PAL0[1..15]` restauram a cor exata.
   O HUD ainda usa PAL0[9..15] e o contrato alvo PAL3 permanece aberto.
5. Integrar ao `resources.res` somente assets com proveniencia e `pixel_contract`
   aprovados; compilar ROM; capturar BlastEm com caminhada canto-a-canto,
   super, round e retorno. Registrar video para parallax/costuras, audio e
   medicao de 1200 quadros da cena pesada no mesmo SHA. So entao mudar D1-D3
   para completo.

O pipeline atual reconhece apenas as sete camadas nomeadas desta fonte e exige
paleta SFF compartilhada. Outros stages MUGEN precisam de parser/compositor
genericamente validado, sem anunciar suporte universal a partir deste caso.

## Inventario das camadas animadas e rota de H-scroll por bandas

O medidor do conversor agora inclui animacoes de fundo, frames SFF/AIR,
duracoes, offsets, flips, tiles nao vazios por frame, ciclo e janelas BGCtrl.
Relatorio completo, derivado da fonte acima com `crop_top=16`:
`rascunho/processado/stage_takeover/suzaku_measure_v2.json` (SHA-256
`b357e7e252337c01b521cdc68981ac25489d15adae34e0dd15507e5d99012257`).

`BG 5`, `BG 5'` e `BG 5''` compartilham a acao 5: 51 frames, 278 ticks por
ciclo, pico de dois tiles nao vazios por frame e uniao de nove padroes de
tile. O BGCtrl ativa IDs 51, 53 e 52 respectivamente nos intervalos
900–1178, 1778–2056 e 3086–3364 do ciclo de 3364 ticks. Cada janela coincide
com um ciclo AIR e nenhuma das tres janelas se sobrepoe. A traducao pode
reutilizar um atlas comum de nove padroes, mas ainda precisa decidir como
animar a nametable, respeitar os offsets/axes SFF, preservar o tempo e provar
o evento em ROM. Nao tratar frames SFF de 1x1 como vazios: eles carregam cor
visivel; somente indice 0 e transparente.

O recorte provisório de 16 px tambem revelou uma correspondencia estrutural
exata para BG_A com H-scroll por linha: `BG 3` ocupa `[0,176)`, `BG 4a`
`[176,212)` e `BG 4b` `[212,224)`. Os deltas sao 0.671875, 0.792410 e
1.102678. SGDK 2.11 declara `VDP_setHorizontalScrollLine(BG_A, line, values,
len, tm)` e recomenda `DMA_QUEUE`; HSCROLL_LINE aplica um offset por linha.
Essa e uma rota de composicao a testar, nao implementacao pronta. Quando a
camera se mover, todos os offsets precisam acompanhar a posicao e a tabela
deve ter dono unico, fonte persistente e budget VBlank medido.

O H-scroll nao fecha a residencia. As fontes frontais somam 700 padroes nao
vazios, sem reuso entre as tres camadas. O grupo BG_B do compositor inclui
BG0a/BG0b/BG1/BG2: a soma por layer e 1.399, mas 378 padroes exatos se
reutilizam, resultando em 1.021; sem o fallback tiled BG0a, o grupo
BG0b/BG1/BG2 tem 959 sem reuso. BG0a e BG0b compartilham dimensao, origem e
delta e sao totalmente opacos; na ordem do compositor atual BG0b cobre BG0a
na area comum, mas essa ordem ainda precisa ser comparada com a fonte em jogo.
Estes numeros sao estimativa de padroes fonte com flip, nao custo ResComp,
mapa ou pico de tiles visiveis. A
camada de fundo ainda tem sobreposicoes de ceu/castelo/muro que nao podem
receber deltas independentes em linhas compartilhadas. Logo, antes do runtime,
medir uma vista H40 completa por janela de camera com as bandas reais,
documentar o compromisso de BG_B e provar paleta/tilemap; streaming sozinho
nao e resposta se a propria janela simultanea exceder o budget.

## Sonda de viewport H-scroll por scanline (2026-09-25)

O contrato local `suzaku_front_bands_contract_2026_09_25.json` alimenta o novo
comando `mugen2sgdk_forge stage-bands`. A ferramenta percorre todas as 449
posicoes inteiras de camera (0..448), aplica o `delta` nativo das tres faixas
frontais e converte o `xscale` do BG4a em deslocamento horizontal por linha.
O significado do `xscale` vem da referencia primaria Elecbyte resumida em
`rascunho/entrada_bruta/elecbyte_mugen_bgs_parallax_note_2026_09_25.md`
(SHA-256 `0d5aa5fdfa41b5a64dc74dd660c9d7324ceb89bbce5a8b72bfabd185bda2ae7b`).
O fator estimado do BG4a varia de 0.792410 na linha 176 a 1.091517833 na linha
211. A rasterizacao subpixel e a regra de arredondamento ainda nao foram
comparadas com MUGEN em execucao.

Relatorio hash-bound: `rascunho/processado/stage_takeover/
suzaku_front_banded_hscroll_v1.json`; vistas de estudo left/center/right em
`front_banded_viewports_2026_09_25/`. Para o plano frontal isolado, a tira
horizontal exige 816 px (102 tiles): nao cabe em 64 colunas/512 px, cabe em
128 colunas/1024 px. A area de nametable correspondente passa de 4 KiB para
8 KiB. No caso fonte por indices, a janela visivel varia de 299 a 460 padroes
8x8 unicos com flips; pico nas cameras 10 e 11. O pico de 460 ja supera em 14
tiles a regiao maxima de palco estimada em 446, antes de carregar BG_B.
Com a paleta candidata ainda nao aprovada do relatorio colorido (mesmo SHA de
fonte; relatorio SHA `293050292ad80d331e41161b7f55ba2af68aa74f697d0c3e5aeedbdc723d05db`),
o pico cai para 431, mas sobrariam apenas 15 tiles para BG_B e qualquer outra
reserva adicional; a
medida nao autoriza a paleta. A uniao de padroes vistos ao longo de todo o
curso continua 796 na fonte e 744 na paleta candidata, portanto a residencia
integral ainda nao cabe.

Usando o limite provisorio atual de 4 unidades de camera por frame, a diferenca
de conjuntos visiveis pede no maximo 9 padroes novos (288 bytes de dados de
tiles) por transicao na rota sem remapeamento. Isso e limite inferior ideal:
nao soma atualizacao de nametable, setup da fila, fragmentacao/pinning do cache,
H-scroll table nem competicao no VBlank. Requer medir a fila e a ROM antes de
qualquer claim de streaming.

### Correcao de semantica do VDP e leitura do compositor (2026-09-25)

A conclusao anterior sobre mascaras estava errada. No Mega Drive, o codigo de
cor 0 nos planos de scroll e transparente; a proxima camada de prioridade mais
baixa aparece. Portanto, os furos de `BG 3` (`mask=1`) podem revelar o plano
inferior. A base tecnica e o *Genesis Software Manual*, revisao 1992-02-20,
pagina 62; nota local hash-bound
`rascunho/entrada_bruta/sega_genesis_software_manual_transparency_note_2026_09_25.md`
(SHA-256 `47bcdf170f9554942c99cd2d9a789ba09482fde15d25039cad1f1d1b26580a51`).
A referencia de parallax Elecbyte continua sendo a nota local citada acima.

A sonda corrigida preserva essa semantica e percorre 449 posicoes inteiras. Nas
bandas frontais medidas, nao encontrou pixel de indice 0 sem mascara visivel em
nenhuma posicao amostrada. Isso nao elimina a regra geral: um pixel de indice 0
em layer MUGEN sem mascara, se visivel, precisa ser remapeado para cor MD nao
zero. O preview RGBA agora distingue explicitamente os vazios mascarados.

O problema de composicao que permanece e outro: a vista estatica completa tem
linhas que exigem mais de dois grupos independentes de velocidade horizontal
(72/32/72 linhas nas cameras left/center/right; maximo 4 grupos). A nova sonda
`stage-plane-tradeoffs` escolhe duas velocidades por scanline, minimizando erro
absoluto ponderado por pixels visiveis e agregando as tres cameras. O piso
matematico reposiciona 19.655 de 215.040 amostras de pixel (9,14%), com erro
medio de 0,04105 px por pixel/frame e pior caso 0,803572 px/frame na linha 62.
Medindo tambem o drift acumulado a partir da camera inicial 224, o erro medio
nos samples e 2,10254 px/pixel; o maior deslocamento estimado e 45 px no extremo
(camera 0, y=62, BG3: 0,671875 -> 0,470982). Portanto, a baixa media por frame
nao torna o compromisso seguro para o percurso completo. Isso e uma classificacao
de velocidades, nao uma solucao de tilemap: a selecao pode variar por scanline,
nao modela prioridade/ownership A/B e nao prova que a costura fique boa. O preview
candidato de source indices mudou 9.625 pixels em left, 0 no center e 6.356 em
right; nenhuma das imagens recebeu aprovacao visual.

Artefatos hash-bound: tradeoff report SHA-256
`84aecf7c49feb100decb0a34fc0972123b2848e92f9dab2918d8e4e7aa342f1f` e preview
report SHA-256 `09a09a959b0b5506816f27c3d6a30cbba9b08f3fc06e23f0cd3a2544f8368885`,
ambos derivados do source-view report
`e4a867f92e682ba81293d788f190163d7b8eeb73c4829ac9cea70f3db2bd4613`.

Conclusao: as tres velocidades das bandas frontais podem ser representadas por
H-scroll de linha porque ocupam faixas verticais disjuntas, mas isso nao fecha o
stage completo. A vista precisa de 816 px/102 colunas e nametable de 8 KiB; o
pico de 460 padroes fonte excede o budget total estimado de 446 antes de BG_B.
A paleta candidata baixa o pico para 431, mas altera cerca de 69% dos pixels e
continua sem aprovacao. A proxima decisao e revisao visual do tradeoff/perfil de
costura, seguida de precomposicao autoral; BG_B completo, budget de tiles,
ResComp, DMA/VBlank, camera runtime, arte aprovada e prova em ROM continuam
pendentes.

## Sweep completo de camera e comparacao de dois objetivos (2026-09-25)

`stage-source-view --sweep-camera-step 1` agora percorre as 449 posicoes
inteiras da camera e agrega visibilidade por velocidade/scanline sem manter os
rasters em memoria. O perfil cobre 32.184.320 amostras visiveis, do mesmo pacote
de fonte SHA `d781b8d5...23fb96`; os tres previews left/center/right continuam
hash-bound ao compositor estatico. Relatorio do sweep:
`rascunho/processado/stage_takeover/suzaku_static_source_view_sweep_v1.json`
(SHA-256 `bd8060753db6c987f876070e5b7e4594cad0a4f1f10f561b99ca588367e8524e`).

O sweep compara duas respostas matematicas, sem afirmar uma composicao VDP:

| Objetivo | Amostras remapeadas | Erro medio estimado/frame | Drift medio desde x=224 | Pior drift |
| --- | ---: | ---: | ---: | ---: |
| Preservar dois deltas-fonte com menor erro ponderado | 1.618.094 (5,03%) | 0,02415 px/amostra | 0,95527 px/amostra | 45,00003 px |
| Dois alvos continuos minimax por scanline | 4.611.304 (14,33%) | 0,04757 px/amostra | 1,48841 px/amostra | 22,50002 px |

Relatorios: perfil discreto SHA `7d8aec62d2d9480ae49072a3cd325070cb7c99b86a22cf47ce15b22648f0fbdd`;
perfil minimax SHA `2b45a186a2b4d2c6fc401b174cbc0e191d3a9b12528f80e220e7a38b96e0482e`;
preview minimax SHA `92d077cee650b62409b764fbb84642dfd237abbd7c53b807631f8f042c283c90`.
O minimax troca a maioria das velocidades por alvos intermediarios e exige
recomposicao/reatoria; seu pior caso e 22,5 px (BG1, y40, 0,470982 -> 0,5714285).
O perfil discreto desloca BG3 ate 45 px (y50, 0,671875 -> 0,470982). Os dois
reproduzem o quadro central sem diferenca de indices, mas nos extremos alteram
8.875/6.614 pixels (discreto) ou 11.920/18.102 (minimax), respectivamente.
Inspecao dos previews encontrou deslocamento visivel da relacao telhado/castelo;
nenhum recebeu aprovacao estetica.

Conclusao de curadoria: nenhum dos dois perfis e candidato a `res/`. O primeiro
minimiza alteracao media e preserva deltas MUGEN existentes, mas deixa drift de
45 px; o segundo limita o pior caso a 22,5 px, ainda perceptivel, e muda 14,33%
das amostras. Ambos continuam abaixo do criterio de fidelidade composicional.
Proxima acao de arte: reautorizar explicitamente quais massas podem compartilhar
duas velocidades por scanline, mantendo o castelo como ancora e telhado/piso
como plano de jogo; depois produzir um novo storyboard em pixels e reavaliar
costuras em 1x. Sem essa decisao, tilemap/priority/residencia, paleta per-tile,
ResComp, DMA/VBlank e ROM permanecem bloqueados. O sweep e um lower bound da
fonte estatica, nao prova de paridade MUGEN, camera em jogo ou hardware.

## Perfis semanticos e ownership (2026-09-26)

O novo `stage-plane-profile` usa um mapeamento de velocidade escolhido por layer
e bloqueia qualquer scanline que ainda precise de mais de dois rates. Isso
permite testar escolhas de direcao visual sem tratar o otimizador numerico como
diretor de arte. A varredura inteira delimita o conflito: linhas 0–39 veem
BG0b/BG2/BG3; linhas 40–111 veem BG0b/BG1/BG2/BG3; linhas 112–175 veem so
BG2/BG3; 176–211 veem BG4a em seu delta variavel por linha; 212–223 veem BG4b.

Foram produzidos dois perfis fonte, ambos sem aprovacao. `castle_anchor_front`
mantem BG2 e BG3 em seus deltas e desloca BG0b/BG1 para .537946; move 43,73% das
amostras e pode deslocar a lua 120,5 px no extremo. `sky_anchor_castle_front`
mantem BG0b em 0 e combina BG1/BG2/BG3 em .671875; move 28,57%, chega a 45 px
de drift e abre um vazio magenta no preview direito. O segundo conserva a
ancora do ceu, mas exige redesenhar o overlap do castelo e da arquitetura. Os
previews estao em `rascunho/processado/stage_takeover/`; hashes, detalhes e
plano de autoria estao em `doc/mugen/stage_plane_ownership_study_2026_09_26.md`.

Foi criado o draft `doc/mugen/suzaku_plane_storyboard_draft_2026_09_26.json`
com céu/lua em BG_B a 0, arquitetura/telhado em BG_A a .671875 até y175,
posições HUD/atores/pés e riscos do perfil céu-ancorado. Ainda não é aprovação
nem ownership tile-level final. Revisar as relações lua-castelo-telhado com os
fighters, preencher BG_A/B/priority/overlap em detalhe e reautorizar a arte que
compartilha velocidade para fechar os vazios. Depois, medir
tiles/paleta/ResComp/VRAM/DMA por viewport. A leitura humana dos previews não
substitui a revisão da arte final ou a prova do VDP.
