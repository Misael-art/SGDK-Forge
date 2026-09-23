# Caderno de aprendizado — palco Showdown no HAMOOPIG

**Para o proximo agente e para a curadoria humana do workflow engine.**
Nao e canon. Nao e AAA. `canonical_promotion_performed=false`.

Projeto: `SGDK_projects/HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]`.
ROM vigente ao fechar este caderno:
`1eb99f6c33cc6fe1c7fb776f5635f31b453a6419f27ff77cd4a215db9e6b00d6` (2.490.368 B).

Hierarquia de verdade: `doc/10-memory-bank.md` > changelog > este caderno.

---

## 0. O que esta entrega e (e o que nao e)

O palco vivo da luta passou a ser o park Showdown (X-Men vs Street Fighter),
traduzido para uma IMAGE 512x256 em BG_B. A fonte e o GIF de estudo em
`data/source_art/showdown/` mais o `showdown.def` MUGEN (camera e deltas).

Nao declare: `ready_for_aaa`, `validado_budget`, pixel nativo final,
parallax executado, IP Capcom, bundle BlastEm selado.

Status maximo: `buildado` + palco observado no BlastEm. Arte: `placeholder`
/ `compare_flat_runtime_prototype`. Mesma politica de Ken.

---

## 1. Doutrina operacional medida nesta sessao

1. **Palco de luta CPS2 nao cabe cru no Mega Drive.** Unique 8x8 nativo ~3191.
   Quatro paletas ja estao tomadas (BG, HUD, P1, P2). Sem segundo plano
   paletavel, a rota honesta e `compare_flat`.
2. **O GIF de 17 frames pode ser estatico.** Aqui os 17 frames sao RGB
   identicos; a agua animada do MUGEN BG2 nao veio no GIF. Nao gaste VRAM
   com animacao que o arquivo nao tem.
3. **Bloco 4px + 10 cores 9-bit** derrubou unique tiles de milhares para 444
   (ResComp BEST ainda funde flip e empacota 257 tiles / 8224 B). Massas do
   park (ceu, serra, arvore, agua, margem) continuam legiveis. Detalhe fino
   morre. Teto de claim: placeholder.
4. **`showdown.def` e o contrato de camera, nao o runtime.** boundleft/right
   ±224, boundhigh -240, verticalfollow 0.5, tension 50, zoffset 215.
   No MD: H travel 192 px (512-320), V travel 32 px (256-224). Plano VDP
   64x32 = 512x256; V extra alem de 32 px exigiria mapa 64x64 e mais tiles.
5. **Rest precisa esconder o headroom, nao o chao.** `vscroll = height-224`
   no idle. Pulo diminui vscroll (olha para cima). Invertido, o chao some
   e o ceu vira faixa morta.
6. **`verticalfollow 0.5` e `camPosY = air/2`.** Sprite e sombra recebem
   `+camPosY` para andar com o chao. Spark e fireball tambem, senao o hit
   aereo nasce no mundo sem a camera.
7. **WINDOW de 5 rows (40 px) come o V travel de 32 px.** O ceu extra do
   pulo fica debaixo do HUD. A prova do follow e o parque inteiro descer
   no ecran e o jumper nao escapar do topo, nao uma fatia de ceu nova.
8. **zoffset MUGEN nao e `gAlturaPiso` HAMOOPIG.** O builder achatou 448 px
   de altura em 256; a margem amarela (agua) come o near-bank. Lutadores
   parecem estar *na* agua. Mapear a linha de chao no PNG convertido, nao
   copiar 215 cego.
9. **Deltas de parallax sem plano/paleta livre sao documento, nao FX.**
   BG0 0.43/0.285, BG1/BG2 0.71/0.635, BG3 1/1 ficam no contrato. Executar
   agora seria mentir (um so pal, um so plano).
10. **Screenshot e o beat.** Bundle VLAB continua `blocked`. Idle/walk/jump
    PNGs com hash da ROM valem mais que o selo recusado.

---

## 2. Checklist de palco de luta (HAMOOPIG)

