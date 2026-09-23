# Diagnostico de capacidade do agente SGDK - 2026-07-18

Status: `diagnostic_registered_no_runtime_promotion`

Escopo: framework canonico de agentes, wrapper SGDK, projetos de referencia e
evidencias existentes no workspace.

Artefato machine-readable associado:
`doc/agent_learning/agent_capability_remediation_backlog_2026-07-18.json`.

## 1. Ordem de leitura para agentes

1. `AGENTS.md` da raiz e regras herdadas.
2. `doc/06_AI_MEMORY_BANK.md`.
3. Este diagnostico.
4. O backlog JSON associado.
5. A skill owner e os workflows citados no item assumido.

Nenhum item deste documento autoriza promocao de status. Implementacao,
build, teste em emulador, validacao de budget e entrega continuam sendo
estados independentes.

## 2. Decisao executiva

O workspace possui um framework avancado de producao SGDK assistida, com ROMs
reais, contratos, skills especializadas e rastreabilidade. Ele ainda nao prova
ser um agente autonomo capaz de criar e entregar jogos completos de alta
qualidade para Mega Drive.

Classificacao atual:

- nivel: `functional_with_human_supervision`;
- nota de auditoria: `2.7/5`;
- claim ceiling global: `technical_vertical_slice_candidate`;
- `ready_for_aaa`: `false`;
- jogo completo: `not_proven`;
- hardware real: `not_proven`;
- autonomia mensurada: `not_measured`.

## 3. Limitacoes da sessao de auditoria

- o host da sessao nao possuia `pwsh`, `powershell` ou executor equivalente;
- o bootstrap canonico, Graphify, build wrapper e uma nova sessao BlastEm nao
  puderam ser reexecutados;
- evidencias existentes foram inspecionadas e tiveram hashes confrontados;
- a maior parte das evidencias maduras data de junho de 2026 e deve ser
  tratada como historica ate nova captura;
- o worktree estava amplamente modificado antes desta auditoria;
- nenhuma mudanca de runtime, arte, ROM ou validador foi feita por este
  diagnostico.

Ausencia de executor nesta sessao e blocker de verificacao fresca, nao prova
de defeito no projeto nem aprovacao implicita.

## 4. Inventario operacional

| Componente | Quantidade/estado | Decisao |
|---|---:|---|
| Skills ativas | 47 | cobertura ampla |
| Workflows | 42 | cobertura ampla |
| Pipelines JSON | 3 | presentes |
| Personas | 10 | pedagogicas; nao fonte operacional |
| Tecnicas no registry | 114 | registry valido |
| Tags de tecnica | 168 | registry valido |
| `MESTRE_STANDARD` | 0 | nenhuma maestria formal |
| `MESTRE_PRIORITARIA` | 0 | nenhuma maestria formal |
| `LABORATORIO` | 49 | exige prova adicional |
| `TEORICA_*` | 65 | conhecimento nao equivale a dominio |

## 5. Achado critico: falso positivo de evidencia visual

A evidencia canonica de BLUE_CIRCUIT esta vinculada por hash a ROM, SRAM e
VDP dump, mas `out/evidence/blastem/screenshot.png` e praticamente branca.

Medidas da captura:

- `is_blank_or_solid=true`;
- cor branca dominante: `0.900528`;
- edge density: `0.014408`;
- titulo da janela: `BlastEm - 48.3 fps`;
- captura runtime: `partial`, com 151 de 900 frames esperados;
- fluidez, leitura, naturalidade e impacto perceptual: `0`.

Em conflito, o contrato
`BLUE_CIRCUIT/doc/contracts/visual_delivery_gate_report.json` registra
`technical_ready=true`, `creative_ready=true` e score visual `0.84`.

Decisao: o gate atual autentica a identidade do arquivo, mas nao a validade
semantica da imagem. Enquanto isso nao for corrigido, screenshot, gameplay,
performance e qualidade criativa nao podem ser promovidos automaticamente.

