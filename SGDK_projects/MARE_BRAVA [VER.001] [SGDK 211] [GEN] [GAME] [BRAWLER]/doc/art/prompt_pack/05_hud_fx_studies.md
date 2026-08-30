# Prompt 05 — HUD e FX (estudos)

Salvar em: `data/source_art/concept/hud_fx/`
Escopo: concept_art. HUD final é pixel-perfect em grid 8x8 no WINDOW
(`doc/11-gdd.md#ui-pixel-surface-seed`) — estes estudos definem forma e
hierarquia, não os pixels finais.

## Prompt A — frame de HUD

```
Game HUD design study for a 16-bit belt-scroll brawler, single horizontal
bar layout for the top of a 320x224 screen: small square character
portrait frame at left (fits 16x16), a chunky segmented health bar with a
visible "chip damage" trailing segment in a second color, six-digit score
counter right-aligned, all elements on a flat dark strip #111122 with
off-white #F2F2E0 foreground and red #CC2244 danger accent. Flat colors,
hard edges, thick readable shapes, no gradients, no glass effects, no
text other than placeholder numbers "000000", 8:1 wide composition.
```

Aceite: barra lê a 2 metros; segmento de chip damage visualmente distinto;
formas grossas que sobrevivem a 8x8.

## Prompt B — hitspark e splash (FX do golpe e do ring-out)

```
Sprite effect design studies on one dark sheet, arranged in rows with
3 frames each: row 1) small geometric impact spark (sharp 4-point star
bursting into shards, off-white #F2F2E0 core with #FF5533 edge), row 2)
medium hit burst, row 3) large water splash for a dockside knockout:
column of sea water #3A6B7A with bold white foam shapes rising then
falling, reads as a satisfying payoff. Flat cel shapes with hard edges,
strong silhouettes, no gradients, no soft glow, no photorealism, each
frame clearly separated, no text.
```

Aceite: cada frame legível isolado; splash tem 3 fases claras
(subida/ápice/queda); shapes fecham em poucas cores.

## Lembrete de gameplay (do GDD)

Splash + shake + score bonus acontecem JUNTOS no ring-out — o splash é
consequência mecânica, não decoração. O estudo precisa parecer "peso caindo
na água", não chafariz ornamental.
