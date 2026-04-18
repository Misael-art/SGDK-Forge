---
name: art-creation-sourcing
description: Criacao e aquisicao de assets visuais quando o projeto nao possui arte. Duas rotas: (A) gerar pixel art com IA descritiva + converter, ou (B) buscar e baixar assets livres na web (opengameart, itch.io) e converter para SGDK. Inclui specs tecnicas para geracao de prompts de pixel art de alta qualidade.
---

# Art Creation & Sourcing

Use esta skill quando o projeto estiver no Cenario 3 (sem nenhuma arte) e o usuario precisar decidir como criar ou obter os assets.

---

## As duas rotas

```
Sem Arte
   │
   ├── ROTA A: GERACAO COM IA ─────────────────────────────────
   │     1. Definir spec visual (bible artistica resumida)
   │     2. Gerar prompts de pixel art precisos
   │     3. Gerar imagens (Stable Diffusion, DALL-E, Ideogram, etc.)
   │     4. Converter com photo2sgdk ou batch_resize_index.py
   │     5. Ajustar paleta e transparencia
   │     6. Validar e promover para res/
   │
   └── ROTA B: BUSCA E DOWNLOAD NA WEB ────────────────────────
         1. Identificar estilo visual do jogo
         2. Buscar em repositorios de assets livres (CC0/CC-BY)
         3. Baixar sprite sheets e tilesets
         4. Avaliar compatibilidade (dimensoes, estilo)
         5. Converter com batch_resize_index.py
         6. Validar e promover para res/
```

---

## ROTA A: Geracao com IA

### Passo 1 — Bible artistica resumida (obrigatorio)

Antes de gerar qualquer arte, definir:

```markdown
## Bible Artistica do Projeto

**Estilo visual:** (ex: "anime anos 90", "arcade briga de rua", "sci-fi dark")
**Resolucao de sprite principal:** (ex: 32x32 px = 4x4 tiles)
**Paleta dominante:** (ex: cores frias, azul/cinza com detalhes laranja)
**Referencias de jogos MD:** (minimo 3 jogos)
  - Referencia 1: [jogo] — herdar: [o que herdar]
  - Referencia 2: [jogo] — herdar: [o que herdar]
  - Referencia 3: [jogo] — herdar: [o que herdar]
**Personagem principal:** (nome, descricao fisica, equipamento)
**Paleta proposta (hex 9-bits):**
  - Cor base: #XXXXXX
  - Sombra: #XXXXXX
  - Destaque: #XXXXXX
  - Contorno: #000000
```

### Passo 2 — Prompts de pixel art para IA

**Estrutura de prompt de alta qualidade:**

```
[TECNICA] pixel art sprite sheet, [PERSONAGEM], [ESTILO],
[DIMENSAO] pixel canvas, [PALETA], transparent background,
[ANIMACOES], front view, [REFERENCIAS],
clean outlines, no anti-aliasing, no gradients,
limited palette [N] colors, Mega Drive style
```

**Exemplos prontos:**

```
# Personagem de plataforma (estilo Sonic/Mega Man):
pixel art sprite sheet, platformer hero character,
32x32 pixel canvas, anime 90s style,
blue and white color scheme with yellow highlights,
idle animation 4 frames, run animation 6 frames,
transparent background, clean black outlines,
no anti-aliasing, 15 color palette max,
Mega Drive Genesis style, Streets of Rage inspired

# Inimigo (estilo briga de rua):
pixel art enemy sprite, muscular thug character,
24x32 pixel canvas, 90s arcade fighting game style,
dark outfit with red details, walk cycle 6 frames,
attack animation 4 frames, hurt frame 1, death 2 frames,
transparent background, hard pixel edges,
Streets of Rage 2 color palette quality,
Mega Drive 15 color limit

# Background tile (cenario urbano):
pixel art tileset, urban alley background tiles,
8x8 pixel tiles seamless, 90s beat em up style,
dark asphalt and brick walls, dim lighting,
15 color palette, dithered shadows,
Streets of Rage 2 / Shinobi III quality,
Mega Drive Genesis resolution 320x224
```

**Dicas para prompts de alta qualidade:**
- Sempre mencionar: "no anti-aliasing", "no gradients", "hard pixel edges"
- Especificar numero maximo de cores: "15 color palette max"
- Referenciar jogos MD especificos para calibrar estilo
- Pedir "transparent background" para sprites
- Mencionar "8x8 tile grid" para tilesets
- Para sprite sheets, especificar frames e animacoes

### Passo 3 — Ferramentas de geracao de imagem

**Opcoes recomendadas (ordem de qualidade para pixel art):**

| Ferramenta | Qualidade | Disponibilidade |
|------------|-----------|-----------------|
| Stable Diffusion (PixelArt LoRA) | Excelente | Local/API |
| Ideogram v2 | Muito bom | Web/API |
| DALL-E 3 | Bom | API OpenAI |
| Midjourney | Bom | Discord/Web |

**Para gerar via API (automacao):**
```python
# Usar Claude API com tool use para coordenar geracao
# O agente art-creator usa esta skill para gerar prompts
# e pode chamar APIs externas de imagem via MCP ou HTTP
```

### Passo 4 — Ps-gerado: ajuste obrigatorio

Toda arte gerada por IA precisara de ajuste antes do SGDK:

```bash
# 1. Inspecionar o que foi gerado
python tools/sgdk_wrapper/art_diagnostic.py --project "<projeto>"

# 2. Corrigir issues (quase sempre necessario)
python tools/image-tools/fix_png_transparency_final.py "<asset>.png"

# 3. Converter para indexado com paleta correta
python tools/image-tools/batch_resize_index.py \
  --spec tools/image-tools/specs/<spec>.json \
  --batch-root "<projeto>/data"

# 4. Abrir no photo2sgdk para ajuste fino de paleta
call tools\photo2sgdk\run.bat
```

