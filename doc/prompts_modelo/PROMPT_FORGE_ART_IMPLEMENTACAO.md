# PROMPT — Implementacao do `forge-art` (fabrica visual canonica)

**versao:** 1.0.0 · **data:** 2026-08-30 · **destino:** agente executor (Opus/Sonnet, sessao dedicada)
**fonte de verdade do escopo:** `doc/05_technical/visual_forge_toolchain_diagnostic_and_implementation_plan_2026-08-29.md` (secoes 1-18 + Addendum v1.1.0)

> Copie o bloco abaixo inteiro como primeira mensagem da sessao do agente executor.
> Nao resuma. Nao corte. O contrato de teto de claim depende da integra.

---

## BLOCO DE PROMPT

Voce vai implementar a suite `forge-art` no workspace SGDK Forge. Leia
`AGENTS.md` primeiro e diga `[Contexto MD Carregado]` antes de propor acao.

### 0. Leitura obrigatoria antes de escrever qualquer linha

1. `AGENTS.md`
2. `doc/05_technical/visual_forge_toolchain_diagnostic_and_implementation_plan_2026-08-29.md` (integral, incluindo o Addendum v1.1.0 no fim)
3. `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`
4. `tools/sgdk_wrapper/.agent/references/production_truth_protocol.md`
5. `tools/sgdk_wrapper/.agent/references/production_visual_quality_contract.md`
6. skills: `art/art-conversion-pipeline`, `art/art-translation-to-vdp`,
   `art/megadrive-pixel-strict-rules`, `art/visual-excellence-standards`,
   `hardware/megadrive-vdp-budget-analyst`, `operation/sgdk-build-wrapper-operator`,
   `governance/aaa-pipeline-guardian`
7. `tools/image-tools/batch_resize_index.py`, `fix_png_transparency_final.py`,
   `normalize_indexed_sgdk_png.py`, `tools/sgdk_wrapper/test_art_pipeline.py`

Ao terminar a leitura, emita um `read_receipt` de uma linha por arquivo
(caminho + sha256 curto + 1 frase do que ele obriga). Sem isso, nao prossiga.

### 1. Tese que governa todo o trabalho

Conversao automatica resolve **conformidade**, nao **qualidade artistica**.

```text
technical_pass != visual_pass != budget_pass != emulator_pass != ready_for_aaa
```

Toda saida da ferramenta nasce como `technical_candidate`. Ela so vira
`visually_approved` com decisao humana registrada no diretorio do job.
Promocao para `res/` exige os dois. Se voce em algum momento sentir vontade de
chamar um resize+quantize de "asset final", pare: e exatamente o erro que este
trabalho existe para eliminar.

### 2. Restricoes duras (violacao = trabalho rejeitado)

- **Nunca sobrescrever a fonte.** Fontes em `data/` sao read-only para a suite.
- **Nunca** usar Lanczos/bilinear/bicubico em caminho de pixel nativo/final.
  Pixel art: nearest-neighbor. Downsample controlado so para foto/render/concept
  explicitamente classificados, e o resultado e `technical_candidate` apenas.
- **Nunca** compor sobre preto para "resolver" transparencia. Index 0 e
  reservado por contrato e deve sobreviver ponta a ponta.
- **Nunca** emitir RGBA como saida final. PNG modo P, PLTE <= 16, ate 15 cores
  visiveis, bit depth compativel com 4bpp.
- **Nunca** criar uma segunda tabela de cor. Toda conversao consome a
  biblioteca canonica unica (item 3). Tabela divergente e blocker P0.
- **Nunca** usar `hash()` do Python para deduplicacao de tiles. SHA-256 sobre
  bytes canonicos.
- **Nunca** copiar codigo de repositorio sem licenca explicita (os repos Vagno
  auditados nao tem licenca). Estude o algoritmo, reimplemente, registre em
  `third_party_manifest`. Backends com licenca observada: SoftLK-tools (CC0),
  tiledpalettequant (MIT).
- **Nunca** relaxar um gate para concluir. Se algo falta, reporte o **menor
  status provado** + a proxima acao causal.
- **Nunca** exceptions silenciosas ou fallback que afrouxe validacao.

### 3. P0 — fundacao (entregar e provar antes de qualquer P1)

**P0.1 — Biblioteca canonica de cor.** Modulo unico com:
`rgb24_to_vdp_color`, `vdp_color_to_authoring_rgb`, `vdp_color_to_display_rgb`,
`snap_rgb_to_vdp_grid`, distancias RGB/HSV/OKLab.
Registre as tres grades como distintas e nao intercambiaveis: display
`00,24,48..FF`; authoring canonico do workspace `00,22,44..EE`; RGBA4444/ABGR
do Palette Generetor auditado **nao** e formato CRAM e e proibido como
substituto silencioso. "9 bits" = 3 bits/canal = 512 combinacoes CRAM; o PNG
final continua indexado. Golden vectors confirmados contra headers e ResComp do
SGDK 2.11. Todas as 512 cores testadas com round-trip.

