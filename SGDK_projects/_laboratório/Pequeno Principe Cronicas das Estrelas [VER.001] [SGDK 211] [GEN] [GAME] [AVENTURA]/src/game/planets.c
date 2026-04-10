#include "project.h"

static const u16 gB612Pal0[16] =
{
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0), RGB3_3_3_TO_VDPCOLOR(7, 7, 7),
    RGB3_3_3_TO_VDPCOLOR(6, 6, 7), RGB3_3_3_TO_VDPCOLOR(5, 5, 7),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 3), RGB3_3_3_TO_VDPCOLOR(7, 4, 2),
    RGB3_3_3_TO_VDPCOLOR(3, 2, 5), RGB3_3_3_TO_VDPCOLOR(1, 1, 2),
    0, 0, 0, 0, 0, 0, 0, 0
};

static const u16 gB612Pal1[16] =
{
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0), RGB3_3_3_TO_VDPCOLOR(5, 6, 2),
    RGB3_3_3_TO_VDPCOLOR(4, 5, 1), RGB3_3_3_TO_VDPCOLOR(7, 7, 4),
    RGB3_3_3_TO_VDPCOLOR(7, 3, 4), RGB3_3_3_TO_VDPCOLOR(4, 2, 1),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 7), RGB3_3_3_TO_VDPCOLOR(2, 1, 0),
    0, 0, 0, 0, 0, 0, 0, 0
};

static const u16 gB612Sky0[6] = { 0, RGB3_3_3_TO_VDPCOLOR(7, 7, 7), RGB3_3_3_TO_VDPCOLOR(6, 6, 7), RGB3_3_3_TO_VDPCOLOR(5, 5, 7), RGB3_3_3_TO_VDPCOLOR(7, 6, 3), RGB3_3_3_TO_VDPCOLOR(7, 4, 2) };
static const u16 gB612Sky1[6] = { 0, RGB3_3_3_TO_VDPCOLOR(7, 6, 7), RGB3_3_3_TO_VDPCOLOR(7, 5, 6), RGB3_3_3_TO_VDPCOLOR(6, 4, 6), RGB3_3_3_TO_VDPCOLOR(7, 5, 2), RGB3_3_3_TO_VDPCOLOR(7, 3, 2) };
static const u16 gB612Sky2[6] = { 0, RGB3_3_3_TO_VDPCOLOR(6, 5, 7), RGB3_3_3_TO_VDPCOLOR(5, 4, 6), RGB3_3_3_TO_VDPCOLOR(4, 3, 5), RGB3_3_3_TO_VDPCOLOR(7, 4, 2), RGB3_3_3_TO_VDPCOLOR(6, 2, 1) };
static const u16 gB612Sky3[6] = { 0, RGB3_3_3_TO_VDPCOLOR(5, 4, 6), RGB3_3_3_TO_VDPCOLOR(4, 3, 5), RGB3_3_3_TO_VDPCOLOR(3, 2, 4), RGB3_3_3_TO_VDPCOLOR(7, 3, 1), RGB3_3_3_TO_VDPCOLOR(5, 1, 1) };
static const u16 *const gB612Cycle[] = { gB612Sky0, gB612Sky1, gB612Sky2, gB612Sky3 };

static const u16 gKingPal0[16] =
{
    0, RGB3_3_3_TO_VDPCOLOR(7, 7, 7), RGB3_3_3_TO_VDPCOLOR(6, 7, 7), RGB3_3_3_TO_VDPCOLOR(4, 6, 7),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 2), RGB3_3_3_TO_VDPCOLOR(5, 3, 1), RGB3_3_3_TO_VDPCOLOR(2, 2, 6), RGB3_3_3_TO_VDPCOLOR(0, 0, 2),
    0, 0, 0, 0, 0, 0, 0, 0
};

static const u16 gKingPal1[16] =
{
    0, RGB3_3_3_TO_VDPCOLOR(4, 3, 6), RGB3_3_3_TO_VDPCOLOR(3, 2, 5), RGB3_3_3_TO_VDPCOLOR(7, 6, 3),
    RGB3_3_3_TO_VDPCOLOR(6, 4, 1), RGB3_3_3_TO_VDPCOLOR(7, 7, 5), RGB3_3_3_TO_VDPCOLOR(2, 1, 4), 0,
    0, 0, 0, 0, 0, 0, 0, 0
};

static const u16 gLampPal0Top[16] =
{
    0, RGB3_3_3_TO_VDPCOLOR(7, 7, 7), RGB3_3_3_TO_VDPCOLOR(6, 6, 6), RGB3_3_3_TO_VDPCOLOR(4, 5, 7),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 2), RGB3_3_3_TO_VDPCOLOR(7, 4, 1), RGB3_3_3_TO_VDPCOLOR(1, 1, 2), RGB3_3_3_TO_VDPCOLOR(0, 0, 1),
    0, 0, 0, 0, 0, 0, 0, 0
};

static const u16 gLampPal0BottomDark[16] =
{
    0, RGB3_3_3_TO_VDPCOLOR(4, 4, 6), RGB3_3_3_TO_VDPCOLOR(3, 3, 4), RGB3_3_3_TO_VDPCOLOR(2, 2, 3),
    RGB3_3_3_TO_VDPCOLOR(3, 2, 1), RGB3_3_3_TO_VDPCOLOR(2, 1, 0), RGB3_3_3_TO_VDPCOLOR(1, 1, 2), RGB3_3_3_TO_VDPCOLOR(0, 0, 1),
    0, 0, 0, 0, 0, 0, 0, 0
};

static const u16 gLampPal0BottomLit[16] =
{
    0, RGB3_3_3_TO_VDPCOLOR(7, 7, 6), RGB3_3_3_TO_VDPCOLOR(7, 6, 4), RGB3_3_3_TO_VDPCOLOR(6, 5, 2),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 2), RGB3_3_3_TO_VDPCOLOR(7, 4, 1), RGB3_3_3_TO_VDPCOLOR(2, 1, 0), RGB3_3_3_TO_VDPCOLOR(0, 0, 1),
    0, 0, 0, 0, 0, 0, 0, 0
};

