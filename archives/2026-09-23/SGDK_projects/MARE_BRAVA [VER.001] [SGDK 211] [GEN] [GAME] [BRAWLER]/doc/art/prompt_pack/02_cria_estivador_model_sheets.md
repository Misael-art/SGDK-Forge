# Prompt 02 — CRIA e ESTIVADOR source candidates

Salvar cada asset em:

- `data/source_art/concept/cria_identity_model_sheet/`
- `data/source_art/concept/cria_attack_telegraph_sheet/`
- `data/source_art/concept/cria_hit_down_poses/`
- `data/source_art/concept/estivador_identity_model_sheet/`
- `data/source_art/concept/estivador_grab_telegraph_sheet/`
- `data/source_art/concept/estivador_hit_down_poses/`
- `data/source_art/concept/character_silhouette_comparison/`

Escopo: `concept_art` / `source_candidate`. Leia junto:
`doc/art/authorial_line_style_contract.json`.

Os dois inimigos compartilham UMA paleta de 15 cores no jogo: azul `#4A5C8A`,
vermelho `#CC2244`, couro `#8A6B4A`, escuro `#2A2A3A`.

## Contraste autoral do trio

- TAÍNA: diagonal controlada, guarda alta, faixa lateral.
- CRIA: flecha nervosa, inclinado para frente, cotovelos/pés pontudos.
- ESTIVADOR: bloco quadrado, braços abertos, luvas/corda/botas pesadas.

Se as três silhuetas em preto puro não forem distinguíveis em 1 segundo, o
asset falhou.

## Prompt A — CRIA identity model sheet

```
Use case: stylized-concept
Asset type: enemy model sheet source candidate, not final sprite
Primary request: model sheet for CRIA, a lean fast Brazilian dockside rusher
enemy for a 1990s coastal brawler.

Subject: male late teen, wiry thin build, body naturally leaning 30 degrees
forward as if always about to sprint. Narrow shoulders, pointy elbows, thin
fast legs, cheap cap backwards as a small wedge shape, faded blue sleeveless
shirt, rolled shorts, flip-flops or barefoot, one small red accent. No weapon.

Authorial line contract: variable dark contour, sparse angular cuts, nervous
thin silhouette, wedge chin, narrow eyes, tense mouth, pointy elbows and knees.
He must read as fast and fragile, not as a generic punk or armed gang member.

Composition: front standing, side standing, sprinting lunge telegraph, wild
haymaker, flinching hit reaction, knocked down, all separated on neutral flat
background.

Style/medium: hand-drawn 16-bit arcade concept art, hard cel shading, 2-3
tones per material, hue-shifted shadows, high black-silhouette readability.

Constraints: no knife, no gun, no gang cliché, no text, no logos, no extra
limbs, no generic muscular thug, no soft airbrush, no gradients.
```

## Prompt B — CRIA attack telegraph sheet

```
Use case: stylized-concept
Asset type: attack telegraph key pose sheet source candidate
Primary request: 12 separated key poses showing CRIA's forward-leaning sprint
attack startup from anticipation to strike.

Preserve: 30-degree forward body lean, backwards cap wedge, narrow shoulders,
pointy elbows, faded blue sleeveless shirt, fragile fast silhouette. The attack
must be understandable from pose alone, no weapon.

Authorial line contract: nervous angular contour, sharp elbows/knees, small
fast fists, tense wedge face. Each pose must read as "fast fragile rusher" in
pure black silhouette.

Constraints: no final animation strip claim, no motion blur, no text, no
weapon, no generic street thug.
```

## Prompt C — CRIA hit/down poses

```
Use case: stylized-concept
Asset type: hit and down key pose sheet source candidate
Primary request: CRIA hit reaction and knockdown poses: light flinch, heavy
hit recoil, airborne knockback, sliding fall, prone down pose, getting-up
anticipation.

Preserve authorial hooks: forward wiry body, cap wedge, pointy elbows, thin
legs, nervous face. Flat hard cel shading, neutral background, no text.
```

## Prompt D — ESTIVADOR identity model sheet

```
Use case: stylized-concept
Asset type: enemy model sheet source candidate, not final sprite
Primary request: model sheet for ESTIVADOR, a heavy Brazilian dock worker
grappler enemy for the same brawler.

Subject: male in his 40s, massive square torso like a cargo block, thick arms,
wide stance, cargo work vest over bare chest, heavy canvas pants, worn work
boots, thick leather gloves, rope coil on one side of the belt. Heavy face:
wide jaw, low brow, simple stubble mass, slow dangerous stare.

Authorial line contract: square mass shapes, heavy dark contour, wedge shadows,
huge glove hands, rope coil silhouette, boots anchoring weight. He must read as
slow, heavy and dangerous up close, not a clean bodybuilder, sailor caricature
or final boss monster.

Composition: front standing, side standing, slow advancing step with both arms
spread wide open, bear-hug grab, overhead slam follow-through, heavy hit
reaction, knocked down, all separated on neutral flat background.

Style/medium: hand-drawn 16-bit arcade concept art, hard cel shading, 2-3
tones per material, hue-shifted shadows, high black-silhouette readability.

Constraints: no text, no logos, no extra limbs, no glossy bodybuilder anatomy,
no fantasy boss armor, no soft airbrush, no gradients.
```

## Prompt E — ESTIVADOR grab telegraph sheet

```
Use case: stylized-concept
Asset type: grab telegraph key pose sheet source candidate
Primary request: 18 separated key poses showing ESTIVADOR's slow dangerous
grab approach: weight shift, arms opening, chest forward, huge gloved hands
ready to grab, final commit.

Preserve: square torso, thick arms, open grab silhouette, rope coil, heavy
boots, low brow. Every pose must read in black silhouette as "slow heavy
grappler, dangerous up close".

Constraints: no final animation strip claim, no text, no extra limbs, no clean
bodybuilder, no boss exaggeration beyond enemy scale.
```

## Prompt F — ESTIVADOR hit/down poses

```
Use case: stylized-concept
Asset type: hit and down key pose sheet source candidate
Primary request: ESTIVADOR hit reaction and knockdown poses: small hit
reaction with heavy poise, stagger, pushed-back recoil, falling backward,
heavy ground impact, prone down pose, getting-up anticipation.

Preserve authorial hooks: square block torso, huge glove hands, rope coil,
heavy boots, low brow. Flat hard cel shading, neutral background, no text.
```

## Prompt G — teste conjunto de silhueta

```
Use case: stylized-concept
Asset type: black silhouette comparison board
Primary request: pure black filled silhouettes on a light neutral background,
showing TAÍNA, CRIA and ESTIVADOR side by side in idle/telegraph poses.

TAÍNA must read as controlled diagonal muay thai guard with sash. CRIA must
read as forward-leaning nervous rusher. ESTIVADOR must read as square heavy
grappler with arms open. No internal detail, no text, no background scene.
```

## Critérios de aceite

- [ ] CRIA inclinado e frágil, nunca capanga armado genérico.
- [ ] ESTIVADOR quadrado e pesado, nunca bodybuilder limpo.
- [ ] Telegraphs de CRIA (12f) e ESTIVADOR (18f) funcionam em silhueta.
- [ ] Trio TAÍNA/CRIA/ESTIVADOR distingue-se em preto puro.
- [ ] Paleta e materiais cabem em meia/uma paleta compartilhada.
