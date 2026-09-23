# Caderno de aprendizado — Musgo no roster HAMOOPIG

**Para o proximo agente e para a curadoria humana do workflow engine.**
Nao e canon. Nao e AAA. `canonical_promotion_performed=false`.

Projeto: `SGDK_projects/HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]`.
ROM vigente ao fechar este caderno:
`c81fee9f9f7b799f30514418f01ceeb8d293788c51b5b6c89fb4376964e98589` (2.490.368 B).

Hierarquia de verdade: `doc/10-memory-bank.md` > changelog > este caderno.

---

## 0. O que esta entrega e (e o que nao e)

Musgo e um grappler autoral `id==3`. A sheet CPS2 de grappler pesado foi ancora
tecnica de massa, timing e cell budget. Nao e fonte de pixel nem IP.

Nao declare: `ready_for_aaa`, `validado_budget`, pixel nativo final,
`testado_em_emulador` da luta, bundle BlastEm selado.

Status maximo: `buildado` + seletor observado. Arte: `source_candidate`.

---

## 1. Doutrina operacional medida nesta sessao

1. **Lutador novo no HAMOOPIG nao e so sprite.** Sem `PLAYER_STATE_*`, tabela,
   `.res`, case de hitbox por `id`, gravidade 550, paleta, SFX, especiais,
   ciclo do seletor e ciclo MODE, o personagem vira fantasma (Ken ja provou).
2. **Hitbox segue o strip real.** Active no ultimo ou unico quadro. Copiar
   frames 2-5 do Ryo quebra Ken e quebraria Musgo.
3. **Arte original olha para a direita.** CPS/SF olha para a esquerda; Ryo
   olha para a direita; `SPR_setHFlip` no P2 assume arte para a direita.
   Musgo foi desenhado a direita. P2 HFlip o vira para o Ryo no seletor.
4. **Downscale direto de concept IA nao e sprite nativo.** LANCZOS + quantize
   9-bit cabe no ResComp e no palco, mas o seletor mostra lama visual contra
   o Ryo. Teto de claim: `source_candidate`.
5. **Screenshot e o beat.** `capture_blastem_evidence_linux.sh` recusou o
   bundle (`vlab_block_missing`, sem `visual_vdp_dump`). O PNG do seletor
   existe e mostra P1 Ryo + P2 Musgo. Recusa de selo nao e ROM morta.
6. **Default P2 = lutador novo** faz o primeiro boot do BlastEm provar o
   personagem no seletor sem input extra.

---

## 2. Checklist de onboarding de lutador (HAMOOPIG)

Reproduzido com Musgo apos o Ken. Se faltar um item, o sintoma volta.

| Item | Owner local | Musgo |
|---|---|---|
| Fonte em `data/source_art/<id>/` com proveniencia | art | sim |
| Converter gera strips 8x8, index 0, paleta unica, cell <=128 | convert_*.py | `convert_musgo.py` |
| `res/<id>.res` SPRITE por estado | rescomp | `res/musgo.res` |
| `inc/player_<id>_table.h` + aliases de estado | runtime | `player_musgo_table.h` |
| `PLAYER_STATE_<ID>` com y=piso, axis, timing, 550 gravity | `player_*.c` | `player_musgo.c` |
| `PLAYER_STATE` despacha `id` | `player.c` | id==3 |
| Paleta PAL2/PAL3 em `FUNCAO_APPLY_FIGHTER_PALETTE` | `player_ken.c` | pal1/pal2 Musgo |
| MODE cicla todos os ids | `FUNCAO_CYCLE_FIGHTER` | 1->2->3->1 |
| Seletor: preview, paleta, nome, cycle_id | `select.c` | 3 nomes no slot |
| `FUNCAO_FSM_HITBOXES` case por id | `fsm.c` | case 3 |
| Especiais QCF/DP so se o id tiver anim; fireball so se tiver sprite | `fsm.c` | 700 slam, sem `spr_ryo_701` |
| SFX reusa mapa GPL ou mapa proprio | `FUNCAO_PLAY_SND` | id==3 no mapa Ryo |
| Gravidade 550 = impulsoY/gravidadeY do Ryo | physics | copiado do Ken |
| Facing: arte para a direita | converter/autoria | Musgo right |

---

## 3. Producao visual — o que funcionou e o que nao

Funcionou:

- Concept 3/4 com ganchos de silhueta (taboa, mascara de casca, cogumelos,
  pe-raiz, kelp) antes do idle de perfil.
