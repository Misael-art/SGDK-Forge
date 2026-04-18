# 13 - Especificacao Tecnica por Cena

**Versao:** 1.0
**Referencia de hardware:** Mega Drive VDP (315-5313), 68000 @ 7.67 MHz, NTSC 60Hz

> **REGRA:** Nenhum efeito visual pode ser adicionado ou modificado sem consultar este documento.
> Se um budget for excedido, o efeito deve ser removido ou simplificado. Nao ha negociacao com hardware real.
> Alteracoes neste documento requerem ordem expressa do usuario.

---

## 1. LIMITES GLOBAIS DO MEGA DRIVE

| Recurso | Limite absoluto | Budget conservador (60fps) |
|---------|-----------------|---------------------------|
| VRAM | 64 KB (2048 tiles) | Usar no maximo 75% = 1536 tiles |
| Paletas | 4 x 16 cores | PAL0-PAL1 para cenario, PAL2-PAL3 reservadas |
| Sprites por scanline | 20 | Limitar a 16 para margem |
| Sprites totais (link table) | 80 | Limitar a 40 para margem |
| DMA por VBlank (NTSC) | ~7200 bytes | Limitar a 5000 bytes para margem |
| CPU por frame | 16.7ms (100%) | Logica + render devem caber em 80% = 13.3ms |
| H-Int callbacks | 1 por frame | Exclusivo para `hint_manager.c` |

---

## 2. BUDGET DO PLAYER (TODAS AS CENAS)

O player esta presente em todos os planetas. Seu budget e fixo e subtraido do budget de cada cena.

| Componente | Tiles VRAM | Sprites HW | DMA/frame | Paleta |
|------------|-----------|------------|-----------|--------|
| Corpo (placeholder) | 6 | 3 | 0 (estatico) | PAL1 |
| Cachecol (5 segmentos) | 1 (compartilhado) | 5 | 0 (estatico) | PAL1 |
| Halo (quando visivel) | 1 | 0 (tile no BG) | 0 | PAL0 |
| **Total player** | **8** | **8** | **0** | **PAL1** |

**Quando assets finais entrarem:**

| Componente | Tiles VRAM (max) | Sprites HW (max) | DMA/frame (max) | Paleta |
|------------|-----------------|-------------------|-----------------|--------|
| Corpo (meta-sprite) | 16 (4x4) | 4 | 128 bytes (animacao) | PAL2 |
| Cachecol | 5 | 5 | 0 | PAL2 |
| **Total player final** | **21** | **9** | **128 bytes** | **PAL2** |

---

## 3. CENA: B-612

### Identidade tecnica
Planeta-tutorial. Line scroll curvo simula curvatura do asteroide. Palette cycling simula ciclo dia/noite. Hilight mode cria halo de luz.

### Budget

| Recurso | Alocado | Usado (atual) | Margem |
|---------|---------|---------------|--------|
| Tiles VRAM (cenario) | 30 | 27 procedurais | 3 |
| Tiles VRAM (rescomp) | 4 | 4 (rose_mark) | 0 |
| Paletas cenario | PAL0 + PAL1 | PAL0 + PAL1 | - |
| Sprites HW (cenario) | 0 | 0 | - |
| DMA/frame | 2000 bytes | ~960 bytes | 1040 |
| Line scroll | 144 linhas (40-184) | 144 | 0 |
| Column scroll | 0 | 0 | - |
| H-Int | Desabilitado | Desabilitado | - |
| Hilight/Shadow | Habilitado | Habilitado | - |

### Efeitos ativos
1. **Line scroll curvo (BG_A):** `depth * depth >> 8` a partir da linha 76. Simula curvatura.
2. **Line scroll paralaxe (BG_B):** Scroll lento com profundidade. Estrelas se movem.
3. **Palette cycling:** 4 estados de paleta (gB612Cycle). Troca a cada 32 frames.
4. **Hilight mode:** VDP_setHilightShadow(TRUE). Halo desenhado como tile no BG.
5. **Cachecol com vento:** windStrength varia com sinFix16.

### DMA detalhado
| Operacao | Bytes | Quando |
|----------|-------|--------|
| PAL_setColors (sky, 6 cores) | 12 | Todo frame |
| Hscroll table (224 words) | 448 | VBlank |
| Vscroll table (0) | 0 | - |
| Tiles de animacao | 0 (placeholders estaticos) | - |
| **Total** | **~960** | **< 2000 budget** |

