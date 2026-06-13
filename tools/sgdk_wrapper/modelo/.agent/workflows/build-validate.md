# Workflow: Build Validate

Use este fluxo para build, rebuild e validacao operacional.

1. Resolver contexto do projeto.
2. Garantir bootstrap da `.agent` local.
3. Carregar `env.bat`.
4. Respeitar `build_policy`.
5. Rodar build.
6. Verificar artefato gerado.
7. Separar `buildado` de `testado_em_emulador`.
