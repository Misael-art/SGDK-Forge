# Art Generation Brief - MARE_BRAVA (CAIS_01)

Pronto para disparo assim que houver canal de geracao (ver `out/logs/generation_channel_decision.json`).
Persistencia obrigatoria: `data/source_art/` + `premium_source_manifest` + aprovacao humana ANTES de conversao para `res/`.

---
context_pack_manifest:
  docs: doc/11-gdd.md, doc/13-spec-cenas.md, doc/art/master_style_manifest.json, doc/art/art_direction_decision_record.json, doc/art/moodboard_manifest.json
  style_catalog: tools/sgdk_wrapper/.agent/references/art_style_catalog.json
  style_anchor: mare_brava_master_v1 (angular_cps2_fighter)

art_generation_brief:
  - target: sprite_sheet
    character: TAINA, 48px altura (frame 48x48), 3.5 heads, muay thai de vila, top esportivo + calca de treino com faixa, silhueta com diagonais
    palette: dominio pal1_heroina (15 cores + index 0): FF5533 / 2E1F3A / F2C29A / 1A6B5A + ramps hue-shift
    action_states: idle, walk, jab, cross, lowkick, knee (aereo), special (A+B), hit_down (minimo 8)
    format: PNG indexado, grid 8x8, PLTE <= 16 cores, index 0 transparente
    prompt_base: "angular arcade fighter anatomy, sharp cel-shadow muscle planes, vibrant limited palette, clean outline pixel clusters, expressive impact poses, late afternoon warm sunlight, brazilian coastal dock 1990s"
    negative: "recolored commercial sprites, neutral gray ramps, soft AA edges, photo realism, AI glow, copying iconic fighter poses"
  - target: sprite_sheet
    character: CRIA, 44px (frame 48x48), rusher magro inclinado para frente, camiseta regata
    palette: dominio pal2_inimigos
    action_states: walk, telegraph (corrida armada), attack, hit, down (minimo 5)
    format: PNG indexado, grid 8x8, PLTE <= 16 cores, index 0 transparente
  - target: sprite_sheet
    character: ESTIVADOR, 56px (frame 56x56), grappler de massa quadrada, colete de carga
    palette: dominio pal2_inimigos (compartilhada com CRIA)
    action_states: walk, grab_telegraph (bracos abertos 18f), grab, hit, down (minimo 5)
    format: PNG indexado, grid 8x8, PLTE <= 16 cores, index 0 transparente
  - target: background_tilemap
    scene: cais de Porto Bravo ao entardecer; BG_A cais jogavel 1344x224 (madeira, caixotes do sindicato, guindaste, barco, beirada com espuma); BG_B mar/ceu 512x224 loop para line-scroll 2 faixas
    palette: dominio pal0_cenario; espuma compartilha pal3
    format: PNG indexado por plano, grid 8x8, PLTE <= 16 cores por plano
    megadrive_rules: sem alpha blending, index 0 transparente, 320x224 viewport
  - target: title_screen
    ref: doc/art/brand_identity_manifest.json (logo MARE BRAVA com quebra de onda, press start, mar em loop)
    palette: pal3_hud para logo, pal0 para mar
  - target: hud_element
    itens: health bar 40x8, fonte 8x8 (0-9 A-Z), retrato TAINA 16x16, hitspark 8x8 (3 frames), splash 32x32 (3 frames)
    palette: pal3_hud
---

Regras herdadas: `doc/art/style_drift_policy.json` define drift e obriga correction brief antes de regerar.
