# sfx-prep-fm-psg-pcm

Use when a Mega Drive project needs sound effects, voice stingers, PCM hits, PSG noise, FM patches or audio asset prep for SGDK.

## Purpose

Turn sound design into driver-compatible assets with clear ownership between FM, PSG and PCM/DAC playback.

## Required Inputs

- Desired SFX list.
- Music driver or playback system.
- Channel ownership assumptions.
- Sample rate/format needs for PCM.
- Gameplay moments where SFX stack heavily.

## Required Outputs

- SFX preparation table.
- FM/PSG/PCM allocation.
- Polyphony and channel-stealing risks.
- Build resource handoff notes.

## Hard Rules

- Do not promise unlimited simultaneous SFX.
- Do not use PCM for every effect without DAC and CPU/Z80 budget.
- Do not bury gameplay-critical cues under music without a priority plan.

## Composição FM/PSG/PCM candidata

Origem: itens de Mega Drive Music Creation e SFX Design do lote
`curation_batch_2026_06_16`, evidência `E1_text`, expansão candidata. Reusa as
saídas existentes (SFX preparation table, FM/PSG/PCM allocation, polyphony/
channel-stealing risks, build resource handoff); não cria schema novo e não
promete áudio aprovado/AAA/runtime.

Esta skill **prepara SFX/assets e define intenção sonora**. A arquitetura
musical final segue `xgm2-audio-director`; o driver customizado e os limites de
ciclo Z80/PCM seguem `z80-pcm-custom-driver` (apenas handoff, não editados aqui).

### YM2612 / FM

- Cada patch declara: papel perceptivo (o que comunica no gameplay), envelope
  (ADSR/rate), algoritmo, feedback e fallback quando o canal for roubado pela
  BGM.
- Patch FM sem papel perceptivo declarado é bloqueado.

### PSG / SN76489

- Declarar uso por função: noise, UI, impacto ou textura, com prioridade
  explícita e convivência declarada com FM/BGM (quem cede canal a quem).

### PCM / DAC

- Declarar sample rate, bit depth/formato, duração, tamanho em ROM, prioridade e
  handoff para `z80-pcm-custom-driver` quando necessário.
- PCM não é default para todo efeito; samples longos exigem budget de ROM e de
  ciclo Z80/DAC.

### Blockers

- usar PCM para todo efeito;
- samples longos sem budget de ROM/Z80;
- patch FM sem papel perceptivo;
- áudio chamado de "AAA" sem áudio real auditado.

### Produção real ainda exige

- `audio_architecture_card`, `sample_format_audit`, channel ownership, teste
  auditivo e, quando aplicável, benchmark Z80/PCM. Nenhum claim de runtime/ROM
  sem emulador/ROM evidence.

## Papel musical e sonoro por gameplay

Origem: transcricao anexada em 2026-06-17 sobre composicao de musica para jogos,
evidencia `E1_text`, absorvida apenas como regra candidata.

- Todo som proposto deve declarar papel de jogo antes de declarar timbre:
  alerta, dano, confirmacao, ameaca, recompensa, ambiente, UI, boss cue,
  transicao, silencio intencional ou textura de cena.
- FM, PSG e PCM devem ser alocados para preservar leitura do feedback critico:
  hit, dano, perigo, confirmacao de input e estado de chefe vencem ornamento.
- SFX que coexistem com BGM precisam de handoff para `xgm2-audio-director` com
  `frequency_masking_plan`, `sfx_priority_matrix` e ownership de canal.
- Som excelente nao nasce de adjetivo de clima; nasce de funcao, prioridade,
  loop/cauda, budget, fallback e teste auditivo.
- Se a musica for adaptativa, esta skill prepara os timbres/assets e entrega os
  papeis sonoros; a decisao de estados, stems e transicoes pertence a
  `xgm2-audio-director`.

## Handoff

- Use `z80-audio-boundary-architect` for driver boundaries.
- Use `xgm2-audio-director` for final music architecture.
- Use `z80-pcm-custom-driver` for custom PCM/DAC driver and Z80 cycle budget.
- Use `rom-mastering` for final audio evidence.
