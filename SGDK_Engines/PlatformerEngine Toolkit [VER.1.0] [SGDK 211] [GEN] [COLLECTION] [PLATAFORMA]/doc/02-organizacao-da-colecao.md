# Organizacao da Colecao

## Estrutura principal

```text
PlatformerEngine Toolkit/
  .mddev/
  doc/
  variants/
    PlatformerEngine Core .../
  companions/
    ImageToGameMap .../
  upstream/
    PlatformerEngine/
    ImageToGameMap/
    Level/
```

## Responsabilidade de cada area

- `variants/`: entradas humanas para itens que o wrapper pode buildar
- `companions/`: componentes auxiliares de host, documentados e isolados
- `upstream/`: preservacao do repositorio original, sem reescrever a historia
- `doc/`: explicacao do por que da estrutura e do fluxo de uso

## Regra pratica

Se a pasta principal agrega mais de um papel tecnico relevante, ela nao deve
ficar rotulada como `ENGINE` unica. Ela deve virar uma `COLLECTION`.