**P0.2 — Substituir o conversor/fixer contraditorio.** `batch_resize_index.py`
e `fix_png_transparency_final.py` saem do caminho canonico (deprecate com
shim que falha explicando). `normalize_indexed_sgdk_png.py` e reaproveitado
como normalizador de entrada ja indexada, nada alem.

**P0.3 — Corrigir `test_art_pipeline.py`.** Hoje ele institucionaliza a
contradicao (aceita RGBA intermediario e chama o fixer). Substitua por
regressao que **falha** com: RGBA, PLTE inflada, interpolacao proibida,
index 0 incorreto, cor fora da grade, saida nao deterministica.

**P0.4 — Jobs imutaveis.** `out/visual_jobs/<asset_id>/<job_id>/` conforme
secao 5 do plano. Mesma fonte + mesma spec + mesmas versoes = mesmo hash.
`--dry-run`, `--explain`, `--resume`, `--force-new-job`, saida JSON estavel,
escrita atomica, rollback, cache SHA-256 invalidado por versao/schema.

**P0.5 — Reconciliacao documental da TAINA (bloqueador de outros agentes).**
Quatro contradicoes coexistem: memory bank diz "rejeitadas"; contrato v02 diz
"aprovadas como referencia de construcao"; relatorio rota B diz GIMP
indisponivel enquanto a decisao final diz GIMP recuperado; e os arquivos
moram numa pasta chamada `rejected/`. Renomeie a pasta para o papel real,
alinhe o memory bank ao contrato v02, **date cada estado**, e preserve a
proibicao de quantizar/tracar essas imagens como asset final — permitindo
gerar `technical_candidate` a partir delas.

**P0.6 — Reconciliar `runtime_probe.c/.h` do MARE_BRAVA** com o modelo
canonico (o meta-gate bloqueia por 20 copias stale). Ate isso fechar, declare
explicitamente que a telemetria do MARE_BRAVA **nao sustenta claims novos de
performance**.

**Gate de saida do P0:** self-checks positivos **e negativos** verdes; fixture
que prova que nenhuma fonte e `res/` foi tocada; meta-gate de ferramentas
desbloqueado ou com o bloqueio explicado e datado.

### 4. P1 — ferramenta visual operacional

Comandos: `forge-art inspect|convert|translate|palette|atlas|tiles|validate|compare|promote`.
CLI e a autoridade; GIMP/Aseprite/Oeste/Ether sao frontends opcionais, nunca
dependencia do core.

**Duas rotas, separadas por classificacao explicita da fonte:**

- **Rota A — `technical_conversion`** (pixel nativo ou quase nativo): nearest,
  index 0 transparente, <=15 cores visiveis, PNG P com PLTE <=16, dimensoes
  alinhadas ao grid, dedup exact/H/V/HV, saida imutavel + hash + report JSON.
- **Rota B — `assisted_native_translation`** (obrigatoria para TAINA e demais
  assets de identidade): fonte high-res permanece referencia aprovada;
  construcao **no canvas 48x64**; silhueta, proporcao, cabelo, rosto, guarda,
  roupa e materiais tratados como **regioes semanticas**; paleta escolhida por
  **funcao**, nao frequencia; comparacao ampliada 8x; aprovacao humana antes de
  animacao e promocao. A conversao automatica pode gerar um controle basico, e
  esse controle **nao se declara final**.

**Seis paineis como contrato semantico mensuravel** (nao como exportacao):
mascara de silhueta, mapa de contornos, mapa de regioes/material, mapa de
sombra, mapa de highlight, composicao final, comparacao ampliada + sobreposicao
contra a fonte. Isso permite ao agente **explicar por que** uma candidata
falhou. Um diagrama de seis paineis nao prova proveniencia dos pixels finais.

**Dithering e opt-in por regiao/material.** Permitido: ceu, agua, pedra,
nevoa, metal, concreto, texturas de background, placas derivadas de render.
Proibido por default: contorno de personagem, rosto, olhos, maos, sprite
48x64, clusters de animacao, hit flash. Para a lineart da TAINA: **desligado**.
Matriz, strength e seed deterministicos e registrados.

**Obrigatorios de UX:** contact sheet automatico por job; escaneamento do grafo
**incremental e cacheado** (varredura total so com `--full`; hoje leva ~1min);
mensagens de falha que nomeiam a proxima acao causal — "nao foi possivel" e
defeito da ferramenta.

