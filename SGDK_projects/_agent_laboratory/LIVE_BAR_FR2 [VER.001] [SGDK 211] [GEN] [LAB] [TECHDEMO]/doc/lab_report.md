# Lab report — LIVE_BAR_FR2

`lab_not_delivery=true`

Axioma R2: PAL0 heroi, PAL1 thug, PAL2 cais, PAL3 FX.

Idle (anim 0), walk 3/4 (anim 1) e punch (anim 2) no mesmo SPRITE
192x192. ROM troca a cada 2 s; punch toca uma vez (8-4-10-12) e
segura recovery. Agua PAL2 cicla.

Punch: anticipation / active / hitstop / recovery. Heroi = punho
com corda enrolada (nao laco). Thug = cruzado de esquerda. Pixels
nativos no grid 48x64, nao downscale do video. Alcance curto
(punho do heroi ja na borda da celula). Pernas ainda salsicha.

Screenshot BlastEm ainda parece walk/guarda. Kit R2 de motion do
fixture: idle+walk+punch. Nao e jogo AAA.
`ready_for_aaa=false`. `visual_pass=false`.
