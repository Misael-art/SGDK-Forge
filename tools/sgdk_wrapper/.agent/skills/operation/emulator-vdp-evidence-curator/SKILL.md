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
- `out/logs/blastem_capture_route_report.json` fresco para o host atual

### Saida minima

- checklist de evidencia
- requisitos de screenshot, SRAM e dump
- mapeamento claim -> evidencia
- `out/logs/evidence_closeout_report.json`
- blockers que impedem `testado_em_emulador`

### Passa quando

- o hash capturado coincide com a ROM atual
- a rota de captura pertence ao host declarado: Linux usa Flatpak/XWayland;
  Windows usa PowerShell/Win32
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
- `System.Windows.Forms` ausente em Linux nao e blocker de emulador; e selecao
  indevida do backend Windows e deve ser corrigida antes de atribuir causa ao host.

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

## Semantica do probe e cobertura real

Para telemetria ou matriz automatizada, ler as secoes 6–7 do caso HAMOOPIG. Declarar unidade, schema, saturacao, regioes e configuracao observada. Bytes enfileirados, contador de eventos e 36 probes curtos nao provam tempo de CPU, game feel nem partidas completas.

[Aprendizado e fixtures HAMOOPIG](../../../references/hamoopig_engine_learning_2026_09_18.md).

## Revisao audiovisual hash-bound

Quando a entrega alegar observacao audiovisual, consumir o pipeline existente
`audiovisual_review.py` em V0-V5. Manter separados `artifact_identity`,
`media_temporal_integrity`, `av_sync`, `game_cadence`, `event_observed`,
`visual_legibility`, `visual_quality`, `motion_quality`, `audio_quality` e
`coverage`. `event_observed` ou screenshot nao aprovam qualidade, movimento ou
som. Registrar reviewer, metodo, ferramentas e intervalos realmente vistos;
sequencia de imagens e metadado sao evidencia limitada, nao playback/audicao.
