# 00 - Diretrizes do Modelo

Este worktree existe para servir como base segura e editavel.

Regras:
- antes de qualquer arte, runtime ou build, classificar `doc/project_methodology_manifest.json` e executar `workflows/project-methodology-adoption.md`;
- o nome real do diretorio, `.mddev/project.json` e `project_methodology_manifest.json` devem permanecer coerentes com o documento do workspace `doc/PADRAO_NOMENCLATURA.md`, sem `KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]`;
- todo material operacional, evidencia e experimento deve permanecer dentro do projeto;
- tecnica catalogada deve ser declarada por `registry_id` e tags em `doc/technique_usage_manifest.json`;
- projeto novo ou escopo ainda difuso deve passar primeiro por `planning/game-design-planning` antes de abrir arte ou runtime;
- projeto novo, reseed ou cena sem familia tecnica declarada deve emitir `route_decision_record` via `workflows/route-decision-gate.md` antes de converter asset, editar `.res` ou escrever runtime;
- cena com parallax, foreground/oclusao, source grande ou referencia interna deve passar por `scene_architecture_triage` e medir janela/painel antes de assumir `IMAGE` residente;
- build, clean, rebuild e run sempre via wrapper;
- assets brutos entram em `res/data/`;
- saida final pronta para o SGDK fica em `res/`;
- alteracoes estruturais e tecnicas usadas devem ser refletidas em `doc/13-spec-cenas.md`, `doc/10-memory-bank.md` e `doc/changelog/changelog.md`;
- `freshness_audit` e obrigatorio antes do closeout para detectar documentacao ou evidencia obsoleta;
- codigo novo deve preservar legibilidade e limites do Mega Drive.
- menu, title screen e front-end devem nascer com identidade declarada no GDD, nao como placeholder tardio.
- os gates finais de `visual_lab_aprovado`, `audio`, `hardware_real` e `ready_for_aaa` devem ter trilha explicita em `doc/14-plano-de-provas-qa.md`.


<!-- BEGIN: diretriz-bloqueio-estetico v3 -->

## Diretriz de bloqueio estetico — leia antes de tocar em arte

**Nenhum pixel de personagem, inimigo, boss ou cenario pode nascer de codigo.**

Primitiva, poligono, retangulo e preenchimento solido — desenhados em C no runtime ou
em Python por `PIL/ImageDraw` no pipeline de assets — servem **apenas** para telemetria,
debug visual de elemento invisivel ao jogador e elemento transitorio de interface como
barra de progresso simples. Nunca para arte de entrega.

Toda entrega visual consome arquivo de imagem externo importado por `res/resources.res`
(`IMAGE`, `SPRITE`, `TILESET`, `TILEMAP`, `MAP`), em pixel art indexada respeitando 15
cores visiveis por bloco mais o index 0 transparente.

**Um PNG desenhado por primitiva nao satisfaz a regra por estar em disco.** O que decide
e a proveniencia declarada em `doc/asset_provenance_manifest.json` — um registro por
simbolo visual do `.res`:

- `source_kind: procedural_primitive` nunca pode ter `acceptance_status: final`;
- `procedural_composed_from_authored` exige fonte autoral persistida em
  `data/source_art/` com hash: codigo pode montar, recortar e paletizar arte autoral,
  nunca desenha-la;
- declarar `hand_authored_pixel` para arquivo escrito por builder de primitivas e
  detectado e bloqueado — o auditor casa o `.res` com os builders que escrevem cada
  arquivo, nao com o nome do arquivo.

Contrato: `tools/sgdk_wrapper/schemas/asset_provenance_manifest.schema.json`.
Regra completa: `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md` secoes 8.2 e 17.

### Estado medido em 2026-08-17

| Metrica | Valor |
|---|---|
| Simbolos visuais no `.res` | 22 |
| Rastreados a builder de primitivas | **21** |
| Proveniencia declarada | 0 |
| Manifesto de proveniencia | `absent` |
| Veredito | **BLOCKED** |

Blockers ativos:

- `asset_provenance_manifest_absent`
- `asset_provenance_undeclared`
- `procedural_asset_promoted_to_res`

Simbolos escritos por builder de primitivas (21) — nenhum pode ser `final`:

