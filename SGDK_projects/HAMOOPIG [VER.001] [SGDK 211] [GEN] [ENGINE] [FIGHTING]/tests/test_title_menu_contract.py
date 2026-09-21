#!/usr/bin/env python3
"""Contrato estatico do menu de titulo.

ATENCAO ao que este teste NAO prova: ele le tokens no fonte, nao executa o
menu.  Navegacao, cursor e retorno de pagina foram verificados por captura com
input real (out/emulator_evidence/yd_pause, yd_240), nao aqui.

Atualizado no P02: a abertura saiu do titulo e virou cena propria, e as trocas
de cena passaram a ser SCENE_request.  Os tokens do desenho antigo
(TITLE_OPENING_FRAMES, TITLE_PHASE_OPENING, 'gRoom = 2') sumiram de proposito;
o que este teste guarda e a INTENCAO original, reescrita para o desenho atual.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    title = (ROOT / "src/title.c").read_text()
    main_c = (ROOT / "src/main.c").read_text()
    opening = (ROOT / "src/opening.c").read_text()
    globals_h = (ROOT / "inc/globals.h").read_text()
    config_h = (ROOT / "inc/config.h").read_text()
    config_c = (ROOT / "src/config.c").read_text()

    # 1. Itens do menu continuam existindo.
    for token in ('"START"', '"OPTION"', '"SFX ON"', '"SFX OFF"',
                  '"MUSIC ON"', '"MUSIC OFF"', '"SPCL ON"',
                  '"SOUND TEST"',
                  '"SPCL OFF"', '"HITS ON"', '"HITS OFF"',
                  '"RULES ON"', '"RULE FREE"', '"STG2 ON"',
                  '"STG2 OFF"', '"INTRO ON"', '"INTRO OFF"',
                  '"FADE ON"', '"FADE OFF"', '"TBG ON"', '"TBG OFF"',
                  '"BACK"', '"DEBUG"'):
        assert token in title, f"item de menu ausente: {token}"
    # O painel possui 18 colunas e cada glyph ocupa 2 colunas: nenhum rótulo
    # pode ultrapassar nove caracteres e ser truncado no framebuffer.
    for label in ('SFX ON', 'SFX OFF', 'MUSIC ON', 'MUSIC OFF', 'SOUND TEST', 'LIFE ON',
                  'LIFE OFF', 'CLOCK ON', 'CLOCK OFF', 'TBG ON', 'TBG OFF',
                  'TIME 60', 'TIME 99', 'TIME OFF', 'SPCL ON', 'SPCL OFF',
                  'HITS ON', 'HITS OFF', 'RULES ON', 'RULE FREE',
                  'STG2 ON', 'STG2 OFF', 'DEBUG', 'DEFAULTS', 'BACK'):
        assert len(label) <= 10, f"rotulo excede painel: {label}"
    for label in ('INTRO ON', 'INTRO OFF', 'FADE ON', 'FADE OFF'):
        assert len(label) <= 9, f"rotulo excede painel: {label}"

    # 2. Ciclo de vida do titulo, chamado pelo main.
    for token in ('FUNCAO_TITLE_INIT', 'FUNCAO_TITLE_UPDATE', 'FUNCAO_TITLE_EXIT',
                  'TITLE_PAGE_OPTIONS', 'KEY_PRESSED'):
        assert token in title, f"token de contrato ausente: {token}"
    assert '#include "title.h"' in main_c
    assert 'FUNCAO_TITLE_INIT();' in main_c
    assert 'FUNCAO_TITLE_UPDATE();' in main_c
    # P03: as preferencias de audio sairam de globals.h para GameConfig.
    assert 'audioSfx' in config_h and 'audioMusic' in config_h, \
        "as preferencias de audio devem viver em GameConfig"
    for token in ('hudSpecialBar', 'hudHitCount', 'specialRules', 'stage2Enabled',
                  'hudTimerBg', 'showOpening', 'useFade'):
        assert token in config_h and token in config_c, f"config sem {token}"
    assert 'gAudioSfxEnabled' not in globals_h, \
        "o global antigo de SFX voltou; ha duas fontes de verdade"

    # P03: defaults e validacao em um lugar so.
    for token in ('CONFIG_setDefaults', 'CONFIG_validate', 'CONFIG_freezeMatchRules'):
        assert token in config_h and token in config_c, f"config sem {token}"

    # P03: regra congelada na partida, nunca lida direto de gConfig na luta.
    hud_c = (ROOT / "src/hud.c").read_text()
    assert 'gMatchRules.timeLimit' in hud_c, \
        "a luta deve ler a regra congelada, nao gConfig"

    # P03: nenhum item de menu sem sistema por tras (plano, secao 3).
    for proibido in ('"STAGE COLOR"', '"STAGE MOTION"'):
        assert proibido not in title, \
            f"{proibido} nao tem sistema implementado; seria botao inerte"

    # OPENING e FADE possuem retorno observável pela seleção/pós-luta.
    select_c = (ROOT / "src/select.c").read_text()
    assert 'select_return_to_title' in select_c and 'SCENE_OPENING' in select_c
    assert 'key_JOY_B_status == KEY_PRESSED' in select_c
    assert 'gfx_select_surface' in select_c and 'VDP_setTileMapEx(BG_A' in select_c
    assert 'VDP_drawText("FIGHTER SELECT", 13, 2)' in select_c
    assert 'VDP_drawText("STAGE //", 12, 25)' in select_c
    assert 'gConfig.showOpening ? SCENE_OPENING : SCENE_TITLE' in main_c

    # 3. O titulo entrega o controle pelo gerenciador, nunca escrevendo gRoom.
    assert 'SCENE_request(SCENE_SELECT)' in title, \
        "o titulo deve pedir a cena de select pelo gerenciador"
    assert 'gRoom = 2' not in title and 'gRoom=2' not in title, \
        "o titulo voltou a escrever gRoom direto"

    # 4. Nada de avanco automatico no bloco do titulo em main.c.
    # Tolerante a espacos: o fonte mistura 'gRoom==X' e 'gRoom == X'.
    def bloco(desde, ate):
        i = re.search(r'gRoom\s*==\s*' + desde, main_c)
        j = re.search(r'gRoom\s*==\s*' + ate, main_c)
        assert i and j, f'nao achei o bloco {desde}..{ate} em main.c'
        return main_c[i.end():j.start()]

    title_block = bloco('SCENE_TITLE', 'SCENE_SELECT')
    assert 'gFrames>=60*2' not in title_block
    assert 'SCENE_request' not in title_block, \
        "o bloco do titulo em main.c nao deve trocar de cena; quem decide e title.c"

    # 5. O menu so fica ativo depois de carregar e revelar.  Era o papel do
    #    TITLE_PHASE_OPENING antigo; agora sao duas fases explicitas.
    for token in ('TITLE_PHASE_LOADING', 'TITLE_PHASE_FADE_IN', 'TITLE_PHASE_ACTIVE',
                  'TITLE_PHASE_FADE_OUT'):
        assert token in title, f"fase de titulo ausente: {token}"
    assert 'sTitlePhase = TITLE_PHASE_LOADING;' in title, \
        "FUNCAO_TITLE_INIT deve reentrar pela fase de carga"
    assert 'TITLE_PANEL_W, sPanelH, TITLE_PANEL_W,' in title and 'sTitleInitialCommit ? DMA' in title, \
        "o mapa inicial do título deve terminar antes do fade"
    assert 'sTitleInitialCommit ? DMA : CPU' in title, \
        "páginas posteriores devem evitar duas DMAs síncronas consecutivas"
    assert 'VDP_waitDMACompletion();' in title, \
        "a restauração do artwork deve terminar antes da escrita CPU do painel"
    assert 'sMainSelectionLatched' in title and 'if(sMainSelectionLatched == TITLE_MAIN_START)' in title, \
        "a confirmação deve usar a seleção principal latched"
    assert 'sTitlePageInputLock = 2' in title and 'if(sTitlePageInputLock > 0)' in title, \
        "a troca de página deve consumir a borda sem cascata"
    assert 'PAL_fadeOutAll(8, TRUE)' in title and 'PAL_isDoingFade()' in title, \
        "START deve aguardar o fade de saida antes de limpar o VDP"
    assert 'sTitlePhase == TITLE_PHASE_FADE_OUT' in title and \
           'FUNCAO_TITLE_EXIT();' in title, \
        "a troca para o seletor deve ocorrer somente ao concluir o fade"
    assert 'title_scene' in title, \
        "o titulo deve possuir uma composicao de fundo propria"
    assert 'VDP_clearPlane(BG_B, TRUE);' in title, \
        "a carga do titulo deve limpar o tilemap da abertura antes do novo fundo"

    # 6. Separacao P02: a abertura nao pode ter voltado para dentro do titulo.
    assert 'TITLE_OPENING_FRAMES' not in title, \
        "a abertura voltou a viver dentro do titulo"
    assert 'FUNCAO_OPENING_UPDATE' in opening and 'SCENE_request(SCENE_TITLE)' in opening, \
        "a abertura deve ser cena propria e entregar o controle ao titulo"

    # 7. O fade do titulo tem de cobrir as quatro paletas.  Deixar PAL1 zerada
    #    apagava as letras do painel -- medido em p02_t4/t7/t12.
    assert 'palette[16]' in title, \
        "o fade do titulo precisa carregar PAL1, senao o texto do menu fica preto"

    print("PASS: itens do menu, ciclo de vida, entrega via gerenciador, sem auto-advance, "
          "fases de carga/fade/ativo, abertura separada e PAL1 no fade")


if __name__ == "__main__":
    main()
