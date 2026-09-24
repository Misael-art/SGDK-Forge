# Visual Forge Toolchain — diagnostico e plano de implementacao

**versao:** 1.0.0
**data:** 2026-08-29
**status:** `partially_implemented_p1_cli_first`
**escopo:** ferramenta compartilhada do workspace + primeira aplicacao no MARE_BRAVA
**claim ceiling atual:** `technical_conversion_tested`; este arquivo nao prova visual, build, ROM ou AAA

## 1. Decisao executiva

O gargalo visual nao deve continuar dependente de automacao de ponteiro no
GIMP. O workspace precisa de uma suite CLI deterministica, retomavel,
auditavel e independente de GUI para ingestao, traducao, conversao,
validacao e promocao de arte SGDK/Mega Drive.

A suite deve manter duas rotas separadas:

1. `technical_conversion`: para pixel art nativa/quase nativa e assets cuja
   conversao mecanica preserva o sentido visual;
2. `assisted_native_translation`: para concept/high-res, personagem heroico,
   cenario autoral e qualquer asset cuja identidade nao sobreviva a quantizacao
   direta.

Regra central:

```text
technical_pass != visual_pass != budget_pass != emulator_pass != ready_for_aaa
```

Uma conversao automatica pode produzir o controle `basic`. A variante `elite`
precisa preservar silhueta, anatomia, materiais, identidade, composicao e papel
de gameplay. Fonte high-res da TAÍNA nunca vira asset final apenas por resize,
indexacao ou snap de cor.

## 2. Evidencia observada em 2026-08-29

### MARE_BRAVA

- 20 simbolos visuais ativos em `res/`; todos tecnicamente analisaveis.
- Os 20 simbolos estao declarados como `procedural_primitive` + `placeholder`.
- 319 fontes visuais em `data/`; 295 requerem conversao/tratamento conforme o
  snapshot do diagnostico.
- A fonte autoral high-res da TAÍNA foi aprovada para traducao pixel.
- Nao existe lineart 48x64 aprovada; `accepted_asset` permanece `null`.
- Candidatas 48x64 anteriores provaram que sintaxe tecnica pode coexistir com
  perda de identidade, proporcao, rosto, guarda e materiais.
- ROM existente comprova integracao tecnica por escopos limitados; nao comprova
  visual AAA, vertical slice, audio completo ou budget final.
- O meta-gate de ferramentas encontrou os nove self-checks canonicos verdes,
  mas bloqueou por copias stale; `runtime_probe.c/.h` do MARE_BRAVA aparece
  divergente do modelo canonico.

### Divergencias documentais que precisam ser eliminadas

- As tres imagens grandes estao artisticamente aprovadas como referencias de
  construcao, mas residem em pasta chamada `rejected/`.
- O memory bank antigo ainda descreve essas imagens como rejeicoes artisticas.
- O historico da rota B diz que o GIMP nao abriu; estado posterior confirma
  GIMP recuperado, mas automacao de ponteiro sem precisao suficiente.
- `doc/04-recursos-e-pipeline.md` ainda descreve `res/data/`, enquanto o layout
  canonico atual usa `data/source_art`, `data/processed` e `res/`.
- O contrato atual proibe promocao direta/quantizacao como final; a nova suite
  deve permitir gerar um `basic_control` sem confundi-lo com `elite/final`.

## 3. Defeitos do pipeline visual atual

### `tools/image-tools/batch_resize_index.py`

- usa `LANCZOS`, criando pixels intermediarios e halo em fontes pixel;
- pode salvar RGBA quando `transparency=true`;
- usa median-cut global sem papeis semanticos de material;
- nao possui oraculo unico SGDK para cor;
- nao produz `basic` e `elite` separados;
- pode sobrescrever o input;
- nao possui job imutavel, cache por hash, rollback ou failure injection;
- nao prova PLTE compacta, bit depth final e index 0 de ponta a ponta.

### `tools/image-tools/fix_png_transparency_final.py`

- converte para RGBA, compoe em preto, quantiza e remove transparencia;
- pode destruir o slot transparente e a semantica da paleta;
- nao deve permanecer como etapa final canonica.

### `tools/sgdk_wrapper/test_art_pipeline.py`

- aceita RGBA intermediario como resultado esperado;
- testa o pipeline antigo, nao o contrato pixel-strict vigente;
- precisa ser substituido por regressao que falhe com RGBA, PLTE inflada,
  Lanczos, index 0 incorreto, cor fora da grade e output nao deterministico.

