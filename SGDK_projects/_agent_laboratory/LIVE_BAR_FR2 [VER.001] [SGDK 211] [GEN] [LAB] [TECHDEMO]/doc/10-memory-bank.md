# 10 - Memory Bank — LIVE_BAR_FR2

**Ultima atualizacao:** 2026-08-29
**Fase:** laboratorio F-R2 (idle + walk 3/4 + punch)
**lab_not_delivery:** true

## Status

- buildado: sim (`out/rom.bin` 131072 B, sha256 `a34c2d0fd8f074b0dee1cb84c6468b91a36f8647da168f91fa1071a1d9cd79da`)
- testado_em_emulador: parcial — BlastEm screenshot + runtime_animation.gif + semantic gate `passed` (`blastem-linux-20260829T160037Z-2172149`)
- ready_for_aaa: false
- live_scene_bar: `needs_review` (fixture de paleta+motion; nao e aaa_game)

Sheet: 192x192, anim 0 idle, anim 1 walk, anim 2 punch, celula 48x64.
Punch times 8-4-10-12, loop off. Alcance do soco curto; pernas ainda salsicha.
Screenshot BlastEm ainda parece walk; as 4 fases do golpe estao na sheet nativa.
