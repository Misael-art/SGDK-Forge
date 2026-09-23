# Como funciona?

A criação de um jogo de luta é uma tarefa bastante complexa.Mesmo em PCs, a solução mais fácil seria utilizar o [MUGEN](http://www.elecbyte.com/mugendocs-11b1/mugen.html), para não ter que criar um ogo a partir do Zero. Com a **HAMOOPI / HAMOOPIG** você terá um ponto de partida, muitas coisas já foram feitas para você ter mais facilidade ao produzir o seu game, e se concentrar no que realmente importa, que é o conteúdo do seu jogo.

A **HAMOOPIG** foi criada para permitir que você crie jogos tão bons quanto aqueles melhores jogos de luta dos arcades dos anos 80 / 90 no auge da era 2D no Genesis! [Vamos começar falando da máquina de estados.](https://www.youtube.com/watch?v=Y8YTk2ibPew)

De maneira simplificada e resumida, a Máquina de estados (*FSM*) controla
os estados, ou ações que o seu personagem pode fazer. Assim, o
movimento parado é um estado, o movimento andando é outro, e socos e
chutes também! A *FSM* controla a transição entre estes estados, que são
finitos. A **HAMOOPIG** possui uma tabela numérica que determina cada um
deles, e é importante você ter esta tabela por perto para criar personagens
nesta engine. Vamos a ela.

## Lista de movimentos

### Curta distância
- 151 ­ Soco Fraco de Perto
- 152 ­ Soco Médio de Perto
- 153 ­ Soco Forte de Perto
- 154 ­ Chute Fraco de Perto
- 155 ­ Chute Médio de Perto
- 156 ­ Chute Forte de Perto

### Abaixado
- 200 ­ Abaixado
- 201 ­ Soco Fraco Abaixado
- 202 ­ Soco Médio Abaixado
- 203 ­ Soco Forte Abaixado
- 204 ­ Chute Fraco Abaixado
- 205 ­ Chute Médio Abaixado
- 206 ­ Chute Forte Abaixado
- 207 ­ Inicio da Defesa Abaixado
- 208 ­ Defendendo Abaixado
- 209 ­ Final da Defesa Abaixado
- 210 ­ Defesa Abaixada, Aplicada
 
### No ar
- 300 ­ Pulo Neutro
- 301 ­ Soco Fraco Aéreo Neutro
- 302 ­ Soco Médio Aéreo Neutro
- 303 ­ Soco Forte Aéreo Neutro
- 304 ­ Chute Fraco Aéreo Neutro
- 305 ­ Chute Médio Aéreo Neutro
- 306 ­ Chute Forte Aéreo Neutro

### No ar e para trás
- 310 ­ Pulo para Trás
- 311 ­ Soco Fraco Aéreo para Trás
- 312 ­ Soco Médio Aéreo para Trás
- 313 ­ Soco Forte Aéreo para Trás
- 314 ­ Chute Fraco Aéreo para Trás
- 315 ­ Chute Médio Aéreo para Trás
- 316 ­ Chute Forte Aéreo para Trás

### No ar e pra frente
- 320 ­ Pulo para Frente
- 321 ­ Soco Fraco Aéreo para Frente
- 322 ­ Soco Médio Aéreo para Frente
- 323 ­ Soco Forte Aéreo para Frente
- 324 ­ Chute Fraco Aéreo para Frente
- 325 ­ Chute Médio Aéreo para Frente
- 326 ­ Chute Forte Aéreo para Frente

### Movimentação
- 410 ­ Andando para Trás
- 420 ­ Andando para Frente
- 470 ­ Esquiva para Baixo / Esquiva para Trás
- 471 ­ Rolamento para Trás
- 472 ­ Rolamento para Frente
- 480 ­ Inicio da corrida
- 481 ­ Correndo
- 482 ­ Final da Corrida

### Queda e levando golpe
- 501 ­ Hit Tipo 1, Fraco
- 502 ­ Hit Tipo 1, Medio
- 503 ­ Hit Tipo 1, Forte
- 504 ­ disponível
- 505 ­ disponível
- 511 ­ Hit Tipo 3, Fraco
- 512 ­ Hit Tipo 3, Medio
- 513 ­ Hit Tipo 3, Forte
- 514 ­ disponível
- 515 ­ disponível
- 516 ­ User Hit
- 517 ­ disponível
- 518 ­ disponível
- 519 ­ disponível
- 520 ­ disponível
- 550 ­ Caindo
- 551 ­ Quicando no chão
- 552 ­ Levantando
- 570 ­ Caido, Morto
- 601 ­ Abaixando
- 602 ­ Levantando
- 603 ­ Inicio Pulo para Trás *(IMG 604)
- 604 ­ Inicio Pulo Neuto
- 605 ­ Inicio Pulo para Frente *(IMG 604)
- 606 ­ Final do Pulo / Aterrisando no chão
- 607 ­ Virando, em Pé
- 608 ­ Virando Abaixado

### Comemorações e derrotas
- 610 ­ Intro
- 611 ­ Win1
- 612 ­ Win2
- 613 ­ Win3
- 614 ­ Win4
- 615 ­ Perdendo por Time Over
- 618 ­ Rage Explosion (Samurai Shodow 2)

### Especiais

Os numeros a partir do 700 podem ser usados para os especiais. Eu recomendo cada dezena para 1 tipo de especial, assim, do 700 até o 900 temos espaço para 20 especiais e supers. Exemplo de como você pode trabalhar um especial (Lembre­se que você pode utilizar as numerações como melhor desejar):

- 700 ­ Especial 1
- 701 ­ Fireball 1
- 702 ­ Spark da Fireball 1
- 703 ­ ­disponível
- 704 ­ ­disponível
- 705 ­ ­disponível
- 706 ­ ­disponível
- 707 ­ ­disponível
- 708 ­ ­disponível
- 709 ­ ­disponível­
