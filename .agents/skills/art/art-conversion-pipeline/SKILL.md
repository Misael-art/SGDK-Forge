---
name: art-conversion-pipeline
description: Use quando assets visuais ja existem e precisam ser convertidos ou corrigidos para o padrao SGDK / Mega Drive em /data ou /res. Cobre quantizacao de paleta, grid 8x8, indexacao, transparencia, spec JSON e ferramentas de conversao. Nao use para diagnosticar o cenario inicial do projeto, criar arte do zero, buscar assets externos, ou fazer traducao interpretativa de uma imagem-fonte high-res que pede preservacao de alma visual; nesse caso use `art-translation-to-vdp`.
---

# Art Conversion Pipeline

Use esta skill quando o projeto tiver assets brutos em `/data` ou assets inadequados em `/res` que precisam ser convertidos para o padrao SGDK.

---

## Visao geral do pipeline

```
data/ (bruto)
  │
  ├─ 1. DIAGNOSTICO ──── art_diagnostic.py ──→ relatorio de issues
  │
  ├─ 2. PRE-PROCESSAMENTO
  │      ├─ Redimensionar para multiplos de 8
  │      ├─ Quantizar para max 15 cores + 1 transparente
  │      └─ Corrigir transparencia (#FF00FF como index 0)
  │
  ├─ 3. CONVERSAO
  │      ├─ ROTA GUI: photo2sgdk.exe  (controle visual preciso)
  │      └─ ROTA CLI: batch_resize_index.py  (lote automatizado)
  │
  ├─ 4. VALIDACAO
  │      ├─ art_diagnostic.py (verificar resultado)
  │      └─ validate_resources.ps1 (verificar integracao SGDK)
  │
  └─ 5. PROMOCAO → res/  (copia para diretorio final)
```

---

## Ferramentas disponíveis

| Ferramenta | Caminho | Uso |
|------------|---------|-----|
| `photo2sgdk.exe` | `tools/photo2sgdk/run.bat` | GUI interativa — melhor para ajuste fino de paleta |
| `batch_resize_index.py` | `tools/image-tools/` | CLI lote — melhor para muitos assets com spec definido |
| `fix_png_transparency_final.py` | `tools/image-tools/` | Corrigir transparencia em PNGs existentes |
| `mergePaletteSGDK.py` | `tools/paletteMergerForSGDK-main/` | Combinar paletas de multiplos assets |
| `ImageMagick` | `tools/ImageMagick/` | Manipulacao geral de imagens |
| `autofix_sprite_res.ps1` | `tools/sgdk_wrapper/` | Corrigir .res automaticamente |
| `validate_resources.ps1` | `tools/sgdk_wrapper/` | Validar assets antes do build |

---

## ROTA GUI: photo2sgdk

**Quando usar:** controle preciso de paleta, assets individuais importantes, sprites de personagens principais.

```bat
call tools\photo2sgdk\run.bat
```

**Fluxo no photo2sgdk:**
1. Carregar imagem (PNG, JPEG, BMP)
2. Definir dimensoes alvo (multiplo de 8)
3. Reduzir paleta para 15 cores + transparente
4. Ajustar manualmente cores criticas (olhos, contornos, destaques)
5. Verificar grid 9-bits no painel de paleta
6. Exportar como PNG indexado para `res/sprite/` ou `res/gfx/`
7. Conferir entrada `.res` sugerida

**Quando o photo2sgdk e obrigatorio:**
- Sprite principal do jogador
- Boss sprites (identificacao visual critica)
- Cenarios com historia visual especifica (bible artistica)

---

## ROTA CLI: batch_resize_index.py

**Quando usar:** muitos assets (5+), tiles de cenario, lotes de sprites secundarios.

### Passo 1 — Criar spec JSON

```json
{
  "production": [
    {
      "name": "player_idle",
      "png_rel": "production/player_idle.png",
      "w": 32,
      "h": 32,
      "bmp_rel": "indexed/player_idle.bmp",
      "bmp_w": 32,
      "bmp_h": 32,
      "transparency": true
    },
    {
      "name": "enemy_walk",
      "png_rel": "production/enemy_walk.png",
      "w": 24,
      "h": 32,
      "bmp_rel": "indexed/enemy_walk.bmp",
      "bmp_w": 24,
      "bmp_h": 32,
      "transparency": true
    }
  ],
  "boards": [
    { "rel": "boards/stage1_bg.png", "w": 320, "h": 224 }
  ]
}
```

**Regras para o spec:**
- `w` e `h` DEVEM ser multiplos de 8
- `transparency: true` para sprites (index 0 sera transparente)
- `transparency: false` para backgrounds e tilesets sem transparencia
- `bmp_w`/`bmp_h` iguais a `w`/`h` na maioria dos casos

### Passo 2 — Organizar arquivos

```
data/
  production/
    player_idle.png    ← assets brutos aqui
    enemy_walk.png
  boards/
    stage1_bg.png
  indexed/              ← sera criado automaticamente
```

### Passo 3 — Executar conversao

```bash
python tools/image-tools/batch_resize_index.py \
  --spec tools/image-tools/specs/<projeto>_spec.json \
  --batch-root "<caminho_do_projeto>/data"
```

### Passo 4 — Corrigir transparencia se necessario

```bash
python tools/image-tools/fix_png_transparency_final.py "<caminho_do_projeto>/data"
```

---

