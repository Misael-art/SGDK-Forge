# Plano — tornar o Forge capaz de pixel art no piso da barra viva

Data: 2026-08-29
Barra: `doc/03_art/18_live_scene_bar.md`
Estado de partida: doutrina escrita; geracao no nivel da barra **nao
provada em ROM**. Gargalo ja medido em
`doc/curation/GRAPHICS_CAPABILITY_REPORT_2026-08-06.md`.

Este plano nao e `ready_for_aaa`. E a rota para a primeira ROM que passe
o laudo `live_scene_bar_report.status=passed` com aprovacao humana.

---

## Diagnostico (por que ainda nao chegamos)

O Forge e um sistema de **veto** maduro e um sistema de **producao de
pixel nativo** imaturo.

| O que ja existe | O que falta para o piso vivo |
|---|---|
| Gates, schemas, proveniencia, BlastEm | Redesenho nativo que preserve anatomia/carisma |
| Sprint source→VDP em prosa | Loop Imagine→lineart→paleta→ROM que um agente complete |
| Prompts de "pixel art sprite sheet" | Fonte high-res + traducao (P1). Os prompts atuais sabotam a barra |
| ComfyUI local rebaixado | Canal nativo (Imagine) nesta classe de agente = Ramo A |
| HAMOOPIG no workspace como engine | Oficio H1-H5 em jogo **autoral**, nao roster dos videos |
| Skills de S/H, multi-plano, budget, XGM2 | Fixtures Y1/C1/M1/D1/S1 alem de P2/P3/R4 |

Nao se chega la escrevendo mais schema. Chega-se la com **imagens no
disco, traducao no grid, e uma ROM vista**.

---

## Principio de execucao

1. Identidade em 1 pagina viva, nao 8 JSON como pedágio de geracao.
2. Gerar fonte premium agora (Ramo A). JSON e rastro do que se viu.
3. Geometria barata (planta, coreografia, scanline) antes do contrato de asset.
4. Traduzir; nunca quantizar cego; nunca downscale como final.
5. Fechar no BlastEm 320x224. Sem isso a fase nao avanca.
6. Laudo `live_scene_bar_report` em todo closeout visual de `aaa_game`.

---

## Fases

### Fase 0 — Doutrina (esta sessao)

Entrega:

- `18_live_scene_bar.md` + `live_scene_bar.json` + schema do laudo
- brief no `.agent/references`
- amarra em AGENTS, SGDK_GLOBAL §39, quality bar, skills, memory bank

Gate: agente novo que abrir o workspace encontra a barra na hierarquia
de verdade e no brief, e entende o oficio sem seguir o X.

Status: em curso nesta sessao.

### Fase 1 — Corrigir o caminho de geracao

Objetivo: o agente **para de pedir pixel-art-final no gerador**.

Trabalho:

- Prompts de Rota A passam a pedir concept high-res, volume, material,
  silhueta; lineart 1px como etapa; sheet so depois da traducao.
- Ramo A (Imagine / native callable) e o canal default quando a sessao
  expoe a ferramenta. Nao instalar ComfyUI neste host AMD.
- Persistencia obrigatoria em `data/source_art/` + lineage.
- Critico cego nas **imagens**, minimo 3 rounds, piso 8.5, sem
  auto-satisfacao (ja esta no successor_quality_protocol; aplicar no
  Ramo A, nao so no C).

Gate: um `asset_lineage_record` de concept persistido, rejeitado se for
fake pixel art, aceito se for fonte forte.

Prova: 1 personagem + 1 cenario autoral em `data/source_art/` de um
projeto vivo (preferencia: MARE_BRAVA para R-densidade, ou lab Pigsy
para P-traducao).

### Fase 2 — Traducao nativa que preserve alma

Objetivo: fechar o gargalo do relatorio grafico de 2026-08-06.

Trabalho:

- Lineart 1px no tamanho alvo (ex. 48x64 / 64x96 conforme GDD), nao
  no tamanho da pintura.
- Paleta semantica por material (3+ degraus), 9-bit, papel de cada slot.
- Dither so como material/atmosfera.
- Par `basic` vs `elite`; elite tem de vencer.
- `model_sheet_to_sprite_fidelity_report` de verdade (olho, mao, roupa,
  feature). Falhou → volta lineart, nao polimento no PNG final.
- Animacao: video curto (`image_to_video`) → harvest de frames → pivot
  e contact. Proibido "sprite sheet completo" num unico prompt.

Gate: contact sheet nativo 320x224 + GIF do output + laudo com
`shared_floor.native_pixel_not_shrunken_photo=pass`.

### Fase 3 — Fixtures de oficio (laboratorio)

Uma ROM lab por axioma critico. Nao e jogo. E prova de que o Forge
sabe o truque. `lab_not_delivery=true`. IP alheia **proibida**.

