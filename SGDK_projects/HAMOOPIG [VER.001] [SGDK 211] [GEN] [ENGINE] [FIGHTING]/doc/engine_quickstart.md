# HAMOOPIG Fighting Engine — quickstart

Este documento descreve o caminho reproduzível para compilar e observar a
engine. Ele não promove a arte a final: a ROM continua com teto `prototype`
enquanto cenário, áudio e budget sensorial não tiverem revisão independente.

## Pré-requisitos

- SGDK 2.11 identificado pelo wrapper local;
- Wine/bridge do workspace;
- BlastEm instalado no Flatpak do usuário;
- `xdotool`/canal de input disponível para capturas interativas.

## Build

Na raiz do projeto:

```sh
bash /mnt/sdcard/Projects/Sgdk\ Forge/tools/sgdk_wrapper/build_sgdk_wine_bridge.sh \
  --project-root "$PWD"
sha256sum out/rom.bin
```

O log fica em `out/logs/`; a ROM é `out/rom.bin`. Sempre registre o SHA junto
com a captura do emulador. Não copie uma captura antiga para provar um build
novo.

## Rotas de evidência

```sh
python3 tests/capture_visual_ko.py --transition --stage2 --specials
python3 tests/capture_visual_ko.py --pal --stage2 --h240 --probe-short
python3 tests/analyze_hprb_probe.py --self-check
```

As capturas são gravadas em `out/emulator_evidence/<session_id>/`. A faixa de
vida e a faixa de especial são medidas separadamente pelo harness; uma métrica
de amarelo não é, sozinha, prova de KO.

Para exercitar a matriz P10 sem alterar a ROM, o harness injeta um mapa P2
temporário sobre o `default.cfg` empacotado do BlastEm e confere o manifesto de
cada sessão:

```sh
python3 tests/run_p10_matrix.py --selection-only --limit=1
python3 tests/run_p10_matrix.py --probe-wait=1
```

`--selection-only` prova apenas a seleção de lutadores/cenário. O modo padrão
usa `probe-short`, registra telemetria de runtime e mantém gameplay, imagem,
áudio e sensação como pendências explícitas. Cada caso só é atualizado após
conferir SHA da ROM, P1, P2, região e cenário no `manifest.json`.

## Suíte host

```sh
python3 tests/test_dma_backpressure_contract.py
python3 tests/test_stage_palette.py
```

Para a suíte completa, execute todos os `tests/test_*.py` pelo wrapper ou pelo
runner local, preservando o relatório de cada teste. Testes host validam
contratos; não substituem a execução da ROM.

## Diagnóstico rápido

- tela azul/fatal de sprite: confira handles liberados em `FUNCAO_INICIALIZACAO`
  e a última mensagem do `emulator.log`;
- cenário preto ou costurado: confirme `gBG_Choice`, `StageDefinition`,
  dimensão do PNG e hash do `res/gfx/*.json`;
- vida aparentemente cheia no KO: verifique apenas a faixa superior do HUD;
  a barra especial ocupa a linha abaixo;
- input duplicado no menu: use bordas `KEY_PRESSED` e confira o lock de página;
- PAL/H240: confirme região e `screen_height` no HPRB antes de interpretar
  qualquer budget.

## Limites conhecidos

O executor atual consegue medir sinal de áudio, mas não ouvir mix/timbre; e
captura quadros isolados, não certifica suavidade temporal de vídeo. Esses
eixos devem permanecer `pending_audio_review`/`pending_visual_review` até o
parecer correspondente.
