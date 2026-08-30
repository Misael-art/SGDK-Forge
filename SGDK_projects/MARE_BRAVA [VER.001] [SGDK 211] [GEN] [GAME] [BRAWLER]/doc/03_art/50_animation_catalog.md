---
status: seed
prd_title: Animation Catalog
last_updated: 2026-07-03
---

# Animation Catalog - MARE_BRAVA

Estados por personagem (frames alvo por estado em `doc/contracts/frame_data/`):
- TAINA: idle, walk, jab, cross, lowkick, knee, special, hit_down (8 estados, 4-8 frames cada)
- CRIA: walk, telegraph, attack, hit, down (5 estados)
- ESTIVADOR: walk, grab_telegraph (18f), grab, hit, down (5 estados)
Regras: antecipacao curta + impacto travado (hitstop); sem smear no slice; strips por estado com janela ativa.
Contratos premium de animacao entram na conversao VDP.
