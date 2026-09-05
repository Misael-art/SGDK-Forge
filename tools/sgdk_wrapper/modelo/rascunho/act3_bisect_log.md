# Act 3 bisect log (measurement only)

Baseline ROM `43854ac6…` = re4/re6/re8.
Capture command: warmup 6s → screenshot is F451. Burst delay 0 → animation_frames are early (not act 3).

## Baseline F451 (`out/evidence/re6/`)

- magenta letterbox: black in screenshot (curtain gap also black)
- wordmarks: MASTER visible; MISAEL not readable (covered by MASTER at F430+)
- anvil: corrupted, brick tiles showing through

## BISECT 6 — disable `sVramAuthor = sVramBgA` (free VRAM after hammer window)

- evidence: `out/evidence/bis_6/blastem-linux-20260817T193054Z-231287`
- frame_counter: 451, over_budget: 0, cpu 96, sealed
- magenta: unchanged (letterbox still black)
- wordmarks: unchanged (MASTER still there, MISAEL still covered)
- anvil: SURVIVED — horn, face, rings readable
- **reveals symptom 3 (anvil gone / corrupted)**

## BISECT 1 — disable curtain (`VDP_setVerticalScrollTile`)

- evidence: `out/evidence/bis_1/blastem-linux-20260817T193233Z-234997`
- frame_counter: 451, over_budget: 0, sealed
- curtain: gone (wall fills the frame) — expected
- magenta: unchanged (letterbox still black)
- wordmarks: MASTER still visible — curtain was NOT covering it
- anvil: still corrupted (VRAM reuse back on)
- **does not reveal symptoms 1, 2 or 3**
- H2 rejected: wordmark missing is not the curtain

## BISECT 5 — disable `SPR_reset()`

- evidence: `out/evidence/bis_5/blastem-linux-20260817T193349Z-238016`
- frame_counter: 451, over_budget: 8, cpu 136, sprite_links 63
- magenta: unchanged (letterbox still black)
- wordmarks: MASTER still there
- anvil: still corrupted
- extra: ember sprite still sitting on MASTER
- **does not reveal symptoms 1, 2 or 3**
- H4 rejected for SPR_reset: it does not restore magenta

## BISECT 2 — disable project wordmark (`f == 430`)

- evidence: `out/evidence/bis_2/blastem-linux-20260817T193503Z-240962`
- frame_counter: 451, over_budget: 0, cpu 92, sealed
- magenta: unchanged (letterbox still black)
- wordmarks: MASTER gone; MISAEL now readable over the anvil; FORGE cleaner
- anvil: less corrupted than baseline (project's 143 tiles were not overwritten)
- **reveals that author wordmark WAS drawn** — at F451 it is only hidden by the project tilemap
- **amplifies symptom 3**: project draw overwrites more of the live BG_A tileset/tilemap

## BISECT 3 — disable presents (`f == BRAND_V2_PRESENTS_IN`)

- evidence: `out/evidence/bis_3/blastem-linux-20260817T193655Z-245060`
- F451 screenshot identical to baseline (presents is F480; not executed yet)
- **does not reveal symptoms 1, 2 or 3 at F451**

## BISECT 4 — disable fade (`PAL_fadeOutAll`)

- evidence: `out/evidence/bis_4/blastem-linux-20260817T193725Z-246685`
- F451 screenshot identical to baseline (fade is F510+; not executed yet)
- **does not reveal symptoms 1, 2 or 3 at F451**

## Map (F451 screenshot is the act 3 sample; burst frames are pre-act-3)

| Symptom | Which disablement changed it |
| magenta borders | none of the 6. F451 letterbox stayed black in every shot. Magenta appears only in burst frame_1 (act 1 start), unchanged across all builds. |
| wordmarks missing | point 2 removed MASTER and revealed MISAEL underneath. Author WAS drawn; at F451 it is covered by the project tilemap. Point 1 (curtain) did not hide/show them. |
| anvil gone | point 6 (stop `sVramAuthor = sVramBgA`). Point 2 reduces the damage (fewer tiles overwritten) but does not restore the anvil. |

## Fix applied

Only the measured cause of symptom 3: wordmarks load after the hammer window, not on top of `sVramBgA`.
