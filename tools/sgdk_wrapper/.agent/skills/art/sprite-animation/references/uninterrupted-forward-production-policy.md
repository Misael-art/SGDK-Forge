# Politica de producao continua sem falso gate humano

Use somente quando o usuario pedir explicitamente um forward-test ou producao
continua sem interrupcoes intermediarias. Esta politica adia a solicitacao de
decisao humana; ela nunca transforma revisao do agente em aprovacao humana.

## Estado operacional

Declare `human_review_policy=deferred_nonpromotional_review`. Enquanto estiver
ativo:

- mantenha `human_gate_status=pending`, `promotable=false` e `res_promotion=false`;
- produza, compare, reprove e refine candidatos em `out/`, `rascunho/` ou lab;
- use `agent_curated_diagnostic_review` para leitura, acting, fidelidade e apelo;
- preserve um incumbent por hash e gere challengers por mudanca causal;
- avance ramos independentes e, quando explicitamente autorizado pelo pedido,
  prototipos downstream reversiveis marcados `speculative_downstream`;
- nunca use prototipo downstream para justificar `visual_pass`, `human_review`,
  promocao, runtime ou AAA.

## Quando continuar sem perguntar

Nao abra gate humano para candidato que ainda possua falha observavel de fonte,
silhueta, identidade, lineart, pose, materiais, movimento, principios, timing,
contato, budget ou integridade. Corrija ou troque a rota. Se uma rota falhar duas
vezes sem delta, encerre a rota e use outra; nao encerre o projeto.

Uma fonte sem frames temporais nao bloqueia autoria de animacao. Ela bloqueia
apenas a alegacao de que escala, translacao, reordenacao ou recolor da mesma pose
sejam movimento novo. Autorize key poses e inbetweens nativos com IDs e hashes
distintos.

## Quando a intervencao humana e realmente irredutivel

Interrompa somente por:

- licenca, proveniencia ou autoridade visual ausente;
- escolha de escala/camera/hitbox que muda gameplay ou produto;
- duas direcoes que passam todos os gates objetivos mas representam escolhas
  artisticas materialmente diferentes;
- acao externa, destrutiva, paga ou fora do escopo;
- impossibilidade de hardware medida cujo fallback muda o produto;
- esgotamento comprovado de todas as rotas seguras.

Se isso ocorrer, consolide uma unica solicitacao humana com opcoes hash-bound.
Nao fragmente a sessao em aprovacoes por pose, frame, strip ou ferramenta.

## Fechamento do forward-test

Entregue uma matriz por projeto: ultimo estagio real, incumbent, challengers,
rotas encerradas, blockers folha, proxima acao causal, claims permitidos e
artefatos. Um projeto bloqueado nao impede os demais. O relatorio final deve
distinguir `agent_curated_diagnostic_review` de decisao humana e listar qualquer
`speculative_downstream` que possa ser descartado.
