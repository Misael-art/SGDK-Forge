# Estudo de distribuição de paleta — Vegetable Valley

Asset visual: `vegetable_valley_palette_distribution_study_v01`, SHA-256 `2019635295fe4041b7d71b5ad6a977373562c3639cd1c03da72018fcfede040f`.

O painel apresenta cada alternativa em thumbnail 4:3, ampliação nearest e composição equivalente a 320×224. É um estudo editorial de hierarquia de paleta, não uma quantização SGDK, não uma conversão da cena e não uma fonte de pixels.

| Opção | Distribuição | Leitura em 1× | Risco | Próximo teste |
|---|---|---|---|---|
| A | PAL2 dedicada ao herói; PAL3 para inimigos/FX; foreground subordinado a PAL1 | maior separação do herói e FX causal forte | PAL3 pode ficar congestionada | medir slots, operadores S/H e contraste no frame de inalação |
| B | PAL2 compartilhada entre herói/inimigo harmonizados; foreground em PAL1; PAL3 para FX | família cromática mais unificada | herói perde prioridade | medir leitura de silhueta e contraste do inimigo |
| C | PAL2 dedicada ao herói; PAL3 dedicada ao FX; inimigo em rampa compatível medida | melhor sinal energético da habilidade | FX pode dominar a cena | medir perceptibilidade, scanline e conflito de rampa |

## Decisão de trabalho

Manter A como hipótese preferida para o próximo estudo nativo, sem travar a PAL2 compartilhada antes de prova visual. B e C permanecem comparações controladas. A decisão final exige paletas RGB333 autoradas, auditoria de operadores Shadow/Highlight, `per_tile_palette_conflict_report` e captura 1× em BlastEm.