| Fixture | Escola | O que prova |
|---|---|---|
| F-R2 paleta com papel | Rheo | 1+1+1+folga visivel, 48 cores, cena ainda rica |
| F-R4 / F-Y1 stage ~980 tiles | Rheo+Pyron | palco reautorado, dedup/H-flip, teto medido |
| F-C1 segundo passe de palco | Chev | original/basic/elite; 320x224 4:3 e o gate |
| F-R5 metasprite estável | Rheo | corpo grande sem junta quebrada, 60 fps |
| F-P2 S/H cor + transparencia | Pigsy | agua/vidro/lua via S/H, slot audit, movimento |
| F-P3 enhanced 8-bit | Pigsy | mesma linguagem, mais cor, split BG/FG, parallax |
| F-P1/P4 source 16-color | Pigsy | traducao de fonte 16 cores (autoral ou CC0) |
| F-M1 carta de paletas | MX | 3 skins compartilhando CRAM, alts testadas no palco |
| F-D1 identidade de chip | Diggo | tema autoral YM2612 que nao e dump; `audio_architecture_card` |
| F-H1 luta contrato | HAMOOPIG | 1 lutador autoral com FSM/hitbox/frame data, nao so sheet |
| F-S1 inversao de plano | Shannon | lab 3D ou equivalente: planes vs sprites declarados, FPS real, musica no DMA |

Gate de cada fixture: BlastEm + dump VDP + GIF se mover +
`live_scene_bar_report.status=passed` no recorte da fixture + aprovacao
humana.

`BENCHMARK_VISUAL_LAB` e o unico laboratorio oficial. Nao espalhar
fixtures em projetos de jogo.

### Fase 4 — Aplicar num projeto vivo

Escolha canonica, nesta ordem, salvo o operador mandar outra:

1. **MARE_BRAVA** — `aaa_game` + `brawler_belt_scroll`. Alvo Rheo:
   densidade de rua, paleta com papel, TAÍNA no grid nativo herdando
   a pose-mestre v02, cais reautorado em tiles. Hoje: `ready_for_aaa=false`,
   arte parcial.
2. So depois, uma cena de traducao Pigsy **autoral** (nao SotN):
   atmosfera, S/H, planos. GOTHAM so entra se a fonte Dark Deco for
   reautorada e o laudo passar; status gerado de "11 assets AAA" nao
   conta como esta barra.

Gate: uma cena jogavel, 60 fps, laudo `passed`, humano aprova o
painel fonte/basic/elite/rom.

### Fase 5 — Enforcement

- `ready_for_aaa=true` exige `live_scene_bar_report.status=passed`
  no slice.
- `aaa-pipeline-guardian` roteia claim visual vivo para esta barra.
- `art_quality_gate.py` ganha checks da tabela de rejeicao (fake
  pixel, palette_role, name_drop). Calibrar contra a arvore existente
  **antes** de publicar (§37): gate que reprova 9/9 projetos e treino
  para ignorar vermelho.
- `validate_resources.ps1` closeout: ausencia do laudo em `aaa_game`
  vira blocker, nao warning.

Gate: um projeto `aaa_game` sem laudo nao fecha closeout.

### Fase 6 — Primeira prova humana da barra

Uma ROM, um recorte, um humano.

Nao e "o Forge ja gera no nivel Rheo/Pigsy". E: "este recorte passou
os 12 checks, os axiomas da escola, o emulador, e o operador disse
sim".

So entao `runtime_proof_status` sobe para `VALIDADA_EM_ROM` e, com
aprovacao, `APROVADA_PELO_HUMANO`.

---

## Fora de escopo (para nao derreter o plano)

- Instalar ComfyUI/Bonsai neste host AMD.
- Copiar frames de KOF, SotN, Shinobi, Metal Slug, Mario.
- Expandir doutrina enquanto Fase 1-2 nao tiverem PNG no disco.
- Declarar `ready_for_aaa` por quantidade de JSON.
- SDREAMFORGE: herda a barra quando o port de disciplina chegar na
  Fase 3; hoje o bloqueio e BIOS, nao pixel.

---

## Ordem de trabalho do proximo agente

1. Confirmar Ramo A (sonda de `image_gen` / equivalente) nesta sessao.
2. Nao reescrever esta doutrina. Executar Fase 1 no projeto que o
   operador apontar (default MARE_BRAVA).
3. Uma fonte premium persistida > dez manifests novos.
4. Qualquer rejeicao usa a tabela da secao 5 de `18_live_scene_bar.md`.
5. Atualizar `doc/06_AI_MEMORY_BANK.md` e o memory bank do projeto
   ao fechar.

---

## Criterio de "chegamos la"

O Forge so e "capaz de forma eficaz" quando:

- um agente novo gera fonte forte sem pedir sprite sheet no prompt;
- traduz no grid nativo sem matar olho/mao/material;
- uma cena `aaa_game` passa o laudo;
- o humano reconhece o oficio (densidade arcade **ou** traducao rica),
  nao o nome dos handles;
- isso foi visto no emulador.

Ate la, o status honesto e: **piso escrito, capacidade nao provada**.
