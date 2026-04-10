# Workflow: Build Validate

Use este fluxo para build, rebuild e validacao operacional.

## Entrada

- raiz do projeto (pasta que contem `.mddev/project.json` quando existir)

## Passos

1. Resolver contexto do projeto (manifesto + layout + `build_policy`).
2. Auditar saude do bootstrap local da `.agent`:
   - se ausente, bootstrap automatico e permitido
   - se presente sem `framework_manifest.json`, marcar como `bootstrap_degradado`
   - se houver drift entre copia local e canônica, registrar explicitamente antes de confiar no contexto local
3. Se `build_policy=disabled`, declarar como referencia/pacote pedagogico e encerrar o fluxo.
4. Rodar build pelo wrapper canonico:
   - preferir `rebuild.bat` quando o objetivo for evidenciar reprodutibilidade
   - usar `build.bat` apenas quando o objetivo for iteracao rapida
5. Verificar artefato:
   - `out/rom.bin` existe
   - registrar tamanho, hash e timestamp do arquivo (para rastreabilidade)
   - tratar essa identidade da ROM como ancora de toda evidencia posterior
6. Verificar logs (quando existirem):
   - `out/logs/build_output.log`
   - `out/logs/build_debug.log`
7. Verificar validacao estruturada:
   - `out/logs/validation_report.json` existe
   - `summary.errors == 0` (qualquer erro bloqueia)
   - warnings devem ser listados e justificados quando aceitos
8. Preparar a sessao de emulador:
   - usar **BlastEm** como gate obrigatorio
   - descobrir o mapeamento de input efetivo a partir da configuracao do emulador quando necessario; nunca presumir teclas sem prova
   - registrar inicio da sessao em `out/logs/emulator_session.json`
   - garantir que o processo e a janela do emulador alvo sejam identificados de forma nao ambigua
9. Capturar evidencia de runtime:
   - produzir captura dedicada da janela do emulador ou screenshot interno do proprio emulador
   - evitar captura da area de trabalho inteira como evidencia primaria
   - registrar arquivos de evidencia no `emulator_session.json`
   - se houver observacao manual de gameplay, anotar claramente o que foi visto: boot, resposta a input, estabilidade, audio
10. Quando `SGDK_RUNTIME_CAPTURE=1` estiver ativo:
   - `out/logs/runtime_metrics.json` deve existir
   - conferir se `samples_recorded` atingiu a janela requerida
   - conferir se o report foi absorvido em `validation_report.json`
   - tratar `validation_report.json` como fonte primaria do status panel a partir desse momento
11. Consolidar artefatos em ordem canonica:
   - primeiro finalizar a sessao e atualizar `emulator_session.json`
   - depois absorver a evidencia em `validation_report.json`
   - por ultimo atualizar memoria operacional e handoff
   - se um build novo ocorrer depois disso, marcar a evidencia anterior como `stale` e rebaixar os eixos dependentes
12. Separar estados:
   - `buildado` = `out/rom.bin` existe
   - `testado_em_emulador` so pode ser marcado quando a ROM foi executada e a evidencia foi registrada; BlastEm e obrigatorio para gate de entrega, BizHawk apenas complementa telemetria
   - `validado_budget` so pode ser marcado quando houver auditoria explicita de VRAM/DMA/sprites por cena ou report equivalente
   - `boot_emulador=ok` exige sessao com `launch_status` pelo menos `captured`
   - `runtime_capture_present=true` exige evidencia realmente listada em `source_artifacts`
13. Checar estabilidade de frame quando houver instrumentacao:
   - `frame_stability` deve ser `estavel`
   - jitter, pior frame e picos devem ser registrados
   - para declaracao AAA, custo por frame nao pode ficar apenas em observacao subjetiva
14. Checar pressao de sprites e scanline quando houver report:
   - `sprite_pressure` nao pode estar em `alto` sem aprovacao explicita
   - overflow potencial por scanline deve bloquear validacao de cena
15. Checar carga de FX:
   - `fx_load` deve registrar se a cena esta `leve`, `moderado` ou `pesado`
   - cenas `pesado` exigem justificativa de Signature Moment e prova de 60fps estavel
16. Checar qualidade perceptiva:
   - `perceptual_quality` deve ser explicitamente declarado
   - responder se o movimento parece fluido, se o FX parece natural e se ha peso/impacto perceptivel
   - se a cena for tecnicamente correta mas perceptualmente fraca, a iteracao nao pode ser chamada de AAA
17. Se nao houver telemetria forte:
   - preencher `frame_stability`, `sprite_pressure`, `fx_load` e `perceptual_quality` com linguagem observacional honesta
   - diferenciar claramente `observado`, `estimado` e `nao_medido`
18. Antes de encerrar:
   - verificar se `validation_report.json` continua coerente com a ultima ROM gerada
   - verificar se `source_artifacts` referencia as capturas reais usadas no gate
   - verificar se a memoria operacional nao contradiz o report final

## Saida minima esperada

- caminho da ROM gerada + hash
- timestamp e tamanho da ROM validada
- resumo do `validation_report.json` (errors/warnings/checked/recovered)
- resumo do `emulator_session.json` com `launch_status` final e arquivos de evidencia
- quando houver: resumo de `runtime_metrics.json` (samples, pico CPU, pico scanline, pico de FX)
- status final por eixo: `buildado`, `testado_em_emulador`, `validado_budget`
- quando houver: `frame_stability`, `sprite_pressure`, `fx_load`, `perceptual_quality`
