# Image Generation Capability Routing

Use this reference before declaring image generation blocked.

## Channels

Classify generation capability in this order:

1. `native_chat_image_generation_callable`
   - A callable tool such as `image_gen` / `imagegen`.
   - Can usually return or save an image artifact.
2. `native_chat_inline_generation`
   - The chat/model can render an image inline in the conversation.
   - Valid real generation even when no callable tool is exposed.
3. `api_cli_generation`
   - SDK, API, CLI, or script path.
   - May fail by billing, quota or key.
4. **local_comfyui_generation (MegaDrive_DEV)**
   - Local ComfyUI via `tools/ai_imagegen/imagegen_tool.py`.
   - Fallback when native/API is unavailable.
   - Profiles: `deck_safe_sd15` (Steam Deck/OLED default), `sdxl_lowvram`, `flux_schnell_gguf` (experimental).
   - Entry points: `python tools/ai_imagegen/imagegen_tool.py route --native-callable false --native-inline false --json`
   - Install when absent: `python tools/ai_imagegen/imagegen_tool.py install --profile deck-safe --dry-run`
   - Full decision flow in tool CLI (`status`, `healthcheck`, `route`, `generate`).
5. `procedural_renderer`
   - Local scripts drawing shapes/placeholders.
   - Never valid as creative asset source.
   - Valid only as `debug_lab`, `visual_lab_control` or `placeholder`.

## Blocking rule

Only declare `BLOCKED_IMAGE_TOOLING` when no real channel exists:

- no callable native generation
- no inline native generation
- no usable API/CLI fallback
- and local ComfyUI is unavailable or host-insufficient (run `healthcheck` to confirm)

API errors such as `billing_hard_limit_reached`, `insufficient_quota` or missing key block only `api_cli_generation`. They do not block `native_chat_inline_generation`.

## Required artifacts

Before blocking, emit:

- `tooling_capability_report`
- `generation_channel_decision`

Minimum fields:

```yaml
native_chat_image_generation_callable: true|false
native_chat_inline_generation_available: true|false
api_cli_generation_attempted: true|false
api_cli_failure_reason: none|billing_hard_limit_reached|insufficient_quota|missing_key|other
procedural_generation_used_as_asset_source: false
selected_generation_channel: native_chat_image_generation_callable|native_chat_inline_generation|api_cli_generation|blocked
blocked_image_tooling: true|false
```

`selected_generation_channel` must never be `procedural_renderer` for a final AAA asset. If procedural output is used, write it under `data/debug_lab/` and mark `acceptance_status: debug_lab`.

## Inline persistence

If an image is rendered inline but not yet saved:

- `native_image_generation_available: true`
- `blocked_image_tooling: false`
- `generation_channel: native_chat_inline_generation`
- `persistence_status: generated_inline_pending_persistence`

The agent must then attempt to persist it into the run folder. If persistence fails, continue reporting the generated inline asset as pending persistence instead of pretending it was saved.

For accepted premium art, pending persistence is not enough. Persist the image into `data/source_art/`, create or update `premium_source_manifest`, then continue conversion.

## Lineage fields

For every generated asset, record:

- `generation_channel`
- `tool_callable`
- `image_rendered_inline`
- `persisted_to_filesystem`
- `output_path` when it exists
- `chat_asset_label` when inline
- `prompt_hash`
- `source_prompt`

Never cite a file path as delivered unless it exists.

## Final file audit

Before final response, check filesystem existence for:

- final report
- run summary
- lineage
- any image path with `persisted_to_filesystem: true`

If a report or image path does not exist, do not cite it as an output.
