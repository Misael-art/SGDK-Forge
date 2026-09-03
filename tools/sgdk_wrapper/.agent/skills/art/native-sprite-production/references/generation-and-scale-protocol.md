# Generation and Scale Protocol

Leia esta referencia quando a fonte vier de IA/high-res ou quando a escala nativa ainda nao estiver comprovada.

## Papeis que nao podem ser misturados

1. `identity_source`: model sheet/concept aprovado; decide identidade.
2. `visual_producer_output`: imagem semanticamente forte; pode ser RGB/high-res.
3. `mechanical_scale_probe`: nearest + paleta limitada para medir sobrevivencia; nunca final.
4. `native_author_output`: pixels decididos no grid alvo, diretamente ou por
   traducao assistida posteriormente aceita nos gates independentes.
5. `runtime_asset`: derivado aprovado, indexado e integrado ao SGDK.

Se um arquivo ocupar dois desses papeis, o registro deve explicar a prova. Aparencia de pixel art nao e prova.

## Sequencia de passes

P0-P5 sao subpasses de `native_pose_construction` (etapa 4 de
`sprite-animation/references/canonical-animation-lifecycle.md`). Eles nao
substituem nem competem com o lifecycle global de animacao. Ao concluir P5, o
handoff volta para a etapa 5; nenhuma strip nasce diretamente destes passes.

### P0 — pose semantica

- uma pose, corpo inteiro, fundo simples
- silhueta, centro de massa, contato e marcadores `must_preserve`
- sem sheet, animacao ou polish

### P1 — lineart e clusters

- linha principal 1 px no grid logico
- separar cabeca, guarda/maos, tronco, pernas, pes e acessorios
- limpar double corners, ilhas, halos e linhas internas decorativas
- se a fonte vier sem alpha, remover somente fundo compativel conectado as
  bordas e emitir `foreground_matte_report`; revisar em fundo claro, escuro e
  chroma antes de qualquer quantizacao

### P2 — color blocking

- cor base por material
- nenhum shading antes de os materiais se separarem em 1x
- paleta funcional planejada antes da quantizacao
- produzir mapa de propriedade material separado do mapa anatomico; `torso` pode
  conter pele exposta e roupa, e `arms_or_guard` pode conter pele, manga e wrap
- declarar indices permitidos por material e outline compartilhado; nenhum
  indice de roupa pode funcionar como AA sobre pele
- verificar as fronteiras que definem figurino e identidade (barra de top,
  manga/axila, luva/mao, bota/perna, armadura/pele, faixa/calca)

### P3 — palette clean

- 1 outline/deep shadow compartilhado
- base + sombra por material; highlight apenas onde compra leitura
- maximo 15 cores visiveis, com papeis nomeados
- cor quase duplicada sem papel e `palette_micro_noise`

### P4 — autoria nativa

- decidir pixels no canvas alvo
- produtor high-res pode orientar, nunca ser chamado de asset nativo
- conversor automatico pode gerar `basic`/probe. Uma saida tecnicamente
  convertida so deixa esse teto quando for registrada como
  `assisted_native_translation` e passar fidelidade, 1x, escala, budget e humano

### P5 — validacao e integracao

- medir PNG, PLTE, index 0, 9-bit, bbox e grid
- deduplicar indices que convergem para o mesmo RGB depois do snap VDP
- revisar em 1x, ampliacao nearest, fundo claro e fundo escuro
- ancorar todas as vistas no SHA-256 do candidato e rederivar as tres vistas
  transformadas; aprovacao humana cita esse mesmo hash
- medir metasprite, scanline, tiles, residencia e DMA
- so depois abrir strips por acao e `resources.res`

## Prompt de produtor visual

Use descritores de forma e funcao. Declare o papel de cada referencia.

```text
Image 1: unica fonte de identidade e anatomia.
Image 2: mapa estrutural/cluster; nao e fonte de detalhe.
Produza exatamente uma pose [papel de gameplay].
Preserve [must_preserve].
Simplifique [can_simplify].
Prioridades: silhueta > contato > maos/rosto > figurino > detalhe.
Saida e visual_source; nao alegar resolucao nativa sem medicao.
```

## Prompt de palette-clean challenger

```text
Preserve pose e identidade. Reduza informacao.
Use uma rampa curta por material: base+sombra; highlight minimo.
Contorno continuo e hard-edge; nenhuma cor intermediaria de AA.
Cada pixel tem um material dono. Cor de um material nao atravessa a fronteira
para suavizar outro; use outline compartilhado ou a sombra do proprio lado.
Punhos, pes e rosto usam clusters geometricos legiveis.
Nao adicione detalhe menor que um pixel logico.
Fundo uniforme ou alpha real; checkerboard desenhado e blocker.
```

O prompt nao garante o contrato. Depois da geracao, meca dimensoes, modo, alpha e cores. Se for TrueColor/high-res, classifique como fonte.

## Gate de escala

### Escala `locked`

- nao testar escala maior como substituicao silenciosa
- se a probe perder identidade, voltar para autoria direta no grid travado
- alternativa maior pode existir apenas como evidencia de tradeoff

### Escala `provisional`

- testar no maximo tres caixas candidatas, todas multiplas de 8
- usar a mesma pose, material map e paleta para isolar o efeito da escala
- comparar leitura 1x, ocupacao da camera, hitbox, workload, metasprite e pior scanline
- adotar escala apenas depois de budget e decisao humana quando mudar FOV/gameplay

### Sintomas e resposta

| Sintoma | Causa provavel | Mudanca causal |
|---|---|---|
| bonito ampliado, ilegivel em 1x | densidade/escala | simplificar clusters ou abrir gate de escala |
| 15 cores mas rosto morto | paleta sem papel semantico | redistribuir slots por material/feature |
| contorno quebrado apos quantizar | AA/microcores na fonte | autoria hard-edge, nao novo quantize |
| 48x64 falha e 64x96 passa | conflito de escala | medir camera/budget; nao promover probe |
| ferramenta GUI trava | canal errado | CLI/headless ou produtor diferente |
| retangulo claro ou graos no recorte | threshold global + resize interpolado | matte conectado as bordas + alpha binario + NEAREST |
| paleta parece ter menos cores que os indices usados | aliases apos snap VDP | compactar RGB e remapear indices antes do pixel gate |
| sprite alto estoura links em toda scanline | metasprite total aplicado por linha | decompor em celulas <=32x32 e medir cada faixa Y |

## Criterio de parada

Pare somente por licenca/fonte ausente, decisao de produto sobre escala, impossibilidade de hardware medida ou esgotamento real de rotas distintas. Falha estetica e instrucao de iteracao, nao pedido para o humano fabricar o PNG.
