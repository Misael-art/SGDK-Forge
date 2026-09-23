# Hardware / FPGA Test Protocol

Status: `awaiting_external_execution`

Este protocolo fecha somente o gate de console Mega Drive real ou FPGA. Ele
nao substitui build, BlastEm, gameplay QA, audio QA, budget ou aprovacao
criativa.

## 1. Congelamento da ROM

1. Usar exatamente `out/rom.bin`.
2. Confirmar 262144 bytes e SHA-256
   `40b924f7895386458c7810204464fe47207c40b7f97d0c4585e840ee8d21bbf5`.
3. Confirmar que o mesmo hash existe em
   `out/evidence/blastem/evidence_manifest.json`.
4. Se a ROM mudar, cancelar a sessao e reiniciar o protocolo.

## 2. Identificacao obrigatoria

Registrar em `doc/hardware_session_manifest.json`:

- tipo: `original_console` ou `fpga`;
- fabricante, modelo e revisao;
- padrao `NTSC_60HZ` ou `PAL_50HZ` e regiao J/U/E/JUE;
- metodo de carga: flashcart, cartucho programado ou SD de FPGA;
- modelo do carregador e versao de firmware/core.

Nao preencher valores por suposicao. Informacao ausente mantem o gate
bloqueado.

## 3. Captura continua

Produzir video continuo, sem cortes que ocultem troca de ROM, cobrindo:

1. identificacao visual do dispositivo e metodo de carga;
2. boot da ROM;
3. input visivel e resposta correspondente;
4. audio audivel, sem substituir a trilha na edicao;
5. gameplay da primeira fatia jogavel;
6. qualquer falha de timing, tearing, sprite, input ou audio.

Copiar a captura para
`out/evidence/hardware/<session_id>/hardware_capture.*`, calcular SHA-256 e
declarar `proves=[boot,input,audio,gameplay]` somente quando todos aparecem.

## 4. Decisoes obrigatorias

- `timing_decision`: `pass`, `fail` ou `accepted_with_known_issue`.
- `audio_decision`: `pass`, `fail` ou `accepted_with_known_issue`.
- Todo problema deve aparecer em `observations.issues`; nao omitir problema
  para obter status positivo.
- O operador externo registra identificador nao sensivel, timestamp e
  `truthful=true`. O agente nao pode preencher essa atestacao pelo humano.

## 5. Fechamento automatizado

Executar:

```bash
python3 tools/sgdk_wrapper/validate_hardware_session.py \
  --project-root "SGDK_projects/BLUE_CIRCUIT [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]" \
  --manifest doc/hardware_session_manifest.json \
  --rom out/rom.bin \
  --output out/logs/hardware_test_gate_report.json
```

O gate passa apenas com dispositivo, regiao, carga, ROM, captura, quatro
provas, decisoes e atestacao coerentes. Estado pendente, arquivo vazio, hash
divergente ou ausencia de evidencia BlastEm bloqueiam explicitamente.
