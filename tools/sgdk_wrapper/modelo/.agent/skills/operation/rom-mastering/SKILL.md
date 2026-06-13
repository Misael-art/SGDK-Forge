---
name: rom-mastering
description: Use quando uma ROM SGDK/Mega Drive for candidata a entrega, release, cartucho, teste fisico, QA final ou compatibilidade regional. Esta skill verifica header, regiao, SRAM, checksum, tamanho/alinhamento, metadados e evidencia de emulador, sem substituir build, runtime, budget ou BlastEm.
---

# ROM Mastering

Esta skill fecha a camada final da ROM. Ela nao torna o jogo bom; ela prova que o binario entregue esta identificavel, alinhado e coerente com a plataforma alvo.

## Contrato Operacional

### Entrada minima

- `out/rom.bin`
- `build_output.log`
- `validation_report.json`
- `emulator_session.json` quando existir
- spec de regiao e SRAM do projeto
- `doc/10-memory-bank.md`

### Saida minima

- `rom_mastering_report`
- hash SHA-256 da ROM
- tamanho e alinhamento
- estado de checksum
- leitura de header, region flags, SRAM range e product id
- decisao: `mastering_ok`, `mastering_needs_fix` ou `mastering_blocked`

### Passa quando

- ROM existe e corresponde ao build validado
- checksum/header/tamanho estao coerentes com a intencao do projeto
- region flags nao contradizem `region_timing_contract`
- SRAM, quando usada, tem range, magic/version/checksum e evidencia de leitura/escrita
- o report referencia a mesma ROM que a evidencia de BlastEm

### Handoff para proxima etapa

- entregar `rom_mastering_report` para `validate_resources.ps1`, `scene_closeout_gate.ps1` e memoria operacional

## Regras

- Nao declarar release, final, pronto ou AAA sem `rom_mastering_report`.
- Mastering nao substitui gameplay, audio, visual gate, budget ou emulador.
- Se o projeto nao usa SRAM, declarar `sram_policy=none` e provar que nao ha dependencia escondida.
- Se a ROM for rebuildada, o mastering anterior fica stale.
- Header/region/checksum corrigidos por ferramenta precisam gerar novo hash e nova evidencia.

## Anti-padroes

- copiar hash antigo apos rebuild
- aceitar `out/rom.bin` sem saber se e a ROM capturada
- assumir regiao mundial sem testar timing PAL/NTSC
- tratar save SRAM de debug como save system de produto
