# Curation Mode

Status: `canonical_workflow`

## Objetivo

Aplicar curadoria canonica com rigor: revisar propostas, eliminar duplicidade,
atualizar documentos certos, rodar regressao e registrar memoria.

Curadoria e o unico modo que pode alterar `tools/sgdk_wrapper/.agent/`,
`tools/sgdk_wrapper/` ou `doc/` canonico, sempre com aprovacao humana
explicita.

## Entradas Permitidas

- propostas locais `not_applied`;
- material externo marcado como nao verificado;
- drift entre docs, schemas e workflows;
- gap observado em projeto real;
- pedido humano explicito de patch canonico.

## Preflight

Antes de editar canone:

1. identifique fonte e tipo de evidencia;
2. confirme aprovacao humana para alterar canone;
3. verifique se ja existe skill, schema, workflow ou doc equivalente;
4. defina menor alteracao suficiente;
5. declare arquivos alvo;
6. preserve compatibilidade com validators existentes.

## Regras De Assimilacao

- Texto rico pode enriquecer docs e abrir `LABORATORIO`/`TEORICA_*`.
- Texto externo sozinho nao promove `MESTRE_*`.
- Projeto de laboratorio sozinho nao promove `MESTRE_*`.
- Projeto aprovado exige build, BlastEm, budget, gameplay/uso real,
  documentacao e aprovacao humana.
- Duplicidade deve ser fundida, nao clonada.
- Nomes devem ser ASCII canonico, sem sinonimos paralelos para o mesmo status.

## Ordem Recomendada

1. Atualizar schema ou registry quando houver contrato machine-readable.
2. Atualizar skill/workflow que opera a regra.
3. Atualizar doc humano de destaque quando a mudanca for pedagógica.
4. Atualizar validadores.
5. Atualizar memoria canonica.
6. Rodar regressao.

## Validacao Minima

Escolha os validadores afetados e rode os gates relevantes. Para mudanca de
framework, preferir:

```powershell
python tools/sgdk_wrapper/ci/test_schema_contract_gates.py
python tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py
powershell -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_all_contract_gates.ps1 -Mode full
```

Se o escopo envolver ROM ou projeto, o gate de entrega continua exigindo
BlastEm conforme `AGENTS.md`.

## Saida

Ao fechar curadoria, registre:

- decisao;
- arquivos alterados;
- evidencias usadas;
- validacoes executadas;
- limitacoes;
- regra factual: o que foi canonizado e o que nao foi aprovado.

