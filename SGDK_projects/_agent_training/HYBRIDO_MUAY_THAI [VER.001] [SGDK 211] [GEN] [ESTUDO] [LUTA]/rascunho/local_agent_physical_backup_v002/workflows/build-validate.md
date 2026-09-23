# Workflow: Build Validate

Use este fluxo para build, rebuild e validacao operacional.

## Entrada

- raiz do projeto
- contexto resolvido pelo wrapper
- `.agent` local nao degradada ou explicitamente tratada como invalida

## Passos

1. Materializar contratos ausentes com `adopt_project_methodology.ps1`, sem sobrescrever arquivos locais.
2. Classificar e validar `doc/project_methodology_manifest.json` e `doc/project_hygiene_manifest.json`; nome placeholder, nome ativo fora de `portable_descriptive_v1`, claim `review_required`, skill/validacao ausente, artefato orfao, evidencia externa sem copia local ou caminho absoluto para outro workspace em material ativo bloqueia closeout.
3. Resolver contexto do projeto e manifesto.
4. Auditar bootstrap local da `.agent`.
   - se faltar manifesto, tentar heal seguro
   - se faltarem `pipelines`, skills de arte ou workflows criticos, tratar como `agent_context_degraded`
5. Rodar `preflight_host.ps1` quando a sessao ainda nao foi saneada.
6. Rodar build pelo wrapper canonico.
7. Registrar identidade da ROM:
   - caminho
   - tamanho
   - hash
   - timestamp
8. Marcar evidencia antiga como `stale` quando a ROM mudar.
9. Atualizar `doc/changelog/` via script canonico:
   - snapshot de assets alterados
   - snapshot da ROM quando o hash mudar
   - atualizacao de `build_meta.json`
   - atualizacao do bloco derivado em `doc/10-memory-bank.md`
   - quando apenas relatorios/gates mudarem, usar `update_project_changelog.ps1 -StatusOnly` para sincronizar o bloco derivado sem criar snapshots ou entradas artificiais no changelog
10. Quando o projeto declarar audio em `.res`:
   - executar `validate_audio.ps1`
   - gravar `out/logs/audio_validation_report.json`
   - tratar `audio_validation_missing`, `audio_validation_stale` e `audio_validation_failed` como sinais canonicos da trilha de audio
11. Executar `validate_resources.ps1 -CloseoutGate` no fechamento de QA; durante iteracao, o wrapper pode usar o modo normal apenas para manter o relatorio coerente sem bloquear o build.
12. Executar `freshness_audit.ps1` quando houver qualquer evidencia previa ou nova ROM, para detectar drift entre contratos, assets, regressao, runtime e docs.
13. Para fechar cena, preferir `scene_closeout_gate.ps1` como orquestrador conservador:
   - build/rebuild
   - `scene_contract_compiler.ps1`
   - `res_graph_audit.ps1`
   - `validate_resources.ps1`
   - `run_runtime_capture.ps1` quando houver `TargetScene`
   - `run_scene_regression.ps1`
   - `freshness_audit.ps1`
14. Para campanha de efeitos, showcase por eixos ou pacote multi-ROM, executar `audit_effect_campaign_semantics.ps1` antes do resumo final. Esse gate reprova painel procedural/debug, fallback generico em massa, ausencia de lib_cases e `ready_for_aaa` sem reports frescos.
15. Conferir blockers de fechamento:
   - `agent_context_degraded`
   - `audio_validation_missing`
   - `audio_validation_stale`
   - `audio_validation_failed`
   - `budget_doc_mismatch`
   - `visual_delivery_gate_missing`
   - `visual_gate_blocked`
   - `emulator_evidence_stale`
   - `scene_closeout_failed`
   - `freshness_audit_stale`
   - `freshness_audit_missing`
   - `scene_closeout_gate_missing`
   - `changelog_missing`
   - `project_naming_invalid`
   - `project_methodology_manifest_missing`
   - `project_methodology_manifest_invalid`
   - `project_hygiene_manifest_missing`
   - `project_hygiene_manifest_invalid`
   - `project_documentation_sync_stale`
   - `perceptual_motion_unvalidated`
   - `road_physics_contract_invalid`
   - `modular_boss_runtime_invalid`
16. Rodar BlastEm pelo contrato canonico de automacao:
   - `run_runtime_capture.ps1` e `run_visual_capture.ps1` devem importar `lib/blastem_automation.psm1`
   - navegacao deve privilegiar `press_until_ready:*` com heartbeat `READY` em SRAM `0x100`
   - `Close-BlastEmGracefully` deve seguir `ESC -> WM_CLOSE -> Alt+F4 -> kill`
   - logs operacionais devem ir para JSONL em `out/logs/*_blastem.log`
   - evidence roots devem ficar dentro de `out/blastem_env_*`, sem fallback para `LocalAppData\blastem\rom`
17. Consolidar:
   - `emulator_session.json`
   - `audio_validation_report.json`
   - `freshness_audit_report.json`
   - `scene_closeout_gate_report.json`
   - `validation_report.json`
   - `doc/changelog/changelog.md`
   - `doc/10-memory-bank.md`
18. Executar `audit_project_learning.ps1 -Mode Capture` depois das evidencias e registros locais:
   - atualizar somente `doc/agent_learning/learning_ledger.json`
   - gerar `out/logs/project_learning_report.json`
   - confirmar `canonical_promotion_performed=false`
   - tratar ausencia em legado como warning, nunca como permissao para inventar licao
19. Se houver novo build depois disso, rebaixar a evidencia anterior para `stale`.

## Semantica do Gate Final

- `visual_lab_aprovado` pode fechar o laboratorio visual, mas nao autoriza entrega AAA sozinho.
- `gameplay_rom_aprovada` exige gameplay real, `performance`, `audio` e `hardware_real` fora de `nao_testado`.
- `ready_for_aaa` so pode ser verdadeiro quando a ROM jogavel estiver aprovada e o budget/runtime estiverem validados.

## Saida minima esperada

- `out/rom.bin` com identidade registrada
- `out/logs/audio_validation_report.json` quando houver audio declarado em `.res`
- `out/logs/validation_report.json`
- `out/logs/project_methodology_report.json`
- `out/logs/freshness_audit_report.json`
- `out/logs/scene_closeout_gate_report.json` no fechamento de cena
- `out/logs/emulator_session.json`
- `out/logs/project_learning_report.json` quando houver contexto local de aprendizado
- `out/logs/*_blastem.log` com trilha JSONL da automacao
- `doc/changelog/changelog.md`
- `doc/10-memory-bank.md` coerente com a ROM vigente

## Regras de Fechamento

- `summary.errors == 0` continua obrigatorio
- nenhum blocker de fechamento pode permanecer ativo
- identidade do projeto, metodologia, skills e validacoes declaradas precisam estar coerentes
- higiene do projeto precisa estar limpa; rascunhos ficam em `rascunho/` e evidencias usadas ficam dentro do projeto
- `blocking_statuses` precisa estar vazio para `ready_for_aaa=true`
- BlastEm e obrigatorio para `testado_em_emulador`
- `doc/changelog` nao e opcional
- memoria operacional nao pode contradizer a ultima ROM validada
- captura de aprendizado nunca aplica patch canonico nem promove `MESTRE_*`
