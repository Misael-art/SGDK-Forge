# Hibrido Fighter v007 Generation Brief

Status: `blocked_image_tooling`

Goal: generate a corrected canonical source candidate after v006 rejection.

## Required Corrections

- Lava/stone arm must always end in a clear readable rock hand/fist.
- The rock/lava hand must never be missing, cropped, amorphous, wrapped or gloved.
- Every pose must still have exactly 2 arms, 2 legs, 1 head and 1 torso.
- Scale, costume markers, red armband and back pose remain required.
- Reduce visual noise: no spray texture, no micro-detail fields, no noisy dithering.
- Shading must be cluster-based with 2-3 well-spaced tones per material.
- Silhouette and material contrast must read before internal detail.
- Character body must be planned around one 16-entry palette: 15 useful colors plus transparency.
- Runtime art must later be indexed PNG with controlled palette and index 0 transparency.
- Align future sprite blocking, cells, pivots and sheet areas to multiples of 8 px.

## Locked Character Design

- Warm bronze skin.
- Black spiky hair.
- Black Muay Thai shorts with gold trim.
- Dirty white wraps on the human hand and feet.
- Red armband on the non-lava biceps.
- Lava arm and lava hand: exposed dark volcanic rock with orange magma cracks, no wrap/glove/bandage.
- Detached FX may use a separate palette/strip; body sheet should not depend on FX colors.

## Prompt Seed Text

Create a clean canonical production model sheet for an original 16-bit fighting game Muay Thai hybrid fighter. Five full-body poses on the same ground baseline: front idle, back view, guarded step, knee strike, teep kick. Same character scale and costume in every pose. The lava arm and lava hand are always exposed dark cracked rock with a clear rock fist/hand in every pose; no wrap, glove or bandage on that arm. Use simple cluster shading, 2-3 tones per material, strong silhouette, hard outlines, limited Mega Drive-friendly palette, no spray texture, no micro-detail noise, no blur, no anti-alias look, no text.

## Tooling Status

- Native image generation attempt: failed with service/server error in this session.
- Local `imagegen_circuit.py preflight`: `license_blocked`; Bonsai license ack missing and host gate failed.
- No v007 source image was promoted.
