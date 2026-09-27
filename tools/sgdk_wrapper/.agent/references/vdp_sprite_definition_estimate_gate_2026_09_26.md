# Regra de closeout: estimativa de sprites internos versus evidencia real

## Decisao operacional

Um alerta baseado apenas na largura e altura declaradas em `SPRITE` nao prova
que um quadro excede 16 sprites internos. Mantenha a estimativa como triagem
informativa; use a decomposicao real do ResComp por quadro como gate rigido do
limite de 16. Avalie separadamente os limites de runtime por scanline, o total
de sprites ativos, a carga de CPU e a evidencia vinculada a ROM e assets exatos.

## Semantica dos limites

- O limite 16 do ResComp aplica-se aos sprites VDP internos de cada quadro de
  uma `SpriteDefinition`; nao e o limite total de sprites visiveis na cena.
- No modo H40, a cena ainda precisa caber nos limites independentes do VDP por
  scanline: 20 sprites e 320 pixels. O total de links de sprite tambem e outro
  eixo. FPS estavel mede cadencia/CPU e nao prova que nenhum sprite foi omitido
  por pressao de scanline.
- A estimativa geometrica existente divide o retangulo inteiro em celulas de
  ate 4x4 tiles. Ela assume implicitamente um retangulo preenchido e nao mede a
  mascara dos pixels, os recortes reais por quadro nem a saida do cutter do
  ResComp. Por isso, uma folha de 31x22 tiles pode estimar 48 celulas mesmo que
  o cutter consiga produzir uma decomposicao valida com 16 ou menos.

## Evidencia e classificacao

1. Registre a estimativa dimensional por recurso como `estimate`, com o metodo
   e dimensoes usados. Resultado acima de 16 e `warning`/`needs_review`, nunca
   `ERROR` de violacao real por si so.
2. O gate rigido por `SpriteDefinition` usa o resultado pos-cutter do ResComp
   para cada quadro. O SGDK 2.11 tenta estrategias para reduzir a contagem e
   interrompe a compilacao se um quadro continuar acima de 16. Build bem
   sucedido so vale quando logs, fontes `.res`, assets e ROM correspondem ao
   mesmo build fresco.
3. Se os metadados pos-cutter nao estiverem disponiveis ou a ROM/build estiver
   stale, use `needs_review`; nao transforme a estimativa em prova nem trate
   um build antigo como evidencia da fonte atual.
4. O gate de cena usa telemetria/dump ou simulacao equivalente no pior quadro,
   cobrindo lutadores, HUD, projeteis e FX simultaneos. Registre pico de
   sprites por scanline e largura em pixels por scanline; teste CPU/FPS em
   separado e com audio quando ele participa da carga.
5. Um overflow real de quadro reportado pelo ResComp, ou uma medicao de runtime
   acima do limite de scanline, e blocker e pede reducao, decomposicao,
   temporizacao ou fallback artistico medido. Nao mascare overflow com flicker.

## Leitura correta do `.res`

A gramatica SGDK 2.11 e:

```text
SPRITE name image width height [compression [time [collision [opt_type [opt_level [opt_duplicate]]]]]]
```

`BALANCED`, `SPRITE`, `TILE` e `NONE` sao opcoes de `opt_type`, cada uma com
tradeoffs diferentes. Um validador deve interpretar os campos de acordo com a
gramatica, nao procurar um sufixo magico como `NONE 1 1`. Nao acrescente esse
sufixo automaticamente: alem de nao corresponder ao `opt_type` declarado, ele
pode deslocar campos e alterar a semantica do recurso. Presenca de uma opcao de
otimizacao tambem nao substitui a medicao pos-cutter.

`opt_type=SPRITE` reduz o numero de sprites de hardware potencialmente ao custo
de mais tiles. So escolha essa rota se a decomposicao real exigir, e reavalie
tiles, VRAM e DMA depois da mudanca.

## Caso observado em Mugenesis, 2026-09-26

Em `SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]/res/mgres_ken.res`,
11 definicoes ultrapassaram a estimativa geometrica 16: seis deram 20; as cinco
folhas grandes de super deram 48, 48, 40, 32 e 64. As linhas observadas declaram
`FAST 0 NONE BALANCED`; `BALANCED` e um `opt_type` valido na sintaxe SGDK.
O validador compartilhado reconhece somente o sufixo `NONE 1 1` como opcao e,
por isso, classifica incorretamente essas linhas como sem otimizacao antes de
emitir erro pelo numero estimado.

Esse caso confirma um falso positivo da regra estatica e um defeito no parser/
classificador do validador. Os numeros acima descrevem somente a estimativa de
dimensoes nessa fonte; nao sao contagem pos-cutter nem prova de runtime. Nao foi
selado aqui um par entre hash da ROM e hash dos assets. Closeouts futuros devem
registrar essa ligacao antes de usar uma compilacao como evidência.
