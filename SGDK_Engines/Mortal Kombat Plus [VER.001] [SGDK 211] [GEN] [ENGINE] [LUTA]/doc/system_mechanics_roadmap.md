# System Mechanics Roadmap - Mortal Kombat Plus

Technical roadmap of the Character Selection System and Navigation Logic.

## 1. System Mind Map: Character selection (ASCII)

```ascii
[ Módulo: Seleção de Personagens ]
 ├── Efeito Persiana (Venetian Blinds)
 │    ├── Design: Revelação em tiras horizontais ao carregar sala.
 │    ├── Lógica: if (gFrames == 20) -> check VenetianBlindsEffect[7]
 │    └── Execução: VDP_setHorizontalScrollLine() -> XGM2_playPCMEx(snd_gongo)
 │
 ├── Navegação em Grid (DPAD)
 │    ├── Design: Cursor move entre retratos (SubZero, Kano, Raiden, etc).
 │    ├── Lógica: if (player[ind].key_JOY_LEFT_status == 1) -> update ID
 │    └── Execução: SPR_setPosition(GE[ind].sprite) -> playCursor()
 │
 ├── Confirmação de Escolha (START)
 │    ├── Design: Pisca retrato e toca voz do locutor.
 │    ├── Lógica: if (player[ind].key_JOY_START_status > 0) -> selecionado = TRUE
 │    └── Execução: XGM2_playPCMEx(loc_jc, size) -> SPR_setAnim(GE[ind+2].sprite)
 │
 └── Transição para Combate
      ├── Design: Fade out coletivo quando ambos jogadores confirmam.
      ├── Lógica: if (player[0].selecionado && player[1].selecionado) -> wait countDown
      └── Execução: PAL_fadeOutAll(18) -> exit() -> gRoom = PALACE_GATES
```

## 2. Technical System Breakdown

### Level 1: Visual Design
- **Animation**: Sprites interact with custom tilesets (BGA/BGB) using `VDP_setTileMapEx`.
- **Feedback**: Immediate visual response on d-pad input via `SPR_setPosition`.

### Level 2: Variables & Rules
- **`gPodeMover`**: Boolean flag in `game_vars.c` used to block input during screen transitions.
- **`selectorBlinkTimer`**: Counter for the blinking effect on confirmation.
- **`OPTIONS_X/Y`**: Fixed coordinate arrays for portraits.

### Level 3: Execution (C Functions)
- **`inputSystem()`**: Core input abstraction located in `input_system.c`.
- **`SPR_update()`**: Global VDP sprite push at the end of each frame.
- **`XGM2_playPCMEx()`**: High-quality voice sample playback for names.

## 3. Global Triggers & Audio
- **Sound Effects**: `snd_gongo` (Gong on load), `snd_cursor` (Navigation tick).
- **Music**: `mus_select_player` (XGM2 background track).
- **Save/Load**: Initial stats (e.g., `player[0].id = JOHNNY_CAGE`) are reset in `main.c` but persists through room transitions.
