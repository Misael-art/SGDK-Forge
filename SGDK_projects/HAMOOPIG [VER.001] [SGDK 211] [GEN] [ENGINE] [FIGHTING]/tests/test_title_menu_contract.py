#!/usr/bin/env python3
"""Static contract for the title menu state machine."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    title = (ROOT / "src/title.c").read_text()
    main_c = (ROOT / "src/main.c").read_text()
    globals_h = (ROOT / "inc/globals.h").read_text()
    required = (
        '"START"', '"OPTION"', '"SFX ON"', '"SFX OFF"',
        '"MUSIC ON"', '"MUSIC OFF"', '"BACK"',
        'FUNCAO_TITLE_INIT', 'FUNCAO_TITLE_UPDATE', 'FUNCAO_TITLE_EXIT',
        'TITLE_PAGE_OPTIONS', 'TITLE_OPENING_FRAMES', 'TITLE_PHASE_OPENING',
        'KEY_PRESSED', 'gRoom = 2',
    )
    for token in required:
        assert token in title, f"missing title contract token: {token}"
    assert '#include "title.h"' in main_c
    assert 'FUNCAO_TITLE_INIT();' in main_c
    assert 'FUNCAO_TITLE_UPDATE();' in main_c
    assert 'gAudioSfxEnabled' in globals_h
    assert 'gAudioMusicEnabled' in globals_h
    # The old unconditional two-second jump must not return.
    title_block = main_c.split('if(gRoom==1)', 1)[1].split('if(gRoom==2)', 1)[0]
    assert 'gFrames>=60*2' not in title_block
    assert 'gRoom=2;' not in title_block
    assert 'sTitlePhase = TITLE_PHASE_OPENING;' in title
    print("PASS: title menu contract, options, input gate, and no auto-advance")


if __name__ == "__main__":
    main()
