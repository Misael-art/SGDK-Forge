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
| `build_*.py` curados | `tools/image-tools/` | Builders de cena/showcase — melhor para casos com source pack, pose aprovada, `virtual_proof` e `case_manifest` ja definidos |
| `fix_png_transparency_final.py` | `tools/image-tools/` | Corrigir transparencia em PNGs existentes |
| `mergePaletteSGDK.py` | `tools/paletteMergerForSGDK-main/` | Combinar paletas de multiplos assets |
| `ImageMagick` | `tools/ImageMagick/` | Manipulacao geral de imagens |
| `autofix_sprite_res.ps1` | `tools/sgdk_wrapper/` | Corrigir .res automaticamente |
| `validate_resources.ps1` | `tools/sgdk_wrapper/` | Validar assets antes do build |
| `freshness_audit.ps1` | `tools/sgdk_wrapper/` | Confirmar que builder, grafo, validator e evidencia nao ficaram stale |

---

## Matriz de escolha de rota

Escolha a ferramenta pela natureza do caso, nao por habito:

| Caso | Rota correta |
|------|--------------|
| lote generico de PNGs em `/data` | `batch_resize_index.py` |
| sprite heroico isolado com ajuste fino de paleta | `photo2sgdk.exe` |
| cena ou showcase com pack multi-camada, pose aprovada, `virtual_proof` ou `case_manifest` | builder dedicado em `tools/image-tools/build_*.py` |

Regra critica:

- se o projeto ja tiver `doc/source_cases/**/case_manifest.json` ou um builder dedicado em `tools/image-tools`, reutilize essa rota antes de iniciar OCR, thumbnailing, crop manual ou tentativa de descobrir bbox no escuro
- se a fonte veio de IA/high-res e pretende virar pixel art nativa, bloquear qualquer downscale que nao seja nearest-neighbor ou redesenho manual em grid nativo
- OCR nao e ferramenta de selecao de pose quando ja existir `animation_manifest` ou bbox curado em builder do projeto
- warning visual em asset promovido volta para o builder/spec do asset; nao compense no runtime sem registrar tradeoff
- antes de declarar promocao concluida, gere ou atualize manifesto do builder e rode `res_graph_audit.ps1`, `validate_resources.ps1` e `freshness_audit.ps1`
- antes de promover sprite/strip gerado por IA, registrar `fake_pixel_art_rejection`, `pixel_perfect_animation_pass` quando houver movimento e `sprite_artifact_report`
- antes de promover UI final, health bar, fonte, micro-icone, caixa ou cursor, registrar `ui_pixel_surface_contract` quando a surface depender de pixel-perfect, atlas, fonte ou barra
- para AAA/stable/release, gerar `asset_optimization_report` com compressao `.res`, dedup/reuse medido, custo ROM, custo VRAM e decisao por recurso

Exemplo canonico:

- `BENCHMARK_VISUAL_LAB_V2` Cena 1 usa `python tools/image-tools/build_bvl_v2_scene1_assets.py`
- esse builder ja conhece o pack de floresta vertical, a pose `stand` do Mega Man, o `virtual_proof` e os manifests da cena

## Curadoria 2026-06-03 - Celestial Chase: source_baked_pixel_art_standard

Licao extraida do projeto `Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]`: usuario entregou source art autoral **ja pixel-art** (PNG com pixels alinhados em 8x8, paleta quantizada, index 0 marcado, frames separados). O pipeline de downscaling desta skill NAO foi aplicado porque a fonte ja nasce pixel.

### Quando NAO usar este pipeline

Use este pipeline (`photo2sgdk`, `batch_resize_index.py`, `tile_dedup_hvflip_hashing`, `palette_remastering_slot_audit`, `arcade_tile_redraw_substitution`) APENAS quando a fonte for:

- foto, render 3D, concept art em alta resolucao, mockup AI, crop high-res.
- pixel-art em resolucao maior que 8x8 (ex.: 16x16 fonte querendo virar 8x8 nativo).
- color hack / ROM hack de arcade (escopo `ARCADE_TILE_REDRAW`).

### Quando usar `source_baked_pixel_art_standard`

