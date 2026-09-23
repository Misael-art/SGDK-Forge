# Prompt Mestre - Telas de Assinatura do Template (v2)

Handoff para o agente de arte que vai produzir os assets da abertura de assinatura.

> **Mudanca importante em relacao a v1 deste documento.** A versao anterior instruia:
> *"voce nao pode encerrar dizendo 'falta gerar assets' se ainda pode entregar a estrutura
> procedural placeholder que compila"*. Essa instrucao produziu 78 simbolos visuais
> desenhados por `PIL/ImageDraw` em 9 projetos do workspace. Ela esta **revogada**. Arte
> procedural agora e blocker declarado, nunca entregavel. Ver a diretriz de bloqueio
> estetico em `AGENTS.md` e `SGDK_GLOBAL.md` secoes 8.2 e 17.

---

## Prompt

```text
[Contexto MD Carregado]

Voce e o agente de arte da abertura de assinatura do projeto ativo. Sua tarefa e produzir
os 8 assets de pixel art do contrato `branding_sequence_v2`. Voce NAO vai escrever o
runtime C: isso e um handoff separado, posterior, e depende da sua arte existir primeiro.

## O que ja esta decidido e nao e sua decisao

O conceito, a linha do tempo, o stack de tecnicas de VDP, o plano de paletas e o orcamento
estao fechados em `doc/branding_sequence_contract.json` (contract_id `branding_sequence_v2`).
Leia esse arquivo inteiro antes de desenhar qualquer pixel. Ele e a autoridade.

Resumo do conceito, para voce nao ter que inferir:

  "A FORJA" — uma unica tomada continua dentro de uma forja. Uma brasa cai, o martelo bate,
  e o impacto forja a marca em metal incandescente. Tres atos, zero cortes a preto.

  Ato 1 IGNITION  (F0-120)   ambiente escuro, brasa caindo, luz mascarada por Shadow/Highlight
  Ato 2 STRIKE    (F120-300) impacto, enxame de estilhaços monta o logo, varredura especular
  Ato 3 SIGNATURE (F300-520) cortina por coluna revela autor, projeto e "presents"

A metafora da forja nao e enfeite: ela e a desculpa mecanica para os pontos fortes reais do
hardware. Emissividade por Shadow/Highlight, metal liquido por rotacao de CRAM, ar quente
por line scroll, estilhaços por multiplexacao de sprites. Sua arte precisa dar suporte
material a esses efeitos — se o metal nao tiver uma rampa com folga de highlight, a
varredura especular do ato 2 simplesmente nao aparece.

## Arquivos canonicos que voce deve ler antes de agir

- `AGENTS.md` — em especial a secao "Diretriz de bloqueio estetico"
- `doc/branding_sequence_contract.json` — o contrato que voce esta cumprindo
- `doc/00-diretrizes-agente.md` — o bloco `diretriz-bloqueio-estetico v1` do projeto
- `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md` — secoes 8.2, 17 e 18
- `tools/sgdk_wrapper/.agent/skills/art/megadrive-pixel-strict-rules/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/art/art-creation-sourcing/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/art/art-conversion-pipeline/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/art/image-generation-routing/SKILL.md`
- `tools/sgdk_wrapper/.agent/references/art_style_catalog.json`
- `doc/03_art/00_visual_quality_bar.md`

## PROIBICAO ABSOLUTA

Nenhum destes 8 assets pode nascer de codigo. Nada de `PIL/ImageDraw`, primitivas,
poligonos, retangulos, preenchimento solido ou script `draw_*` gerando arte final.

Um PNG desenhado por primitiva NAO satisfaz a regra por estar em disco. O auditor casa
cada arquivo do `.res` com os builders que o escrevem e detecta a laundering. Se voce
declarar `hand_authored_pixel` para um arquivo escrito por um builder de primitivas, o
gate bloqueia e a entrega e reprovada.

Codigo PODE: recortar strip, alinhar grid de 8px, quantizar paleta, indexar PNG, deduplicar
tile, montar folha a partir de quadros autorais que ja existiam. Isso e
`procedural_composed_from_authored` e exige a fonte autoral persistida em
`data/source_art/` com hash.

Codigo NAO PODE: desenhar a silhueta, o volume, a rampa de luz, a lineart ou qualquer
forma que o jogador veja como personagem, objeto, cenario ou marca.

## FASE 1 — MODEL SHEET (pare aqui e espere aprovacao humana)

Nao produza os 8 assets finais nesta fase. Pedido de pacote final direto ja falhou 4 vezes
neste workspace; a rota que funciona entrega direcao primeiro.

**A direcao de arte NAO e sua decisao e ja esta escrita.** Leia integralmente antes de
desenhar:

- `doc/branding_v2_art_direction.md` — a direcao. Logica de luz, gramatica de material,
  arquitetura de paleta com papel de indice travado, voz tipografica, `silhouette_hooks`,
  `generic_blockers` e o layout exato dos 5 paineis do model sheet.
- `doc/art_direction_decision_record.json` — as 6 travas da Visual Quality Bar ja
  preenchidas com as decisoes tomadas. Voce completa apenas os campos `execution_*` e nao
  altera as decisoes. Se discordar da direcao, abra a discordancia com o curador humano em
  vez de divergir em silencio.

Tres coisas que decidem aprovacao ou reprovacao, resumidas aqui para voce nao errar por nao
ter lido:

1. **A forja ilumina de baixo.** O plano superior de cada volume esta em sombra, a face
   inferior esta iluminada, a sombra sobe pela parede. Asset que possa ser lido como
   iluminado de cima reprova, ainda que a rampa tenha 15 cores e o dither seja impecavel.
2. **Sombra de metal quente e fria**, violeta-azul. Rampa de sombra em cinza neutro reprova.
3. **PAL1[13..14] sao folga de highlight** e precisam ficar abaixo do branco maximo. Se a
   rampa de metal chegar ao branco, o operador de Shadow/Highlight do VDP nao tem para onde
   clarear e a varredura especular do ato 2 simplesmente nao existe.

Entregue: o model sheet em `data/source_art/branding_v2/model_sheet_forge_v01.png` conforme a
secao 9 da direcao, mais `doc/authoriality_gate_report.json` com `clone_risk_score` medido,
mais um paragrafo honesto de autocritica apontando onde a folha ficou fraca. Folha sem
autocritica volta.

### O gate mecanico existe antes de voce comecar — rode nele

O criterio de aceitacao esta medido, nao sera discutido depois. Folha que nao passa o gate
mecanico nao chega a revisao humana:

```bash
python3 tools/sgdk_wrapper/validate_model_sheet_contract.py \
  --model-sheet data/source_art/branding_v2/model_sheet_forge_v01.png \
  --output doc/model_sheet_contract_report.json