- `img_brand_fx_tiles` <- build_branding_intro_assets.py
- `img_brand_engine_logo` <- build_branding_intro_assets.py, build_branding_v3_assets.py, build_branding_v4_assets.py
- `img_brand_author_logo` <- build_branding_intro_assets.py
- `img_brand_project_logo` <- build_branding_intro_assets.py, build_branding_v3_assets.py, build_branding_v4_assets.py
- `img_brand_presents_text` <- build_branding_intro_assets.py
- `img_ph_sky` <- build_p1_remaining_assets.py
- `img_ph_mount` <- build_p1_remaining_assets.py
- `img_ph_hills` <- build_p1_remaining_assets.py
- `img_ph_terrain` <- build_p1_remaining_assets.py
- `spr_ph_kirby` <- build_p1_kirby.py, build_p1_remaining_assets.py
- `spr_ph_fg` <- build_p1_remaining_assets.py
- `spr_ph_enemy` <- build_p1_remaining_assets.py
- `spr_ph_particle` <- build_p1_remaining_assets.py
- `spr_ph_branch` <- build_p1_remaining_assets.py
- `spr_ph_boss_face` <- build_p1_remaining_assets.py
- `spr_ph_apple` <- build_p1_remaining_assets.py
- `img_ph_trunk` <- build_p1_remaining_assets.py
- `img_ph_title_hill` <- build_p1_remaining_assets.py
- `img_ph_title_stars` <- build_p1_remaining_assets.py
- `img_ph_title_logo` <- build_p1_remaining_assets.py
- `spr_ph_ability_fx` <- build_p1_remaining_assets.py

### Cena de marca: eixo `brand_comprehension_consequence`

Branding, title card, selo de autor e credits nao tem gameplay: nao existe rota, risco ou
decisao do jogador para a arte alterar. Nesse escopo — e somente nesse — o eixo canonico de
consequencia jogavel e substituido por `brand_comprehension_consequence`, aprovado pela
curadoria em 2026-08-17:

> cada decisao de arte precisa mudar o que o espectador entende sobre quem fez este jogo.

**Cena jogavel continua obrigada ao eixo canonico.** Nunca use essa substituicao para
escapar dele.

A substituicao so vale porque pode reprovar. Toda tecnica declarada no contrato da cena
carrega `brand_comprehension_claim` + `brand_comprehension_negative_test` +
`brand_comprehension_strength`, ou e classificada `enabling_discipline` (previne artefato,
nao ensina nada ao espectador, isenta mas obrigatoria). Tecnica que nao e nem um nem outro e
espetaculo sem consequencia.

```bash
python3 tools/sgdk_wrapper/validate_brand_comprehension_gate.py \
  --all-projects SGDK_projects --write-reports
```

Contrato de cena de marca ATIVO sem nenhuma tecnica declarada nao passa: ausencia de
declaracao nao e aprovacao. Se o contrato foi substituido, marque-o inativo em vez de
deixa-lo vazio.


### Doutrina de audacia — folga nao medida e timidez

O teto do hardware e o **alvo**, nao a margem de seguranca. Entregar a 40% do orcamento sem
ter medido ate onde dava nao e prudencia: e uma decisao que ninguem tomou.

- **audacia e sobre a ambicao, nunca sobre o claim.** Empurre o que voce tenta; meca o que
  voce afirma. Quanto mais ousado o alvo, mais rigorosa precisa ser a medicao;
- **antes de fechar um orcamento, meca o proximo degrau.** Se 32 cabem, meca 48 e 64. Pare
  quando MEDIR o estouro, nao quando sentir receio;
- **direcao de arte, level design e premissas do projeto vencem a densidade** — mas por
  declaracao, nunca por omissao. "Menos porque a cena precisa respirar" e razao legitima;
  silencio nao e;
- **falsa audacia** e a que parece ousada e piora o resultado: flicker para mascarar overflow,
  efeito sem consequencia, densidade que destroi leitura. O canon bloqueia cada uma.

O VDP impoe DOIS limites por scanline ao mesmo tempo (H40: 20 sprites e 320 px; H32: 16 e
256). Para sprites de 16px eles fecham no mesmo ponto, o que faz parecer que existe so um.

```bash
python3 tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py --input <cena>.json
```

`unexploited_headroom` e aviso, nao blocker: limpa-se declarando `headroom_justification`.

Regra completa: `SGDK_GLOBAL.md` secao 30.


### Rota de saida — nao contorne, execute

1. Criar/completar `doc/asset_provenance_manifest.json` declarando **cada** simbolo visual
   do `.res`.
2. Asset desenhado por primitiva: declarar `procedural_primitive` + `placeholder`. Isso
   torna o estado honesto; o asset segue bloqueando `ready_for_aaa` e `elite_ready`, o que
   e o resultado correto — nao um contorno.
3. Para promover a `final`: re-autorar a arte por canal externo, ou persistir a fonte
   autoral em `data/source_art/` e declarar `procedural_composed_from_authored` com hash.
4. Rodar o auditor e anexar o report ao closeout:

```bash
python3 tools/sgdk_wrapper/audit_procedural_asset_provenance.py \
  --project-root "<este projeto>" --shared-builder-root tools/image-tools
```

**Build limpo, ROM no BlastEm e screenshot nao substituem este gate.** Nova build so conta
como progresso visual se reduzir os blockers acima.

<!-- END: diretriz-bloqueio-estetico v3 -->