### `normalize_indexed_sgdk_png.py`

- e aproveitavel como normalizador de PNG ja indexado;
- nao resolve classificacao, paleta semantica, traducao nativa ou 9-bit oracle.

## 4. Modelo de cor canonico

Nao misturar:

- `vdp_code`: niveis 0..7 por canal / palavra CRAM;
- `authoring_rgb`: `00,22,44,66,88,AA,CC,EE` conforme regra do workspace;
- `display_rgb`: expansao para monitor/emulador, que pode usar outra curva;
- RGBA4444/ABGR: formato distinto e proibido como substituto silencioso da
  paleta CRAM.

Criar uma biblioteca unica com:

- `rgb24_to_vdp_color`;
- `vdp_color_to_authoring_rgb`;
- `vdp_color_to_display_rgb`;
- `snap_rgb_to_vdp_grid`;
- distancia RGB, HSV e OKLab;
- selecao perceptual com preservacao de contraste e papeis de material;
- golden vectors comparados aos headers/ResComp SGDK 2.11;
- self-check positivo e negativo.

Todas as ferramentas de cor devem depender dessa biblioteca. Tabelas copiadas
e divergentes sao proibidas.

## 5. Arquitetura proposta

Nome de trabalho: `forge-art`.

```text
source + lineage + contract
  -> inspect/classify
  -> semantic parse
  -> route selection
      -> technical_conversion -> basic
      -> assisted_native_translation -> elite
  -> palette/index/grid
  -> sprite/tile/map assembly
  -> pixel + visual + budget gates
  -> staged promotion
  -> ResComp/build
  -> BlastEm/evidence/freshness
```

### Comandos previstos

```text
forge-art inspect
forge-art convert
forge-art translate
forge-art palette
forge-art atlas
forge-art tiles
forge-art validate
forge-art compare
forge-art promote
forge-rom symbols
forge-rom banks
forge-scene budget
```

O CLI e a autoridade. GIMP, Aseprite, Oeste Editor, Ether ou outro editor sao
frontends/adaptadores opcionais, nunca dependencia do core.

### Contrato de job

Cada execucao cria um diretorio imutavel identificado por hash:

```text
out/visual_jobs/<asset_id>/<job_id>/
  input_manifest.json
  source_hashes.json
  toolchain_versions.json
  route_decision.json
  observed_ir.json
  derived_structure_ir.json
  semantic_parse_report.json
  basic/
  elite/
  review/
  reports/
  promotion_candidate/
```

Requisitos:

- mesma fonte + mesma spec + mesmas versoes = mesmo hash de output;
- nunca sobrescrever a fonte;
- escrita atomica e rollback;
- `--dry-run`, `--explain`, `--resume`, `--force-new-job`;
- cache por SHA-256 e invalidacao por versao/schema;
- saida JSON estavel e codigos de erro documentados;
- um report deve explicar a proxima acao causal;
- nenhuma excecao silenciosa ou fallback que relaxe gate.

## 6. Rotas visuais

### 6.1 `technical_conversion`

Indicada para:

- arte nascida pixel;
- asset ja proximo do tamanho final;
- lote secundario com identidade nao heroica;
- normalizacao de indexacao/paleta/grid.

Politica de escala:

- pixel art: nearest-neighbor somente;
- foto/render/concept: downsample controlado pode gerar apenas `basic_control`;
- Lanczos/bilinear/bicubico sao blockers em pixel nativo/final;
- padding/crop precisam ser declarados e preservar pivot/baseline.

### 6.2 `assisted_native_translation`

Indicada para:

- personagem heroico 48x64;
- boss, NPC expressivo e inimigo principal;
- cena autoral/monumental;
- fonte high-res ou IA;
- material cuja alma visual se perde na quantizacao.

Ordem obrigatoria:

1. fonte de verdade + `visual_dna_manifest`;
2. semantic parse;
3. silhueta e lineart 1 px em grid nativo;
4. volumes/material regions;
5. paleta por material;
6. sombras;
7. highlights;
8. polimento de clusters;
9. `original/basic/elite` em nativo e ampliacao;
10. fidelidade, pixel strict, budget e ROM.

O processo dos seis paineis fica formalizado como artefato de explicacao:

- Base/silhueta;
- Contornos;
- Volumes;
- Sombras;
- Iluminacao;
- Polimento final.

