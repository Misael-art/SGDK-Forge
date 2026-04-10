# 12 - Roteiro

**Versao:** 2.0
**Tom geral:** Poetico, contemplativo, sem didatismo. O texto fala com o jogador como se fosse um amigo que mostra algo bonito.

> **REGRA:** Nenhum dialogo pode ser alterado sem atualizar este documento primeiro.
> A implementacao em codigo deve refletir exatamente o que esta aqui.
> Se houver divergencia, este documento vence.

---

## 1. DIRETRIZES DE TOM

### O que o texto DEVE ser
- Curto (max 4 linhas por encontro).
- Poetico sem ser pretensioso.
- Concreto: referencia ao que o jogador ve/faz, nao abstracionismo vazio.
- Voz propria de cada speaker (ver tabela abaixo).

### Vozes dos speakers

| Speaker | Tom | Exemplo de cadencia |
|---------|-----|---------------------|
| ROSA | Intima, doce, protetora | "Cuida do teu pequeno mundo." |
| REI | Cerimonioso, pausado, grandioso | "Nem todo plano corre igual." |
| VAIDOSO | Exuberante, expectante, fragil por dentro | "Diga que sou esplendido!" |
| BEBADO | Melancolico, circular, repetitivo | "Bebo para esquecer que bebo." |
| CONTADOR | Seco, numerico, distraido | "Quinhentos e um milhoes..." |
| ACENDEDOR | Ritmico, mecanico-poetico, fiel | "Acendo a noite linha por linha." |
| GEOGRAFO | Curioso, meticuloso, sedentario | "Descreva-me o que viu." |
| SERPENTE | Enigmatica, concisa, profunda | "Toco quem toco e volto a terra." |
| VENTO | Impessoal, vasto, antigo | "No deserto, o vento fala devagar." |
| ROSAS | Coral, vagas, indistintas | "Somos todas iguais, dizemos." |
| AVIADOR | Caloroso, nostalgico, fraterno | "Desenha-me um carneiro." |

### O que o texto NAO DEVE ser
- Tecnico (nada de "line scroll", "DMA", "palette" nos dialogos).
- Expositivo ("voce esta no planeta X e precisa fazer Y").
- Longo (mais de 4 linhas quebra window plane e ritmo).
- Generico (frases que caberiam em qualquer jogo).

### Regra de ouro
Se o dialogo nao funcionaria lido em voz alta para uma crianca de 10 anos, ele precisa ser reescrito.

---

## 2. TELA: TITLE

**Texto:**
```
PEQUENO PRINCIPE
CRONICAS DAS ESTRELAS

Pressione START
```

---

## 3. TELA: STORY

**Texto (pagina unica):**
```
Certa noite, um menino de cabelo dourado
acordou num asteroide tao pequeno
que cabia num abraco.

O cachecol tremeu. O vento soprou.
E ele soube: havia outros mundos
esperando alguem que soubesse olhar.
```

---

## 4. PLANETA: B-612

### Speaker: ROSA

### Encontro de introducao
```
ROSA
Cuida do teu pequeno mundo.
O por do sol muda com teu passo.
O vento desenha o cachecol.
Quando ouvir isso, a rota abre.
```

### Encontro pos-resolucao
```
ROSA
A rosa ja escutou teu passo.
Agora voce le B-612 com calma.
C abre a rota quando quiser.
Leve esse cuidado adiante.
```

### Audio: voice_rose.wav + fx_bloom.wav
### Objetivo: Aproximar-se da rosa (centro, raio 18px) + A.
### Saida: C → Viagem A → Planeta do Rei.

---

## 5. VIAGEM A — CAVALGANDO ESTRELA

### Virtude: CORAGEM
### Texto de abertura (pre-viagem, 2 linhas)
```
Uma estrela amiga ofereceu suas costas.
Segure firme — o cosmos e veloz!
```

### Texto de chegada (pos-viagem, 2 linhas)
```
A coragem trouxe voce ate aqui.
Um novo mundo espera quem ousa.
```

---

## 6. PLANETA: REI

### Speaker: REI

### Encontro de introducao
```
REI
Nem todo plano corre igual.
Profundidade tambem e autoridade.
Escute o eco entre frente e fundo.
Quando o trono responder, siga.
```