Quando a fonte JA e pixel-art (8x8-aligned, paleta quantizada, frames separados):

- NAO rodar `photo2sgdk`.
- NAO rodar `batch_resize_index.py` (downscaling desnecessario e potencialmente destrutivo).
- NAO rodar `tile_dedup_hvflip_hashing` alem de checagem final.
- NAO aplicar `palette_remastering_slot_audit` alem de validacao.
- Em vez disso, produzir os 3 specs canonicos:
  - `spec/pixel_lock.json` (lock de pixels em 8x8, paleta, index 0, dithering opcional).
  - `spec/animation_strip.json` (frames, pivos, contact points, duracao em frames).
  - `spec/motion_gif.json` (preview de movimento, link para o gif ou caminho do asset).
- Rodar `megadrive-pixel-strict-rules` como conformance.
- Registrar `human_approval_record.md` para o asset.
- A partir dai, o asset pode entrar no `validate_resources.ps1` (gate `source_baked_pixel_art_standard`) e seguir para `.res`/`img`.

### Anti-padrao: aplicar downscaling em arte ja pixel

Sintomas de violacao:

- PNG fonte ja 8x8-aligned mas ainda passa por `batch_resize_index.py` com `--scale 1.0` "so para confirmar".
- `tile_dedup_hvflip_hashing` roda em sprite sheet ja planejado para tile-by-tile.
- `palette_remastering_slot_audit` tenta "harmonizar" paleta ja canonica do autor.
- `motion_gif` ausente mesmo com `animation_strip` presente.

Consequencia: perda de precisao de pixel, falso dithering, "blur" em regiao que nao precisava, retrabalho de aprovacao humana.

## Builder Gate

Para cena AAA com fonte grande, spritesheet ou painéis:

- primeiro mapear builders existentes em `tools/image-tools/build_*.py`
- se nao existir builder adequado, criar builder dedicado antes de editar `resources.res` manualmente
- registrar `scene*_asset_promotion_report.json` e manifesto de paineis/poses em `out/logs` ou `doc/source_cases`
- atualizar `.res` a partir do builder, nao por tentativa manual repetida
- rodar `freshness_audit.ps1` apos gerar assets e antes de abrir runtime

## Gate de fonte premium e estrutura canonica

Leia `references/canonical_asset_structure.md` antes de promover asset critico.

Regras:

- arte premium aceita deve estar em `data/source_art/` com `premium_source_manifest`
- `data/raw_ai/` e staging; nao promove para `res/` diretamente
- `data/debug_lab/` guarda `local_author_pixel_rasterization`, `procedural_renderer`, controles e placeholders; nunca asset critico final
- `data/processed/` recebe candidatos convertidos antes de `res/`
- `res/` recebe apenas assets aprovados para runtime, com lineage e spec/builder rastreavel
- `res/` vazio ou sem `.res` nao significa pipeline aprovado: classifique como `asset_pipeline_not_started`
- projeto com intencao de entrega visual/gameplay sem `res/resources.res` fica `resources_res_missing_for_visual_delivery`; runtime desenhado por tiles em C pode ser debug/prototipo, mas nao substitui conversao de assets
- projeto com scripts ou relatorios soltos na raiz deve ser tratado como `legacy_scattered_artifacts` ate reancorar a fonte no layout canonico

## Contrato para personagens grandes animados

Para lutadores, bosses, inimigos grandes ou qualquer personagem com celulas acima de 48x64, a unidade de curadoria NAO deve ser um atlas monolitico. A rota canonica e:

```text
res/sprites/characters/<personagem>/
  palettes/
    pal1.png              # portador de paleta/material slots
  idle.png                # strip de uma acao
  walk_forward.png
  jab.png
  ...
```

Regras:

- cada arquivo de pose/estado contem uma unica acao em strip horizontal;
- o atlas completo, quando necessario para o runtime, e apenas derivado em `data/processed/runtime_atlas/` ou artefato declarado de preview;
- `resources.res` deve declarar os strips por pose com simbolos estaveis (`spr_<personagem>_<estado>`) quando o projeto precisar auditar cortes/pivots;
- cada pose exige `contact_sheet`, `pivot_overlay`, `motion_phase_map`, `frame_delta_report`, `foot_contact_report` e `preview.gif`;
- pose premium, golpe, dano, lutador ou boss exige tambem `animation_direction_contract`; golpes exigem `timing_spacing_report`, `impact_frame_contract`, `smear_frame_manifest` quando houver smear, e `recovery_curve_report`; hurt/knockdown exigem `hit_reaction_contract`;
- o builder deve registrar `runtime_layout` no `animation_manifest` (`per_pose_sprites`, `per_pose_sprites_with_preview_atlas` ou justificativa equivalente);
- largura/altura de celula de lutador, boss ou personagem grande deve vir de `slicing_cell_contract` com `max_bbox + padding` por estado, ou de celula fixa justificada por manifest; `FRAME_W`/`FRAME_H` hardcoded sem contrato bloqueia promocao;
- se um strip vier de imagem gerada ou fonte irregular, a etapa de slicing deve remover fragmentos de celulas vizinhas antes da promocao e registrar isso como curadoria de corte, nao como nova arte procedural;
- pivots e linha de chao sao contrato por estado; se pes, maos ou cabeca forem cortados, a pose volta para `needs_review` e nao deve ser escondida dentro de atlas maior.
- rode `analyze_sprite_strip_integrity.py` em cada strip heroico antes de copiar para `res/`; `FRAME_EDGE_CLIPPING`, `NON_INDEX0_BACKGROUND_MATTE`, `TRANSPARENCY_INDEX0_BACKGROUND_MISMATCH`, `SMALL_ISLAND_DEBRIS`, `STRAY_LARGE_COMPONENT`, `SCALE_INCONSISTENCY` e `BAKED_FX_IN_CHARACTER_SHEET` bloqueiam promocao.
- FX de impacto, hit spark, projetil, poeira e brilho nao devem ficar baked-in na paleta do personagem; exporte como sprite/FX separado quando tiver papel de gameplay ou reuso.
- flash frame e impacto especial precisam de `palette_flash_policy` e `palette_domain_report`; nao promova frame re-quantizado que mistura material do personagem com FX.
- bosses/chefes ou criaturas grandes devem usar `modular_boss_rig_contract` quando a estrategia full-body comprometer VRAM, DMA, scanline ou reuso; cada parte precisa de bbox, pivô e dominio de paleta.

### Curadoria 2026-06-03: rescomp, dedup e remasterizacao

Quando o asset envolver personagem grande, lutador, boss, port/remaster visual ou material vindo de estudo externo, registre as tecnicas no `doc/technique_usage_manifest.json` do projeto e gere relatorios antes de promover para `res/`.

- `rescomp_metasprite_decomposition_audit`
  - medir bbox real por frame/pose, areas transparentes cortadas, hardware sprites gerados, tiles unicos e pior scanline;
  - `resources.res` ou screenshot nao provam que a decomposicao cabe; precisa `asset_optimization_report` e `sprite_scanline_pressure_report`.
- `large_metasprite_vblank_fit_audit`
  - para cada frame streamado, calcular `tiles_unicos * 32` e comparar com o envelope seguro de VBlank;
  - se nao couber, exigir recorte de janela ativa, partes estaticas, preload honesto ou reducao visual.
- `tile_dedup_hvflip_hashing`
  - quando builder deduplicar tiles, reportar hashes normal/H/V/HV, flags de tilemap, economia real e risco de colisao de indices VRAM;
  - flip por hardware e economia valida so contam quando preservam pivots, prioridade, paleta e leitura.
- `palette_remastering_slot_audit`
  - remover cores mortas e remapear por material com `palette_slot_audit`;
  - nao quebrar indice 0 transparente, slots reservados de Shadow/Highlight ou dominios de paleta de HUD/personagem/FX.
- `arcade_tile_redraw_substitution`
  - manter `LABORATORIO` ate haver lineage/licenca, aprovacao humana e separacao clara entre estudo, romhack e asset final de projeto autoral.

### Curadoria 2026-06-04: rotacao, escala, espelhamento e paleta temporal