Os paineis nao provam por si so a proveniencia dos pixels finais. Eles formam
um contrato semantico e um painel de review.

## 7. Paleta e dithering

### Paleta

- index 0 reservado conforme papel do asset;
- ate 15 cores visiveis por sub-paleta;
- PLTE compacta <= 16;
- PNG modo P, bit depth compativel com 4 bpp;
- slots semanticos por material: outline, pele, roupa principal/secundaria,
  sombra, base, highlight, acento;
- OKLab pode auxiliar selecao, mas nao substitui julgamento de material;
- `palette_vitality_check` para evitar paleta tecnicamente valida e morta.

### Dithering

- opt-in por regiao/material;
- Bayer permitido em ceu, agua, pedra, nevoa, metal e texturas quando melhora
  leitura CRT-aware;
- proibido como default em lineart, olhos, rosto, maos, outline e hit signal;
- toda matriz, strength e seed precisam ser deterministicas e registradas;
- `dither off` deve existir como controle.

## 8. Sprites, atlas e animacao

Incorporar, por reimplementacao testada:

- envelope comum de frames;
- bbox justo;
- alinhamento bottom-center;
- pivots e contact points;
- padding para multiplo de 8;
- strips por acao, nao atlas monolitico como unidade de curadoria;
- remocao de fragmentos/islands;
- preview GIF/WebP do output final;
- `frame_delta_report`, `foot_contact_report`, `pivot_overlay`;
- separacao de personagem e FX;
- custo por frame e active animation window.

KMeans aleatorio, deteccao de fundo pelo primeiro pixel, BGR/RGB ambiguo e
hardcode de celula sem contrato sao proibidos.

## 9. Tiles, mapas e cenarios

### Deduplicacao

- hash estavel de bytes canonicos, nunca `hash()` do Python;
- medir exact, H, V e HV;
- preservar indice, palette, priority, H/V flags e origem;
- emitir `tilemap_flag_report.json` e economia real;
- heatmap e tileset sheet como review visual.

### Multi-paleta por tile

Adaptar a ideia do Tiled Palette Quantization para:

- atribuicao de PAL0-PAL3 por tile;
- index zero configuravel;
- conflito por tile;
- custo/reuso apos atribuicao;
- `per_tile_palette_conflict_report.json` com zero conflitos para entrega;
- output SGDK e report deterministico.

### Cenario

- imagem inteira convertida e suspeita por default;
- medir kit modular, landmarks, metatiles, janela ativa e streaming;
- separar world total de resident window;
- gerar `scene_tilemap_conversion_report.json`;
- comparar `basic`, `elite` e `rom`;
- cenario do CAIS precisa de profundidade, faixa jogavel, narrativa ambiental e
  hierarquia BG_B < BG_A < atores, nao apenas imagem bonita.

## 10. Flip horizontal de IMAGE/BG

Principio aprovado:

- inverter a ordem das colunas da tilemap;
- alternar HFLIP por tile.

Antes de canonizar o helper:

- extrair `src_index` com mascara correta;
- preservar/trocar deliberadamente palette, priority e VFLIP;
- usar XOR no HFLIP original;
- impedir soma de `baseTileIndex` sobre palavra com atributos;
- validar VRAM range e overlap;
- usar buffer estatico/retangulo, nao heap no loop;
- medir custo de escrita/DMA;
- fixtures assimetricas para normal, H, V e HV;
- teste comprimido/descomprimido conforme API real;
- captura BlastEm e tilemap flag report.

## 11. Analise de ROM, bancos e simbolos

### `forge-rom symbols`

- usar `sgdk-symbol-usage` como referencia/base quando a licenca permitir;
- parser CLI, sem GUI obrigatoria;
- tamanho por symbol/map com tratamento do ultimo simbolo e gaps;
- separar ROM, RAM, codigo, dados, audio, sprites, tiles/maps;
- JSON + tabela humana + CSV opcional;
- origem e confianca de cada classificacao.

### `forge-rom banks`

- mapper e layout declarados em spec, sem hardcode SSF2;
- validar range, overlap, gaps, near/far e teto;
- reportar banco, ocupacao, maior simbolo, fragmentacao e risco;
- fixtures de ultimo simbolo, gap grande, banco vazio e overflow.

### Heatmap e map blocks