static const u16 gLampPal1[16] =
{
    0, RGB3_3_3_TO_VDPCOLOR(5, 5, 2), RGB3_3_3_TO_VDPCOLOR(4, 4, 1), RGB3_3_3_TO_VDPCOLOR(7, 7, 3),
    RGB3_3_3_TO_VDPCOLOR(7, 5, 1), RGB3_3_3_TO_VDPCOLOR(2, 1, 0), RGB3_3_3_TO_VDPCOLOR(6, 6, 6), 0,
    0, 0, 0, 0, 0, 0, 0, 0
};

static const u16 gLampTop6[6] = { 0, RGB3_3_3_TO_VDPCOLOR(7, 7, 7), RGB3_3_3_TO_VDPCOLOR(6, 6, 6), RGB3_3_3_TO_VDPCOLOR(4, 5, 7), RGB3_3_3_TO_VDPCOLOR(7, 6, 2), RGB3_3_3_TO_VDPCOLOR(7, 4, 1) };
static const u16 gLampBottomDark6[6] = { 0, RGB3_3_3_TO_VDPCOLOR(4, 4, 6), RGB3_3_3_TO_VDPCOLOR(3, 3, 4), RGB3_3_3_TO_VDPCOLOR(2, 2, 3), RGB3_3_3_TO_VDPCOLOR(3, 2, 1), RGB3_3_3_TO_VDPCOLOR(2, 1, 0) };
static const u16 gLampBottomLit6[6] = { 0, RGB3_3_3_TO_VDPCOLOR(7, 7, 6), RGB3_3_3_TO_VDPCOLOR(7, 6, 4), RGB3_3_3_TO_VDPCOLOR(6, 5, 2), RGB3_3_3_TO_VDPCOLOR(7, 6, 2), RGB3_3_3_TO_VDPCOLOR(7, 4, 1) };

static const u16 gDesertPal0[16] =
{
    0, RGB3_3_3_TO_VDPCOLOR(7, 7, 7), RGB3_3_3_TO_VDPCOLOR(7, 6, 5), RGB3_3_3_TO_VDPCOLOR(6, 5, 4),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 2), RGB3_3_3_TO_VDPCOLOR(6, 4, 1), RGB3_3_3_TO_VDPCOLOR(2, 2, 4), RGB3_3_3_TO_VDPCOLOR(0, 0, 1),
    0, 0, 0, 0, 0, 0, 0, 0
};

static const u16 gDesertPal1[16] =
{
    0, RGB3_3_3_TO_VDPCOLOR(6, 5, 2), RGB3_3_3_TO_VDPCOLOR(5, 4, 1), RGB3_3_3_TO_VDPCOLOR(7, 7, 4),
    RGB3_3_3_TO_VDPCOLOR(7, 5, 2), RGB3_3_3_TO_VDPCOLOR(3, 2, 1), RGB3_3_3_TO_VDPCOLOR(2, 2, 5), 0,
    0, 0, 0, 0, 0, 0, 0, 0
};

static const char *const gB612Codex[] =
{
    "B-612",
    "Line scroll curva o horizonte do asteroide.",
    "Paleta muda em ciclos de amanhecer para crepusculo.",
    "Hilight halo sugere luz limpa sem alpha nativo.",
    "O cachecol usa sinFix16 e atraso por segmento."
};

static const char *const gKingCodex[] =
{
    "Planeta do Rei",
    "BG_B anda devagar e BG_A intercala bandas para",
    "parecer mais de dois planos ao mesmo tempo.",
    "Column scroll move o palacio em colunas discretas.",
    "O objetivo aqui e legibilidade sem jitter."
};

static const char *const gLampCodex[] =
{
    "Planeta do Acendedor",
    "SYS_setHIntCallback troca parte da paleta no meio",
    "do frame para separar ceu e zona de lampiao.",
    "Line scroll local cria o ar quente da chama.",
    "Hilight halo da a sensacao de luz real."
};

static const char *const gDesertCodex[] =
{
    "Deserto das Estrelas",
    "Line scroll cria vento e miragem no horizonte.",
    "A viagem usa raios de estrela e escala predefinida.",
    "O DMA fica leve: quase nada de sprite fora do heroi.",
    "O foco e ritmo contemplativo e leitura limpa."
};

static const char *const gVainCodex[] =
{
    "Planeta do Vaidoso",
    "Placeholder: espelho e reflexo.",
    "Cena em desenvolvimento."
};

static const char *const gDrunkCodex[] =
{
    "Planeta do Bebado",
    "Placeholder: garrafa e circulo.",
    "Cena em desenvolvimento."
};

static const char *const gCounterCodex[] =
{
    "Planeta do Homem de Negocios",
    "Placeholder: livro de contas.",
    "Cena em desenvolvimento."
};

static const char *const gGeographerCodex[] =
{
    "Planeta do Geografo",
    "Placeholder: mapa e exploracao.",
    "Cena em desenvolvimento."
};

static const char *const gSnakeCodex[] =
{
    "Planeta da Serpente",
    "Placeholder: circulo e portal.",
    "Cena em desenvolvimento."
};

static const char *const gGardenCodex[] =
{
    "Jardim das Rosas",
    "Placeholder: canteiro e rosas.",
    "Cena em desenvolvimento."
};

static const char *const gWellCodex[] =
{
    "Poco no Deserto",
    "Placeholder: poco e aviador.",
    "Cena em desenvolvimento."
};

static const char *const gB612ReturnCodex[] =
{
    "B-612 (Retorno)",
    "O principe volta ao asteroide.",
    "O ciclo se fecha."
};

static const char *const gVainDialogueIntro[] =
{
    "Bata palmas! Eu sou esplendido!",
    "Veja como o espelho me conhece.",
    "Mas... voce ve algo alem do reflexo?",
    "Olhe mais fundo, por favor."
};

