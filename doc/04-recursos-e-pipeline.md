# 04 - Recursos e Pipeline — __PROJECT_NAME__

## Formatos Obrigatorios

- **Sprites**: PNG (8-bit indexado), multiplos de 8x8. Transparencia no Index 0.
- **Backgrounds**: PNG (8-bit indexado), maximo 15 cores por camada.
- **Audio**:
  - Musica: XGM2 (driver de 4 canais PCM + FM).
  - SFX: WAV (Mono, 8-bit ou 16-bit, 11-22kHz).

## Pipeline de Conversao

1. Criar arte em ferramenta externa (Aseprite/Photoshop).
2. Validar paletas em `res/`.
3. Adicionar entrada em `res/resources.res`.
4. Compilar via `build.bat` (ResComp processa automaticamente).

## Limites Tecnicos

- Maximo de 16 sprites internos por scanline (VDP Limit).
- Maximo de 64 sprites totais na tela (VDP Limit).

## Estrutura sugerida

- `res/gfx/`
- `res/ui/`
- `res/audio/`