### Riscos
- Palette cycling + hilight pode causar flash visual se timing de DMA nao for respeitado.
- Com assets finais (player animado), DMA sobe ~128 bytes/frame.

---

## 4. CENA: PLANETA DO REI

### Identidade tecnica
Parallax multicamada simulado. BG_A e BG_B correm a velocidades diferentes. Column scroll faz colunas do palacio oscilarem.

### Budget

| Recurso | Alocado | Usado (atual) | Margem |
|---------|---------|---------------|--------|
| Tiles VRAM (cenario) | 30 | 27 procedurais | 3 |
| Tiles VRAM (rescomp) | 4 | 4 (throne_mark) | 0 |
| Paletas cenario | PAL0 + PAL1 | PAL0 + PAL1 | - |
| Sprites HW (cenario) | 0 | 0 | - |
| DMA/frame | 2500 bytes | ~1632 bytes | 868 |
| Line scroll | 152 linhas (32-184) | 152 | 0 |
| Column scroll | 4 colunas (8-11) | 4 | 0 |
| H-Int | Desabilitado | Desabilitado | - |
| Hilight/Shadow | Desabilitado | Desabilitado | - |

### Efeitos ativos
1. **Parallax por linha (BG_B):** 3 faixas de velocidade (lento, medio, rapido) com micro-jitter.
2. **Parallax por linha (BG_A):** Scroll lento com alternancia de +1/-1.
3. **Column scroll (BG_A, colunas 8-11):** sinFix16 para oscilar colunas do palacio.

### DMA detalhado
| Operacao | Bytes | Quando |
|----------|-------|--------|
| Hscroll table (224 x 2 planes x 2 bytes) | 896 | VBlank |
| Vscroll table (20 x 2 planes x 2 bytes) | 80 | VBlank |
| Tile updates | 0 | - |
| **Total** | **~1632** | **< 2500 budget** |

### Riscos
- Column scroll + line scroll no mesmo frame e o cenario mais pesado de DMA do slice.
- Com 4 colunas oscilando e 152 linhas de hscroll, qualquer adicao de DMA deve ser medida.

---

## 5. CENA: PLANETA DO LAMPIAO

### Identidade tecnica
H-Int split de paleta divide o frame em ceu frio (topo) e zona quente (base). Heat wobble via line scroll local. Hilight para halo da chama.

### Budget

| Recurso | Alocado | Usado (atual) | Margem |
|---------|---------|---------------|--------|
| Tiles VRAM (cenario) | 30 | 27 procedurais | 3 |
| Tiles VRAM (rescomp) | 4 | 4 (lamp_mark) | 0 |
| Paletas cenario | PAL0 + PAL1 | PAL0 + PAL1 | - |
| Sprites HW (cenario) | 0 | 0 | - |
| DMA/frame | 2000 bytes | ~972 bytes | 1028 |
| Line scroll | 80 linhas (96-176) | 80 | 0 |
| Column scroll | 0 | 0 | - |
| H-Int | Ativo (split na linha 95) | Ativo | Exclusivo |
| Hilight/Shadow | Habilitado | Habilitado | - |

### Efeitos ativos
1. **H-Int split de paleta:** Linha 95 divide frame. Acima: paleta fria. Abaixo: paleta quente (ou escura se lampiao apagado).
2. **Heat wobble (BG_A):** sinFix16 por linha entre 112-160. Simula ar quente.
3. **Hilight mode:** Halo sobre lampiao quando aceso.
4. **Transicao de estado:** Ao resolver, paleta inferior muda de escura para iluminada.

### DMA detalhado
| Operacao | Bytes | Quando |
|----------|-------|--------|
| PAL_setPalette (full, 16 cores) | 32 | Frame init |
| PAL_setColors (top, 6 cores) | 12 | Frame init |
| H-Int palette swap (6 cores) | 12 | Mid-frame (H-Int) |
| Hscroll table (parcial, 80 linhas) | 160 | VBlank |
| **Total** | **~972** | **< 2000 budget** |

### Riscos
- **CRITICO:** H-Int swap de paleta no meio do frame e a operacao mais sensivel a timing do slice.
- Se o split acontecer durante DMA de sprite, pode corromper.
- A linha 95 foi escolhida para ficar abaixo da area de sprites do player (que fica acima).
- Qualquer mudanca na posicao Y do player ou na linha de split requer revalidacao.

---

## 6. CENA: DESERTO DAS ESTRELAS

### Identidade tecnica
Cenario mais leve do slice. Line scroll simula vento e miragem. Foco em ritmo contemplativo.

