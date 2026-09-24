# Hybrid cleanup shootout — human gate

Decision received: `approve_hybrid_cleanup_shootout`; scale locked at `56x80`. Base pixels may survive, but blind pixel promotion is forbidden.

No numeric score or automatic winner is declared.

| candidate | base route | candidate SHA-256 | observable tradeoff |
|---|---|---|---|
| hybrid_cleanup_primary_im_lanczos3_v01 | im_lanczos3 | 3e60cd9efb233d0ce715c543e9cacdaacbe044b253c088dd06ada52f131b4cf1 | mais contraste local; exige vigilancia de halos e microjaggies |
| hybrid_cleanup_challenger_im_mitchell_netravali_v01 | im_mitchell_netravali | 8e8eb7cbb6d0aaa8906f88f7a12c4352f431d41cd823f57e958c41c3d19bcd61 | contorno mais calmo; perde parte da separacao fina em mao/sash |
| hybrid_cleanup_control_im_catmull_rom_v01 | im_catmull_rom | e4376a53b4aec651b50f57676e2550a14ba738dd01196a850f46a2762fcde45c | controle intermediario; menos contraste e menor ruido de borda |

All candidates are staging-only `technical_candidate` outputs. Review 1x, nearest 8x, light/dark/chroma and the face/guard/sash/feet crops before choosing.

Human gate status: `pending_human_decision`. No candidate is a final pose.
