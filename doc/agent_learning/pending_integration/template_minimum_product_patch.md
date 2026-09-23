# Pending Integration: Minimum Playable Product Template

Data: 2026-06-01
Motivo: `sgdk_templates/base-elite/` e `tools/sgdk_wrapper/modelo/` ja estavam modificados antes desta rodada. A orientacao segura e registrar proposta e nao sobrescrever runtime/template em andamento.

## Status antes

| Template | Papel | Status observado |
|---|---|---|
| `tools/sgdk_wrapper/modelo` | `CANONICAL_BOOTSTRAP` em `doc/template_registry.json` | Ja possui scene manager simples, cenas `branding/boot/menu/demo`, input edge/hold, overlay debug desligavel, runtime probe SRAM, docs 10/11/13 e wrappers. Ainda falta player controller minimo, camera minima, pause formal, transicao visual, contrato de audio routing de produto e PAL/NTSC aplicado a gameplay. |
| `sgdk_templates/base-elite` | `REFERENCE_TEMPLATE` | Possui estrutura SGDK, docs 10/11/13 e wrappers, mas runtime ainda e state machine minima em `src/main.c`. Falta a maior parte do produto minimo. |

## Decisao proposta

Promover o `tools/sgdk_wrapper/modelo` como base de produto minimo e tratar `sgdk_templates/base-elite` como referencia legada ate receber port controlado.

## Patch funcional recomendado para `tools/sgdk_wrapper/modelo`

1. Manter `APP_changeScene` como unico scene manager.
2. Criar `src/gameplay/template_player.c` e `inc/gameplay/template_player.h` com:
   - posicao `fix16`;
   - velocidade horizontal;
   - gravidade/pulo;
   - bounds de tela;
   - API `TEMPLATE_Player_init`, `TEMPLATE_Player_update`, `TEMPLATE_Player_drawDebug`.
3. Criar `src/gameplay/template_camera.c` e `inc/gameplay/template_camera.h` com:
   - camera X/Y inteira derivada do player;
   - clamp em mundo minimo;
   - helper para scroll BG_B.
4. Expandir `system/input` para contrato 3/6 botoes:
   - `A/B/C/START` como minimo;
   - `X/Y/Z/MODE` expostos se presentes;
   - sem remap por enquanto, marcado `futuro_arquitetural`.
5. Adicionar pause formal ao core:
   - `START` em gameplay alterna `APP_PAUSED`;
   - pause nao altera cena, apenas bloqueia update de gameplay e preserva audio;
   - menu continua cena propria, nao pause.
6. Adicionar transicao conservadora:
   - fade curto por paleta na entrada/saida;
   - reset simetrico de scroll, WINDOW, sprites e paleta especial.
7. Criar `system/audio.c/h`:
   - init, play_ui_confirm, play_ui_back, play_pause, stop_scene_audio;
   - implementacao PSG simples ate XGM/FM final.
8. Declarar `region_timing_contract`:
   - `SYS_isPAL()` define target fps e escala timers de cena;
   - nenhum gameplay usa frame counts magicos sem nota.
9. SRAM:
   - manter runtime probe como evidencia;
   - save de jogo fica `optional_not_enabled` ate GDD exigir persistencia.
10. Documentacao:
   - garantir `doc/10-memory-bank.md`, `doc/11-gdd.md`, `doc/13-spec-cenas.md`;
   - adicionar bloco `minimum_playable_product_contract`.

## Patch recomendado para `sgdk_templates/base-elite`

Nao editar diretamente nesta rodada. Depois de estabilizar o worktree:

1. Rebasear `base-elite` a partir do `modelo` canonico ou declarar deprecacao parcial.
2. Remover `out/` somente com manifest, SHA-256 e rollback.
3. Validar wrappers e build essentials.
4. Rodar build + BlastEm antes de promover como template ativo.

## Status depois desta rodada

- `implementation_status`: `proposal_safe_due_dirty_template_state`
- `claim_ceiling`: `vertical_slice_candidate_seed`
- `runtime_changed`: `false`
- `reason`: preservar trabalho alheio e evitar conflito em templates ja modificados.

## Proximo marco seguro

Abrir rodada dedicada ao `tools/sgdk_wrapper/modelo` com diff limpo, implementar os modulos acima, buildar, validar, capturar BlastEm e atualizar `doc/template_registry.json`.