### Encontro pos-resolucao
```
REI
O palacio ja respira em camadas.
Voce viu planos conversarem.
C leva isso ao proximo mundo.
Continue em frente.
```

### Audio: voice_king.wav + fx_throne.wav
### Objetivo: Aproximar-se do trono (centro, raio 20px) + A.
### Saida: C → Viagem B → Planeta do Vaidoso.

---

## 7. VIAGEM B — SURFANDO COMETA COM REDE

### Virtude: DETERMINACAO
### Texto de abertura
```
Um cometa passou — rapido, rapido!
A rede de borboletas o alcancou.
```

### Texto de chegada
```
Quem nao solta a rede chega longe.
A determinacao venceu a velocidade.
```

---

## 8. PLANETA: VAIDOSO

### Speaker: VAIDOSO

### Encontro de introducao
```
VAIDOSO
Bata palmas! Eu sou esplendido!
Veja como o espelho me conhece.
Mas... voce ve algo alem do reflexo?
Olhe mais fundo, por favor.
```

### Encontro pos-resolucao
```
VAIDOSO
O espelho mostrou a verdade.
Nem tudo que brilha e so superficie.
C abre o caminho — va em frente.
Leve a coragem de olhar dentro.
```

### Audio: voice_vain.wav + fx_mirror.wav
### Objetivo: Interagir com o espelho (centro, raio 18px) + A.
### Saida: C → Viagem C → Planeta do Bebado.

---

## 9. VIAGEM C — GUINCHADO POR PASSAROS

### Virtude: HUMILDADE
### Texto de abertura
```
Os passaros vieram sem ser chamados.
O cachecol virou rédea — confie neles.
```

### Texto de chegada
```
Quem aceita ser carregado aprende a voar.
A humildade e mais alta que o orgulho.
```

---

## 10. PLANETA: BEBADO

### Speaker: BEBADO

### Encontro de introducao
```
BEBADO
Bebo para esquecer... esquecer o que?
O mundo gira, mas nao sai do lugar.
Ha um circulo triste aqui dentro.
Voce pode ver sem girar?
```

### Encontro pos-resolucao
```
BEBADO
O giro parou um instante.
Obrigado por olhar sem tontura.
C te leva daqui — va reto.
Reto e bonito quando se pode.
```

### Audio: voice_drunk.wav + fx_bottle.wav
### Objetivo: Interagir com a garrafa (centro, raio 20px) + A.
### Saida: C → Viagem D → Planeta do Homem de Negocios.

---

## 11. VIAGEM D — DESLIZANDO EM ARCO-IRIS

### Virtude: COMPAIXAO
### Texto de abertura
```
Um arco-iris surgiu entre dois mundos.
Deslize sobre a luz — ela carrega todos.
```

### Texto de chegada
```
A luz nao escolhe quem ilumina.
Compaixao e o arco-iris da alma.
```

---

## 12. PLANETA: HOMEM DE NEGOCIOS

### Speaker: CONTADOR

### Encontro de introducao
```
CONTADOR
Quinhentos e um milhoes de estrelas.
Todas minhas! Anotadas no livro.
Mas... para que serve possuir?
Voce sabe a resposta?
```

### Encontro pos-resolucao
```
CONTADOR
O livro se fechou sozinho.
Talvez as estrelas nao sejam de ninguem.
C leva voce ao proximo planeta.
Va — sem levar nada. E leve.
```

### Audio: voice_counter.wav + fx_ledger.wav
### Objetivo: Interagir com o livro de contas (centro, raio 18px) + A.
### Saida: C → Viagem E → Planeta do Acendedor.

---

## 13. VIAGEM E — CARONA NA ESTRELA AMIGA

### Virtude: CONFIANCA
### Texto de abertura
```
A estrelinha voltou — mas nao enxerga bem.
Grite as direcoes! Confie, mesmo assim.
```

### Texto de chegada
```
Confiar e voar sem ver o chao.
E chegar inteiro mesmo assim.
```

---

## 14. PLANETA: ACENDEDOR

### Speaker: ACENDEDOR

### Encontro de introducao
```
ACENDEDOR
Acendo a noite linha por linha.
A luz muda o mundo no meio.
Veja o calor dancar na chama.
Leve esse ritmo com voce.
```