static const char *const gVainDialogueAfter[] =
{
    "O espelho mostrou a verdade.",
    "Nem tudo que brilha e so superficie.",
    "C abre o caminho — va em frente.",
    "Leve a coragem de olhar dentro."
};

static const char *const gDrunkDialogueIntro[] =
{
    "Bebo para esquecer... esquecer o que?",
    "O mundo gira, mas nao sai do lugar.",
    "Ha um circulo triste aqui dentro.",
    "Voce pode ver sem girar?"
};

static const char *const gDrunkDialogueAfter[] =
{
    "O giro parou um instante.",
    "Obrigado por olhar sem tontura.",
    "C te leva daqui — va reto.",
    "Reto e bonito quando se pode."
};

static const char *const gCounterDialogueIntro[] =
{
    "Quinhentos e um milhoes de estrelas.",
    "Todas minhas! Anotadas no livro.",
    "Mas... para que serve possuir?",
    "Voce sabe a resposta?"
};

static const char *const gCounterDialogueAfter[] =
{
    "O livro se fechou sozinho.",
    "Talvez as estrelas nao sejam de ninguem.",
    "C leva voce ao proximo planeta.",
    "Va — sem levar nada. E leve."
};

static const char *const gGeographerDialogueIntro[] =
{
    "Descreva-me o que viu la fora!",
    "Eu anoto tudo, mas nunca saio.",
    "Montanhas, rios, vulcoes — conte!",
    "Um explorador me faz falta."
};

static const char *const gGeographerDialogueAfter[] =
{
    "Anotei tudo no meu mapa.",
    "Agora o mundo e maior aqui dentro.",
    "C te leva alem do meu papel.",
    "Va — e me conte depois."
};

static const char *const gSnakeDialogueIntro[] =
{
    "Toco quem toco e volto a terra.",
    "O circulo fecha onde comeca.",
    "Voce procura caminho ou destino?",
    "Os dois moram no mesmo lugar."
};

static const char *const gSnakeDialogueAfter[] =
{
    "O circulo se desenhou sozinho.",
    "Voce entendeu sem ter medo.",
    "C te leva a Terra dos homens.",
    "La, tudo e mais complicado."
};

static const char *const gGardenDialogueIntro[] =
{
    "Somos todas iguais, dizemos.",
    "Mas uma rosa e diferente para voce.",
    "O que a faz unica nao e a forma.",
    "E o tempo que voce deu a ela."
};

static const char *const gGardenDialogueAfter[] =
{
    "Agora voce sabe a diferenca.",
    "Uma entre mil — e so sua.",
    "C te leva ao ultimo encontro.",
    "O essencial esta quase visivel."
};

static const char *const gWellDialogueIntro[] =
{
    "Desenha-me um carneiro.",
    "A agua esta la embaixo, no escuro.",
    "O essencial e invisivel aos olhos.",
    "So se ve bem com o coracao."
};

static const char *const gWellDialogueAfter[] =
{
    "A agua subiu — doce, clara.",
    "Voce encontrou o que procurava.",
    "C te leva de volta pra casa.",
    "A viagem mais longa e a de voltar."
};

static const char *const gB612ReturnDialogue[] =
{
    "Voce voltou.",
    "O por do sol te esperou.",
    "O cachecol lembra de tudo.",
    "Cuida do teu pequeno mundo."
};

static const char *const gB612DialogueIntro[] =
{
    "Cuida do teu pequeno mundo.",
    "O por do sol muda com teu passo.",
    "O vento desenha o cachecol.",
    "Quando ouvir isso, a rota abre."
};

static const char *const gB612DialogueAfter[] =
{
    "A rosa ja escutou teu passo.",
    "Agora voce le B-612 com calma.",
    "C abre a rota quando quiser.",
    "Leve esse cuidado adiante."
};

static const char *const gKingDialogueIntro[] =
{
    "Nem todo plano corre igual.",
    "Profundidade tambem e autoridade.",
    "Escute o eco entre frente e fundo.",
    "Quando o trono responder, siga."
};

static const char *const gKingDialogueAfter[] =
{
    "O palacio ja respira em camadas.",
    "Voce viu planos conversarem.",
    "C leva isso ao planeta da luz.",
    "Continue em frente."
};

static const char *const gLampDialogueIntro[] =
{
    "Acendo a noite linha por linha.",
    "A luz muda o mundo no meio.",
    "Veja o calor dancar na chama.",
    "Leve esse ritmo com voce."
};

static const char *const gLampDialogueAfter[] =
{
    "A chama agora divide ceu e terra.",
    "O raster achou o tempo certo.",
    "C segue ao deserto das estrelas.",
    "Va enquanto a luz ainda canta."
};

static const char *const gDesertDialogueIntro[] =
{
    "No deserto, o vento fala devagar.",
    "A miragem prepara a travessia.",
    "Olhe a leste e sinta a rota abrir.",
    "Quando o marco responder, siga."
};

static const char *const gDesertDialogueAfter[] =
{
    "O deserto aceitou teu silencio.",
    "A travessia termina quando quiser.",
    "C encerra este primeiro capitulo.",
    "As estrelas ja sabem teu caminho."
};

static void Planet_applyB612Scroll(GameContext *game)
{
    s16 line;
    s16 camera = (game->player.screenX - 160) >> 2;

    for (line = 40; line < 184; line++)
    {
        s16 depth = line - 76;
        if (depth > 0)
        {
            game->hscrollB[line] = -((game->stateTimer >> 2) + (depth >> 2));
            game->hscrollA[line] = camera - ((depth * depth) >> 8);
        }
        else
        {
            game->hscrollB[line] = -(game->stateTimer >> 3);
        }
    }
}

static void Planet_applyKingScroll(GameContext *game)
{
    s16 line;
    s16 col;

    for (line = 32; line < 184; line++)
    {
        if (line < 72) game->hscrollB[line] = -(game->stateTimer >> 3);
        else if (line < 112) game->hscrollB[line] = -(game->stateTimer >> 2) - ((line & 3) - 1);
        else game->hscrollB[line] = -(game->stateTimer >> 1) - ((line & 1) ? 2 : -2);

        game->hscrollA[line] = -((game->stateTimer >> 2) + ((line & 1) ? 1 : -1));
    }

    for (col = 8; col <= 11; col++)
    {
        game->vscrollA[col] = (sinFix16((game->frameCounter << 3) + (col * 48)) + 64) >> 5;
    }
}

