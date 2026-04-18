# Fluxo de Trabalho

## Para estudar

1. Abra uma variante em `variants/`.
2. Leia o `README.md` dela.
3. Abra o `src/main.c` no caminho `upstream/...` indicado.
4. Rode `build.bat` pela raiz da variante.

## Para evoluir o material

- Ajustes genericos de build vao para `tools/sgdk_wrapper/`.
- Ajustes especificos da colecao devem ser registrados nesta pasta `doc/`.
- Material ambiguo ou historico deve ir para `archives/manual_review/`.

## Para manter a colecao limpa

- A raiz da colecao nao deve acumular binarios, logs ou wrappers legados.
- Cada demo deve entrar no ecossistema por um diretório nominal proprio.
- Todo conteudo upstream relevante deve continuar preservado em `upstream/`.
