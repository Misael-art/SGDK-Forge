# Implementacao de proficiencia — 2026-09-07

Estado: parcial; cadeia tecnica observada, entrega global nao concluida. Nao e certificacao de jogo completo.
Autorizacao: pedido explicito para implementar o diagnostico e adaptar skills
visuais/sonoras a este host. Checkout anterior preservado; sem commit automatico.

## Alteracoes concretas

- F02: CI de recursos exige a fixture FORGE_REFERENCE existente; ausencia falha.
  Runner Linux separado `tools/sgdk_wrapper/ci/run_reference_e2e.py` cobre
  contratos, preflight, regressao, build, BlastEm, FREF observado e identidade da ROM.
- F03: inventario SHA-256 de todo SDK, parametros LTO/release e bridge;
  invalidacao de staging/biblioteca e identidade consumida no report de build.
- F04: alias de SDK por workspace, permissoes Flatpak derivadas de caminhos,
  eliminacao do alias global `/mnt/sdcard/sgdk_forge_wine_211` e lock com
  descritor fechado para processos Wine. Portabilidade Windows nao testada.
- F01: 23 divergências foram inventariadas; 5 ferramentas, 2 cópias do probe do
  `SMOKE_TEST` e 2 cópias do probe do `SCENE_TILEMAP_CURATION_FIXTURE` agora
  estão alinhadas/observadas, restando 14 divergências ativas em
  `measurement_drift_triage.json`. As migrações preservaram ABI, compilaram pela
  rota Linux e selaram evidência BlastEm; as demais cópias não foram sobrescritas
  nem recertificadas sem regressão própria.
- Referencia pixel-art: adaptacao dentro de art-conversion-pipeline; fonte,
  traducao nativa, paletas, tiles, animacao e preview usam as rotas existentes.
- Composicao: skill `megadrive-music-composition` descoberta na arvore central;
  compilador offline `tools/audio-tools/psg_score.py` emite VGM de partitura
  autoral com tres tons PSG, NTSC/PAL e loop. Conversao oficial XGM2 exercitada.
  Nao implementa FM/ruido/PCM e nao aprova mix ou trilha final por si so.

## Verificacoes concluidas

| Verificacao | Resultado | Escopo |
|---|---|---|
| Preparo do ambiente | ready; Graphify fresh apos recuperacao automatica | Host consultivo |
| Preflight | exit 0 sem avisos | Dependencias de build deste host |
| Contexto/higiene/metodologia FORGE_REFERENCE | passaram | Fixture existente |
| Identidade SDK | 2 testes passaram | Alteracoes header/fonte/gcc/lib/bridge/remocao, determinismo, ausencia |
| CI sem alvo | guard 8/8; exit 1 esperado | Regressao negativa do falso verde |
| Contratos canonicos | 10/10 | Hash, denominador zero, observacao, limites de claim |
| Audio existente | 15/15 | Ferramentas e contratos |
| PSG novo | 2 testes passaram + self-check | Parser independente e conversor oficial NTSC/PAL |
| Arte existente | 135/135 | Conformidade; nenhuma aprovacao estetica |
| Skill nova | quick_validate passou | Frontmatter e estrutura |
| Meta-gate | 19/19 self-checks; BLOCKED | 14 divergencias ativas ainda presentes |

Primeira execucao de build ficou parada em `sega.s`. Um servico Wine herdou
FD do lock; a heranca foi corrigida. Nova execucao tambem atingiu timeout no
mesmo ponto, portanto a heranca nao foi apresentada como causa unica do hang.
Compilacao isolada, primeiro minima com `-v`, depois com os flags completos,
passou. O runner agora registra atividade a cada 20s e interrompe uma etapa
apos 120s sem progresso de log, encerrando o grupo de processos.

## Limites vigentes

F05–F11 nao estao encerrados. O piloto recomendado continua MARE_BRAVA:
fidelidade nativa, residencia, BGM, performance e aprovacao em cena pesada
precisam ser resolvidas no projeto. Fonte autoral e qualidade final nao sao
produzidas automaticamente por um preset ou pelo numero de skills.
As alteracoes desta rodada nao promovem registry, `ready_for_aaa` ou produto.

Composicao VGM baseada na especificacao primaria
[VGM Specification](https://vgmrips.net/wiki/VGM_Specification), consultada
em 2026-09-07, e no contrato PSG dos fontes SGDK locais.

## Resultado vivo da fixture

E2E `passed` em 2026-09-07, screenshot inspecionado. ROM
`79020498f34d0ca4b8d2907659c82d4f605c77ecf5a8a650a09e478c1002f337` (131072 bytes), igual a referencia historica.
Frame 390, 349 amostras, zero violacoes, observed/required=7 e completed=true.
Report: `SGDK_projects/FORGE_REFERENCE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]/out/logs/reference_e2e_report.json`.
Bundle: `SGDK_projects/FORGE_REFERENCE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]/out/blastem_env_e2e_20260907T202559306613Z/blastem-linux-20260907T202650Z-2364411`.
Escopo estrito: contratos tecnicos FREF; nao e prova de arte/audio/jogo completo.
Cold build ainda exige investigacao do hang Wine observado; o caminho com
biblioteca recompilada e reutilizada fechou a cadeia.

## CI ampla e status consolidado

`run_golden_validate.ps1` foi executado com o alvo padrao: ainda reprova por
bootstrap local degradado. O default valida recursos de uma fixture tecnica;
`-DeliveryCloseout` aciona explicitamente os gates de entrega. A primeira
execucao com CloseoutGate obrigatorio acusava GDD/arte/AAA num laboratorio
neutro; a separacao de escopo foi corrigida sem aprovar o bootstrap antigo.

Resumo machine-readable: `validation_summary.json`. Fontes desta rodada:
`source_manifest.json`. Nenhum resultado autoriza declarar o workspace inteiro
pronto, o piloto finalizado ou a cadeia fria portavel em qualquer host.


## Atualizacao vigente — 2026-09-08: cold build observado

A execucao `20260907T203646582966Z` recompilou a biblioteca (`library_rebuild=true`)
e o jogo na mesma sessao Flatpak/Wine, depois fechou captura e FREF no BlastEm.
O log comprova os dois makes; o problema de passagem entre sessoes deixou de
se reproduzir nessa execucao. Nao e certificacao de todos os hosts.

ROM `79020498f34d0ca4b8d2907659c82d4f605c77ecf5a8a650a09e478c1002f337`, 131072 bytes, mesmo binario de referencia.
FREF: frame 360, 319 amostras, zero violacoes; observed/required=7, completed=true.
Screenshot inspecionado. Bundle vigente desta rodada:
`SGDK_projects/FORGE_REFERENCE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]/out/blastem_env_e2e_20260907T203646582966Z/blastem-linux-20260907T204142Z-2440026`.
Report historico preservado: `out/logs/reference_e2e_20260907T203646582966Z_report.json`.

A cura segura de caminhos ausentes foi executada por ensure_project_agent;
a `.agent` existente continua versao 2026.06.19 contra canonica 2026.09.05,
com `architecture_drift`. Arquivos existentes nao foram sobrescritos.
Prova de ROM nao apaga esse blocker da CI ampla.