O utilitario `tools/image-tools/screenshot_integrity.py` detectou corretamente
a captura branca, mas estava untracked e nao integrado ao gate canonico no
momento da auditoria. Ele e candidato a integracao, nao canon aprovado por
inercia.

## 6. Matriz claim -> owner -> artefato -> decisao

| Claim | Owner primario | Artefato minimo | Decisao atual |
|---|---|---|---|
| Build/ROM | `sgdk-build-wrapper-operator` | ROM + validation report + hash | historicamente comprovado |
| Boot BlastEm | `emulator-vdp-evidence-curator` | screenshot + SRAM + VDP dump | historico; exige refresh |
| Gameplay | `sgdk-runtime-coder` | captura informativa + input/runtime probe | parcial |
| Input | `input-system-sgdk` | contrato + teste de held/pressed/released | implementacao encontrada |
| Colisao | `collision-system-architect` | fixture + runtime evidence | implementacao parcial |
| Camera | `camera-system-sgdk` | contrato + movimento capturado | parcial |
| Entidades | `entity-polymorphism-architect` | archetypes + runtime evidence | parcial |
| VDP/DMA/sprites | `megadrive-vdp-budget-analyst` | dump + budget + scanline | tecnico parcial |
| Qualidade visual | `visual-excellence-standards` | captura valida + aprovacao perceptual | reprovada |
| Assets | `art-asset-diagnostic` | report tecnico + fonte rastreada | parcial |
| Audio | `xgm2-audio-director` | XGM/FM/PSG + SFX simultaneo | parcial; `total_xgm=0` |
| 60 fps | `emulator-vdp-evidence-curator` | janela completa de metricas | nao comprovado |
| Hardware real | `rom-mastering` | sessao rastreada em hardware/FPGA | ausente |
| Autonomia | `aaa-pipeline-guardian` | ledger de intervencoes/tentativas | nao mensurada |
| Continuidade | `game-state-transition-architect` | retomada reproduzivel + memoria coerente | parcial |
| Entrega AAA | `aaa-pipeline-guardian` | todos os gates aplicaveis | rejeitada |

## 7. Evidencias verificadas

Os bundles abaixo tiveram ROM, screenshot, SRAM e VDP dump confrontados com
os hashes declarados:

### BLUE_CIRCUIT

- ROM: `ff8fb909620a13f5fdf402f03b1bdac292244a23096dac50ac80f3ad98bdd160`;
- ROM size: `262144` bytes;
- screenshot: `a1a796...14807`;
- SRAM: `fba01d...995f`;
- VDP dump: `4119fc...f11e`;
- identidade do bundle: confirmada;
- validade semantica da captura: rejeitada.

### Celestial Chase Revive

- ROM: `4c8302...d60e`;
- ROM size: `131072` bytes;
- screenshot: `8f6422...4462`;
- SRAM: `112ee0...dd06`;
- VDP dump: `421446...eb7a`;
- identidade do bundle: confirmada;
- qualidade criativa: bloqueada pelo proprio report.

### Celestial Chase visual benchmark

- ROM: `984d31...62a9`;
- ROM size: `393216` bytes;
- screenshot: `d1c570...b903`;
- SRAM: `b6b334...4210`;
- VDP dump: `e06a7a...b9e3`;
- identidade do bundle: confirmada;
- screenshot principal: tela textual de resultado, insuficiente para provar
  gameplay ou excelencia visual.

Hashes abreviados acima servem como indice humano. Agentes devem obter os
valores completos dos reports e recalcular SHA-256 antes de qualquer promocao.

## 8. Resultados dos testes portaveis

| Teste | Resultado | Consequencia |
|---|---|---|
| `self_check_agentic_aaa_contracts.py` | passou | self-checks basicos ativos |
| strip/scanline/DMA/YM2612 self-checks | passaram | ferramentas isoladas funcionais |
| `validate_technique_registry.py` | passou | 114 entradas, 168 tags |
| `validate_template_registry.py` | passou | 2 templates |
| `validate_skill_framework.py` | falhou | 13 hashes lifecycle divergentes |
| `test_schema_contract_gates.py` | falhou ao iniciar | dependencia `jsonschema` ausente |