- `prerendered_sprite_scaling` e `pre_shifted_sprite_rotation`
  - tratar como custo de ROM, strips e residencia; cada escala/angulo precisa preservar silhueta, pivot, material e leitura;
  - preferir H/V flip apenas quando a assimetria do personagem permitir.
- `smear_frame_animation`
  - produzir `smear_frame_manifest`; smear e um frame de animacao dirigido, nunca blur automatico.
- `software_sprite_mirroring`
  - permanece `LABORATORIO`; preferir arte dedicada ou espelhamento parcial por hardware antes de transformar tiles em RAM e criar DMA extra.
- `temporal_dithering_palette_blending`
  - exige variante/fallback para LCD e auditoria de flicker; nao vender retencao de fosforo CRT como transparencia real.
- `dynamic_palette_slot_clustering`
  - permanece `LABORATORIO`; agrupamento de inimigos por direcao de arte e mais seguro do que remapear slots em todo frame.

### Paleta por material

Paleta de personagem autoral deve ser curada por material, nao por quantizacao global:

- `palettes/pal1.png` ou manifesto equivalente deve preservar slots semanticos: transparente, contorno, roupa/material principal, roupa secundaria, pele, patches/acento e FX quando existir;
- variante P2 so pode ser palette swap curado depois do P1 aprovado e deve remapear indices por material, nao re-quantizar por distancia RGB;
- gi branco exige faixa de sombras frias + highlights limpos conforme `white_material_palette_contract`;
- se a variante muda gi branco para azul/cinza, os slots do gi mudam, mas pele, outline e patches continuam em slots coerentes;
- `PALETTE_WASTE`, material misturado por quantizacao ou perda forte de contraste em P2 bloqueiam promocao visual e devem voltar ao builder/spec.

### Gate anti-fake-pixel-art para fontes IA/high-res

Nenhuma geracao ou mockup high-res vira sprite final apenas por "parecer pixel
art". A rota aceita e:

1. `source` preservado em `data/source_art/` ou `data/raw_ai/`.
2. Reducao para resolucao alvo apenas por nearest-neighbor, ou redesenho manual
   em canvas nativo.
3. Indexacao para ate 15 cores visiveis + transparente.
4. Snap para grade 9-bits.
5. Limpeza manual/pixel-perfect: jaggies, double corners, halos, ilhas,
   fragmentos fora da celula e matte residual.
6. Para animacao, `pixel_perfect_animation_pass` e preview animado antes de
   qualquer promocao para `res/`.

Blockers:

- `fake_pixel_art_artifact`
- `non_nearest_downscale`
- `palette_micro_noise`
- `residual_chroma_matte`
- `orphan_pixels_outside_character`
- `ui_fractional_scale_artifact`
- `health_bar_antialiased_fill`
- `ui_pixel_surface_contract_missing`

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

Regra de budget:

