# pipeline de Recursos - __PROJECT_NAME__

## Formatos Obrigatórios
- **Sprites**: PNG (8-bit indexado), múltiplos de 8x8. Transparência no Index 0.
- **Backgrounds**: PNG (8-bit indexado), máximo 15 cores por camada.
- **Áudio**: 
    - Música: XGM2 (driver de 4 canais PCM + FM).
    - SFX: WAV (Mono, 8-bit ou 16-bit, 11-22kHz).

## Pipeline de Conversão
1. Criar arte em ferramenta externa (Aseprite/Photoshop).
2. Validar paletas em `res/`.
3. Adicionar entrada em `res/resources.res`.
4. Compilar via `build.bat` (ResComp processa automaticamente).

## Limites Técnicos
- Máximo de 16 sprites internos por scanline (VDP Limit).
- Máximo de 64 sprites totais na tela (VDP Limit).
