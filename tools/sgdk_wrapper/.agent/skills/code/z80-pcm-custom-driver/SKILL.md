---
name: z80-pcm-custom-driver
description: Use quando a tarefa envolver drivers Z80 customizados, streaming PCM avancado, manipulacao direta de DAC/YM2612, controle de PSG por registrador, mixing de canais PCM, otimizacao de ciclos Z80, bus contention 68K/Z80, banco de ROM via Z80, conversao de formato de sample ou qualquer tecnica de audio que vá alem do wrapper XGM2 padrao do SGDK. Nao use para playback simples via API XGM2 — isso e xgm2-audio-director.
---

# Z80 PCM Custom Driver — Drivers de Audio Customizados

Esta skill existe para o gap critico de audio AAA que separa projetos medianos de superproducoes no Mega Drive: a capacidade de criar, otimizar e integrar drivers de audio Z80 customizados que entregam reproducao cristalina de PCM, vozes digitalizadas limpas e efeitos sonoros complexos — o mesmo nivel de qualidade que jogos como Gauntlet IV, Sonic 3 e Thunder Force IV alcancaram.

## Nao substitui outras skills

- `xgm2-audio-director`
  - continua dono da arquitetura de audio XGM2, ownership de canal, eventos de gameplay e audio_architecture_card
- `sgdk-runtime-coder`
  - continua dono da integracao C, loop principal e callbacks de runtime
- `sgdk-build-wrapper-operator`
  - continua dono do wrapper, layout e politica de build
- `megadrive-vdp-budget-analyst`
  - continua dono do budget DMA que impacta bus contention com Z80

## Ler antes de agir

1. `references/z80_driver_architecture.json`
2. `references/pcm_streaming_patterns.md`
3. `references/hardware_audio_memory_map.json`
4. `references/sample_format_decision_system.md`
5. `sdk/sgdk-2.11/inc/z80_ctrl.h`
6. `sdk/sgdk-2.11/inc/snd/xgm2.h`
7. `sdk/sgdk-2.11/inc/snd/pcm/snd_pcm.h`
8. `sdk/sgdk-2.11/inc/snd/pcm/snd_pcm4.h`
9. `sdk/sgdk-2.11/inc/snd/pcm/snd_dpcm2.h`
10. `sdk/sgdk-2.11/inc/psg.h`
11. `sdk/sgdk-2.11/src/snd/` (drivers Z80 fonte: drv_null.s80, drv_pcm.s80, drv_pcm4.s80, drv_dpcm2.s80, xgm2/drv_xgm2.s80)
12. `doc/05_technical/99_aaa_audio_architecture_guide.md`
13. `tools/sgdk_wrapper/validate_audio.ps1`

## Quando usar

- projetar driver Z80 customizado para playback PCM de alta fidelidade
- implementar streaming PCM por ring buffer a partir de ROM
- manipular DAC do YM2612 diretamente para reproducao de voz digitalizada limpa
- controlar PSG (SN76489) por registrador para envelopes customizados e efeitos
- otimizar ciclos Z80 para maximizar sample rate sem starvation
- resolver bus contention 68K/Z80 durante DMA e acesso a VRAM
- converter formatos de sample (8-bit signed, 4-bit DPCM, ADPCM, u-law)
- dimensionar ROM budget de audio (samples vs. tiles vs. code)
- implementar mixing de multiplos canais PCM no Z80
- carregar driver customizado via `Z80_loadCustomDriver()`
- gerenciar banking de ROM (68K ROM acessado pelo Z80 via bank register 0xA06000)
- implementar sistema de prioridade de audio com preempcao de canais
- criar efeitos especiais: echo, reverb simulado, pitch shifting, volume ramping

## Saidas obrigatorias

- `z80_driver_spec`
  - clock budget por sample, registradores usados, mapa de memoria Z80, protocolo de comando 68K→Z80
- `pcm_streaming_plan`
  - ring buffer layout, taxa de alimentacao, alinhamento de samples, estrategia de bank switching
- `bus_contention_analysis`
  - janelas de DMA, impacto no audio, mitigacao (Z80_setBusProtection, delay DMA)
- `sample_format_audit`
  - formato, sample rate, alinhamento, tamanho, qualidade vs. ROM trade-off
- `cycle_budget_card`
  - ciclos Z80 por sample, overhead de mixing, margem de seguranca, worst-case timing
- `rom_audio_budget`
  - bytes totais de audio, proporcao do ROM total, estrategia de compressao
- `hardware_register_map`
  - YM2612 DAC, PSG ports, Z80 bank register, timer A/B config
- `integration_contract`
  - como o driver customizado se integra com xgm2-audio-director e sgdk-runtime-coder
- `blastem_audio_proof_plan`
  - teste de reproducao limpa, teste de bus contention, teste de loop, teste de prioridade
- `delivery_findings`

## Regras canonicas

### Z80 Driver Core

- todo driver customizado DEVE ser carregado via `Z80_loadCustomDriver(drv, size)` ou operar dentro de driver SGDK existente
- o driver DEVE respeitar o protocolo de comando em `Z80_DRV_COMMAND` (0xA00100) e status em `Z80_DRV_STATUS` (0xA00102)
- Z80 RAM e 8KB (0xA00000-0xA01FFF); driver + buffers + tabelas DEVEM caber nesse espaco
- registrador de banco (0xA06000) DEVE ser configurado antes de acessar ROM do 68K a partir do Z80
- todo acesso YM2612 do Z80 DEVE respeitar timing: data write = 53 ciclos, address write = 6 ciclos, DAC/timer = 8 ciclos