## PALETA: garantindo qualidade maxima

### Grid 9-bits obrigatorio

Cada canal (R, G, B) deve ser multiplo de 0x22:

| Nivel | Hex | Decimal |
|-------|-----|---------|
| 0     | 00  | 0       |
| 1     | 22  | 34      |
| 2     | 44  | 68      |
| 3     | 66  | 102     |
| 4     | 88  | 136     |
| 5     | AA  | 170     |
| 6     | CC  | 204     |
| 7     | EE  | 238     |

**Dica:** O VDP trunca os 5 bits menos significativos. Uma cor `#FF6600` vira `#EE6600`. Projete cores JA no grid para precisao maxima.

### Distribuicao de paleta recomendada (15 cores)

Para sprite de personagem de alto padrao (referencia: Sonic, Comix Zone, Streets of Rage):

```
Index 0:  Transparente (#FF00FF no PNG fonte)
Index 1:  Contorno principal (preto ou cor escura)
Index 2:  Sombra primaria
Index 3:  Cor base primaria
Index 4:  Destaque primario
Index 5:  Cor base secundaria
Index 6:  Sombra secundaria
Index 7:  Destaque secundario
Index 8:  Cor de pele / rosto base
Index 9:  Sombra de pele
Index 10: Destaque de pele
Index 11: Detalhes (botoes, equipamento)
Index 12: Cor de flash / dano (vermelho ou branco quente)
Index 13: Livre (efeito ou variante)
Index 14: Livre (efeito ou variante)
Index 15: Cor de background do sprite (se necessario)
```

### Tecnica de dithering manual (para gradientes)

Com apenas 15 cores, simule gradientes com dithering checkerboard 2x2:

```
Claro  Claro
Claro  Escuro   ← alternancia tile a tile
```

Isso e visivel em jogos como Vectorman, Toy Story MD. Nao use anti-aliasing.

---

## GERACAO DE ENTRADAS .res

Apos conversao, gerar entradas `.res` corretas:

### sprite.res

```
# Sprite de personagem 4x4 tiles (32x32 px)
SPRITE player_idle "sprite/player_idle.png" 4 4 FAST 5

# Sprite de inimigo 3x4 tiles (24x32 px)
SPRITE enemy_walk "sprite/enemy_walk.png" 3 4 BEST 5
```

Calculo de tiles: `w_tiles = width_px / 8`, `h_tiles = height_px / 8`
Opcoes de compressao: `FAST` (mais rapido), `BEST` (menor tamanho), `NONE` (sem compressao)

### gfx.res (tileset + mapa)

```
PALETTE palette_stage1 "gfx/stage1_fg.png"
TILESET stage1_fg_ts   "gfx/stage1_fg.png" BEST ALL
MAP     stage1_fg_map  "gfx/stage1_fg.png" stage1_fg_ts BEST 0

TILESET stage1_bg_ts   "gfx/stage1_bg.png" BEST ALL
MAP     stage1_bg_map  "gfx/stage1_bg.png" stage1_bg_ts BEST 0
```

---

## VALIDACAO POS-CONVERSAO

### Checklist automatizado

```bash
# 1. Re-diagnosticar para confirmar que issues criticos foram resolvidos
python tools/sgdk_wrapper/art_diagnostic.py --project "<projeto>" --output doc/art_post_conversion.json

# 2. Validar integracao com ResComp
powershell -File tools\sgdk_wrapper\validate_resources.ps1

# 3. Auto-fix .res se necessario
powershell -File tools\sgdk_wrapper\autofix_sprite_res.ps1

# 4. Build de teste
call build.bat
```

### Criterio de aceitacao pos-conversao

```
✅ art_diagnostic.py exit code = 0 (sem issues criticos)
✅ validate_resources.ps1 sem IDENTIFY_FAILED
✅ PNG modo P (indexado) confirmado
✅ Max 15 cores visiveis
✅ Dimensoes multiplas de 8
✅ build.bat compila sem erros
✅ ROM abre no emulador sem artefatos visuais
```

---

## PALETA COMPARTILHADA (mergePaletteSGDK)

Para cenas com multiplos sprites que compartilham 1 paleta no hardware:

```bash
# Colocar todos os PNGs indexados no mesmo diretorio e executar
cd tools/paletteMergerForSGDK-main
python mergePaletteSGDK.py
```

Util quando: player + inimigos + itens precisam caber em PAL1 (15 cores max).

---

## REFERENCIA DE QUALIDADE (Jogos comerciais MD)

Ao converter sprites, use estes jogos como benchmark visual:

| Jogo | Destaque tecnico | Aplicar em |
|------|-----------------|------------|
| Streets of Rage 3 | Shading muscular, contornos duplos | Sprites de briga de rua |
| Comix Zone | Dithering de sombra, linhas cruzadas | Personagens com volume |
| Vectorman | Dithering esfera, reflexos metalicos | Personagens mecanicos |
| Sonic 3 & Knuckles | Paleta de 3 tons por material, silhueta limpa | Plataforma, personagens |
| Thunder Force IV | Gradiente de ceu, estrelas em parallax | Backgrounds espaciais |
| Shinobi III | Tiles de cenario urbano, animacao fluida | Briga de rua, ninja |

**Regra do benchmark:** antes de aprovar um asset, coloque ele mentalmente ao lado de um sprite de Streets of Rage 3. Ele se sustenta? Se nao, refine.