### 5. P2 — integracao de producao

`forge-rom symbols` (base preferivel: `sgdk-symbol-usage` CLI, nao o ROM
Analyser GUI; trate ultimo simbolo e gaps — calculo por diferenca de enderecos
e fragil), `forge-rom banks` (mapper parametrizado, sem hardcode SSF2),
heatmap de reuso de tiles (portar so a visualizacao, SHA-256 no lugar de
`hash()`), tilemap multi-paleta por tile (adaptar tiledpalettequant, MIT),
helper de flip de BG, `forge-scene budget`, `forge-evidence capture`.

**Flip horizontal — endurecer antes de canonizar:** espelhar cada tile nao
espelha a imagem; e preciso inverter a **ordem das colunas** da tilemap **e**
alternar HFLIP por tile. Antes de entrar no framework: extrair indice com
`TILE_INDEX_MASK`; nunca somar `baseTileIndex` a uma palavra cheia de
atributos; preservar ou substituir deliberadamente palette/priority/VFLIP;
XOR no HFLIP original; buffer estatico sem `MEM_alloc/MEM_free` no ciclo;
escrever linhas/retangulos em vez de uma chamada por tile sem medicao; validar
bounds e colisao de VRAM; testar imagem assimetrica em normal/H/V/HV e tilemap
comprimida; provar no BlastEm. A economia de tiles so pode ser **declarada**
depois do relatorio de deduplicacao e residencia.

MAP Blocks entra como sugestao/debug de ocupacao, **nunca** como colisao final
automatica. Transparencia vem de indice/papel declarado, nao de magenta
hardcoded.

### 6. Matriz de testes minima (nao negociavel)

- **Unitarios:** 512 cores + round-trip; snap em limites e empates; OKLab
  deterministico; alpha 0/255 aceito e alpha parcial rejeitado; index 0 so
  conforme contrato; PLTE 1/16/17/256; bit depth 1/2/4/8; dimensoes pares,
  impares e multiplas de 8; nearest vs interpolacao proibida; hashes
  exact/H/V/HV; ultimo simbolo, gaps e overflow de banco.
- **Golden/integracao:** conversao de paleta batendo com SGDK 2.11/ResComp
  (RGB2Genesis vira oraculo, nao dependencia); sprite transparente 48x64;
  personagem com 15 cores + index 0 passa; asset com 16 cores visiveis
  **falha**; tile com conflito de sub-paleta **falha**; atlas com pivos e
  footline; background 320x224 multi-paleta; tilemap assimetrica espelhada;
  build fixture SGDK lido no BlastEm.
- **Determinismo/resiliencia:** mesma entrada = mesmo SHA; interrupcao permite
  `--resume`; output parcial nunca substitui aprovado; cache invalida ao mudar
  tool/schema; arquivo corrompido falha fechado; dependencia opcional ausente
  degrada **com explicacao**; source read-only intacto; execucoes concorrentes
  nao colidem; failure injection em save, quantizacao, ResComp e captura.

### 7. Criterio de conclusao

`forge-art` so pode ser declarado `implemented` quando: CLI e schemas existem;
unitarios + golden + integracao + determinismo + failure injection passam;
self-checks exercitam fixture positiva **e** negativa; fonte nunca sobrescrita;
`technical_candidate` e `visually_approved` sao indistinguiveis em nenhum
status; um caso de sprite, um de background e um de tilemap passam ponta a
ponta; a conversao bate com o oraculo SGDK/ResComp; os relatorios sao
reproduziveis por outro agente; documentacao, memoria e changelog apontam para
o mesmo estado.

`ready_for_aaa` **nao** e criterio da ferramenta. Esse claim pertence ao jogo e
exige arte final, runtime, budget, audio, QA e evidencia de emulador.

### 8. Protocolo de reporte a cada entrega parcial

Sempre nesta ordem:

1. **O que foi provado** — comando executado + saida real (cole, nao parafraseie).
2. **O que falhou** — inclua a saida do erro. Teste que falha e reportado como falha.
3. **O que nao foi tentado** — explicito.
4. **Teto de claim atual** — um de: `documentado` / `implementado` /
   `testado` / `build_ok` / `rom_observada_no_blastem` / `slice_visual_aprovado`.
5. **Proxima acao causal** — uma frase, acionavel.

Nunca declare sucesso que os testes nao mostram. Nunca arredonde um gate.
Se o ambiente Linux quebrar (PATH shadowing conhecido em build.sh/new_project.sh/
graphify), reporte a quebra em vez de contornar silenciosamente.

Comece pelo `read_receipt` do item 0.

---

## FIM DO BLOCO DE PROMPT