### PCM Streaming

- samples PCM DEVEM ser alinhados a 256 bytes (128 para DPCM) conforme requisito do hardware
- ring buffer DEVE ter double-buffer minimo para evitar crackling durante bank switch
- taxa de alimentacao do 68K DEVE superar taxa de consumo do Z80 em todas as condicoes (incluindo DMA heavy)
- sample rate de referencia: 13.3 Khz (XGM2), 14 Khz (XGM), 16 Khz (PCM4), 22 Khz (DPCM2), ate 32 Khz (single PCM)
- NUNCA assumir que o sample estara disponivel no proximo frame; validar underrun

### Bus Contention

- DMA do VDP PAUSA o Z80 completamente; audio crackling durante DMA e bug, nao feature
- usar `Z80_setBusProtection(true)` durante transfers DMA criticas
- `Z80_setForceDelayDMA(true)` adiciona ~3 scanlines de delay mas protege PSG
- prever worst-case: H-blank DMA + scroll update + sprite DMA no mesmo frame
- bus protection NAO e optional para audio AAA — e mandatoria

### Qualidade AAA

- voz digitalizada limpa = sample rate minimo 13.3 Khz + 8-bit signed + volume adequado
- "abafado" ou "distorcido" indica: sample rate muito baixo, formato errado, clipping, ou bus starvation
- audio AAA NAO aceita crackling, popping, ou gaps audíveis em nenhuma condicao de runtime
- todo sample DEVE ser auditado com headphones antes de integrar
- silence padding no final de samples previne cliques de loop

### Formato e Conversao

- 8-bit signed PCM: qualidade maxima, custo maximo de ROM
- 4-bit DPCM: 50% do espaco, qualidade boa para SFX, nao ideal para voz
- u-law/A-law: compressao logaritmica, otimo para voz com ROM limitada
- tabela de conversao de volume (PCM4: 256x16 bytes em Z80 RAM) e obrigatoria para mixing com envelope
- NUNCA converter sample com dithering inadequado; usar profissional (SoX, Audacity export)

### ROM Budget

- audio NAO deve exceder 40% do ROM total (regra AAA para balance com arte e codigo)
- samples de voz: priorizar compressao (DPCM, u-law) antes de cortar sample rate
- BGM em XGM2 e dramaticamente mais eficiente que samples raw — usar sempre que possivel
- tabela de alocacao DEVE existir antes de qualquer sample ser integrado
- `validate_audio.ps1` DEVE auditar assets declarados em `.res` antes de qualquer integracao ou fix manual

## Senior Competencies

- `z80_assembly_optimization`
  - contagem de ciclos por instrucao, unrolling, lookup tables, register allocation otimizada para audio real-time
- `pcm_ring_buffer_architecture`
  - double/triple buffer, bank switching transparente, underrun detection e recovery
- `dac_direct_manipulation`
  - escrita direta no DAC do YM2612, timing de sample output, mixing no Z80
- `bus_contention_mastery`
  - janelas seguras para DMA, protecao de audio, scheduling cooperativo 68K/Z80
- `sample_format_engineering`
  - conversao entre formatos, trade-offs de qualidade/espaco, pipeline de preparacao de assets
- `psg_register_control`
  - envelopes customizados, noise shaping, tone generation para efeitos especiais
- `rom_budget_management`
  - alocacao de espaco ROM entre audio/arte/codigo, estrategias de compressao
- `driver_protocol_design`
  - protocolo de comando 68K→Z80, status reporting, handshake sem race condition
- `audio_quality_assurance`
  - deteccao de artefatos (crackling, popping, clipping), validacao de loop, prova em BlastEm

## Anti-padroes

- carregar driver customizado sem validar que cabe em 8KB de Z80 RAM
- ignorar bus contention e aceitar crackling como "limitacao do hardware"
- usar sample rate abaixo de 8 Khz para voz — sempre soa abafado
- fazer mixing de PCM no 68K em vez do Z80 — desperdiça ciclos preciosos do processador principal
- acessar YM2612 sem respeitar timing de write — causa registradores corrompidos
- esquecer de alinhar samples a 256 bytes — causa lixo de audio ou crash
- confiar que bank switching e instantaneo — tem latencia e DEVE ser bufferizado
- nao testar com headphones — artefatos sutis escapam em speakers
- aceitar "funciona no emulador" como prova — BlastEm e acurado mas hardware real e o gate final
- implementar echo/reverb sem budget de ciclos — starvation garantido
- usar 100% do Z80 para audio — nao sobra margem para picos de processamento

## Integracao

- combinar com `xgm2-audio-director` para channel ownership quando driver customizado coexiste com XGM2
- combinar com `sgdk-runtime-coder` para callbacks de estado, inicializacao de driver e integracao no main loop
- combinar com `megadrive-vdp-budget-analyst` para budget de DMA que afeta bus contention com Z80
- combinar com `scene-state-architect` para audio state handoff entre cenas e cleanup de driver na transicao
- fornecer `integration_contract` para que xgm2-audio-director saiba quais canais e recursos o driver customizado reserva