### Encontro pos-resolucao
```
ACENDEDOR
A chama agora divide ceu e terra.
O raster achou o tempo certo.
C segue ao proximo planeta.
Va enquanto a luz ainda canta.
```

### Audio: voice_lamp.wav + fx_lamp.wav
### Objetivo: Aproximar-se do lampiao (centro, raio 18px) + A.
### Saida: C → Viagem F → Planeta do Geografo.

---

## 15. VIAGEM F — SUBINDO A ARVORE COSMICA

### Virtude: PERSEVERANCA
### Texto de abertura
```
Uma arvore gigante liga dois mundos.
Amarre os baloes e suba — devagar, mas sem parar.
```

### Texto de chegada
```
Quem sobe devagar sobe mais alto.
Perseveranca e raiz que vira asa.
```

---

## 16. PLANETA: GEOGRAFO

### Speaker: GEOGRAFO

### Encontro de introducao
```
GEOGRAFO
Descreva-me o que viu la fora!
Eu anoto tudo, mas nunca saio.
Montanhas, rios, vulcoes — conte!
Um explorador me faz falta.
```

### Encontro pos-resolucao
```
GEOGRAFO
Anotei tudo no meu mapa.
Agora o mundo e maior aqui dentro.
C te leva alem do meu papel.
Va — e me conte depois.
```

### Audio: voice_geographer.wav + fx_map.wav
### Objetivo: Interagir com o mapa (centro, raio 20px) + A.
### Saida: C → Viagem G → Planeta da Serpente.

---

## 17. VIAGEM G — BARCO ESPACIAL ARTESANAL

### Virtude: CRIATIVIDADE
### Texto de abertura
```
Com madeira, tecido e imaginacao,
o barco voador esta pronto. Sopre a vela!
```

### Texto de chegada
```
Com pouco se faz muito.
A criatividade e o motor mais leve.
```

---

## 18. PLANETA: SERPENTE

### Speaker: SERPENTE

### Encontro de introducao
```
SERPENTE
Toco quem toco e volto a terra.
O circulo fecha onde comeca.
Voce procura caminho ou destino?
Os dois moram no mesmo lugar.
```

### Encontro pos-resolucao
```
SERPENTE
O circulo se desenhou sozinho.
Voce entendeu sem ter medo.
C te leva a Terra dos homens.
La, tudo e mais complicado.
```

### Audio: voice_snake.wav + fx_circle.wav
### Objetivo: Interagir com o circulo na areia (centro, raio 18px) + A.
### Saida: C → Viagem H → Deserto das Estrelas.

---

## 19. VIAGEM H — AVIAOZINHO MONOMOTOR

### Virtude: ESPERANCA
### Texto de abertura
```
Um aviaozinho esquecido no deserto.
O motor tossiu — e acordou.
```

### Texto de chegada
```
Mesmo em tempestade, o destino existe.
A esperanca e motor que nao para.
```

---

## 20. PLANETA: DESERTO DAS ESTRELAS

### Speaker: VENTO

### Encontro de introducao
```
VENTO
No deserto, o vento fala devagar.
A miragem prepara a travessia.
Olhe a leste e sinta a rota abrir.
Quando o marco responder, siga.
```

### Encontro pos-resolucao
```
VENTO
O deserto aceitou teu silencio.
A travessia continua adiante.
C te leva a quem voce precisa.
As estrelas ja sabem teu caminho.
```

### Audio: voice_wind.wav + fx_star.wav
### Objetivo: Aproximar-se do marco estelar (x=248, raio 20px) + A.
### Saida: C → Viagem I → Jardim das Rosas.

---

## 21. VIAGEM I — DANCA COM A RAPOSA

### Virtude: AMIZADE
### Texto de abertura
```
A raposa apareceu no campo.
"Me cativa", pediu. "Danca comigo."
```

### Texto de chegada
```
Tu te tornas responsavel por quem cativas.
A amizade e a danca mais bonita.
```

---

## 22. PLANETA: JARDIM DAS ROSAS

### Speaker: ROSAS

### Encontro de introducao
```
ROSAS
Somos todas iguais, dizemos.
Mas uma rosa e diferente para voce.
O que a faz unica nao e a forma.
E o tempo que voce deu a ela.
```

