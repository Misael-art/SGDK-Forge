# Host Format Handoff

Documento de retomada segura do workspace `MegaDrive_DEV` depois de formatação do host
ou troca de máquina.

## Ponto de retomada canônico

- repositório remoto: `https://github.com/Misael-art/SGDK-Forge.git`
- branch-base para reidratação: `codex/workspace-salvage-wave1`
- commit âncora validado: `c1703bd26098f07372c41b202be840b0dcbb152e`
- branch complementar de curadoria técnica: `codex/hardware-mastery-roadmap`
- commit complementar de maestria hardware-level: `35dffe2e914476b7827682b45fcee2ce4968c5eb`

## Verdade operacional atual

- o workspace salvo no Git já contém framework, docs, `SGDK_projects`, `SGDK_Engines`,
  `tools`, templates e handoffs de governança
- o laboratório oficial continua sendo `SGDK_projects/BENCHMARK_VISUAL_LAB`
- a trilha de curadoria AAA já está registrada em:
  - `doc/03_art/AAA_SKILL_CANONIZATION_PROTOCOL.md`
  - `doc/03_art/AAA_SKILL_CURATION_STATUS.md`
- a trilha de maestria hardware-level já está registrada em:
  - `doc/05_technical/93_16bit_hardware_mastery_matrix.md`
  - `doc/05_technical/93_16bit_hardware_mastery_registry.json`
  - `doc/05_technical/94_16bit_hardware_mastery_roadmap.md`

## O que ficou fora do Git de propósito

- `assets/`
- `.tmp/`
- caches locais:
  - `.cursor/`
  - `.kilocode/`
  - `.playwright-cli/`
  - `.trae/`
  - `.mypy_cache/`
- clone interno de laboratório:
  - `SGDK_projects/_laboratório/SGDK-Forge/`

Se qualquer uma dessas áreas for importante, ela DEVE ser restaurada a partir de backup
manual fora do Git após o clone.

## Repositórios aninhados e snapshots

Cinco engines permaneceram fora do monorepo como diretórios com `.git` próprio.
Para evitar submódulos acidentais, o conteúdo foi preservado como snapshot em:

- `workspace_salvage/nested_repo_snapshots/`

Snapshots existentes:

- `platformerstudio_editor_snapshot.zip`
- `raycastingengine_3d_snapshot.zip`
- `mega_genius_puzzle_snapshot.zip`
- `msu_example_audio_snapshot.zip`
- `state_machine_rpg_snapshot.zip`

Regra:

- NÃO promover essas roots diretamente para o monorepo sem uma passada específica de
  normalização
- NÃO assumir que o histórico Git interno foi preservado; o snapshot protege o conteúdo,
  não o grafo de commits interno

## Ordem de leitura obrigatória para a próxima IA

1. `AGENTS.md`
2. `doc/06_AI_MEMORY_BANK.md`
3. `doc/03_art/AAA_SKILL_CANONIZATION_PROTOCOL.md`
4. `doc/03_art/AAA_SKILL_CURATION_STATUS.md`
5. `doc/05_technical/92_sgdk_engine_pattern_frontdoor.md`
6. `doc/05_technical/92_sgdk_engine_pattern_registry.json`
7. `doc/05_technical/93_16bit_hardware_mastery_matrix.md`
8. `doc/05_technical/93_16bit_hardware_mastery_registry.json`
9. `doc/05_technical/94_16bit_hardware_mastery_roadmap.md`
10. `SGDK_projects/BENCHMARK_VISUAL_LAB/doc/13-spec-cenas.md`
11. `SGDK_projects/BENCHMARK_VISUAL_LAB/doc/09-checklist-anti-alucinacao.md`

## Sequência de reidratação recomendada

```powershell
git clone https://github.com/Misael-art/SGDK-Forge.git MegaDrive_DEV
cd MegaDrive_DEV
git checkout codex/workspace-salvage-wave1
git rev-parse HEAD
```

O hash retornado DEVE ser:

```text
c1703bd26098f07372c41b202be840b0dcbb152e
```

Depois disso:

1. restaurar `assets/` a partir de backup externo, se necessário
2. restaurar `.tmp/` apenas se houver evidência ou capturas úteis a preservar
3. executar leitura da ordem obrigatória acima
4. criar branch nova a partir de `codex/workspace-salvage-wave1`
5. só então continuar curadoria, build ou validação

## Regras de segurança para a próxima IA

- DIZER `[Contexto MD Carregado]` antes de propor ação
- NÃO usar `main` como base de continuação
- NÃO tratar documento como prova de hardware
- NÃO declarar pronto sem BlastEm
- NÃO canonizar técnica nova sem ROM + evidência + aprovação humana
- NÃO mexer em `assets/` como se estivessem versionados
- NÃO mexer nos 5 engines aninhados sem explicitar a estratégia
- USAR `BENCHMARK_VISUAL_LAB` como laboratório oficial de prova

## Branches importantes

- `codex/workspace-salvage-wave1`
  - baseline de reidratação segura
- `codex/hardware-mastery-roadmap`
  - curadoria de competências hardware-level
- `codex/aaa-diagnosis-reconciliation`
  - reconciliação do diagnóstico AAA com a verdade atual do repo

## Último estado conhecido relevante

- `BENCHMARK_VISUAL_LAB` recebeu edições locais preservadas em:
  - `res/gfx/sunny_land_bg_a.png`
  - `res/gfx/sunny_land_bg_b.png`
  - `src/scenes/scene_sunny_land.c`
- essas mudanças já estão incluídas na branch de salvamento

## Checklist de retomada

- [ ] clone concluído
- [ ] branch `codex/workspace-salvage-wave1` checkoutada
- [ ] hash confere com `c1703bd26098f07372c41b202be840b0dcbb152e`
- [ ] backup externo de `assets/` restaurado ou conscientemente descartado
- [ ] leitura obrigatória concluída
- [ ] nova branch de trabalho criada
- [ ] nenhuma canonização iniciada sem gate humano

## Critério de sucesso deste handoff

Outra IA deve conseguir:

- reconstruir o contexto sem depender da máquina antiga
- saber exatamente qual branch é a base correta
- diferenciar o que está protegido no Git do que ficou fora
- continuar a curadoria sem promover falso positivo de prontidão