static void Planet_applyLampScroll(GameContext *game)
{
    s16 line;

    for (line = 96; line < 176; line++)
    {
        s16 wave = (sinFix16((line << 3) + (game->frameCounter << 4)) + 64) >> 5;
        if ((line > 112) && (line < 160))
        {
            game->hscrollA[line] = wave;
        }
        game->hscrollB[line] = -(game->stateTimer >> 3);
    }
}

static void Planet_applyDesertScroll(GameContext *game)
{
    s16 line;

    for (line = 56; line < 184; line++)
    {
        s16 wave = sinFix16((line << 2) + (game->frameCounter << 3)) >> 4;
        game->hscrollB[line] = -((game->stateTimer >> 2) + (line >> 4));
        if (line > 120)
        {
            game->hscrollA[line] = wave;
        }
    }
}

static void Planet_drawB612Base(GameContext *game)
{
    const u16 *sky = gB612Cycle[(game->stateTimer >> 5) & 3];

    Render_beginScene(gB612Pal0, gB612Pal1);
    PAL_setColors(0, sky, 6, DMA_QUEUE);
    Render_drawSky(PP_TILE_DITHER, true, PAL0);
    VDP_setTileMapXY(BG_B, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, PP_TILE_SUN), 30, 6);
    Render_drawDisc(BG_A, 20, 19, 7, PP_TILE_GROUND, PP_TILE_HATCH, PAL1);
    VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, PP_TILE_TRACE), 19, 13);
    VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, PP_TILE_TRACE), 20, 14);
}

static void Planet_drawKingBase(void)
{
    s16 x;

    Render_beginScene(gKingPal0, gKingPal1);
    Render_drawSky(PP_TILE_PAPER, true, PAL0);

    for (x = 2; x < 38; x += 4)
    {
        VDP_setTileMapXY(BG_B, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, (x & 4) ? PP_TILE_DITHER : PP_TILE_HATCH), x, 8 + ((x >> 2) & 1));
        VDP_setTileMapXY(BG_B, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, PP_TILE_TRACE), x + 1, 9 + ((x >> 3) & 1));
    }

    Render_drawTower(18, 22, 9, PAL1);
    Render_drawBeacon(26, 21, PAL1);
}

static void Planet_drawLampBase(GameContext *game)
{
    Render_beginScene(gLampPal0Top, gLampPal1);
    PAL_setPalette(PAL0, game->lampLit ? gLampPal0BottomLit : gLampPal0BottomDark, DMA_QUEUE);
    PAL_setColors(0, gLampTop6, 6, DMA_QUEUE);
    Render_drawSky(PP_TILE_PAPER, true, PAL0);
    Render_drawDisc(BG_A, 20, 20, 6, PP_TILE_GROUND_ALT, PP_TILE_HATCH, PAL1);
    Render_drawBeacon(26, 21, PAL1);
}

static void Planet_drawDesertBase(void)
{
    Render_beginScene(gDesertPal0, gDesertPal1);
    Render_drawSky(PP_TILE_DITHER, true, PAL0);
    Render_drawDunes(18, PAL1);
    VDP_setTileMapXY(BG_B, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, PP_TILE_RING), 9, 8);
    VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, PP_TILE_TRACE), 30, 20);
    VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, PP_TILE_TRACE), 31, 21);
}

static void B612_enter(GameContext *game)
{
    game->lampLit = false;
    game->haloVisible = true;
    game->haloX = 238;
    game->haloY = 42;
    game->windStrength = 0;
    HintFx_disable();
    VDP_setHilightShadow(TRUE);
    Player_reset(game, PLANET_B612);
}

static void B612_input(GameContext *game, u16 pressed, u16 held)
{
    (void) held;

    if ((pressed & BUTTON_A) && Player_isNear(game, 160, 18))
    {
        if (!game->planetSolved[PLANET_B612])
        {
            game->planetSolved[PLANET_B612] = true;
            Audio_playSolveFx(PLANET_B612);
            Dialogue_open(game, "ROSA", gB612DialogueIntro, 4);
        }
        else
        {
            Dialogue_open(game, "ROSA", gB612DialogueAfter, 4);
        }

        Audio_playDialogueVoice(PLANET_B612);
    }

    if ((pressed & BUTTON_C) && game->planetSolved[PLANET_B612])
    {
        game->nextPlanet = PLANET_KING;
        Game_requestState(game, GAME_STATE_TRAVEL);
    }
}

static void B612_update(GameContext *game)
{
    game->windStrength = sinFix16((game->frameCounter << 3) & 1023) >> 5;
    game->haloX = 236 + ((sinFix16((game->frameCounter << 2) & 1023) + 64) >> 6);
    game->haloY = 42 + ((cosFix16((game->frameCounter << 2) & 1023) + 64) >> 7);
}

static void B612_draw(GameContext *game)
{
    Render_clearScroll(game);
    if (game->redrawScene)
    {
        Planet_drawB612Base(game);
        game->redrawScene = false;
    }
    PAL_setColors(0, gB612Cycle[(game->stateTimer >> 5) & 3], 6, DMA_QUEUE);
    Planet_applyB612Scroll(game);
}

static void B612_exit(GameContext *game)
{
    (void) game;
    HintFx_disable();
    VDP_setHilightShadow(FALSE);
}

static void King_enter(GameContext *game)
{
    game->haloVisible = false;
    game->windStrength = 1;
    HintFx_disable();
    VDP_setHilightShadow(FALSE);
    Player_reset(game, PLANET_KING);
}