| Item | Owner local | Showdown |
|---|---|---|
| Fonte em `data/source_art/<stage>/` com GIF/DEF e hash | art | sim |
| Converter gera IMAGE indexada 8x8, 9-bit, unique tiles medidos | `convert_showdown.py` | 604 no exportador / 385 tiles ResComp |
| Contrato de camera (H/V travel, follow, clamp) ao lado do PNG | `doc/art/showdown/camera_motion_contract.json` | sim |
| `IMAGE` no `.res` + proveniencia `procedural_composed_from_authored` | `res/gfx.res` / manifest | `gfx_showdown` |
| Load PAL0 apos BG, tileset soma em `gInd_tileset` antes do HUD | `init.c` | sim |
| `gBG_Width`/`gBG_Height` reais, nao 320x224 copiado | globals/init | 512x256 |
| Camera H no medio dos dois, clamp 0…width-320 | `FUNCAO_CAMERA_BGANIM` | sim |
| Camera V follow no ar, rest vscroll = height-224 | idem | 32 px |
| Sprites de luta/sombra/FX usam camPosX e camPosY | graphics/fsm/physics | sim |
| Parallax so se houver plano+paleta livres; senao gravar e nao executar | contrato | gravado |
| IP de estudo = placeholder, mesmo teto do Ken | proveniencia | Capcom XMvSF |
| BlastEm idle + walk H + jump V com o mesmo hash | evidencia | 225648Z |

---

## 3. O que funcionou e o que nao

Funcionou:

- Copiar o GIF para dentro do projeto (nao apontar para outro workspace).
- Medir unique tiles *antes* de escolher TILEMAP vs IMAGE.
- `compare_flat` quando 4 paletas e ~3191 tiles bloqueiam multi-plano.
- Rest vscroll=32: margem amarela e arvore visiveis, HUD WINDOW intacto.
- Walk left vs right muda o recorte da serra/arvore (H camera viva).
- Jump peak: P1 no ar, P2 no chao, clock 99, ~60 fps.
- Hit com spark no park (`07_hit.png` clock 88).

Nao funcionou / nao e esta entrega:

- Manter o detalhe nativo do GIF (bloco 4px e o preco da residencia).
- Agua animada (frames identicos).
- Parallax de 3 camadas.
- V travel MUGEN de 240 px.
- Chao visual alinhado ao zoffset 215 apos o squash 448→256.

---

## 4. Propostas para curadoria (nao aplicadas)

1. Owner `multi-plane-composition`: quando `compare_flat` for a unica rota
   de um palco CPS, exigir contrato de camera + unique-tile budget +
   `parallax_executed: false` explicito. Nao vender 3 camadas no claim.
2. Owner `camera-system-sgdk`: fighting camera e um owner so. H no medio,
   V follow 0.5, rest vscroll = height-224, sprites `+camPosY`. WINDOW HUD
   nao e camera.
3. Owner `art-conversion-pipeline`: palco 512x256 com bloco NxN so depois
   de medir unique tiles; 4px foi o degrau que coube (444). 2px fica como
   proxima medicao, nao como default.
4. Owner `megadrive-vdp-budget-analyst`: plano 64x32 esgota a altura; V
   extra exige 64x64 e recontar tiles. Nao assumir que height>256 "so
   scrolla".

Toda proposta permanece `not_applied`. Humano decide. Capture nao edita
`.agent`.

---

## 5. Evidencia

- ROM estável `363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f`
- BlastEm 59.6 fps `out/emulator_evidence/interactive-showdown-20260911T225648Z/`
- `01_idle_hud.png` park + barras + clock 98
- `02_walk_left.png` / `03_walk_right.png` H scroll
- `05_jump_peak.png` P1 aereo, clock 99
- `06_land.png` retorno
- `07_hit.png` spark + clock 88
- Fonte GIF sha256 `04060f6ed50702894b36804c4d9f578818e595c4a3c2ea1ee01db065d9037f68`
- PNG `res/gfx/showdown.png` sha256 `bb70df8d61ffce1ac21d2a4e2a59030e02d6851854bcce51edb2b24ee3ca2f8e`

## 6. Experimento 2x2 rejeitado (2026-09-12)

- A variante `BLOCK=2` reduziu o cenário para 1.393 tiles e parecia mais
  próxima do preview do laboratório, mas exigiu `SPR_initEx(320)`.
- A captura `interactive-round-integrity-20260912T132630Z` mostrou corrupção
  severa de HUD, mapa e sprites: a reserva de 320 tiles não absorve as
  animações simultâneas dos dois lutadores.
- Decisão: restaurar `BLOCK=4` e `SPR_init()`; ROM estável preservada
  (`363774d9`). O próximo ganho visual deve vir de streaming/multi-plane
  medido, não de reduzir cegamente a reserva do Sprite Engine.
