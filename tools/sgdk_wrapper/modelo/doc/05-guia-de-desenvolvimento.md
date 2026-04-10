# 05 - Guia de Desenvolvimento Complementar

## Para adicionar nova cena

1. criar o header em `inc/scenes/`;
2. implementar a cena em `src/scenes/`;
3. registrar a entrada e a atualizacao em `src/core/app.c`;
4. documentar a nova responsabilidade em `doc/03-arquitetura.md`.

## Para adicionar assets reais

1. colocar o bruto em `res/data/`;
2. declarar o recurso final em `res/resources.res` quando o asset existir;
3. rebuildar via wrapper;
4. revisar `out/logs/asset_preparation.log` e `validation_report.json`.

## Para ampliar a base

- mantenha `main.c` pequeno;
- concentre roteamento em `src/core/`;
- coloque leitura de hardware em `src/system/`;
- mantenha cada cena autocontida;
- atualize a documentacao quando a verdade do projeto mudar.