- heatmap usa hashes estaveis e pode sobrepor frequencia/reuso;
- MAP Blocks serve como proposta/debug de ocupacao, nunca colisao final;
- transparencia deve vir de indice/papel declarado, nao RGB magenta hardcoded;
- slopes, one-way, solid/hit/hurt/push continuam em contratos de colisao.

## 12. Matriz de incorporacao das referencias estudadas

| Item | Valor | Acao |
|---|---|---|
| GDB_ROM_ANALISER | drilldown e categorias | reescrever CLI/JSON; nao importar GUI/heuristicas cegas |
| GDB_BANK_ANALISER | visualizacao de bancos | parametrizar mapper e corrigir tamanho/gaps |
| GDB_COLOR_CUBE | vizinhanca das 512 cores | reusar conceito sobre biblioteca canonica de cor |
| GDB_HEATMAP | visual de reuso | portar visualizacao; substituir `hash()` |
| MAP_BLOCKS | ocupacao 8x8 | manter como debug/proposta |
| SLK_img2pixel/SoftLK | CLI, paleta, dither, pos | backend opcional; CC0 observado |
| Tiled Palette Quantization | otimizacao tile-aware | adaptar como backend de background; MIT observado |
| sgdk-aseprite-scripts | OKLab/ramps/editor | adaptador opcional, nao core |
| sgdk-symbol-usage | parser/relatorio de simbolos | base preferencial para `forge-rom symbols` |
| Ether | GUI/batch palette | comparador/backend opcional |
| ferramentas Vagno | UX, Bayer, gradient, match | reimplementar conceitos apos oraculo/licenca |
| Sprite Converter Colab | bbox/atlas/alinhamento | reescrever deterministico e com pivots |
| RGB2Genesis | comparacao de conversao | converter em golden oracle |
| mugen2sgdk | AIR/frames/hitboxes | importador opcional apos licenca/proveniencia |
| Tile Analysis | custo por frame | integrar com ResComp/residencia |
| Oeste Editor/Discord | referencia incompleta | pendente de conteudo/licenca auditavel |

Repositorio publico sem licenca explicita nao autoriza copiar codigo. Registrar
licenca, versao, hash e arquivos incorporados em `third_party_manifest`.

## 13. Plano de implementacao

### P0 — fundacao e falsos verdes

1. criar ADR e schemas do `forge-art`;
2. criar biblioteca canonica de cor + golden tests SGDK/ResComp;
3. substituir comportamento destrutivo de resize/transparency;
4. corrigir testes que aceitam RGBA/PLTE inflada;
5. implementar jobs imutaveis, hashes, cache, resume e dry-run;
6. criar self-checks positivos e negativos;
7. reconciliar docs da TAÍNA e `runtime_probe` stale;
8. provar que a nova rota nao altera sources nem `res/` sem promocao.

### P1 — conversao visual resiliente

1. inspect/classify/semantic parse;
2. converter `basic_control`;
3. paleta semantica/OKLab/9-bit;
4. transparencia/index/PLTE/bit depth;
5. atlas, pivots, islands e strips;
6. tiles exact/H/V/HV + heatmap;
7. multi-paleta por tile;
8. contact sheets e `original/basic/elite`;
9. reports de promocao.

### P2 — aplicacao no MARE_BRAVA

1. gerar controle basic da fonte aprovada da TAÍNA sem promovê-lo;
2. reconstruir lineart 48x64 elite no grid nativo;
3. aprovar identidade/fidelidade antes de cor;
4. fechar paleta por material e idle/guarda;
5. produzir strips minimos do slice com pivots/motion;
6. seguir para o segundo personagem;
7. reautorar CAIS como kit modular e composicao multi-plano;
8. FX/HUD/audio/runtime somente conforme contratos;
9. budget VDP e pior quadro;
10. build, BlastEm, VDP dump, freshness e visual delivery.

### P3 — analise e integracoes

1. symbols/banks;
2. helper de flip BG;
3. MUGEN importer;
4. adapters Aseprite/GIMP/Oeste/Ether;
5. UI opcional sobre o CLI comprovado.

## 14. Matriz minima de testes

### Unitarios

- 512 cores VDP e round-trip;
- snap em limites/empates;
- OKLab deterministico;
- alpha 0/255 e alpha parcial rejeitado;
- index 0 usado somente conforme contrato;
- PLTE 1, 16, 17 e 256;
- bit depth 1/2/4/8;
- dimensoes pares, impares e multiplos de 8;
- nearest vs interpolacao proibida;
- hashes exact/H/V/HV;
- ultimo simbolo, gaps e overflow de banco.

