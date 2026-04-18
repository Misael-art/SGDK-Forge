# Memory Bank — Pequeno Príncipe: Crônicas das Estrelas VER.002

## Identidade do Projeto

- **Nome:** Pequeno Príncipe: Crônicas das Estrelas
- **Versão:** VER.002
- **Plataforma:** Sega Mega Drive / Genesis
- **SDK:** SGDK 2.11
- **Gênero:** Aventura Contemplativa
- **Status geral:** `implementado` (estrutura completa), `buildado` (pendente), `testado_em_emulador` (pendente)

---

## Estado atual da sessão

- Arquitetura VER.002 desenhada do zero com qualidade elite
- Todos os ficheiros de código criados
- Art: Cenário 3 (sem arte) — aguarda bible artística e geração de assets
- Build: pendente execução

---

## Decisões arquiteturais principais

### 1. FSM de 8 estados
```
BOOT → TITLE → INTRO → PLANET → TRAVEL → PAUSE → CODEX → CREDITS
```
- Estado armazenado em `GameCtx.state` / `GameCtx.nextState`
- Transições via `Engine_requestState()`
- Cada estado tem `enter()`, `update()`, `draw()`, `exit()` separados

### 2. VBlank callback
- `vblank.c` implementa callback único registrado com `SYS_setVBlankCallback`
- Cola hscroll/vscroll via DMA a partir dos buffers `ctx.hscrollA[224]`, `ctx.vscrollA[20]`
- Garante scroll suave sem tearing

### 3. Física fix32
- Gravidade: `FIX32(0.25)` por frame
- Velocidade máxima queda: `FIX32(5.0)`
- Glide (A): reduz gravidade para `FIX32(0.06)`, adiciona flutuação
- Cachecol: 5 segmentos com spring chain `sinFix16` — sem float

### 4. Sistema de diálogo
- Speaker name no alto da caixa, cor por personagem
- Máximo 4 linhas por falas
- Input A/C avança, START pula para fim
- Typewriter character-by-character (16 chars/frame)

### 5. H-Int para split de tela
- Linha 176: split entre planeta e HUD (Window Plane 28 linhas = 7px margin)
- Acima da linha: scrolling normal com line scroll
- HUD sempre fixo (Window Plane)

### 6. Parallax multicamada (Planeta Rei)
- Plano A: foreground (coluna scroll individual por tile coluna)
- Plano B: background sky com hscroll line
- 3 camadas simuladas com velocidades diferentes no mesmo plano B

### 7. Pseudo-3D Travel A
- Floor: hscroll line por linha, convergência em horizonte y=112
- Estrelas: sprites pequenos com escala por Z (tabela pré-computada)
- Velocidade perspectiva: `scale = 256 / (z - cameraZ)` com inteiros

### 8. XGM2 Audio
- `audio.c` wrappa XGM2_play, XGM2_playPCM, XGM2_fadeIn, XGM2_fadeOut
- Tema por planeta (12 temas distintos)
- SFX de interação e diálogo
- Fade automático em transitions

---

## Budget VRAM (global)

| Região | Tiles | Uso |
|--------|-------|-----|
| Plano A (40×28) | 1120 tiles | scrolling foreground |
| Plano B (64×32) | 2048 tiles ref | scrolling background |
| Window (40×28) | 1120 tiles | HUD fixo |
| Sprites | 128 slots HW | player + NPC + FX |
| TILE_USER_INDEX | 1344 livres | tilesets de jogo |
| Palettas | 4×16 cores | PAL0-PAL3 |

Budget por cena limitado em `spec-cenas.md`.

---

## Sprites (Player)

| Frame | Descrição |
|-------|-----------|
| 0 | Idle frame 1 |
| 1 | Idle frame 2 |
| 2 | Walk 1 |
| 3 | Walk 2 |
| 4 | Walk 3 |
| 5 | Walk 4 |
| 6 | Jump / Glide |
| 7 | Land |

Cachecol: 5 sprites separados 8×8, paleta PAL1.

---

## Progressão (12 planetas + 11 viagens)

```
B-612 → Travel A → Rei → Travel B → Vaidoso → Travel C →
Bêbado → Travel D → Homem Neg. → Travel E → Acendedor →
Travel F → Geógrafo → Travel G → Serpente → Travel H →
Deserto → Travel I → Jardim → Travel J → Poço →
Travel K → B-612 Retorno
```

---

## Audio Inventory

| ID | Tipo | Descrição |
|----|------|-----------|
| BGM_TITLE | XGM2 | Tema título — suave, contemplativo |
| BGM_B612 | XGM2 | B-612 — vento, melancolia |
| BGM_REI | XGM2 | Rei — orquestral pomposo |
| BGM_TRAVEL | XGM2 | Viagem espacial — ambient |
| SFX_STEP | PCM | Passos no solo |
| SFX_JUMP | PCM | Salto do Príncipe |
| SFX_INTERACT | PCM | Interação/diálogo ding |
| SFX_SOLVE | PCM | Planeta resolvido — chime |
| SFX_TRAVEL_LAUNCH | PCM | Launch da viagem |

---

## Referências visuais (Bible Artística VER.002)

1. **Panzer Dragoon Saga (Saturn)** → paleta etérea, degradês de céu
2. **Wonder Boy in Monster World (MD)** → proporção do herói, expressividade
3. **Phantasy Star IV (MD)** → tiles de fundo, skylines detalhados
4. **Sonic 3 (MD)** → velocidade e fluidez de scroll, water level look
5. **Comix Zone (MD)** → uso criativo de cores limitadas, outlines fortes

---

## Handoff

Última sessão: criação do projeto VER.002 do zero.
Próxima sessão: executar build, diagnosticar arte (cenário 3), criar bible artística e assets.
