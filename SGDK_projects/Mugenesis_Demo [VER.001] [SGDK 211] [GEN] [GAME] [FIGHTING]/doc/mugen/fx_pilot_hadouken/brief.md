# Piloto de FX — Hadouken (Ken), para o agente grafico

Gerado por `python3 -m mugen2sgdk_forge fx-pilot <ken_masters_adv.zip> --project . --name hadouken --actions 750,751`.
- Pixels (terceiros, fora do Git): `rascunho/processado/fx_pilot_hadouken/`. O `source_*.png` e RGBA: so o indice 0 e transparente, e o preto visivel continua opaco.
- Contratos versionados: esta pasta.
- Hashes de tudo: `source_hashes.json`.

## Escopo
- **So** a familia do hadouken normal (Statedef 850): acao **750** (voo) e **751** (dissipacao no acerto), sprites `750,0`..`750,4`.
- Fora: corpo, escala, hitbox (Clsn), outras familias, gameplay.
- **Aceite do piloto nao e aceite do Ken.** O `palette-check` global continua reprovando enquanto as outras familias estiverem na linha antiga. Nao se usa `--waiver` para aprovar.

## Contrato de quadros (`frame_contract.json`)
- 8 elementos AIR com tempo, deslocamento, eixo e Clsn.
- A acao 750 alterna `750,0` / `750,1` com **quadros vazios (-1)**: o piscar faz parte do desenho e deve ser mantido.
- Manter trajetoria, ponto de origem (eixo) e limites de quadro.

## Paleta alvo (`palette_roles.json`) — linha do lutador, orcamento 8 + 6 + 1
| slots | papel |
|---|---|
| 1, 2, 3, 4, 5, 8, 11, 15 | estaveis: iguais nas 12 variantes; **podem** ser usados no efeito |
| 7, 9, 10, 12, 13, 14 | roupa: mudam por variante; **proibidos** no efeito |
| **6** | **unico slot de efeito** (liberado pela fusao sem perda 6 -> 1, aplicada e provada no conversor) |
| 0 | transparente |

- Nao existem outros slots livres.
- As estaveis sao sobretudo tons quentes de pele/cabelo, escuros, preto e branco. O azul do hadouken tera de vir do slot 6 somado aos claros/escuros estaveis. **Isso e desafio de direcao de arte.**
- **O slot 6 e um so para TODAS as familias do Ken.** Antes de fixar a cor dele, olhar `fx_catalog.json` -> `source_by_family` (cores da FONTE original das 15 familias, com o remapeamento atual e a perda em dE). O `current_by_family` e so diagnostico do estado degradado. Nao escolher uma cor que so sirva ao hadouken sem registrar o conflito.

## Orcamento (`budget_report.json`)
<!-- budget:begin (gerado por fx-pilot; nao editar) -->
**Limite de projeto do candidato:** ate **26 tiles** 8x8 e **2 sprites de hardware** por quadro (limite de PROJETO do piloto = pior quadro atual da familia (nao piora o que existe)).

| sprite | tiles 8x8 (estimativa) | sprites HW (estimativa) |
|---|---|---|
| 750,0 | 22 | 2 |
| 750,1 | 26 | 2 |
| 750,2 | 14 | 1 |
| 750,3 | 8 | 1 |
| 750,4 | 14 | 1 |

Estimativa da fonte, nao medicao: tiles 8x8 nao vazios da celula; hw_sprites = blocos 32x32 nao vazios (_hw_estimate); dma = tiles x 32 B. ESTIMATIVA: nao e a decomposicao final do rescomp.
Medicao compilada: a medir (maxNumTile/numSprite do SpriteDefinition na ROM (symbol.txt) + captura com dois lutadores, HUD e FX juntos antes de aceite global).
<!-- budget:end -->

## Achado sobre o estado ATUAL (referencia a NAO seguir)
O `current_md_*.png` mostra o que a ROM desenha hoje, e ja esta degradado pelo conversor. A paleta de efeitos compartilhada (k-means dominado pelas chamas) nao tem preto, e a distancia ponderada leva:
- o **nucleo preto (8,8,8) -> vermelho (216,0,0)**, 68 px em `750,1`;
- **cinco azuis diferentes -> um unico azul (108,144,216)**: a rampa do hadouken some.

A referencia de desenho e o `source_*.png`, nao o atual. O defeito fica registrado. Nao sera corrigido na linha antiga, porque os efeitos migram para a linha do lutador.

## Entrega esperada
- **Capacidade:** confirmar que ve as referencias, gera/edita e persiste imagem. Registrar os limites de indexacao e de consistencia de animacao.
- **Direcao:** 2 alternativas + 1 ciclo completo da escolhida, em tamanho nativo, sobre fundo claro e escuro e ao lado de dois lutadores.
- **Arquivos:** fonte de edicao + PNG persistido. Se o canal so entrega RGB, dizer isso: a indexacao passa pelo pipeline tecnico.
- **Relatorio:** mapa de cores usado, perdas conhecidas e transformacoes.
- A saida e **candidata**: a integracao e a medicao sao do agente tecnico, e `visually_approved` exige revisao humana.
- Se o orcamento 8+6+1 nao permitir leitura suficiente, **demonstrar o conflito** e devolver alternativas de compromisso. Nao inventar slots.