- `FAST`, `BEST` e `NONE` afetam custo de ROM, tempo/comportamento de decompress e carga inicial.
- Apos o asset estar carregado, o custo em VRAM e o numero de tiles descompactados residentes continuam sendo medidos por tiles reais.
- Nao aprovar asset como "mais barato em VRAM" apenas porque usa `BEST`.

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
✅ validate_resources.ps1 sem IDENTIFY_FAILED nem PALETTE_INFLATED
✅ PNG modo P (indexado) confirmado — byte 25 do header = 3
✅ BitDepth = 4 (nao 8) — byte 24 do header
✅ Entradas PLTE <= 16 (nao confiar apenas em cores unicas)
✅ Max 15 cores visiveis
✅ Dimensoes multiplas de 8
✅ build.bat compila sem erros
✅ ROM abre no emulador sem artefatos visuais
```

> **ATENCAO:** Uma imagem pode ter 11 cores unicas mas 256 entradas de paleta (8bpp indexed).
> O ImageMagick reporta 11 cores e PASSA. Mas o rescomp trata indices de paleta como identidade de tile.
> Pixeis com mesma cor RGB mas indices diferentes geram tiles "unicos" falsos,
> inflando o tileset e causando corrupcao visual. Verifique SEMPRE as entradas PLTE.

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

## Contrato Operacional

### Entrada minima

- raiz do projeto e layout `data/`, `res/` e `.res` resolvidos
- assets fonte existentes em `/data`, `/res` ou builder dedicado declarado
- `premium_source_manifest` quando o asset for personagem, cenario, boss, HUD heroico ou outro asset critico
- `asset_lineage_record` e `master_style_manifest` quando o asset veio de geracao/sourcing
- alvo de conversao: sprite, tileset, image, map ou palette
- restricoes conhecidas de paleta, grid 8x8, transparencia e cena

### Saida minima

- assets convertidos ou corrigidos em caminho rastreavel
- spec de conversao ou builder usado registrado
- relatorio de promocao com dimensoes, paleta, index 0 e grid
- referencia ao `asset_lineage_record` preservada no relatorio quando existir
- `source_to_rom_asset_map` quando o asset critico entrar em `res/`
- `asset_optimization_report` quando houver alegacao AAA/stable/release ou ROM size/budget relevante
- `.res` atualizado apenas quando a promocao estiver tecnicamente consistente
- comandos de validacao executaveis para o proximo gate

### Passa quando

- PNGs promovidos sao indexados, com PLTE <= 16 e index 0 correto
- dimensoes sao multiplas de 8 e nao ha cores fora do grid 9-bits
- `validate_resources.ps1` nao acusa blockers de asset promovido
- `res_graph_audit.ps1` nao esta em `method=no_res_files` nem `code_loaded_tiles_unmeasured` para entrega visual/AAA
- compressao `.res` nao e tratada como reducao falsa de VRAM residente
- compressao `.res` escolhida por recurso fica documentada (`FAST`, `BEST`, `NONE`, `APLIB`, `LZ4W` quando aplicavel); ausencia de politica vira `asset_optimization_unmeasured`
- dedup/reuse de tiles so conta quando medido por report; promessa de economia ou "30%" sem medicao fica `dedup_unmeasured`
- `asset_optimization_report` separa economia de ROM/load de VRAM residente e nao usa compressao como desculpa para estouro visual
- qualquer warning visual volta para builder/spec antes de compensacao em runtime
- asset gerado nao perde rastreabilidade de estilo/origem durante slicing, quantizacao ou crop
- asset critico nao vem de `local_author_pixel_rasterization`, `procedural_renderer` ou `data/debug_lab/`
- asset critico em `res/` aponta para fonte premium real em `data/source_art/`
- promocao para `res/` fica bloqueada quando `source_validity=false`, `authoriality_gate!=passed`, `clone_risk_score` ou `benchmark_similarity_index` acima dos limites declarados, `needs_review`, `placeholder`, `debug_lab`, `benchmark-derived`, `rework`, `perceptual_quality=nao_medido`, `elite_ready=false`, `blocked_image_tooling`, `blocked_no_premium_source`, `lab_not_delivery` ou `source_to_rom_visual_match < 8` ja estiver registrado
- para personagem animado critico, promocao para `res/` tambem fica bloqueada quando `animation_direction_contract`, `timing_spacing_report`, `impact_frame_contract`, `recovery_curve_report`, `hit_reaction_contract` aplicavel, `shading_motion_report` ou `palette_flash_policy` aplicavel estiver ausente, sintetico ou contraditorio com o strip
- benchmark tecnico nao vira fonte visual nem substitui `premium_source_manifest`
- `PALETTE_WASTE` em asset critico bloqueia promocao; gi branco ou tecido claro exige `white_material_palette_contract`
- UI de entrega exige `ui_pixel_surface_contract` quando houver atlas/fonte/barra; health bar precisa container, fill ativo, buffer latente, drenagem por pixels inteiros e bordas hard-edge

### Handoff para proxima etapa

- entregar assets promovidos, spec/builder, `.res`, relatorio e lineage quando existir para `megadrive-pixel-strict-rules`
- quando o asset entrar em cena, entregar tambem para `megadrive-vdp-budget-analyst`
- quando ja houver ROM alvo, entregar logs para `sgdk-runtime-coder` e `sgdk-build-wrapper-operator`