### Golden/integracao

- comparar conversao de paleta ao SGDK 2.11/ResComp;
- sprite transparente 48x64;
- personagem com 15 cores + index 0;
- asset com 16 cores visiveis deve falhar;
- tile com conflito de sub-paleta deve falhar;
- atlas com pivots e footline;
- background 320x224 multi-paleta;
- tilemap assimetrica espelhada;
- build fixture SGDK e leitura no BlastEm.

### Determinismo e resiliencia

- mesma entrada gera mesmo SHA;
- interrupcao no meio permite `--resume`;
- output parcial nunca substitui aprovado;
- cache invalida quando tool/schema muda;
- arquivo corrupto falha fechado;
- dependencia opcional ausente degrada com explicacao;
- source read-only continua intacto;
- execucoes concorrentes nao colidem;
- failure injection em save, quantizacao, ResComp e captura.

### Gates finais

- `pixel_compliance_report`;
- `model_sheet_to_sprite_fidelity_report`;
- `palette_vitality_check`;
- `sprite_artifact_report`;
- `asset_optimization_report`;
- `vram_residency_report`;
- `sprite_scanline_pressure_report`;
- `visual_delivery_gate_report`;
- `live_scene_bar_report`;
- `validation_report`, `freshness_audit`, `scene_closeout_gate`;
- BlastEm com screenshot, SRAM e VDP dump vinculados ao hash da ROM.

## 15. Criterio de conclusao da ferramenta

O `forge-art` so pode ser declarado `implemented` quando:

- CLI e schemas existem;
- testes unitarios, golden, integracao, determinismo e failure injection passam;
- self-checks exercitam fixture positiva e negativa;
- fonte nunca e sobrescrita;
- `basic` e `elite` nao podem ser confundidos no status;
- um caso de sprite, um de background e um de tilemap passam ponta a ponta;
- a conversao bate com o oraculo SGDK/ResComp;
- relatórios sao reproduziveis por outro agente;
- documentacao, memoria e changelog apontam para o mesmo estado.

`ready_for_aaa` nao e criterio da ferramenta isolada. O claim pertence ao jogo
e exige arte final, runtime, budget, audio, QA e evidencia de emulador.

## 16. Criterio de conclusao no MARE_BRAVA

O plano nao termina ao gerar a TAÍNA. O primeiro fechamento honesto exige:

- TAÍNA aprovada visualmente e integrada;
- segundo personagem do slice com o mesmo piso;
- CAIS reautorado com kit modular e hierarquia de planos;
- FX de gameplay com fases e consequencia;
- HUD/identidade nao-debug;
- combate minimo do slice funcional;
- audio implementado e validado;
- pior quadro dentro do budget;
- ROM corrente observada no BlastEm;
- sete eixos de QA e barra viva fechados;
- nenhum blocker vigente nos reports de promocao.

Se qualquer item faltar, retornar o menor status provado e a proxima acao
causal. Nunca relaxar gate para concluir.

## 17. Referencias externas auditadas

- https://captain4lk.itch.io/slk-img2pixel
- https://github.com/Captain4LK/SoftLK-tools
- https://rilden.github.io/tiledpalettequant/
- https://github.com/retrodevbr/sgdk-aseprite-scripts
- https://github.com/retrodevbr/sgdk-symbol-usage
- https://github.com/retrodevbr/awesome-sgdk
- https://github.com/junixbr/Ether
- https://github.com/VagnoSilva/SGDK_FLIP_BG_IMAGE
- https://github.com/VagnoSilva/SGDK_Palette_Generetor
- https://github.com/VagnoSilva/SGDK_Bayer_Dithering_Converter
- https://github.com/VagnoSilva/SGDK_Gradiente_generator
- https://github.com/VagnoSilva/SGDK_color_match

Patreon/Oeste Editor e mensagem Discord permanecem `pending_auditable_content`.

## 18. Fontes internas obrigatorias

- `AGENTS.md`
- `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`
- `tools/sgdk_wrapper/.agent/references/production_truth_protocol.md`
- `tools/sgdk_wrapper/.agent/references/production_visual_quality_contract.md`
- `tools/sgdk_wrapper/.agent/skills/art/art-conversion-pipeline/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/art/art-translation-to-vdp/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/art/megadrive-pixel-strict-rules/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/operation/sgdk-build-wrapper-operator/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/governance/aaa-pipeline-guardian/SKILL.md`

