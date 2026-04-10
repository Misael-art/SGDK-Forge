# Pequeno Principe Cronicas das Estrelas

Projeto autoral para Mega Drive / Genesis em **SGDK 2.11**.

O projeto tem um **vertical slice jogavel (baseline)** com 4 micro-planetas:

- `B-612`: curvatura, paleta dinamica e halo em hilight
- `Planeta do Rei`: parallax multicamada e column scroll
- `Planeta do Lampiao`: H-Int, split de paleta e calor
- `Deserto das Estrelas`: vento, miragem e travel entre mundos

As telas de `titulo`, `historia`, `travel`, `pause`, `codex` e `creditos` tambem ja fazem parte da direcao do projeto: sao compostas com tile art procedural, scroll leve de fundo e uma leitura pensada para jogo e estudo ao mesmo tempo.

O objetivo do projeto e ser ao mesmo tempo:

- um jogo autoral com identidade propria
- um laboratorio pedagogico de tecnicas do Mega Drive
- uma base solida para futuros assets finais via `rescomp`

Neste baseline, os 4 micro-planetas ganharam encontros curtos em `window plane`, para que narrativa e efeito convivam sem sofrer com o scroll do cenario.

Os 4 marcos centrais agora tambem usam assets reais via `rescomp` e cada encontro recebeu voz curta e micro-SFX em `WAV/XGM2`, mantendo o slice dentro de um budget visual enxuto.

## Controles

- `LEFT / RIGHT`: caminhar
- `A`: interagir e planar curto no ar
- `START`: pausar
- `C`: viajar quando o objetivo do planeta estiver resolvido

## Build

```bat
build.bat
```

O projeto usa somente os wrappers canonicos do workspace.

## Status (producao)

- **Baseline jogavel**: 4 micro-planetas (B-612, Rei, Lampiao, Deserto).
- **Arquitetura expandida**: enums e fluxo preparados para 12 planetas + 11 viagens (parte ainda placeholder).
- **Assets**: hibrido (procedural + `rescomp` para marcos e audio de encontros).

Para o estado canonico e proximo passo, use `doc/10-memory-bank.md` (autoridade maxima).

## Estrutura

- `src/core/`: bootstrap e loop principal
- `src/states/`: state machine (boot/title/story/planet/travel/pause/codex/credits)
- `src/game/`: planetas, progressao e player
- `src/render/`: tiles gerados em codigo, scroll e H-Int
- `inc/project.h`: contratos centrais do projeto
- `doc/`: arquitetura, pipeline e guias pedagogicos

## Fase 1

Os placeholders atuais sao **gerados por codigo** para destravar engenharia e performance sem depender de arte final. Isso inclui tanto os micro-planetas quanto a camada de apresentacao do slice.

A entrada de assets finais via `resources.res` ja esta preparada e documentada em `doc/04-recursos-e-pipeline.md`.

Lotes externos de arte agora passam primeiro por `tmp/imagegen/inbox/pequeno_principe_v2/`, depois por `tools/image-tools/validate_pequeno_principe_asset_batch.ps1` e so entao podem ser promovidos para `res/`.