python3 tools/sgdk_wrapper/art_diagnostic.py    # formato tecnico geral
python3 tools/sgdk_wrapper/art_quality_gate.py  # qualidade artistica
```

O gate de contrato confere 6 coisas: canvas 512x384, os 5 paineis com conteudo, painel B como
silhueta de tinta unica, `PAL1[13..14]` com canal maximo `<= 0xCC`, `PAL0[9..12]` fechando como
anel uniforme, e painel E em escala real em vez de ampliacao. Ele **nao** julga se a luz esta
correta — isso e a revisao humana.

**PARE. Espere aprovacao humana explicita do model sheet antes da fase 2.**

## FASE 2 — OS 8 ASSETS

Somente depois da aprovacao. Larguras/alturas de SPRITE sao em TILES e valem por quadro.

| res_symbol | arquivo | dimensao | paleta | funcao | ato |
|---|---|---|---|---|---|
| `img_forge_bg_b` | `branding/forge_bg_b_320x224.png` | 320x224 (40x28) | PAL0 | interior da forja, escuro, piso lavado por brasa | 1 |
| `img_forge_bg_a_props` | `branding/forge_bg_a_props_320x224.png` | 320x224 (40x28) | PAL0 | bigorna, martelo e ferramentas em foreground | 1 |
| `spr_forge_ember` | `branding/spr_forge_ember_16x16_strip.png` | 64x16 (4 quadros de 2x2) | PAL3 | brasa que cai | 1 |
| `spr_forge_shard` | `branding/spr_forge_shard_16x16_strip.png` | 64x16 (4 quadros de 2x2) | PAL3 | estilhaço do enxame | 2 |
| `img_logo_engine_v2` | `branding/logo_engine_224x64.png` | 224x64 (28x8) | PAL1 | wordmark da engine em metal | 2 |
| `img_logo_author_v2` | `branding/logo_author_192x32.png` | 192x32 (24x4) | PAL2 | wordmark do autor | 3 |
| `img_logo_project_v2` | `branding/logo_project_224x48.png` | 224x48 (28x6) | PAL2 | wordmark do projeto | 3 |
| `img_presents_text_v2` | `branding/presents_text_96x16.png` | 96x16 (12x2) | PAL2 | wordmark "presents" | 3 |

### Restricoes de hardware que a arte precisa respeitar

- PNG indexado, index 0 transparente, **maximo 15 cores visiveis por paleta**;
- dimensoes multiplas de 8, alinhamento de grid de 8px;
- sem canal alpha e sem semi-transparencia: pixel e 100% visivel ou 100% transparente;
- sem gradiente suave: use dither manual de 2-3 cores ou rampa curta;
- `img_forge_bg_b` e `img_forge_bg_a_props` compartilham PAL0 — o plano de foreground nao
  tem paleta propria, projete os dois juntos;
- `spr_forge_shard` tem apenas 4 quadros porque o runtime gera 16 orientacoes por flip H/V.
  Desenhe os 4 quadros de forma que o flip produza orientacoes plausiveis, nao espelhos
  obvios de uma forma assimetrica;
- **`img_logo_engine_v2` precisa de folga de highlight nos indices 13 e 14 de PAL1**: se a
  rampa de metal chegar ao branco maximo, o operador de highlight do VDP nao tem para onde
  clarear e a varredura especular do ato 2 desaparece. Deixe os dois degraus mais claros
  abaixo do maximo, de proposito;
- a rampa de brasa de PAL0 nos indices 9 a 12 vai rotacionar em CRAM. Essas 4 cores precisam
  formar um ciclo continuo, nao uma rampa com inicio e fim visiveis.

### O que esta proibido no ato 3

Autor, projeto e "presents" sao assets de pixel art. O v1 usava `VDP_drawTextBG` com um
cursor de maquina de escrever — estetica de painel de debug. Nao reproduza isso.

## FASE 3 — DECLARAR E VALIDAR

Para cada asset entregue:

1. descomente a linha correspondente em `res/resources.res` (o bloco pendente ja esta la);
2. adicione a entrada em `doc/asset_provenance_manifest.json`, com `source_kind`,
   `acceptance_status`, `generated_by` e, se houver composicao por codigo,
   `authored_source` + `authored_source_hash`;
3. rode os gates:

```bash
python3 tools/sgdk_wrapper/audit_procedural_asset_provenance.py \
  --project-root "<este projeto>" --shared-builder-root tools/image-tools