static void King_input(GameContext *game, u16 pressed, u16 held)
{
    (void) held;

    if ((pressed & BUTTON_A) && Player_isNear(game, 160, 20))
    {
        if (!game->planetSolved[PLANET_KING])
        {
            game->planetSolved[PLANET_KING] = true;
            Audio_playSolveFx(PLANET_KING);
            Dialogue_open(game, "REI", gKingDialogueIntro, 4);
        }
        else
        {
            Dialogue_open(game, "REI", gKingDialogueAfter, 4);
        }

        Audio_playDialogueVoice(PLANET_KING);
    }

    if ((pressed & BUTTON_C) && game->planetSolved[PLANET_KING])
    {
        game->nextPlanet = PLANET_VAIDOSO;
        Game_requestState(game, GAME_STATE_TRAVEL);
    }
}

static void King_update(GameContext *game)
{
    game->windStrength = 1 + (sinFix16((game->frameCounter << 2) & 1023) >> 6);
}

static void King_draw(GameContext *game)
{
    Render_clearScroll(game);
    if (game->redrawScene)
    {
        Planet_drawKingBase();
        game->redrawScene = false;
    }
    Planet_applyKingScroll(game);
}

static void King_exit(GameContext *game)
{
    (void) game;
    HintFx_disable();
}

static void Lamp_enter(GameContext *game)
{
    game->lampLit = false;
    game->haloVisible = false;
    game->windStrength = 0;
    HintFx_configure(gLampTop6, gLampBottomDark6, 6, 95);
    VDP_setHilightShadow(TRUE);
    Player_reset(game, PLANET_ACENDEDOR);
}

static void Lamp_input(GameContext *game, u16 pressed, u16 held)
{
    (void) held;

    if ((pressed & BUTTON_A) && Player_isNear(game, 160, 18))
    {
        if (!game->planetSolved[PLANET_ACENDEDOR])
        {
            game->lampLit = true;
            game->planetSolved[PLANET_ACENDEDOR] = true;
            game->haloVisible = true;
            HintFx_configure(gLampTop6, gLampBottomLit6, 6, 95);
            game->redrawScene = true;
            Audio_playSolveFx(PLANET_ACENDEDOR);
            Dialogue_open(game, "ACENDEDOR", gLampDialogueIntro, 4);
        }
        else
        {
            Dialogue_open(game, "ACENDEDOR", gLampDialogueAfter, 4);
        }

        Audio_playDialogueVoice(PLANET_ACENDEDOR);
    }

    if ((pressed & BUTTON_C) && game->planetSolved[PLANET_ACENDEDOR])
    {
        game->nextPlanet = PLANET_GEOGRAFO;
        Game_requestState(game, GAME_STATE_TRAVEL);
    }
}

static void Lamp_update(GameContext *game)
{
    game->windStrength = 0;
    game->haloX = 154 + ((sinFix16((game->frameCounter << 4) & 1023) + 64) >> 6);
    game->haloY = 118;
}

static void Lamp_draw(GameContext *game)
{
    Render_clearScroll(game);
    if (game->redrawScene)
    {
        Planet_drawLampBase(game);
        game->redrawScene = false;
    }
    Planet_applyLampScroll(game);
}

static void Lamp_exit(GameContext *game)
{
    (void) game;
    HintFx_disable();
    VDP_setHilightShadow(FALSE);
}

static void Desert_enter(GameContext *game)
{
    game->haloVisible = false;
    game->windStrength = 1;
    HintFx_disable();
    VDP_setHilightShadow(FALSE);
    Player_reset(game, PLANET_DESERTO);
}

static void Desert_input(GameContext *game, u16 pressed, u16 held)
{
    (void) held;

    if ((pressed & BUTTON_A) && Player_isNear(game, 248, 20))
    {
        if (!game->planetSolved[PLANET_DESERTO])
        {
            game->planetSolved[PLANET_DESERTO] = true;
            Audio_playSolveFx(PLANET_DESERTO);
            Dialogue_open(game, "VENTO", gDesertDialogueIntro, 4);
        }
        else
        {
            Dialogue_open(game, "VENTO", gDesertDialogueAfter, 4);
        }

        Audio_playDialogueVoice(PLANET_DESERTO);
    }

    if ((pressed & BUTTON_C) && game->planetSolved[PLANET_DESERTO])
    {
        game->nextPlanet = PLANET_JARDIM;
        Game_requestState(game, GAME_STATE_TRAVEL);
    }
}

static void Desert_update(GameContext *game)
{
    game->windStrength = 1 + (sinFix16((game->frameCounter << 2) & 1023) >> 5);
}

static void Desert_draw(GameContext *game)
{
    Render_clearScroll(game);
    if (game->redrawScene)
    {
        Planet_drawDesertBase();
        game->redrawScene = false;
    }
    Planet_applyDesertScroll(game);
}

static void Desert_exit(GameContext *game)
{
    (void) game;
    HintFx_disable();
}

static void Generic_enter(GameContext *game, PlanetId id)
{
    game->haloVisible = false;
    game->windStrength = 1;
    HintFx_disable();
    VDP_setHilightShadow(FALSE);
    Player_reset(game, id);
}

static void Vain_enter(GameContext *game)
{
    Generic_enter(game, PLANET_VAIDOSO);
}

static void Vain_input(GameContext *game, u16 pressed, u16 held)
{
    (void) held;
    if ((pressed & BUTTON_A) && Player_isNear(game, 160, 18))
    {
        if (!game->planetSolved[PLANET_VAIDOSO])
        {
            game->planetSolved[PLANET_VAIDOSO] = true;
            Audio_playSolveFx(PLANET_VAIDOSO);
            Dialogue_open(game, "VAIDOSO", gVainDialogueIntro, 4);
        }
        else
        {
            Dialogue_open(game, "VAIDOSO", gVainDialogueAfter, 4);
        }
        Audio_playDialogueVoice(PLANET_VAIDOSO);
    }
    if ((pressed & BUTTON_C) && game->planetSolved[PLANET_VAIDOSO])
    {
        game->nextPlanet = PLANET_BEBADO;
        Game_requestState(game, GAME_STATE_TRAVEL);
    }
}

