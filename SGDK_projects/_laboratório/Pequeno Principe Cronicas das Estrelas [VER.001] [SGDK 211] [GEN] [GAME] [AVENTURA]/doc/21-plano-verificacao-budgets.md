# 21 - Plano de Verificacao Conservadora de Budgets

**Versao:** 1.0
**Data:** 2026-03-16
**Contexto:** Fase 1 — Criterios e procedimentos para validar VRAM, DMA e sprites apos integracao de assets

> Apos cada alteracao visual, executar este plano para garantir que nenhuma cena
> exceda os limites do hardware. Inclui criterios de recuo (rollback) quando necessario.

---

## 1. LIMITES DE REFERENCIA (doc/13-spec-cenas.md)

| Recurso | Limite absoluto | Budget conservador |
|---------|-----------------|-------------------|
| VRAM total | 2048 tiles | 1536 tiles (75%) |
| DMA/VBlank (NTSC) | ~7200 bytes | 5000 bytes |
| Sprites/scanline | 20 | 16 |
| Sprites totais (link) | 80 | 40 |

---

## 2. VERIFICACAO DE VRAM

### 2.1. Tabela de ocupacao por cena (pos-integracao)

Para cada cena, preencher:

| Componente | Tiles | Nota |
|------------|-------|------|
| Tiles procedurais (se mantidos) | X | Paper, dither, hatch, fill |
| TILESET cenario | 30 | Por planeta |
| TILESET marcos | 16 | 4 x 4 tiles |
| Sprite player | 16–21 | Corpo + cachecol + halo |
| TILESET UI (se carregado) | 16 | Travel, telas texto |
| Font SGDK | ~80 | Compartilhado |
| **Total cena** | **≤ 1536** | |

### 2.2. Criterio de sucesso

- Total de tiles ativos na cena ≤ 1536.
- Nenhum tile duplicado desnecessariamente (verificar H-flip/V-flip).

### 2.3. Criterio de recuo

Se total > 1536:
- Reduzir tiles do TILESET de cenario (menos variantes).
- Usar carregamento por cena (slot unico) em vez de manter todos os planetas na VRAM.
- Reduzir frames de animacao do player (menos tiles unicos).
- Manter tiles procedurais para UI em vez de ts_ui_panels.

---

## 3. VERIFICACAO DE DMA POR FRAME

### 3.1. Soma por cena (pos-integracao)

| Operacao | Bytes | Cena |
|----------|-------|------|
| PAL_setColors (sky, 6) | 12 | B-612 |
| Hscroll table (224 words) | 448 | Todas com line scroll |
| Vscroll table | 80 | Rei |
| Animacao player | 128 | Planetas |
| Palette cycling | 12–64 | B-612, Travel |
| H-Int palette swap | 12 | Lampiao |
| **Total** | **< budget cena** | |

Budgets por cena: B-612 2000, Rei 2500, Lampiao 2000, Deserto 1500, Travel 1000.

### 3.2. Criterio de sucesso

- Soma < budget da cena.
- Margem de pelo menos 10% (ex: B-612 < 1800 bytes).

### 3.3. Criterio de recuo

Se DMA exceder budget:
- Desabilitar animacao do player na cena mais pesada (ex: Rei).
- Reduzir frequencia de palette cycling (ex: 64 frames em vez de 32).
- Simplificar Hscroll (menos linhas com scroll independente).
- Se DMA > 7000 bytes: cancelar atualizacao de tiles em tempo real; usar apenas palette cycling ou alterar durante fade.

---

## 4. VERIFICACAO DE SPRITES POR SCANLINE

### 4.1. Contagem por cena

| Elemento | Sprites | Linhas tipicas (Y) |
|----------|---------|-------------------|
| Corpo player | 3–4 | screenY a screenY+24 |
| Cachecol (5 segmentos) | 5 | Variado |
| Halo | 1 (2x2) | haloY a haloY+16 |
| Marco | 1 (2x2) | markY a markY+16 |

Pior caso: player em Y=100, cachecol em Y=106–120, halo em Y=42, marco em Y=96. Verificar quantos sprites na mesma scanline.

### 4.2. Criterio de sucesso

- Max 16 sprites em qualquer scanline.
- Distribuicao vertical evita clustering (cachecol e corpo proximos, mas 5+4=9 < 16).

### 4.3. Criterio de recuo

Se sprites/scanline > 16:
- Implementar sprite flickering (alternar par/impar por frame) para cachecol ou halo.
- Reduzir segmentos de cachecol de 5 para 3 em cenas criticas.
- Ocultar halo quando muito proximo do player.
- Reposicionar marco para evitar overlap vertical com player.

---

## 5. PROCEDIMENTO DE TESTE

### 5.1. Pre-requisitos

- Build verde (`build.bat`).
- Emulador com debug de VDP (Blastem preferencial).
- ROM em `out/rom.bin`.

### 5.2. Checklist por cena

Para cada cena (B-612, Rei, Lampiao, Deserto, Travel, Title, Pause, Codex, Credits):

1. [ ] Entrar na cena e observar por 5 segundos.
2. [ ] Verificar ausencia de: crash, freeze, tearing, sprite overflow (invisibilidade).
3. [ ] Se Blastem: inspecionar contagem de sprites por scanline no pior frame.
4. [ ] Anotar qualquer jitter ou flash suspeito (possivel DMA excessivo).

### 5.3. Teste de stress (opcional)

- B-612: deixar palette cycling rodar 100+ frames; verificar estabilidade.
- Lampiao: acender lampiao e verificar H-Int + hilight sem corrupcao.
- Rei: scroll rapido (mover player) e verificar column scroll.
- Deserto: cena mais leve; baseline de performance.

---

## 6. REGISTRO DE VERIFICACAO

Manter em `doc/10-memory-bank.md` ou em anexo:

```
## Verificacao de budgets (YYYY-MM-DD)

| Cena | VRAM tiles | DMA/frame | Sprites/scanline max | Status |
|------|------------|-----------|----------------------|--------|
| B-612 | XXX | XXX | XX | OK / RECUO |
| Rei | XXX | XXX | XX | OK / RECUO |
| ... | ... | ... | ... | ... |
```

---

## 7. DECISOES CONSERVADORAS PREVISTAS (doc MISSION DIRECTIVE)

| Conflito | Acao |
|----------|------|
| DMA > 7000 bytes | Cancelar tiles em tempo real; palette cycling ou fade apenas |
| Sprites > 16/scanline | Flickering imediato |
| Sprites > 80 total | Flickering ou reducao de entidades |
| CPU seno/cosseno gargalo | Migrar para LUT em ROM |
| Arte excede 15 cores | Simplificar; dithering no lugar de alpha |

---

## 8. REFERENCIAS

- `doc/13-spec-cenas.md` — Budgets por cena
- `doc/00-diretrizes-agente.md` — Gate de entrega
- `doc/09-checklist-anti-alucinacao.md` — Gates praticos
