---
name: emulator-vdp-evidence-curator
description: Use quando uma entrega SGDK/Mega Drive precisar fechar evidencia de ROM, BlastEm, screenshot, SRAM, VDP dump, captura visual ou alegacoes de runtime vinculadas ao hash exato do binario.
---

# Emulator VDP Evidence Curator

Aplica a regra: se nao foi visto rodando no emulador, nao existe. A skill fecha
a identidade e a integridade do pacote de evidencia; nao aprova qualidade por
conta propria.

## Contrato Operacional

### Entrada minima

- ROM buildada e seu caminho
- alvo de emulador, com BlastEm obrigatorio no gate de entrega
- cena/estado esperado
- claims visuais, VDP ou runtime a fechar
- contratos de SRAM ou VDP dump aplicaveis

### Saida minima

- checklist de evidencia
- requisitos de screenshot, SRAM e dump
- mapeamento claim -> evidencia
- `out/logs/evidence_closeout_report.json`
- blockers que impedem `testado_em_emulador`

### Passa quando

- o hash capturado coincide com a ROM atual
- todos os artefatos declarados existem e possuem hash no selo
- a evidencia nao esta stale
- o emulador e os artefatos satisfazem o claim declarado

### Handoff para proxima etapa

- entregar o selo para `rom-mastering`, `megadrive-vdp-budget-analyst` e
  `aaa-pipeline-guardian` conforme o claim

## Regras

- Nao declarar `pronto`, `AAA`, `validado_budget` ou
  `testado_em_emulador` apenas por build.
- BizHawk nao substitui o gate BlastEm.
- Relatorio textual nao substitui screenshot, SRAM ou VDP dump exigido.

## Freeze, Capture, Seal

- A ordem canonica e: build final -> hash da ROM -> captura -> relatorios ->
  `finalize_emulator_evidence.ps1`.
- A captura pertence a um unico hash. Qualquer rebuild posterior rejeita o selo
  com `rom_identity_changed_after_capture`.
- Relatorios podem ser gerados depois da captura desde que nao alterem a ROM.
- `out/logs/evidence_closeout_report.json` deve registrar hash capturado, hash
  atual, paths e hashes dos artefatos e `seal_status`.
- `seal_status=sealed` prova apenas que o pacote pertence a ROM atual; nao prova
  sozinho gameplay, qualidade visual, audio, performance ou budget.
- Recapturar e necessario somente quando a ROM muda de proposito ou quando os
  artefatos exigidos pelo claim estavam ausentes/defeituosos.