---

# Addendum v1.1.0 — reafirmacao e deltas (2026-08-30)

**status histórico:** `approved_plan_pending_implementation`; superado pelo Addendum v1.2.0
**claim ceiling:** `documentado`. Este addendum nao prova build, ROM nem AAA.

O diagnostico de 2026-08-29 foi reapresentado integralmente em 2026-08-30 e
confirmado sem contradicao. As secoes 1-18 permanecem canonicas. Os itens
abaixo sao deltas ou enfases que ainda nao estavam explicitos.

## A1. Tese central reafirmada

Conversao automatica resolve **conformidade**; ela **nao** produz qualidade
artistica AAA. Reduzir uma ilustracao high-res para 48x64, indexar e aplicar
9 bits gera uma **candidata tecnica**, nunca uma personagem fiel. As candidatas
nativas anteriores ja provaram isso: passaram em requisitos fisicos e perderam
identidade, anatomia e leitura.

Regra de nomenclatura de saida (obrigatoria, dois niveis):

```text
technical_candidate   # gerado por maquina; NUNCA promovivel sozinho
visually_approved     # exige decisao humana registrada no job
```

Promocao para `res/` so ocorre depois dos **dois** gates.

## A2. Comandos adicionais na suite

Alem dos listados na secao 5:

```text
forge-art promote          # ja previsto, agora com os dois niveis acima
forge-evidence capture     # NOVO: captura BlastEm/VDP/screenshot vinculada a hash de ROM
```

## A3. Requisitos de UX/performance nao registrados antes

- **Contact sheet automatico** para aprovacao humana em cada job (nao opcional).
- **Escaneamento incremental do grafo ativo**: o diagnostico atual leva ~1 min
  porque percorre centenas de fontes/evidencias. O scanner deve ser incremental
  e cacheado por hash; varredura total vira `--full`.
- **Falhas com causa acionavel**: mensagem deve nomear a proxima acao causal.
  "nao foi possivel" e considerado defeito da ferramenta.

## A4. Divergencia numerica de cor — registro explicito

Existem tres grades circulando e elas **nao** sao intercambiaveis:

| Origem | Passo por canal | Papel |
|---|---|---|
| GDB Color Cube / ferramentas Vagno | `00,24,48,...,FF` | display/visualizacao |
| Regra estrita do workspace | `00,22,44,...,EE` | `authoring_rgb` canonico |
| SGDK_Palette_Generetor auditado | RGBA4444/ABGR (4 bits/canal) | **NAO** e o formato CRAM do MD |

"9 bits" = 3 bits por canal = 512 combinacoes teoricas de CRAM. Nao significa
"PNG de 9 bits": o PNG final permanece indexado, modo P, ate 16 entradas PLTE.
Qualquer ferramenta que produza tabela de cor propria em vez de consumir a
biblioteca canonica e um blocker P0.

## A5. Meta-gate de ferramentas — estado bloqueado

Os nove self-checks canonicos passam, mas o gate geral **bloqueia** por 20
copias desatualizadas, entre elas `runtime_probe.c` e `runtime_probe.h` do
MARE_BRAVA. Consequencia operacional imediata:

> A telemetria do MARE_BRAVA **nao pode sustentar novos claims de performance**
> ate ser reconciliada com o modelo canonico.

## A6. P0 — reconciliacao documental da TAINA (bloqueador de agentes)

Quatro contradicoes fisicas/documentais coexistem hoje e ja induziram erro:

1. memory bank diz que as imagens grandes foram **rejeitadas**;
2. `visual_source_of_truth_taina_v02.json` diz que foram **aprovadas
   artisticamente como referencia de construcao**;
3. o relatorio da rota B diz GIMP **indisponivel**; a decisao final diz
   `native_pixel_authoring_in_progress_in_recovered_gimp`;
4. os arquivos continuam fisicamente numa pasta chamada `rejected/`.

Acao P0: renomear a pasta para papel real (ex.: `data/source_art/reference/`),
alinhar memory bank ao contrato v02, datar cada estado (estado temporal
explicito) e manter a proibicao de quantizar/tracar essas imagens como asset
final — permitindo, porem, gerar `technical_candidate` a partir delas.

## A7. Estado do MARE_BRAVA congelado nesta data

- 20 assets ativos em `res/`, todos declarados `procedural_primitive` +
  `placeholder`;
