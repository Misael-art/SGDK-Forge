# Programando

IMPORTANTE: No canal do GameDevBoss existe um [vídeo](https://www.youtube.com/watch?v=H0XNUe4wY7E) ensinandocomo iniciar seu primeiro projeto na [SGDK](https://github.com/Stephane-D/SGDK/)! Assista ao vídeo para saber como compilar o HAMOOPIG em seu computador!

Isso é o mais importante para começar. Agora vamos a uma breve descrição das funções que você vai encontrar no código fonte, e o que você encontrará dentro delas.

## FUNCAO_INPUT_SYSTEM()

A FUNCAO_INPUT_SYSTEM() é importantíssima, pois ela vai retornar o estado de cada botão dos controles, permitindo criar lógica de troca de estados com a FSM. 

Assim, um comando do tipo *if(P[1].key_JOY_START_status==1)* está verificando se o Player 1 acabou de apertar o START, permitindo que você faça alguma coisa na sequência.

### Variáveis de joypad

- P[1].key_JOY_LEFT_status
- P[1].key_JOY_RIGHT_status
- P[1].key_JOY_UP_status
- P[1].key_JOY_DOWN_status
- P[1].key_JOY_A_status
- P[1].key_JOY_B_status
- P[1].key_JOY_C_status
- P[1].key_JOY_X_status
- P[1].key_JOY_Y_status
- P[1].key_JOY_Z_status
- P[1].key_JOY_MODE_status
- P[1].key_JOY_START_status

### Valores das variáveis de joypad

- 0 => Nao apertado
- 1 => Acabou de apertar
- 2 => Mantem apertado
- 3 => Acabou de soltar

## FUNCAO_FSM

A FUNCAO_FSM faz a troca de estados de acordo com as condições estabelecidas. Estas condições podem ser bem simples, ou bastante complexas dependendo do caso. Um exemplo simples:

```c
if(gDistancia>64)
{
    //soco fraco de pe de longe
    if( (P[i].key_JOY_X_status==1) && (P[i].state==100) )
    {
    PLAYER_STATE(i,101);
    }
}
```

## FUNCAO_ANIMACAO()

A FUNCAO_ANIMACAO() também faz parte da FSM, pois é ela que faz o retorno das animações de ataque ao estado parado, entre outras coisas. Assim, ao soltar um SOCO FORTE (103), ao terminar a animação, será carregado o estado PARADO (100). Quem faz isso é a FUNCAO_ANIMACAO. Outra coisa importantíssima que essa função faz é receber parâmetros para criar uma animação de tempo customizável. Resumidamente, este é um sistema de animação criado pelo GameDevBoss
que permite colocar um tempo diferente para cada quadro de sua animação, tornando possível animações de nível profissional, muito melhores que as realizadas com o sistema de animação padrão da SGDK.
­­­
A PLAYER_STATE é provavelmente uma das funcoes mais importantes, ao lado da FSM. É nela que configuramos os parâmetros dos nossos personagens. Vejamos:

```c
if(P[Player].id==1)
{
    if(State==100)
    {
        P[Player].y = gAlturaPiso;
        P[Player].w = 10*8;
        P[Player].h = 15*8;
        P[Player].axisX = P[Player].w/2;
        P[Player].axisY = P[Player].h;
        P[Player].dataAnim[1] = 8;
        P[Player].dataAnim[2] = 7;
        P[Player].dataAnim[3] = 7;
        P[Player].dataAnim[4] = 7;
        P[Player].dataAnim[5] = 7;
        P[Player].dataAnim[6] = 7;
        P[Player].animFrameTotal = 6;
        P[Player].sprite = SPR_addSpriteExSafe(...);
    }
    ...
}
```

- *P[n].id==1 significa Haohmaru, o primeiro personagem do jogo.*
- *State é o estado do Player, neste caso, Parado (100)*
- *P[n].x e P[n].y definem a posição do personagem na tela*
- *P[n].w e P[n].h definem largura (width) e altura (height) do sprite (em pixels)*
- *P[n].axisX e P[n].axisY definem a posição do ponto pivot da imagem*
- *P[n].dataAnim[n] define o tempo que cada frame é exibido na tela; 0­255*
- *P[n].animFrameTotal define a quantidade total de quadros desta animação, que deve ser igual a quantidade de dataAnim's definidos pelo programador.*
- *P[n].sprite faz o carregamento da imagem / sprite deste movimento.*

As imagens usadas na **SGDK** devem seguir o padrão do Genesis. A partir deste momento chamaremos elas de *sprites*. Esses sprites devem ter o tamanho multiplo de 8 pixels. Cada conjunto de 8x8 pixels é chamado de *TILE*. Além disso eles devem ter apenas 16 cores, sendo que a primeira cor da paleta é reservada para a cor transparente. Cada conjunto de sprites, formando uma sequência de animação é chamada de Sprite Sheet, Folha de Sprites, ou simplesmente *ESTADO*, na **HAMOOPIG**. Este é o estado PARADO (100) do personagem Haohmaru. Cada sprite desta sequência é chamado de *FRAME*.

## PLAYER_STATE(u8 Player, u16 State)
Recebe o Player(1;2) e o State(nnn). É a função que carrega os parâmetros de animacao do personagem, carrega a imagem do sprite, entre outras coisas importantes

## FUNCAO_PLAY_SND(u8 Player, u16 State)
Recebe o Player(1;2) e o State(nnn). Toca os sons do jogo, barulhos de
golpes por exemplo

## FUNCAO_RELOGIO()
Atualiza o sprite do relogio, no HUD do jogo

## FUNCAO_BARRAS_DE_ENERGIA()
Atualiza as barras de energia e barras de especial

## FUNCAO_SPR_POSITION()
Ajusta a posição do sprite, depois que nós movemos ele

## FUNCAO_INPUT_SYSTEM()
Verifica os botões dos controles dos jogadores

## FUNCAO_FSM()
O Cérebro da engine. A própria engine.

## FUNCAO_FSM_HITBOXES(u8 Player)
Recebe Player (1;2). Carrega as informações sobre as caixas de colisão. É a alma de um jogo de luta consistente.

## FUNCAO_PHYSICS()
Move os objetos no jogo. Recomendo investigar como os pulos (300) e o movimento cair (550) foram programados. Um utiliza hard code, outro, um sistema de física extremamente simples e rápido criado pelo GameDevBoss para rodar especificamente no Mega Drive.

## FUNCAO_CAMERA_BGANIM()
Controla a camera e animação do background.

## FUNCAO_DEPTH(u8 Player)
Muda a ordem de empilhamento dos sprites. Um ataque sempre deve ficar por cima, por exemplo.

## FUNCAO_SAMSHOFX()
Algumas coisas que dizem respeito ao Samurai Shodown 2, e portanto deve ser alterado ou suprimido em outros tipos de jogos.

## FUNCAO_DEBUG()
Mostra algumas informações importantes na tela, desde que você não esteja printando sprites em seus caracteres alfa numéricos.

## FUNCAO_COLISAO(s16 R1x1, s16 R1y1, s16 R1x2, s16 R1y2, s16 R2x1, s16 R2y1, s16 R2x2, s16 R2y2)
Pense numa função que faz testes de colisão extremamente rápidos. Basta informar para ela o x1, y1, x2, y2 de um objeto e x1, y1, x2, y2 de outro, e ela vai retornar TRUE ou FALSE para você.

## FUNCAO_UPDATE_LIFESP(u8 Player, u8 EnergyType, s8 Value)
Recebe Player(1;2) EnergyType(1;2) e Value(nnn).
Permite tirar ou aumentar a energia normal ou especial dos Players.

## FUNCAO_INICIALIZACAO()
Inicializa alguns sistemas importantes.

## FUNCAO_ROUND_INIT()
Inicializa o round pela primeira vez.

## FUNCAO_ROUND_RESTART()
Reinicializa o round.

## CLEAR_VDP()
Limpa a VDP; Video Display Processor.
