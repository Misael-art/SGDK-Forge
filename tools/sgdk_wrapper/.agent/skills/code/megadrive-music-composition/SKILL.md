---
name: megadrive-music-composition
description: Compor e arranjar musica autoral para Mega Drive, de motivo e partitura a VGM/XGM2, com loop, FM/PSG/PCM e espaco para SFX. Use para criar BGM nativa; ownership e integracao runtime pertencem a xgm2-audio-director.
---

# Composicao musical Mega Drive

## Direcao e arranjo

Leia `doc/17-audio-design.md`, GDD e spec da cena. Defina funcao, andamento,
metro, centro tonal, motivo, estrutura A/B, ponto de loop e momentos que
precisam abrir espaco para cues. Use `composition_scope_contract` existente.
Os nomes de escopo indicam complexidade pretendida, nao tempo garantido.

Escreva um motivo reconhecivel, uma resposta e uma variacao ritmica antes
de orquestrar. Varie registro, densidade e articulacao entre secoes;
evite preencher continuamente o registro do alerta, impacto ou voz.
Especifique envelopes e patches FM, em vez de pedir apenas "som retro".
YM2612/PSG/PCM e o alvo: preset NES/SNES e referencia estetica, nao contrato
de instrumento. DAC compartilha o sexto canal FM; confirme driver e uso
nos headers locais `inc/snd/xgm2.h` e `bin/xgm2.txt`.

## Rota executavel neste workspace

Para rascunho PSG autoral sem tracker, use o compilador central:

```bash
python3 tools/audio-tools/psg_score.py --self-check
python3 tools/audio-tools/psg_score.py --score <projeto>/data/source_audio/score.json --out <projeto>/out/audio/sketch.vgm
python3 tools/audio-tools/vgm_to_xgm2.py --input <projeto>/out/audio/sketch.vgm --out <projeto>/out/audio/sketch.xgm
```

A partitura JSON usa `schema_version: "1.0.0"`, `region: "ntsc"|"pal"`,
`frames`, `loop_frame` e `notes`. Cada nota declara `channel` (0..2),
`frame`, `duration`, `midi` e `attenuation` (0 forte..14 fraco).
Timing e em VBlank da regiao; escreva a partitura regional explicitamente.
Notas fora da faixa PSG, sobrepostas no mesmo canal ou atravessando a
entrada do loop sao rejeitadas. A entrada reinicializa volumes.
Esse compilador oferece tres vozes de tom, sem FM, ruido ou PCM; serve
para composicao e teste, nao para prometer arranjo completo.

Para arranjo FM/PSG/DAC completo, preserve projeto de tracker autoral e
exporte VGM. Sonde o executavel e a exportacao real do tracker disponivel
antes de prometer automacao. Nao instale MusicGen/HeartMuLa como dependencia
do build. Audio gerado por IA pode orientar timbre/forma; WAV/MP3 nao vira
sequencia de registradores por renomeacao. Reconstrua notas e patches ou
orcamente explicitamente PCM, tamanho e perda de canais.

O VGM e a entrada do recurso `XGM2` no ResComp; nao ofereca o binario
convertido ao ResComp como se fosse VGM. Confira `bin/rescomp.txt`.
Preserve fonte, hashes, identidade autoral e licenca em cada exportacao.

## Escuta e integracao

Entregue partitura/tracker, patches, VGM, conversao auditada, mapa de eventos
e contrato ao `xgm2-audio-director`. Compare duas voltas de loop, ataque e
release na emenda, fadiga, masking, pause/resume e troca de cena.
Capture audio efetivo no BlastEm com a mesma ROM da cena pesada e seus
inputs observados. Um arquivo valido ou silencio sem dropout nao prova BGM.
Proficiencia final depende da escuta contextual, qualidade do arranjo e
integracao medida; self-check prova somente o compilador.
