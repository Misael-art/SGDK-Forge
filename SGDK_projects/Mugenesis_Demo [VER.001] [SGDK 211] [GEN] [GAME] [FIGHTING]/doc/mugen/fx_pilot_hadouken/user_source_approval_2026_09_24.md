# Human acceptance record — Hadouken source pose

Date: 2026-09-24

## Decision

The user accepted the attached Hadouken image for the game's context, with the qualification that it remains selected unless a better result is found. The technical comparison did not demonstrate a better result, so this source pose remains the selected visual direction.

## Hash-bound identity

- User attachment: `codex-clipboard-892bf7d4-74c4-408d-8e5a-e2f35808a46d.png`
- Attachment SHA-256: `a27fba0915dc079d4e6638ddebf9a0efd652a19c69432762250a61855d92a463`
- Project source copy: `rascunho/processado/fx_pilot_hadouken/source_750_1.png`
- Project source SHA-256: `2a60f8b75e12156a6d4c8e2fb2a3bbb099cf4ed38a9210e3cd9a63d443764164`
- Identity check: both are 56x28 RGBA. Alpha masks match; all 1,154 visible pixels match exactly. The 414 alpha-zero pixels have different hidden RGB: attachment `(0,0,0)`, project copy `(250,0,250)`. This difference is invisible and does not alter the accepted silhouette or transparency.

## Approval scope

This decision approves the visual source pose and its use as the project's selected direction. It does not approve a palette remap, slot 6 (`0xE82` or another word), an indexed candidate hash, conversion of the remaining AIR elements, production `res/` promotion, runtime integration, or ROM evidence. Those decisions remain separate gates.
