# Runtime Scene Contracts

## Objetivo

Congelar contratos de runtime que quebram cena, loop ou composicao quando esquecidos.

## 1. Ordem canonica do loop

```c
while (TRUE) {
    INPUT_update();
    APP_update();
    SPR_update();
    SYS_doVBlankProcess();
}
```

Regras:

- `INPUT_update()` primeiro
- update de cena depois
- `SPR_update()` antes do VBlank process
- `SYS_doVBlankProcess()` fecha o frame

## 2. Reset ao sair da cena

Ao voltar de uma cena com scroll, sprites ou HUD, revisar:

- `SPR_reset()`
- `VDP_clearPlane(BG_A, TRUE)`
- `VDP_clearPlane(BG_B, TRUE)`
- `VDP_setHorizontalScroll(BG_A, 0)`
- `VDP_setHorizontalScroll(BG_B, 0)`
- limpeza de WINDOW/texto
- reset de callbacks especiais se existirem

Sem isso:

- sprites fantasma
- scroll residual
- corrupcao da proxima cena

## 3. Transparencia e index 0

- `index 0` e a ancora de transparência entre planos
- para composicao `BG_B -> BG_A`, o PNG de `BG_A` precisa sair indexado com `transparency=0`
- nao assumir que o exportador fez isso sozinho

## 4. Wrapping de scroll

- em plano `64x32`, o wrap horizontal vem do proprio plano
- nao adicionar codigo de infinito fake sem necessidade
- primeiro provar que o plano nao esta resolvendo sozinho

## 5. TILE_USER_INDEX e empilhamento

Padrao:

```c
u16 ind = TILE_USER_INDEX;
VDP_loadTileSet(bg_a.tileset, ind, DMA);
ind += bg_a.tileset->numTile;
VDP_loadTileSet(bg_b.tileset, ind, DMA);
ind += bg_b.tileset->numTile;
```

Regra:

- nunca empilhar tilesets no escuro
- sempre declarar quem entrou primeiro e quanto consumiu

## 6. IMAGE vs MAP

Escolha `IMAGE` quando:

- a arte cabe no plano
- nao precisa de streaming de mapa
- o objetivo e scroll simples

Escolha `MAP` quando:

- a fase excede o plano efetivo
- precisa de scroll amplo e streaming
- o mapa deve ser tratado como mundo, nao como imagem unica

## 7. Contrato de transicao

Toda cena deve declarar:

- o que aloca
- o que precisa ser resetado
- o que pode vazar para a proxima cena
- qual callback global ela mexe
