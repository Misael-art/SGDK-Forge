# Build and Emulator Gate

## Objetivo

Garantir que a skill feche o ciclo ate ROM + evidencia, sem declarar sucesso so porque o codigo compila.

## 1. Build

Passos minimos:

1. resolver o projeto alvo
2. buildar pelo wrapper canonico
3. verificar `out/rom.bin`
4. registrar hash, tamanho e timestamp
5. ler `validation_report.json`

## 2. Evidencia de emulador

Gate canonico:

- BlastEm obrigatorio
- BizHawk so complementa

Evidencia minima aceita:

- screenshot dedicada da janela do BlastEm
- quando existir no projeto: `save.sram` + `visual_vdp_dump.bin`
- sessao de emulador coerente com a ROM buildada

## 3. O que nao vale

- compilar sem rodar
- rodar ROM antiga sem ancorar hash/timestamp
- screenshot de desktop inteiro como evidencia primaria
- declarar `testado_em_emulador` sem artefato rastreavel

## 4. Saida da skill

A skill deve sempre explicitar:

- status de `buildado`
- status de `testado_em_emulador`
- status de `validado_budget` quando aplicavel
- o que ainda e `parcial`, `placeholder` ou `nao_testado`
