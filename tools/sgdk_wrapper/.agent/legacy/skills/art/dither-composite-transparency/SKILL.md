# dither-composite-transparency

Use when an asset or scene simulates transparency with checkerboard dithering, composite-video blending, smoke, water, glass, shadows or soft light.

## Purpose

Separate real Mega Drive constraints from modern preview illusions. Dithering can look blended on CRT/composite output but may look like a visible mesh on sharp displays.

## Required Inputs

- Target display assumption: raw pixels, CRT shader, composite blend, RGB capture or emulator screenshot.
- Pattern size and alignment.
- Affected palette and priority.
- Gameplay readability requirement.

## Required Outputs

- Dither pattern spec.
- Display-risk statement.
- Capture/profile matrix: raw RGB/LCD, CRT shader and composite-style capture
  expectations.
- Priority and collision implications.
- Capture mode required for approval.

## Hard Rules

- Do not call dithering alpha blending.
- Do not hide collision-critical objects behind noisy dither.
- Do not approve the effect from a single scaled screenshot.
- Do not make composite-video blending a required gameplay condition. If raw
  pixels show a harsh mesh, the design needs a readable fallback.
- 50 percent checkerboard mesh is a specific display-dependent effect, not a
  general transparency system.
- Dither must be locked to pixel grid and motion cadence; moving mesh can shimmer
  or flicker on modern displays.

## Candidate Curation Note

Source: attached graphical-tricks transcript summary reviewed on 2026-06-17,
`E1_text`. The retained improvement is stricter display-risk handling:
composite/CRT fusion may be an intended presentation, but final gameplay still
needs a readable capture profile and fallback.

## Handoff

- Use `palette-cram-curator` for contrast.
- Use `visual-excellence-standards` for readability and style.
- Use `emulator-vdp-evidence-curator` before final visual claims.
