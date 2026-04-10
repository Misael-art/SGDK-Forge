# 04 - Recursos e Pipeline — BENCHMARK_VISUAL_LAB [VER.001] [SGDK 211] [GEN] [TOOL] [TEST]

## Formatos Obrigatorios

- **Sprites**: PNG (8-bit indexado), multiplos de 8x8. Transparencia no Index 0.
- **Backgrounds**: PNG (8-bit indexado), maximo 15 cores por camada.
- **Audio**:
  - Musica: XGM2 (driver de 4 canais PCM + FM).
  - SFX: WAV (Mono, 8-bit ou 16-bit, 11-22kHz).

## Pipeline de Conversao

1. Criar arte em ferramenta externa (Aseprite/Photoshop).
2. Colocar os brutos em `res/data/`, mantendo as subpastas desejadas.
3. Deixar o wrapper espelhar e converter automaticamente para `res/`.
4. Se um arquivo final antigo precisar ser substituido, o backup vai para `res/data/backup/`.
5. Adicionar entrada em `res/resources.res`.
6. Compilar via `build.bat` (ResComp processa automaticamente).

## Limites Tecnicos

- Maximo de 16 sprites internos por scanline (VDP Limit).
- Maximo de 64 sprites totais na tela (VDP Limit).

## Estrutura sugerida

- `res/data/`
- `res/data/backup/`
- `res/gfx/`
- `res/ui/`
- `res/audio/`