static void Vain_update(GameContext *game)
{
    game->windStrength = 1 + (sinFix16((game->frameCounter << 2) & 1023) >> 5);
}

static void Vain_draw(GameContext *game)
{
    Render_clearScroll(game);
    if (game->redrawScene)
    {
        Planet_drawDesertBase();
        game->redrawScene = false;
    }
    Planet_applyDesertScroll(game);
}

static void Vain_exit(GameContext *game)
{
    (void) game;
    HintFx_disable();
}

static void Drunk_enter(GameContext *game)
{
    Generic_enter(game, PLANET_BEBADO);
}

static void Drunk_input(GameContext *game, u16 pressed, u16 held)
{
    (void) held;
    if ((pressed & BUTTON_A) && Player_isNear(game, 160, 20))
    {
        if (!game->planetSolved[PLANET_BEBADO])
        {
            game->planetSolved[PLANET_BEBADO] = true;
            Audio_playSolveFx(PLANET_BEBADO);
            Dialogue_open(game, "BEBADO", gDrunkDialogueIntro, 4);
        }
        else
        {
            Dialogue_open(game, "BEBADO", gDrunkDialogueAfter, 4);
        }
        Audio_playDialogueVoice(PLANET_BEBADO);
    }
    if ((pressed & BUTTON_C) && game->planetSolved[PLANET_BEBADO])
    {
        game->nextPlanet = PLANET_HOMEM_NEG;
        Game_requestState(game, GAME_STATE_TRAVEL);
    }
}

static void Drunk_update(GameContext *game)
{
    game->windStrength = 1 + (sinFix16((game->frameCounter << 2) & 1023) >> 5);
}

static void Drunk_draw(GameContext *game)
{
    Render_clearScroll(game);
    if (game->redrawScene)
    {
        Planet_drawDesertBase();
        game->redrawScene = false;
    }
    Planet_applyDesertScroll(game);
}

static void Drunk_exit(GameContext *game)
{
    (void) game;
    HintFx_disable();
}

static void Counter_enter(GameContext *game)
{
    Generic_enter(game, PLANET_HOMEM_NEG);
}

static void Counter_input(GameContext *game, u16 pressed, u16 held)
{
    (void) held;
    if ((pressed & BUTTON_A) && Player_isNear(game, 160, 18))
    {
        if (!game->planetSolved[PLANET_HOMEM_NEG])
        {
            game->planetSolved[PLANET_HOMEM_NEG] = true;
            Audio_playSolveFx(PLANET_HOMEM_NEG);
            Dialogue_open(game, "CONTADOR", gCounterDialogueIntro, 4);
        }
        else
        {
            Dialogue_open(game, "CONTADOR", gCounterDialogueAfter, 4);
        }
        Audio_playDialogueVoice(PLANET_HOMEM_NEG);
    }
    if ((pressed & BUTTON_C) && game->planetSolved[PLANET_HOMEM_NEG])
    {
        game->nextPlanet = PLANET_ACENDEDOR;
        Game_requestState(game, GAME_STATE_TRAVEL);
    }
}

static void Counter_update(GameContext *game)
{
    game->windStrength = 1 + (sinFix16((game->frameCounter << 2) & 1023) >> 5);
}

static void Counter_draw(GameContext *game)
{
    Render_clearScroll(game);
    if (game->redrawScene)
    {
        Planet_drawDesertBase();
        game->redrawScene = false;
    }
    Planet_applyDesertScroll(game);
}

static void Counter_exit(GameContext *game)
{
    (void) game;
    HintFx_disable();
}

static void Geographer_enter(GameContext *game)
{
    Generic_enter(game, PLANET_GEOGRAFO);
}

static void Geographer_input(GameContext *game, u16 pressed, u16 held)
{
    (void) held;
    if ((pressed & BUTTON_A) && Player_isNear(game, 160, 20))
    {
        if (!game->planetSolved[PLANET_GEOGRAFO])
        {
            game->planetSolved[PLANET_GEOGRAFO] = true;
            Audio_playSolveFx(PLANET_GEOGRAFO);
            Dialogue_open(game, "GEOGRAFO", gGeographerDialogueIntro, 4);
        }
        else
        {
            Dialogue_open(game, "GEOGRAFO", gGeographerDialogueAfter, 4);
        }
        Audio_playDialogueVoice(PLANET_GEOGRAFO);
    }
    if ((pressed & BUTTON_C) && game->planetSolved[PLANET_GEOGRAFO])
    {
        game->nextPlanet = PLANET_SERPENTE;
        Game_requestState(game, GAME_STATE_TRAVEL);
    }
}

static void Geographer_update(GameContext *game)
{
    game->windStrength = 1 + (sinFix16((game->frameCounter << 2) & 1023) >> 5);
}

static void Geographer_draw(GameContext *game)
{
    Render_clearScroll(game);
    if (game->redrawScene)
    {
        Planet_drawDesertBase();
        game->redrawScene = false;
    }
    Planet_applyDesertScroll(game);
}

static void Geographer_exit(GameContext *game)
{
    (void) game;
    HintFx_disable();
}

static void Snake_enter(GameContext *game)
{
    Generic_enter(game, PLANET_SERPENTE);
}

static void Snake_input(GameContext *game, u16 pressed, u16 held)
{
    (void) held;
    if ((pressed & BUTTON_A) && Player_isNear(game, 160, 18))
    {
        if (!game->planetSolved[PLANET_SERPENTE])
        {
            game->planetSolved[PLANET_SERPENTE] = true;
            Audio_playSolveFx(PLANET_SERPENTE);
            Dialogue_open(game, "SERPENTE", gSnakeDialogueIntro, 4);
        }
        else
        {
            Dialogue_open(game, "SERPENTE", gSnakeDialogueAfter, 4);
        }
        Audio_playDialogueVoice(PLANET_SERPENTE);
    }
    if ((pressed & BUTTON_C) && game->planetSolved[PLANET_SERPENTE])
    {
        game->nextPlanet = PLANET_DESERTO;
        Game_requestState(game, GAME_STATE_TRAVEL);
    }
}