### Budget

| Recurso | Alocado | Usado (atual) | Margem |
|---------|---------|---------------|--------|
| Tiles VRAM (cenario) | 30 | 27 procedurais | 3 |
| Tiles VRAM (rescomp) | 4 | 4 (desert_mark) | 0 |
| Paletas cenario | PAL0 + PAL1 | PAL0 + PAL1 | - |
| Sprites HW (cenario) | 0 | 0 | - |
| DMA/frame | 1500 bytes | ~704 bytes | 796 |
| Line scroll | 128 linhas (56-184) | 128 | 0 |
| Column scroll | 0 | 0 | - |
| H-Int | Desabilitado | Desabilitado | - |
| Hilight/Shadow | Desabilitado | Desabilitado | - |

### Efeitos ativos
1. **Line scroll vento (BG_B):** Scroll por linha com profundidade progressiva.
2. **Line scroll miragem (BG_A):** sinFix16 por linha a partir da linha 120. Simula calor do deserto.

### DMA detalhado
| Operacao | Bytes | Quando |
|----------|-------|--------|
| Hscroll table (parcial, 128 linhas x 2 planes) | 512 | VBlank |
| **Total** | **~704** | **< 1500 budget** |

### Riscos
- Cenario mais leve. Principal risco e adicionar efeitos desnecessarios que quebrem a simplicidade.
- O vento variavel (windStrength com sinFix16) afeta cachecol e scroll simultaneamente.

---

## 7. CENA: TRAVEL

### Budget

| Recurso | Alocado | Usado (atual) | Margem |
|---------|---------|---------------|--------|
| Tiles VRAM | 30 | ~20 procedurais | 10 |
| Paletas | PAL0 + PAL1 | PAL0 + PAL1 | - |
| Sprites HW | 0 | 0 (player oculto) | - |
| DMA/frame | 1000 bytes | ~200 bytes | 800 |
| Line scroll | 0 | 0 | - |
| H-Int | Desabilitado | Desabilitado | - |

### Efeitos
- Circulos concentricos desenhados no tilemap (procedural).
- Escala animada por frame counter.
- Sem sprites, sem scroll, sem H-Int.
- Cena mais barata do slice.

---

## 8. CENAS DE TEXTO (TITLE, STORY, PAUSE, CODEX, CREDITS)

### Budget compartilhado

| Recurso | Alocado |
|---------|---------|
| Tiles VRAM | Font SGDK + ~10 decorativos |
| Paletas | PAL0 |
| Sprites HW | 0 |
| DMA/frame | < 200 bytes |
| Scroll | Nenhum |
| H-Int | Desabilitado |

Estas cenas sao essencialmente estaticas. O unico custo e a escrita inicial no tilemap.

---

## 9. TABELA RESUMO DE BUDGETS

| Cena | Tiles | Sprites HW | DMA/frame | Line scroll | Column scroll | H-Int | Hilight |
|------|-------|------------|-----------|-------------|---------------|-------|---------|
| B-612 | 34+player | 8 (player) | 2000 | Sim (144 linhas) | Nao | Nao | Sim |
| Rei | 34+player | 8 (player) | 2500 | Sim (152 linhas) | Sim (4 cols) | Nao | Nao |
| Lampiao | 34+player | 8 (player) | 2000 | Sim (80 linhas) | Nao | Sim (L95) | Sim |
| Deserto | 34+player | 8 (player) | 1500 | Sim (128 linhas) | Nao | Nao | Nao |
| Travel | ~20 | 0 | 1000 | Nao | Nao | Nao | Nao |
| Texto | ~10 | 0 | 200 | Nao | Nao | Nao | Nao |

---

## 10. REGRAS DE ALTERACAO

1. **Nenhum budget pode ser aumentado** sem evidencia de que o hardware suporta (teste em Blastem com debug overlay).
2. **Nenhum efeito pode ser adicionado** a uma cena sem atualizar esta tabela primeiro.
3. **Se um novo asset entrar** (sprite, tilemap, paleta), recalcular o budget total da cena afetada.
4. **O Lampiao e a cena mais sensivel.** Qualquer mudanca no H-Int split, posicao de sprites ou DMA timing requer validacao especifica.
5. **O Rei e a cena mais pesada em DMA.** Se BGM for adicionada, medir impacto de XGM2 no DMA budget restante.
6. **O Deserto e a cena com mais margem.** Ainda assim, nao e licenca para desperdicar.
