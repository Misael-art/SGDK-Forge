# HAMOOPIG [VER.1.0] - Engine Architecture Nodes

Technical lifecycle and architectural mapping of the SGDK-based fighting engine.

## 1. Hardware & System Setup (Node: INIT)

Initial configuration of the Mega Drive hardware and SGDK global systems.

- **SYS_init()**: Initializes the system and sets core timers.
- **VDP_init()**: Sets screen mode to **H40 (320x224)**.
- **SPR_init()**: Allocates the Sprite Engine buffer.
- **VDP_setPlaneSize(64, 64)**: Configures the background planes.

---

## 2. Global State Controller (Node: ROOM_MANAGER)

The execution flow is divided into `gRoom` states to manage transitions between screens.

| Room ID | Purpose | Key Operations |
|:---:|:---|:---|
| **1** | Intro Screen | `SND_haohmaru_intro`, `VDP_drawImage`. |
| **2** | Presentation | `SPR_addSprite(Logo)`, `gFrames` counter. |
| **3** | Char Select | `SPR_setPosition(Cursor)`, `P[i].id` assignment. |
| **4** | Stage Select | `VDP_setPalette(Background)`, `gStage` ID. |
| **9** | Decompression | Animation loop while loading heavy resources. |
| **10** | **In-Game (Fight)** | **Core Engine Execution Loop.** |
| **11** | Post-Match | Winner display, `wins` update, `gRoom=3` reset. |

---

## 3. Fighting Engine Core (Node: CORE_V1.0)

Inside `gRoom == 10`, the engine processes the fighter lifecycle every frame.

### 3.1 Input System (Node: INPUT)
- **`FUNCAO_INPUT_SYSTEM()`**: Reads `JOY_1` and `JOY_2`.
- **State Logic**: Detects `Pressed`, `Hold`, and `Released` states for all buttons.
- **Buffer**: Fills `inputArray` for motion command detection.

### 3.2 Finite State Machine (Node: FSM)
- **`FUNCAO_FSM()`**: Processes fighter transitions.
- **Collision Engine**: Uses `FUNCAO_COLISAO(HBox, BBox)` to detect hits.
- **State Switcher**: `PLAYER_STATE(Player, NewState)` updates animation, hitboxes, and physics properties.

### 3.3 Physics & Gravity (Node: PHYSICS)
- **Gravity**: Global `gravidadePadrao` applied to `P[i].y` when the player is airborne.
- **Impulse**: `impulsoPadrao` applied to `P[i].y` during jumps or blowbacks.
- **Floor Detection**: `gAlturaPiso` (typically 200) serves as the ground plane.

### 3.4 Animation & Visuals (Node: SPRITE)
- **`FUNCAO_ANIMACAO()`**: Increments `frameTimeAtual`. Switches `animFrame` when `frameTimeTotal` is reached.
- **`FUNCAO_SPR_POSITION()`**: Adjusts sprite coordinates factoring in `axisX` and `axisY` (hotspots).
- **VDP Update**: `SPR_update()` sends SPR data to SAT during VBlank.

### 3.5 HUD & Utilities (Node: UI)
- **`FUNCAO_RELOGIO()`**: Manages the match timer (99-00).
- **`FUNCAO_BARRAS_DE_ENERGIA()`**: Interpolates health bars (`energiaBase`) for a smooth drainage effect.

---

## 4. Technical Resources

- **VRAM Slotting**:
  - `gRoom 10` carefully manages `SPR_setVRAMTileIndex` to avoid collisions between Player 1 and Player 2 sprites in VRAM.
- **Sound (XGM)**:
  - **Channel 3**: Reserved for P1 SFX.
  - **Channel 4**: Reserved for P2 SFX.
  - **Music**: Background music played via `XGM_startPlay()`.

---

## 5. Maintenance Nodes (Node: DEBUG)

- **`gDebug` Mode**: Enabled via **MODE + START**.
- **Hitbox Visualization**: Uses `VDP_drawText` and placeholder sprites (Rect1HB1, etc.) to show collision boxes in real-time.
