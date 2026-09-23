# Brief — concepcao artistica (leia antes de conceber qualquer pixel)

Direcao: `art-direction-selector` -> `concept_art_direction_brief`
Traducao: `art-translation-to-vdp` (basic + elite)
Conversao: `megadrive-pixel-strict-rules` + `art-conversion-pipeline`

Este brief distingue **consciencia de alvo** (saber para onde o asset vai, sem
amarrar o desenho) de **trava** (restricao que so decide na traducao/conversao).
Confundir as duas e o que produz arte sem alma ou conversao direta.

## Regra-mae

Nunca transforme uma restricao de conversao em limite de concepcao.
Arte que "cabe" por ter nascido amputada e arte sem alma. A alma e desenhada
livre; a conversao decide o que sobrevive. Nao ha sprite final sem a rota de
traducao.

## Por camada

| Camada | Consciencia de alvo (nao trava) | Trava (regra dura) |
|---|---|---|
| Concepcao | silhueta forte, material legivel, atuacao por estado; alvo de hardware como contexto (dimensao final, "cabera em 1 paleta de 16 / 3 tons por material") | nenhuma restricao de cor, tamanho ou pixel embutida no desenho; nunca "pintar ja com 15 cores" ou "ja em 80x112" |
| Traducao | gerar `basic` + `elite`; paleta por material, nao por frequencia | `lineart_blocking_1px` antes do color blocking |
| Conversao | celula de slice com `max_bbox + padding` por estado (evita clipping sem desperdicio) | indice 0 = transparente (magenta no fonte); PNG indexado; max 15 cores + 0; grade 9-bits; grid 8x8 |

## Sequencia obrigatoria

concepcao livre (alma) -> `lineart_blocking_1px` -> model sheet
-> `basic` + `elite` (`art-translation-to-vdp`) -> conversao
-> ROM -> evidencia em emulador.

## Proibido

- gerar direto o PNG do SGDK: converter concept por quantizacao cega sem passar
  por `art-translation-to-vdp` (basic/elite) e `lineart_blocking_1px`;
- reduzir a paleta cedo demais se isso matar gradiente, iluminacao, volume ou
  recorte de alpha;
- tratar "caber em 16 cores" como decisao de arte; e decisao de traducao;
- promover sprite final sem `translation_route_skipped` checado no gate.

## Anti-ambiguidade

- "fundo transparente" so existe no arquivo final: transparencia = indice 0
  (magenta `#FF00FF`) da paleta, um unico slot. Alpha RGBA nao e indice 0.
- "linha de 1px" e a etapa de bloqueio da forma (`lineart_blocking_1px`), antes
  do color blocking; nunca um refino do PNG final.
- "sombreamento simples" e 3 estados por material (luz/base/sombra); o teto
  aplica-se aos niveis de sombra, nao as cores totais.
- "margem" nao e estetica; e `max_bbox + padding` por estado.
