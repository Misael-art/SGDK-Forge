# 04 - Recursos e Pipeline

## Solucao Canonica

O fluxo canonico deste workspace e:

1. colocar os arquivos brutos em `res/data/`;
2. deixar o wrapper gerar a versao final em `res/`;
3. usar `res/data/backup/` como area de seguranca para backups automaticos.

## Proposito

- separar fonte bruta de saida final;
- permitir correcao automatica sem perder o original;
- padronizar o caminho de ingestao para IA e para humanos;
- garantir rastreabilidade quando o wrapper agir sobre os assets.

## Como o wrapper atua

- varre `res/` e corrige imagens finais incompativeis;
- move o arquivo antigo para `res/data/backup/` antes da correcao;
- varre `res/data/` recursivamente;
- ignora `res/data/backup/`;
- espelha a hierarquia para `res/`;
- registra tudo em `out/logs/asset_preparation.log`,
  `asset_preparation_report.json` e `asset_preparation_preview.png`.

## Estrutura sugerida

- `res/data/sprites/`
- `res/data/bgs/`
- `res/data/ui/`
- `res/sprites/`
- `res/bgs/`
- `res/ui/`