static void Snake_update(GameContext *game)
{
    game->windStrength = 1 + (sinFix16((game->frameCounter << 2) & 1023) >> 5);
}

static void Snake_draw(GameContext *game)
{
    Render_clearScroll(game);
    if (game->redrawScene)
    {
        Planet_drawDesertBase();
        game->redrawScene = false;
    }
    Planet_applyDesertScroll(game);
}

static void Snake_exit(GameContext *game)
{
    (void) game;
    HintFx_disable();
}

static void Garden_enter(GameContext *game)
{
    Generic_enter(game, PLANET_JARDIM);
}

static void Garden_input(GameContext *game, u16 pressed, u16 held)
{
    (void) held;
    if ((pressed & BUTTON_A) && Player_isNear(game, 160, 20))
    {
        if (!game->planetSolved[PLANET_JARDIM])
        {
            game->planetSolved[PLANET_JARDIM] = true;
            Audio_playSolveFx(PLANET_JARDIM);
            Dialogue_open(game, "ROSAS", gGardenDialogueIntro, 4);
        }
        else
        {
            Dialogue_open(game, "ROSAS", gGardenDialogueAfter, 4);
        }
        Audio_playDialogueVoice(PLANET_JARDIM);
    }
    if ((pressed & BUTTON_C) && game->planetSolved[PLANET_JARDIM])
    {
        game->nextPlanet = PLANET_POCO;
        Game_requestState(game, GAME_STATE_TRAVEL);
    }
}

static void Garden_update(GameContext *game)
{
    game->windStrength = 1 + (sinFix16((game->frameCounter << 2) & 1023) >> 5);
}

static void Garden_draw(GameContext *game)
{
    Render_clearScroll(game);
    if (game->redrawScene)
    {
        Planet_drawDesertBase();
        game->redrawScene = false;
    }
    Planet_applyDesertScroll(game);
}

static void Garden_exit(GameContext *game)
{
    (void) game;
    HintFx_disable();
}

static void Well_enter(GameContext *game)
{
    Generic_enter(game, PLANET_POCO);
}

static void Well_input(GameContext *game, u16 pressed, u16 held)
{
    (void) held;
    if ((pressed & BUTTON_A) && Player_isNear(game, 160, 20))
    {
        if (!game->planetSolved[PLANET_POCO])
        {
            game->planetSolved[PLANET_POCO] = true;
            Audio_playSolveFx(PLANET_POCO);
            Dialogue_open(game, "AVIADOR", gWellDialogueIntro, 4);
        }
        else
        {
            Dialogue_open(game, "AVIADOR", gWellDialogueAfter, 4);
        }
        Audio_playDialogueVoice(PLANET_POCO);
    }
    if ((pressed & BUTTON_C) && game->planetSolved[PLANET_POCO])
    {
        game->nextPlanet = PLANET_B612_RETORNO;
        Game_requestState(game, GAME_STATE_TRAVEL);
    }
}

static void Well_update(GameContext *game)
{
    game->windStrength = 1 + (sinFix16((game->frameCounter << 2) & 1023) >> 5);
}

static void Well_draw(GameContext *game)
{
    Render_clearScroll(game);
    if (game->redrawScene)
    {
        Planet_drawDesertBase();
        game->redrawScene = false;
    }
    Planet_applyDesertScroll(game);
}

static void Well_exit(GameContext *game)
{
    (void) game;
    HintFx_disable();
}

static void B612Return_enter(GameContext *game)
{
    game->lampLit = false;
    game->haloVisible = true;
    game->haloX = 238;
    game->haloY = 42;
    game->windStrength = 0;
    HintFx_disable();
    VDP_setHilightShadow(TRUE);
    Player_reset(game, PLANET_B612_RETORNO);
}

static void B612Return_input(GameContext *game, u16 pressed, u16 held)
{
    (void) held;
    if ((pressed & BUTTON_A) && Player_isNear(game, 160, 18))
    {
        game->planetSolved[PLANET_B612_RETORNO] = true;
        Audio_playSolveFx(PLANET_B612_RETORNO);
        Dialogue_open(game, "ROSA", gB612ReturnDialogue, 4);
        Audio_playDialogueVoice(PLANET_B612_RETORNO);
    }
    if ((pressed & BUTTON_C) && game->planetSolved[PLANET_B612_RETORNO])
    {
        game->nextPlanet = PLANET_COUNT;
        Game_requestState(game, GAME_STATE_TRAVEL);
    }
}

static void B612Return_update(GameContext *game)
{
    game->haloX = 238;
    game->haloY = 42 + ((cosFix16((game->frameCounter << 2) & 1023) + 64) >> 7);
}

static void B612Return_draw(GameContext *game)
{
    Render_clearScroll(game);
    if (game->redrawScene)
    {
        Planet_drawB612Base(game);
        game->redrawScene = false;
    }
    PAL_setColors(0, gB612Cycle[(game->stateTimer >> 5) & 3], 6, DMA_QUEUE);
    Planet_applyB612Scroll(game);
}

static void B612Return_exit(GameContext *game)
{
    (void) game;
    HintFx_disable();
    VDP_setHilightShadow(FALSE);
}

