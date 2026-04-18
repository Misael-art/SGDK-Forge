# Documentacao de MegaDriving Streeter Util Test Project [VER.001] [SGDK 211] [GEN] [ENGINE] [CORRIDA]

Este diretorio concentra a documentacao tecnica e pedagogica do projeto.
Ele existe para que o codigo nao precise carregar sozinho todo o contexto de
arquitetura, fluxo de build e regras de desenvolvimento.

## Ordem de leitura recomendada

1. `01-visao-geral.md`
2. `02-build-wrapper.md`
3. `03-arquitetura.md`
4. `04-recursos-e-pipeline.md`
5. `05-guia-de-desenvolvimento.md`
6. `06-debug-migracao.md`

## Objetivo desta pasta

- Facilitar onboarding de quem abre o projeto pela primeira vez
- Explicar o motivo da estrutura de pastas e do uso do wrapper central
- Registrar decisoes tecnicas sem espalhar notas em arquivos soltos
- Servir como material de estudo para SGDK e Mega Drive

## Convencoes

- Documentacao de produto e onboarding fica no `README.md` da raiz
- Documentacao tecnica e operacional fica em `doc/`
- Ajustes genericos de build vao para `tools/sgdk_wrapper/`, nao para este projeto
- Mudancas especificas deste projeto devem ser registradas aqui

Leitura complementar: `07-notas-da-variante.md`.
