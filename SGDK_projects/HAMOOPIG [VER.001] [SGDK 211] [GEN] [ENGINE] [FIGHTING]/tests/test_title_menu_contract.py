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

    # 1. Itens do menu continuam existindo.
    for token in ('"START"', '"OPTION"', '"SFX ON"', '"SFX OFF"',
                  '"MUSIC ON"', '"MUSIC OFF"', '"BACK"', '"DEBUG"'):
        assert token in title, f"item de menu ausente: {token}"

    # 2. Ciclo de vida do titulo, chamado pelo main.
    for token in ('FUNCAO_TITLE_INIT', 'FUNCAO_TITLE_UPDATE', 'FUNCAO_TITLE_EXIT',
                  'TITLE_PAGE_OPTIONS', 'KEY_PRESSED'):
        assert token in title, f"token de contrato ausente: {token}"
    assert '#include "title.h"' in main_c
    assert 'FUNCAO_TITLE_INIT();' in main_c
    assert 'FUNCAO_TITLE_UPDATE();' in main_c
    assert 'gAudioSfxEnabled' in globals_h
    assert 'gAudioMusicEnabled' in globals_h

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
    for token in ('TITLE_PHASE_LOADING', 'TITLE_PHASE_FADE_IN', 'TITLE_PHASE_ACTIVE'):
        assert token in title, f"fase de titulo ausente: {token}"
    assert 'sTitlePhase = TITLE_PHASE_LOADING;' in title, \
        "FUNCAO_TITLE_INIT deve reentrar pela fase de carga"

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