- Idle de perfil em chroma magenta como mestre.
- Video-first para idle e walk (camera travada, no lugar).
- Key pose autoral para haymaker e slam.
- Hibrido no soco: anticipation do video + impacto da key pose, porque o
  video quebrou o perfil no active frame.

Falhou / limite:

- `ffmpeg -i .../f%03d.png` dentro de path com `%2F` (URL-encoded) nao e
  sequencia. Extrair para `/tmp/.../f%03d.png`.
- Punch video foi para 3/4 no impacto (identidade e camera drift).
- JPEG/video deixa halo rosa; chroma key por faixa, nao so `#FF00FF`.
- Quantizacao global do concept 480x640 para 80x104 e downscale direto.
  Nao substitui lineart 1px nativa nem `art_gameplay_direction_gate`.

Budget observado no ResComp (nao e scanline):

- idle Musgo: 7-9 HW sprites, 95-100 tiles/frame (Ken idle era menor).
- Total de sprites VDP do metasprite nao e pressao por scanline; ainda
  falta `vdp_scanline_simulator.py` antes de fechar budget.

---

## 4. Evidencia

| Artefato | Papel |
|---|---|
| `out/rom.bin` sha256 `c81fee9f9f7b799f30514418f01ceeb8d293788c51b5b6c89fb4376964e98589` | ROM Musgo id=3 |
| `out/emulator_evidence/blastem-linux-20260911T212135Z-1769103/screenshot.png` | seletor P1 Ryo P2 Musgo |
| mesmo dir, bundle `blocked` (`vlab_block_missing`) | selo canonico recusado |
| `res/sprite/musgo/100.png` 320x104 (4x80) | idle |
| `rascunho/musgo_convert_report.json` | cells e hashes |
| `doc/art/musgo/character_identity.md` | DNA |
| `doc/changelog/changelog.md` secao Musgo | claim |

---

## 5. Fila para curadoria humana do workflow engine

Nada disto entra em `.agent` sem ato humano.

1. Patch em `planning/fighting-game-design` + `code/sgdk-runtime-coder`:
   checklist de onboarding de lutador (tabela da secao 2).
2. Patch em `art/sprite-animation`: harvest video-first nao pode viver em
   path com `%`; hibrido keypose quando o video quebra o perfil.
3. Patch em `art/art-translation-to-vdp`: downscale direto + quantizacao
   global de concept IA para sprite de luta fica `source_candidate`.
4. Patch em `operation/emulator-vdp-evidence-curator`: engine sem VLAB
   ainda pode ter screenshot dedicado; recusa de bundle nao apaga o boot.
5. Nao criar skill nova. Owners ja existem.

---

## 6. Proximo agente

- Nao use a sheet do Hulk como img2img.
- Nao declare a luta Musgo testada.
- Nao promova `res/sprite/musgo/` a pixel nativo.
- Se for para o palco: A no seletor, START, capturar luta e scanline.
- Se for arte: voltar ao model sheet / lineart 1px, nao melhorar a sheet
  quantizada.

## 7. Correcao persistente do KO (2026-09-12)

- Sintoma: ao terminar a queda, Musgo reiniciava o primeiro frame e nunca
  estabilizava no chao.
- Causa: `graphics.c` chamava `PLAYER_STATE(570)` no proprio estado 570;
  esse despachante zera `animFrame` e `frameTimeAtual`, reiniciando a animacao
  a cada ciclo.
- Correcao: quando a energia permanece zero, o estado 570 agora fixa
  `animFrame=animFrameTotal` e `frameTimeAtual=frameTimeTotal`; a transicao para
  552 continua disponivel se a energia for restaurada.
- Regra: estados terminais devem segurar o ultimo frame autoral, nunca
  reentrar no proprio despachante de estado. O teste de emulador dedicado ao
  KO ainda e obrigatorio antes de promover o claim.
- Build de referencia apos o patch: `out/rom.bin` sha256
  `363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f`.

## 8. Zero autoritativo no HUD (2026-09-12)

`energiaBase` e a fonte da barra amarela e `energia` e apenas o atraso
visual. A hipotese anterior de residual sobrevivendo ao reset foi retirada:
o reset ja restaurava ambos, e nao houve evidencia de cache corrompido.
O caso zero agora preenche as 16 colunas pretas uma vez, preservando o cache.
Vida positiva conserva ao menos uma coluna. O dano de especial nao pode
reentrar em 550 apos dano letal de vida: este era um lancamento duplicado.
Teste das funcoes C: `rascunho/temporario/test_health_contract.py`.
Arte terminal distinta e espera pelo pouso estao registradas no fechamento
`doc/curation/2026_09_12/visual_ko_closeout.md`.
