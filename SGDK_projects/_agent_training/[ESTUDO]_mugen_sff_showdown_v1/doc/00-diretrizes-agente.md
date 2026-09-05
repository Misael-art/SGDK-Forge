# 00 - Diretrizes do Agente

Regras de processo deste projeto. Autoridade #4 da hierarquia de verdade.


<!-- BEGIN: diretriz-bloqueio-estetico v5 -->

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

### Rota de conversao vigente — nao redescubra, nao improvise

A suite canonica e `forge-art` (`tools/sgdk_wrapper/forge_art/`). Ela existe porque
conversao automatica resolve **conformidade**, nunca **qualidade artistica**:

```text
technical_pass != visual_pass != budget_pass != emulator_pass != ready_for_aaa
```

Toda saida de maquina nasce `technical_candidate`. Ela so vira `visually_approved`
com decisao humana registrada. Promocao para `res/` exige os **dois**.

| Preciso de | Use |
|---|---|
| converter cor para o CRAM | `python3 tools/sgdk_wrapper/forge_art/vdp_color.py --convert R,G,B` |
| medir um PNG contra o contrato pixel-strict | `python3 tools/sgdk_wrapper/forge_art/pixel_contract.py --validate <png> --index0-role transparent0` |
| normalizar PNG **ja indexado** (PLTE inflada, papel do index 0) | `python3 tools/image-tools/normalize_indexed_sgdk_png.py transparent0 <png>` |
| traduzir fonte high-res de personagem/cenario de identidade | **nenhuma rota automatica.** Skill `art/art-translation-to-vdp`, construcao em canvas nativo |

**Mortos — falham fechado de proposito, nao tente reviver:**

- `tools/image-tools/batch_resize_index.py` — usava LANCZOS em pixel nativo, salvava
  RGBA por cima da fonte e compunha BMP sobre branco;
- `tools/image-tools/fix_png_transparency_final.py` — compunha sobre preto e removia o
  marcador `transparency`; o nome dizia o oposto do que o codigo fazia.

**Dois oraculos de cor existem e divergem em 112 de 256 valores por canal.** O ResComp
(`Util.java:38`) trunca; o macro C (`pal.h:35`) arredonda. O default e o ResComp, porque
e ele que escreve os bytes que vao para a ROM. Nunca crie uma segunda tabela de cor:
tabela divergente e blocker P0.

**Grade de autoria e `00,22,44,66,88,AA,CC,EE`** — a unica que faz round-trip exato nos
dois oraculos. A grade de exibicao quebra em 387 das 512 cores sob o macro C.

Fonte em `data/` e **read-only** para a suite. Interpolacao em caminho de pixel nativo e
blocker (`non_nearest_downscale`). RGBA nunca e saida final.

### Estado medido em 2026-08-30

| Metrica | Valor |
|---|---|
| Simbolos visuais no `.res` | 0 |
| Rastreados a builder de primitivas | **0** |
| Proveniencia declarada | 0 |
| Manifesto de proveniencia | `absent` |
| Veredito | **BLOCKED** |

Blockers ativos:

- `resources_res_missing_for_visual_delivery`

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


### Registro de folga de sprites — pendente para quem assumir

Varredura de 2026-08-17 pela curadoria. **Nada foi corrigido neste projeto**; isto e
registro para o proximo agente agir.

- declaracoes de pressao encontradas: **5**
- `unexploited_headroom` (abaixo de 60% do teto): **0**
- `hardware_idle_undeclared` (zero sprites sem declarar que e decisao): **3**
- `sprite_pressure_unmeasured` (prosa, nada computavel): **2**

Declaracoes que pedem acao:

- `branding_sequence_contract.json` -> `scanline_sprite_pressure` = "0 sprites neste baseline" (0%) -> `hardware_idle_undeclared`
- `branding_sequence_contract.json` -> `max_scanline_sprites` = "0" (0%) -> `hardware_idle_undeclared`
- `scene-contracts.json` -> `scanline_sprite_pressure` = "0 sprites no baseline" (0%) -> `hardware_idle_undeclared`
- `scene-contracts.json` -> `scanline_sprite_pressure` = "nao_medido" (sem numero) -> `sprite_pressure_unmeasured`
- `scene-contracts.json` -> `scanline_sprite_pressure` = "nao_medido" (sem numero) -> `sprite_pressure_unmeasured`

**O que fazer quando for atuar aqui:** preencha `worst_frame_sprite_layout` no
`scene-contracts.json` da cena (campo novo do schema canonico, formato do simulador),
rode o simulador, e entao ou empurre a densidade ate medir o teto ou declare
`headroom_justification` dizendo por que a direcao de arte ou o level design pedem menos.

```bash
python3 tools/sgdk_wrapper/audit_scene_headroom.py --root SGDK_projects
python3 tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py --input <cena>.json
```

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
python3 tools/sgdk_wrapper/audit_tile_residency.py --project-root "<este projeto>"
```

O segundo mede residencia de tiles em VRAM **a partir do asset**, sem precisar de runtime.
Fundo grande com deduplicacao baixa foi composto como imagem e quantizado, nao autorado como
tiles: custa como arte unica e costuma ainda parecer repetitivo.

**Build limpo, ROM no BlastEm e screenshot nao substituem este gate.** Nova build so conta
como progresso visual se reduzir os blockers acima.

<!-- END: diretriz-bloqueio-estetico v5 -->
