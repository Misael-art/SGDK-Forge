# Showdown Native-Scale Streaming Lesson

## Status

- scope: local_training_fixture
- ready_for_aaa: false
- promote_to_master: false
- curation_required: true

## Failure Captured

The earlier regression produced `frame_0000.png` with a large solid magenta void. That proves the failure happened during logical MUGEN stage reconstruction, before SGDK binary export or emulator rendering.

The root cause was not a palette conversion issue alone. The pipeline read properties from the SFF/DEF files but did not execute the 2D engine composition rules:

- `mask = 1` must convert palette index 0 to transparent alpha before composition.
- BG sections must render back-to-front in DEF order.
- `start` offsets must be applied in world coordinates.
- `tile` repetition must fill the intended stage span.

## Non-Negotiable Reconstruction Rule

Do not resize the MUGEN stage down to the Mega Drive viewport.

The Showdown stage is larger than 320x224. The correct SGDK fixture behavior is:

- reconstruct the native world at 768x480;
- export the world as 96x60 8x8 tiles;
- keep global deduplicated tiles in ROM;
- stream only the active camera window into VDP;
- move the camera horizontally and vertically to expose the full stage.

## Anti-Magenta Gate

Every reconstructed frame must be checked before SGDK export:

- inspect `work/reconstructed_layers/frame_0000.png`;
- calculate the RGB histogram inside the 320x224 useful viewport;
- fail the pipeline if RGB `255,0,255` exceeds 5 percent of the checked pixels;
- treat any large magenta region as a catastrophic transparency/composition failure.

## SGDK Budget Lesson

The viewer uses a 42x30 tile streaming window for a 320x224 viewport with scroll slack. The exported fixture currently declares:

- world: 768x480 pixels;
- map: 96x60 tiles;
- global unique ROM tiles: 2253;
- active VDP cache capacity: 1151 tiles;
- exporter-reported max active window unique tiles: 1087;
- tile cache margin: 64 tiles.

This is a training fixture contract. It does not by itself make the project `ready_for_aaa`; canonical promotion still requires stronger wrapper-native telemetry or VDP dump evidence.

## Curation Candidate

Candidate future wrapper/tooling improvement:

- add a canonical MUGEN stage reconstruction gate that checks alpha mask, DEF layer order, tiling, native world size, camera extents, and active VRAM cache budget in one report.
- do not promote the local parser/exporter to a global tool until `tools/mugen2sgdk` has either been reused/wrapped or formally replaced by human-approved curation.