static const PlanetScene gScenes[PLANET_COUNT] =
{
    {
        PLANET_B612,
        "B-612",
        "Planeta-tutorial",
        "Fale com a rosa no centro do planeta.",
        "A rosa abriu a rota. C leva voce ao Rei.",
        "FX: line scroll curvo e paleta viva",
        "Cachecol dinamico com halo em hilight",
        "C viaja quando a cena estiver resolvida.",
        gB612Codex,
        5,
        { PP_SCROLL_LINE | PP_HILIGHT_MODE, 43, 960, 0, 0 },
        B612_enter, B612_input, B612_update, B612_draw, B612_exit
    },
    {
        PLANET_KING,
        "Planeta do Rei",
        "Profundidade e autoridade",
        "Aproxime-se do trono e aceite o peso do eco.",
        "O trono respondeu. C abre rota ao Vaidoso.",
        "FX: parallax multicamada interleaved",
        "Column scroll faz o palacio respirar",
        "C viaja quando o trono tiver respondido.",
        gKingCodex,
        5,
        { PP_SCROLL_LINE | PP_SCROLL_COLUMN | PP_INTERLEAVED_PLANES, 43, 1184, 0, 1 },
        King_enter, King_input, King_update, King_draw, King_exit
    },
    {
        PLANET_VAIDOSO,
        "Planeta do Vaidoso",
        "Espelho e reflexo",
        "A interaja com o espelho no centro.",
        "O espelho mostrou a verdade. C segue.",
        "FX: placeholder",
        "Cena em desenvolvimento",
        "C viaja quando o espelho responder.",
        gVainCodex,
        3,
        { PP_SCROLL_LINE, 43, 896, 0, 0 },
        Vain_enter, Vain_input, Vain_update, Vain_draw, Vain_exit
    },
    {
        PLANET_BEBADO,
        "Planeta do Bebado",
        "Garrafa e circulo",
        "A interaja com a garrafa no centro.",
        "O giro parou. C segue ao Homem de Negocios.",
        "FX: placeholder",
        "Cena em desenvolvimento",
        "C viaja quando a cena estiver resolvida.",
        gDrunkCodex,
        3,
        { PP_SCROLL_LINE, 43, 896, 0, 0 },
        Drunk_enter, Drunk_input, Drunk_update, Drunk_draw, Drunk_exit
    },
    {
        PLANET_HOMEM_NEG,
        "Planeta do Homem de Negocios",
        "Livro de contas",
        "A interaja com o livro no centro.",
        "O livro se fechou. C segue ao Acendedor.",
        "FX: placeholder",
        "Cena em desenvolvimento",
        "C viaja quando o livro responder.",
        gCounterCodex,
        3,
        { PP_SCROLL_LINE, 43, 896, 0, 0 },
        Counter_enter, Counter_input, Counter_update, Counter_draw, Counter_exit
    },
    {
        PLANET_ACENDEDOR,
        "Planeta do Acendedor",
        "Raster, tempo e luz",
        "A toque o lampiao para acender a noite.",
        "A chama esta viva. C segue ao Geografo.",
        "FX: H-Int troca paleta no meio do frame",
        "Heat wobble e halo limpo sem alpha",
        "C viaja quando o lampiao ficar aceso.",
        gLampCodex,
        5,
        { PP_SCROLL_LINE | PP_HINT_SPLIT | PP_HILIGHT_MODE, 43, 1120, 95, 0 },
        Lamp_enter, Lamp_input, Lamp_update, Lamp_draw, Lamp_exit
    },
    {
        PLANET_GEOGRAFO,
        "Planeta do Geografo",
        "Mapa e exploracao",
        "A interaja com o mapa no centro.",
        "Anotei tudo. C segue a Serpente.",
        "FX: placeholder",
        "Cena em desenvolvimento",
        "C viaja quando o mapa responder.",
        gGeographerCodex,
        3,
        { PP_SCROLL_LINE, 43, 896, 0, 0 },
        Geographer_enter, Geographer_input, Geographer_update, Geographer_draw, Geographer_exit
    },
    {
        PLANET_SERPENTE,
        "Planeta da Serpente",
        "Circulo e portal",
        "A interaja com o circulo na areia.",
        "O circulo se desenhou. C segue ao Deserto.",
        "FX: placeholder",
        "Cena em desenvolvimento",
        "C viaja quando o circulo responder.",
        gSnakeCodex,
        3,
        { PP_SCROLL_LINE, 43, 896, 0, 0 },
        Snake_enter, Snake_input, Snake_update, Snake_draw, Snake_exit
    },
    {
        PLANET_DESERTO,
        "Deserto das Estrelas",
        "Vento, miragem e travessia",
        "A observe o marco das estrelas a leste.",
        "O deserto respondeu. C segue ao Jardim.",
        "FX: vento em line scroll e palette shift",
        "Travel usa escala predefinida e baixo DMA",
        "C viaja quando a observacao terminar.",
        gDesertCodex,
        5,
        { PP_SCROLL_LINE, 43, 896, 0, 2 },
        Desert_enter, Desert_input, Desert_update, Desert_draw, Desert_exit
    },
    {
        PLANET_JARDIM,
        "Jardim das Rosas",
        "Canteiro e rosas",
        "A interaja com o canteiro no centro.",
        "Voce sabe a diferenca. C segue ao Poco.",
        "FX: placeholder",
        "Cena em desenvolvimento",
        "C viaja quando o canteiro responder.",
        gGardenCodex,
        3,
        { PP_SCROLL_LINE, 43, 896, 0, 0 },
        Garden_enter, Garden_input, Garden_update, Garden_draw, Garden_exit
    },
    {
        PLANET_POCO,
        "Poco no Deserto",
        "Poco e aviador",
        "A interaja com o poco no centro.",
        "A agua subiu. C volta pra casa.",
        "FX: placeholder",
        "Cena em desenvolvimento",
        "C viaja quando o poco responder.",
        gWellCodex,
        3,
        { PP_SCROLL_LINE, 43, 896, 0, 0 },
        Well_enter, Well_input, Well_update, Well_draw, Well_exit
    },
    {
        PLANET_B612_RETORNO,
        "B-612 (Retorno)",
        "O principe volta ao asteroide",
        "A fale com a rosa. C encerra a jornada.",
        "Voce voltou. C leva aos creditos.",
        "FX: line scroll curvo e paleta viva",
        "O ciclo se fecha",
        "C encerra a jornada.",
        gB612ReturnCodex,
        3,
        { PP_SCROLL_LINE | PP_HILIGHT_MODE, 43, 960, 0, 0 },
        B612Return_enter, B612Return_input, B612Return_update, B612Return_draw, B612Return_exit
    }
};

const PlanetScene *Planet_getScene(PlanetId id)
{
    if (id >= PLANET_COUNT)
    {
        return NULL;
    }

    return &gScenes[id];
}
