# Playtest de especiais após reset — 2026-09-13

## Identidade

- ROM capturada: `out/rom.bin`
- SHA-256: `532d44539809e40ad3ae8150532f27c91d7f638ee12d6b194cd53897f294a953`
- Sessão: `out/emulator_evidence/visual_ko_20260913T230125Z/`
- Região: NTSC/U; BlastEm reportou aproximadamente 60 fps no título.
- Escopo: teste exploratório de comandos, não aprovação de gameplay nem de orçamento.

## Resultado observado

O capturador executou o comando documentado em `src/fsm.c` (baixo, diagonal/frente,
frente + golpe) para os dois jogadores antes do KO e novamente após o reset do
round. Foram registrados 288 quadros dedicados em `manifest.json`.

- Ryo (P1, id 1): a sequência contém a animação de golpe e a emissão visível do
  projétil `spr_ryo_701`; a criação ocorre em `state==700`, `animFrame==12`,
  conforme o código. A emissão é visível na tira `after_reset_p1_*`.
- Musgo (P2, id 3): o mesmo comando produz a animação de impacto/“slam” de
  `spr_musgo_700`; não se espera uma bola de fogo para este personagem.
- O reset foi alcançado após o primeiro KO: `special_reset_health.png` mostra as
  barras restauradas e a sessão continuou com a tira `after_reset_*`.

Uma repetição posterior com a sonda HPRB integrada (`visual_ko_20260913T230902Z`,
ROM `8cb4a553...`) repetiu o mesmo roteiro de especiais e gerou o SRAM usado no
laudo VDP; a primeira sessão continua sendo a referência visual mais completa.

## Limites

Esta captura prova presença visual do evento em uma sessão real do BlastEm e a
reentrada do comando após reset. Não mede hitbox, dano, latência, SAT, DMA,
scanline pressure ou qualidade perceptiva. A revisão auditiva dos SFX continua
pendente; nenhuma promoção de técnica do registry foi feita.