### Encontro pos-resolucao
```
ROSAS
Agora voce sabe a diferenca.
Uma entre mil — e so sua.
C te leva ao ultimo encontro.
O essencial esta quase visivel.
```

### Audio: voice_roses.wav + fx_garden.wav
### Objetivo: Interagir com o canteiro (centro, raio 20px) + A.
### Saida: C → Viagem J → Poco no Deserto.

---

## 23. VIAGEM J — TORRE DOS VENTOS

### Virtude: FIDELIDADE
### Texto de abertura
```
Uma torre de ventos solidificados.
Suba firme — o mundo balanca, voce nao.
```

### Texto de chegada
```
Fidelidade e ficar de pe
quando o chao danca.
```

---

## 24. PLANETA: POCO NO DESERTO

### Speaker: AVIADOR

### Encontro de introducao
```
AVIADOR
Desenha-me um carneiro.
A agua esta la embaixo, no escuro.
O essencial e invisivel aos olhos.
So se ve bem com o coracao.
```

### Encontro pos-resolucao
```
AVIADOR
A agua subiu — doce, clara.
Voce encontrou o que procurava.
C te leva de volta pra casa.
A viagem mais longa e a de voltar.
```

### Audio: voice_aviator.wav + fx_well.wav
### Objetivo: Interagir com o poco (centro, raio 20px) + A.
### Saida: C → Viagem K → B-612 (retorno).

---

## 25. VIAGEM K — VOO FINAL PARA CASA

### Virtude: SABEDORIA
### Texto de abertura
```
Tudo o que aprendeu voa com voce.
O caminho de volta e o mais bonito.
```

### Texto de chegada
```
Quem volta sabio olha com o coracao.
B-612 nunca esteve tao perto.
```

---

## 26. PLANETA: B-612 (RETORNO)

### Speaker: ROSA

### Encontro unico (nao repete)
```
ROSA
Voce voltou.
O por do sol te esperou.
O cachecol lembra de tudo.
Cuida do teu pequeno mundo.
```

### Audio: voice_rose.wav (mesmo, mas com eco) + fx_bloom.wav
### Objetivo: Aproximar-se da rosa + A.
### Saida: Automatica → Credits.

---

## 27. TELA: CREDITS

**Texto:**
```
PEQUENO PRINCIPE
CRONICAS DAS ESTRELAS

Projeto pedagogico para Mega Drive
Inspirado na obra de Saint-Exupery

SGDK 2.11

"O essencial e invisivel aos olhos."

Pressione A para voltar ao titulo
```

---

## 28. CODEX — ENTRADAS DE VIAGEM

### Viagem A: Cavalgando Estrela
```
Viagem A: Cavalgando Estrela
Pseudo-3D via line scroll por scanline no chao.
Sprites em 6 tamanhos simulam profundidade Z.
Projecao perspectiva com LUT pre-calculada.
A CPU projeta 16 objetos a 60fps.
```

### Viagem B: Surfando Cometa
```
Viagem B: Surfando Cometa
Parallax de 6 camadas com line scroll horizontal.
Meteoros massivos desenhados no Plane A via tile swap.
Distorcao de calor com sine wave LUT no hscroll.
Object pool de 32 entidades com colisao AABB.
```

### Viagem C: Guinchado por Passaros
```
Viagem C: Guinchado por Passaros
Scroll vertical com line scroll no Plane B para vertigem.
Nuvens gigantes via tile swap no Plane A.
Relampago com palette flash full-screen.
6 passaros como meta-sprites flanqueando o heroi.
```

### Viagem D: Deslizando em Arco-Iris
```
Viagem D: Deslizando em Arco-Iris
Palette cycling agressivo simula fluxo de luz.
48 particulas via flickering par/impar a 60fps.
Pseudo-alpha blending com paleta alternante.
A cena mais leve e mais bonita do jogo.
```

### Viagem E: Carona na Estrela
```
Viagem E: Carona na Estrela
Chao 3D via palette cycling puro — zero tile swap.
Apenas 32 bytes de CRAM por frame criam ilusao.
Controle com delay de 4 frames simula estrela miope.
Inspirado em Mickey Mania: The Moose Chase.
```

### Viagem F: Arvore Cosmica
```
Viagem F: Arvore Cosmica
DMA streaming injeta frames de tronco na VRAM.
24 quadros de rotacao pre-renderizados e comprimidos.
~4 KB de DMA por update no VBlank.
Inspirado em Mickey Mania: The Mad Doctor Tower.
```