Payloads lifecycle com hash divergente:

- `architecture/level-manifest-architect`;
- `art/color-conversion-curator`;
- `art/dither-composite-transparency`;
- `art/palette-cram-curator`;
- `art/sprite-asset-budget-curator`;
- `art/tilemap-attribute-director`;
- `audio/sfx-prep-fm-psg-pcm`;
- `audio/z80-audio-boundary-architect`;
- `code/articulated-sprite-architect`;
- `code/software-tile-rasterizer`;
- `hardware/hscroll-linescroll-road-fx`;
- `hardware/raster-palette-hint-director`;
- `hardware/sprite-scanline-budgeter`.

## 9. Diagnostico de assets

| Projeto | Resultado tecnico | Leitura correta |
|---|---|---|
| BLUE_CIRCUIT | 20 assets; 6 precisam conversao | fonte e `res/` nao devem ser confundidos |
| Celestial Chase Revive | 15 aceitos tecnicamente | alertas de cor, magenta e dimensao permanecem |
| Visual benchmark | 55 assets; 17 precisam conversao | pipeline ainda heterogeneo |
| MUGEN | retornou `3_no_art` | bug de integracao: arte existente nao foi descoberta |

O `art_diagnostic.py` tambem emitiu avisos de deprecacao de `Image.getdata`
para versoes futuras do Pillow.

## 10. Prioridade de correcao

### P0 - bloqueia claims fortes

1. Integrar validacao semantica de screenshot ao closeout.
2. Fazer reconciliacao pessimista entre runtime, captura, visual report,
   freshness e memory bank.
3. Restaurar execucao de schemas com dependencia Python fixada.
4. Corrigir os 13 hashes lifecycle ou registrar migracao intencional.
5. Exigir bundle fresco e de uma unica sessao para claims de entrega.

### P1 - prova profissional minima

1. Corrigir discovery de arte do cenario MUGEN.
2. Provar musica FM/PSG/XGM2 real com SFX simultaneo.
3. Medir 60 fps por janela completa e reproduzivel.
4. Criar protocolo e evidencia de hardware real/FPGA.
5. Instrumentar ledger de autonomia e intervencoes humanas.
6. Produzir vertical slice completo com inicio, gameplay, boss, resultado e
   retorno ao menu.

### P2 - continuidade e manutencao

1. Eliminar drift entre memory banks, reports e changelogs.
2. Testar retomada em sessao independente.
3. Separar alteracoes do worktree em unidades revisaveis.
4. Promover tecnicas do registry somente com fixture, ROM, BlastEm, budget e
   aprovacao humana.

## 11. Protocolo para assumir um item

O agente que iniciar uma correcao deve:

1. selecionar somente um item `ready_for_assignment` do backlog JSON;
2. confirmar que o blocker ainda existe;
3. ler a skill owner completa;
4. registrar arquivos que serao alterados e preservar mudancas alheias;
5. implementar o menor ataque direto ao blocker;
6. executar todos os acceptance checks do item;
7. atualizar o status e anexar caminhos de evidencia;
8. atualizar memory bank e changelog aplicaveis;
9. nao promover claim acima do menor gate provado.

Expansao de infraestrutura enquanto `P0-001` permanecer aberto deve ser
tratada como desvio, salvo se for dependencia direta da sua correcao.

## 12. Definicao de pronto do programa de correcao

O agente so pode ser reavaliado como candidato de producao quando uma execucao
nova e rastreavel demonstrar:

- jogo curto completo, nao apenas fixture;
- captura semanticamente valida;
- 60 fps medidos;
- budgets VDP/DMA/sprites aprovados;
- arte coerente e aprovada perceptualmente;
- musica FM/PSG e SFX simultaneos;
- BlastEm e hardware real/FPGA;
- inicio, progressao, boss, resultado/creditos e retorno;
- recuperacao de contexto em nova sessao;
- autonomia e intervencoes mensuradas;
- reports, memory bank e changelog sem contradicao.

Regra final: `Se nao foi visto rodando no emulador, nao existe.`