python3 tools/sgdk_wrapper/art_diagnostic.py    # formato tecnico
python3 tools/sgdk_wrapper/art_quality_gate.py  # qualidade artistica
```

`art_diagnostic.py` valida formato (PNG indexado, PLTE, 9-bit, dimensoes). `art_quality_gate.py`
valida silhueta, escala, lineart, pose, appeal e coerencia. **Asset tecnicamente OK nao pode
elevar status se o gate artistico reprovar.**

## Politica de parada — leia com atencao

Voce **pode e deve** encerrar dizendo que a arte nao atingiu o nivel, se for verdade. Isso e
uma entrega honesta, nao uma falha. Registre `visual_aesthetic_report=rework` com o motivo
concreto e o proximo passo.

Voce **nao pode**:
- entregar arte desenhada por primitiva como substituta;
- promover PNG bruto de gerador direto para `res/` sem conversao e validacao;
- declarar `fonte_premium_aprovada` sem lineage, conversao, validacao de paleta e revisao;
- declarar qualquer status de entrega visual sem ROM no BlastEm.

Se o bloqueio for de canal de geracao de imagem, emita `tooling_capability_report` e
`generation_channel_decision` distinguindo callable nativo, geracao inline, API/CLI e
renderer procedural — e pare com o blocker nomeado. Renderer procedural nao e rota de saida.

## Status permitido

`documentado` · `implementado` · `buildado` · `testado_em_emulador` · `validado_budget` ·
`placeholder` · `fonte_premium_aprovada` (somente com lineage completa)

## Prioridade de canal de imagem

Para asset premium, use primeiro o recurso nativo de geracao de imagem do agente, se
disponivel. `tools/ai_imagegen` nao e caminho padrao: serve apenas como fallback tecnico ou
prova de canal, e resultado apenas legivel deve ser marcado
`aceito_apenas_como_prova_tecnica`, nunca `fonte_premium_aprovada`.
```

---

## Handoff seguinte (nao e deste agente)

Depois que os 8 assets existirem e passarem os gates, um agente de runtime implementa
`branding_sequence_v2` seguindo `inc/scenes/branding_v2.h` e a ordem de implementacao do
contrato. O passo 1 dessa implementacao e corrigir o spike de CPU medido no v1 movendo o
upload da tabela de HScroll de CPU para DMA no VBlank.

## Incorporacao no Modelo

O modelo canonico nasce com `APP_SCENE_BRANDING` em `src/scenes/scene_branding.c`, que hoje
contem a implementacao v1 e consome os 5 placeholders procedurais `brand_*`. Esses
placeholders permanecem declarados como `procedural_primitive`/`placeholder` em
`doc/asset_provenance_manifest.json` e nunca podem ser promovidos a final. Eles saem quando
o v2 entregar substitutos.