- 319 fontes em `data/`; 295 ainda exigem conversao/tratamento;
- fonte autoral high-res da TAINA: **aprovada** como referencia;
- lineart 48x64: **inexistente**; `accepted_asset: null`;
- TAINA runtime existente: `runtime_candidate_not_aaa_not_source`;
- ROM atual: prova de integracao tecnica, **nao** vertical slice visual.

Fontes: `doc/10-memory-bank.md:16` e
`doc/contracts/visual_source_of_truth_taina_v02.json:1` do MARE_BRAVA.

## A8. Licencas — restricao dura

Os repositorios Vagno auditados **nao apresentaram licenca explicita** nos
snapshots baixados. Algoritmos e comportamentos podem ser estudados;
**codigo nao pode ser copiado** para a ferramenta canonica sem autorizacao
esclarecida. Patreon do Oeste Editor e a mensagem privada do Discord
permanecem `pending_auditable_content` — referencia, nunca dependencia.

Backends com licenca observada e utilizavel: SoftLK-tools (CC0),
tiledpalettequant (MIT).

## A9. Prioridades consolidadas (substituem a numeracao da secao 13 em caso de conflito)

- **P0 — fundacao:** harmonizar documentos da TAINA; substituir
  conversor/fixer contraditorio; biblioteca canonica de cor; golden tests com
  preservacao de index 0; reconciliar `runtime_probe` do MARE_BRAVA.
- **P1 — ferramenta visual operacional:** classificador de fontes; conversao
  deterministica; paleta semantica e tile-aware; atlas/pivos/dedup; relatorios
  e contact sheets; rota assistida de traducao 48x64.
- **P2 — integracao de producao:** heatmap estavel; tilemap multi-paleta;
  ROM/symbol/bank analysis; helper de flip; gates ResComp/VRAM/BlastEm.
- **P3 — integracoes opcionais:** Aseprite, GIMP, Oeste Editor e Ether como
  frontends; importador MUGEN; painel interativo do cubo de cores.

## A10. Veredito

O metodo esta correto porque o projeto **recusou promover assets tecnicamente
inadequados** e preservou honestidade de proveniencia. A autonomia artistica
emperrou por dois motivos distintos, que precisam continuar separados:

1. dependencia de interacao manual imprecisa (automacao de ponteiro no GIMP);
2. pipeline de conversao que contradiz as proprias regras estritas.

A evolucao correta nao e "automatizar qualquer reducao e chamar de final". E
construir uma fabrica visual que automatiza integralmente a **conformidade**,
assiste a **traducao** de high-res para pixel nativo, mede fidelidade e
orcamento, registra decisoes humanas, e so declara AAA depois da cena viva
comprovada no BlastEm.

**Prompt de execucao:** `doc/prompts_modelo/PROMPT_FORGE_ART_IMPLEMENTACAO.md`

---

# Addendum v1.2.0 — CLI-first e persistencia causal (2026-08-30)

**status:** `partially_implemented_p1_cli_first`
**claim ceiling:** `technical_conversion_tested`; nenhum claim visual/AAA

## B1. Estado medido

- `forge-art convert` existe e passou o E2E técnico staging-only.
- `forge-art self-check` passou 107/107 após esta curadoria.
- GIMP 3.2.4 passou preflight headless com `python-fu-eval`, sentinel observado
  e exit 0.
- O adaptador GIMP possui zero operações de produção registradas. Isso é
  deliberado: preflight não equivale a conversor ou produtor artístico.

## B2. Decisão de ferramenta

Operação determinística por screenshots/ponteiro é
`interaction_channel_mismatch`. A ordem canônica passa a ser:

1. `forge-art` para cor VDP, indexação e contrato pixel;
2. Pillow/ImageMagick para transformação mecânica;
3. GIMP batch apenas para operação GIMP/GEGL estática, versionada e testada;
4. produtor visual capaz/gate humano para tradução semântica.

GIMP GUI é frontend humano opcional. Script Python-Fu gerado arbitrariamente
pelo prompt, escrita direta em source/`res/` e promoção automática permanecem
proibidos.

## B3. Persistência

`tools/sgdk_wrapper/.agent/workflows/causal-persistence-loop.md` é o owner de
blocker repetido, falha de uma única ferramenta e pedidos de continuidade. A
falha encerra a rota após duas tentativas equivalentes sem evidência nova; o
projeto só para quando o blocker crítico e o esgotamento de rotas seguras forem
provados.