### Viagem G: Barco Artesanal
```
Viagem G: Barco Artesanal
Rotacao falsa do oceano via tile pattern swap.
32 frames de rotacao — trocar 32 tiles gira tudo.
Barco em 16 angulos pre-desenhados.
Inspirado no Vectorman: Buggy Stage.
```

### Viagem H: Aviaozinho Monomotor
```
Viagem H: Aviaozinho Monomotor
Parallax de 8 camadas com line scroll agressivo.
32 particulas de chuva via flickering engine.
Nuvens massivas no Plane A sem gastar sprites.
Cena mais exigente em CPU: ~85%.
```

### Viagem I: Danca com a Raposa
```
Viagem I: Danca com a Raposa
Raposa com 12 partes articuladas por cinematica.
Posicao de cada junta calculada via sinFix16.
Inspirado em Gunstar Heroes: Seven Force.
A CPU calcula angulos de 12 juntas a 60fps.
```

### Viagem J: Torre dos Ventos
```
Viagem J: Torre dos Ventos
Torre distorcida por sine wave no hscroll.
H-Int aplica deslocamento senoidal por scanline.
Reflexo na agua com sine invertido e paleta escura.
Inspirado em Castlevania Bloodlines: Torre de Pisa.
```

### Viagem K: Voo Final
```
Viagem K: Voo Final para Casa
Rotacao e zoom do chao por software rendering.
68000 calcula texture mapping linha por linha.
DMA agressivo de ~6.5 KB/frame para VRAM.
Inspirado em Red Zone. A cena mais pesada do jogo.
```

---

## 29. CODEX — ENTRADAS DE PLANETA (NOVOS)

### Planeta do Vaidoso
```
Planeta do Vaidoso
Sprite reflection duplica o personagem invertido.
Palette flash simula brilho de espelho.
Efeito de eco visual com delay de 4 frames.
A vaidade e um reflexo que nao ouve.
```

### Planeta do Bebado
```
Planeta do Bebado
Screen wobble via hscroll senoidal global.
Desaturacao progressiva por palette manipulation.
O mundo gira mesmo parado — efeito de tontura.
A repeticao e a armadilha mais triste.
```

### Planeta do Homem de Negocios
```
Planeta do Homem de Negocios
Tile counter anima numeros caindo do ceu.
Number rain via sprite pool reutilizado.
O VDP conta tiles como o contador conta estrelas.
Possuir nao e cuidar.
```

### Planeta do Geografo
```
Planeta do Geografo
Map scroll com scrolling duplo coordenado.
Minimap overlay via window plane parcial.
O mapa cresce conforme o principe descreve.
Explorar e dar nome ao desconhecido.
```

### Planeta da Serpente
```
Planeta da Serpente
Shadow mode escurece o cenario progressivamente.
Fade to black controlado por CRAM gradual.
O circulo na areia e desenhado tile por tile.
O fim e um comeco disfarçado.
```

### Jardim das Rosas
```
Jardim das Rosas
Palette cycling floral: 5000 rosas em 3 paletas.
Multi-sprite preenche a tela de petalas.
Flickering cria densidade sem estourar sprites.
Uma entre mil — e a diferenca e o amor.
```

### Poco no Deserto
```
Poco no Deserto
Column scroll profundo simula descida ao poco.
Echo effect: palette cycling com delay temporal.
A agua sobe quando o jogador se aproxima.
O essencial e invisivel aos olhos.
```

---

## 30. REGRAS DE EDICAO DO ROTEIRO

1. Qualquer mudanca de dialogo deve ser feita AQUI primeiro, depois refletida no codigo.
2. O tom de cada speaker e inviolavel (ver tabela na secao 1).
3. Maximo 4 linhas por encontro. Sem excecao.
4. Nenhum dialogo pode conter termos tecnicos (DMA, VRAM, palette, scroll, etc.).
5. O codex e a unica excecao: la, termos tecnicos sao obrigatorios.
6. Textos de abertura/chegada de viagem sao max 2 linhas cada.
7. Ao adicionar novo planeta ou viagem, criar entrada completa neste documento ANTES de implementar.