---

## ROTA B: Busca e Download na Web

### Repositorios recomendados

| Site | URL | Licenca | Qualidade |
|------|-----|---------|-----------|
| OpenGameArt | opengameart.org | CC0/CC-BY/GPL | Variada — filtrar por "16-bit" |
| itch.io Assets | itch.io/game-assets | Variada (muitos CC0) | Alta — buscar "16-bit pixel art" |
| Kenney | kenney.nl | CC0 | Media — estilo simples mas limpo |
| GameArt2D | gameart2d.com | Pago/Free | Alta qualidade |
| Spriters Resource | spriters-resource.com | Fair Use | Sprites de jogos comerciais MD |

### Estrategia de busca eficiente

**Termos de busca recomendados:**
```
"16-bit sprite" + [genero do jogo]
"Sega Genesis style" + [personagem/cenario]
"retro platformer sprite sheet" transparent
"beat em up character sprites" free CC0
"pixel art tileset" 8x8 16-bit
"side scroller background" pixel art free
```

**Filtros obrigatorios ao avaliar asset:**
1. Licenca: CC0 (melhor) ou CC-BY (dar credito) — nunca usar assets sem licenca explicita
2. Resolucao base compativel com redimensionamento para multiplos de 8
3. Estilo visual coerente com o jogo (comparar com bible artistica)
4. Sprite sheet organizado (frames em grid regular)

### Avaliacao de sprite sheet baixado

```bash
# Verificar o que foi baixado
python tools/sgdk_wrapper/art_diagnostic.py --project "<projeto>"

# Identificar dimensoes e modo
magick identify -verbose "<sprite_sheet>.png" | head -30

# Verificar grid de frames (para sprite sheets)
# Largura/altura deve ser divisivel pelo tamanho do frame
# Ex: 192x32 px com frames 32x32 = 6 frames horizontais
```

**Checklist de avaliacao:**

- [ ] Licenca verificada e compativel (CC0 ou CC-BY)
- [ ] Sprite sheet tem grid regular de frames
- [ ] Dimensoes de frame compativeis com multiplos de 8
- [ ] Estilo visual coerente com bible artistica
- [ ] Numero de cores visiveis <= 15 (ou redutivel sem perda critica)
- [ ] Fundo transparente ou removivel

### Download e organizacao

```
data/
  raw/                  ← assets baixados sem modificacao
    sprite_sheet_cc0.png
    tileset_urban_cc0.png
  production/           ← assets cortados e prontos para conversao
    player_idle.png     ← frame recortado do sprite sheet
    player_walk_01.png
  ASSETS_CREDITS.md     ← registro de licencas e origens
```

**ASSETS_CREDITS.md (obrigatorio para CC-BY):**
```markdown
# Creditos de Assets

| Asset | Origem | Autor | Licenca | URL |
|-------|--------|-------|---------|-----|
| player_idle.png | OpenGameArt | Autor X | CC-BY 4.0 | url |
| stage1_bg.png | itch.io | Estudio Y | CC0 | url |
```

### Corte de sprite sheet

Para extrair frames de um sprite sheet com ImageMagick:

```bash
# Cortar grid de sprites (ex: sheet 192x32 com frames 32x32)
magick "<sheet>.png" -crop 32x32 +repage +adjoin "production/frame_%02d.png"

# Cortar frame especifico (x_offset, y_offset, w, h)
magick "<sheet>.png" -crop 32x32+0+0 +repage "production/player_idle.png"
magick "<sheet>.png" -crop 32x32+32+0 +repage "production/player_walk_01.png"
magick "<sheet>.png" -crop 32x32+64+0 +repage "production/player_walk_02.png"
```

---

## Decisao: qual rota escolher?

| Fator | Rota A (IA) | Rota B (Web) |
|-------|-------------|--------------|
| Controle visual total | Sim | Parcial |
| Estilo unico garantido | Sim | Dificil |
| Velocidade | Media | Alta |
| Qualidade pixel art | Media-alta | Alta (se bom repositorio) |
| Custo | API de imagem | Gratis (CC0) |
| Coerencia visual entre assets | Alta (mesmo prompt) | Media (mixer de estilos) |
| Recomendado para | Jogos originais com identidade visual propria | Prototipos, jams, projetos educacionais |

**Regra geral:** para personagem principal e arte central do jogo → Rota A com ajuste manual. Para tiles de background e assets secundarios → Rota B com curadoria.

---

## Saida esperada desta skill

Para o usuario decidir a rota, entregar:

```markdown
## Analise de Arte — <Nome do Projeto>

**Assets necessarios identificados:**
- [ ] Sprite do jogador (32x32 px, ~8 frames de animacao)
- [ ] 3 tipos de inimigos (24x32 px)
- [ ] Tileset de cenario fase 1 (256 tiles unicos estimados)
- [ ] HUD icons (8x8 px a 16x16 px)

**Rota A (IA):**
- Estimativa: X assets, Y prompts necessarios
- Ferramentas: Stable Diffusion + photo2sgdk
- Tempo estimado de ajuste manual: Z horas

**Rota B (Web):**
- Repositorios sugeridos: OpenGameArt, itch.io
- Termos de busca: [lista]
- Assets CC0 encontrados possivelmente compativeis: [lista com URLs]

**Recomendacao:** [Rota A / Rota B / Hibrido] porque [justificativa]
```
