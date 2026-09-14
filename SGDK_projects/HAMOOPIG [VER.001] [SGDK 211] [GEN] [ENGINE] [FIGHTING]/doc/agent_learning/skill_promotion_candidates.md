# Skill Promotion Candidates

Este arquivo lista candidatos locais que talvez merecam virar skill, workflow, regra, script ou `lib_case` canonico no futuro.

Nenhum item aqui esta promovido.

| Data | Classificacao | Candidato | Problema resolvido | Evidencia minima | Risco | Proxima revisao humana |
|---|---|---|---|---|---|---|
| 2026-08-18 | `promotion_candidate` | Patch em sgdk-runtime-coder: unpack IMAGE BEST e load-time | Impedir unpack APLIB no display; dest estatico; assar TILE_ATTR; DataRect+DMA | ROM e6437530/ceaa7028; d3/d4 cpu 160→83 | medio (API dest.tilemap) | Humano confirma texto da skill + teste de unpack |
| 2026-08-18 | `promotion_candidate` | Patch em emulator-vdp-evidence-curator: VLAB != beat | Screenshot e autoridade; frame_counter e degrau de 60; void escuro pode ser recusado e ainda ser evidencia | d2_reveal/d2_lock mesmo F151; d5_sky rejected | baixo | Humano aceita nota no selo |
| 2026-08-18 | `promotion_candidate` | Patch em shadow-highlight-scroll-fx: VSCROLL_COLUMN nao e cortina | Nao vender coluna como lift local da COIFA | pres4/pres6; memoria | baixo | Ja esta na doutrina; so explicitar o anti-padrao |
| 2026-09-11 | `promotion_candidate` | Patch em sgdk-runtime-coder + fighting-game-design: checklist de onboarding de lutador | Lutador novo sem case de hitbox/paleta/550/MODE/seletor vira fantasma; Ken e Musgo repetiram o mesmo buraco | ROM c81fee9f…; musgo_roster_lessons.md secao 2; Ken 05_ken_attack.png | medio (HAMOOPIG-especifico ate provar em outro fighting) | Humano confirma checklist na skill, sem criar skill nova |
| 2026-09-11 | `promotion_candidate` | Patch em sprite-animation: harvest video-first | Path com `%` quebra ffmpeg `%03d`; video de golpe pode sair do perfil no impacto | musgo_roster_lessons.md secao 3; haymaker.jpg | baixo | Humano aceita nota de harvest + hibrido keypose |
| 2026-09-11 | `promotion_candidate` | Patch em art-translation-to-vdp: downscale direto | downscale direto + quantizacao global de concept IA para sprite de luta fica source_candidate | screenshot seletor Musgo vs Ryo; ROM c81fee9f… | medio | Humano confirma teto de claim; fixture 48x64/80x104 |
| 2026-09-11 | `promotion_candidate` | Patch em emulator-vdp-evidence-curator: engine sem VLAB | Bundle blocked `vlab_block_missing` com screenshot de seletor valido; screenshot e o beat | blastem-linux-20260911T212135Z-1769103/screenshot.png | baixo | Humano aceita evidencia informal vs selo para ports de engine |
| 2026-09-11 | `promotion_candidate` | Patch em multi-plane-composition + camera-system-sgdk: palco CPS compare_flat | Unique tiles nativos e 4 paletas forcam IMAGE unica; camera H/V precisa de contrato (rest vscroll, follow 0.5, sprites +camPosY); parallax so no papel | ROM 1eb99f6c…; showdown_stage_lessons.md; 01_idle_hud / 03_walk_right / 05_jump_peak | medio (HAMOOPIG-especifico ate outro fighting) | Humano confirma nota nas skills existentes, sem skill nova |


## Criterios minimos

- Deve ter sido usado com sucesso em contexto real do projeto.
- Deve reduzir erro recorrente, custo de producao ou ambiguidade.
- Deve ter limites declarados.
- Deve exigir revisao humana antes de qualquer mudanca canonica.
