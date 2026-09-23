# Laboratory Mode

Status: `canonical_workflow`

## Objetivo

Permitir experimentos tecnicos controlados sem risco de contaminar projetos de
producao, memoria canonica ou status de proficiencia.

Laboratorio e espaco de prova. Nao e entrega.

## Local Permitido

Laboratorio vive em:

- `SGDK_projects/_agent_laboratory/`

Cada experimento deve ficar em subprojeto proprio e manter:

- `rascunho/` para entradas externas copiadas;
- `doc/lab_report.md`;
- `doc/technique_usage_manifest.json` quando envolver tecnica;
- logs em `out/logs/`;
- evidencia local, quando houver;
- flag textual ou report equivalente `lab_not_delivery=true`.

## Quando Usar

Use laboratorio para:

- tecnica `LABORATORIO`;
- hipotese sem evidencia;
- benchmark isolado;
- repro de bug;
- experimento visual ou runtime que ainda nao pertence ao GDD.

Nao use laboratorio para:

- entregar jogo;
- substituir BlastEm de gate;

Tecnica extrema da barra viva (multiplex alem do SAT, 3D software, raycast,
sprite doubler, plane-scroll experimental) **so existe aqui**, com
`lab_not_delivery=true`. Nao vaza para `aaa_game` sem prova em ROM e
aprovacao humana. Tetos: `doc/03_art/live_scene_bar_parameters.json`.
- provar status `MESTRE_*`;
- aplicar patch canonico;
- corrigir producao sem atualizar docs do projeto real.

## Fluxo

1. Declare pergunta do experimento.
2. Declare tecnica, tag, registry id e status humano.
3. Crie ou selecione subprojeto em `_agent_laboratory/`.
4. Copie entradas externas para `rascunho/` com hash.
5. Execute build/teste apenas dentro do laboratorio.
6. Gere `doc/lab_report.md`.
7. Se houver licao, rode `audit_project_learning.ps1 -Mode Capture`.
8. Mantenha proposta canonica como `not_applied`.

## Relatorio Minimo

`doc/lab_report.md` deve registrar:

- pergunta;
- tecnica e status;
- arquivos alterados;
- comandos executados;
- resultado observado;
- blockers;
- riscos;
- decisao: descartar, repetir, promover para treino, ou enviar para curadoria.

## Regra De Status

- Sucesso em laboratorio nao promove para `MESTRE_*`.
- Tecnica `LABORATORIO` continua bloqueada em entrega nao-lab.
- Prototipo visto no emulador ainda e laboratorio se nao passou por projeto
  aprovado, budget e revisao humana.

