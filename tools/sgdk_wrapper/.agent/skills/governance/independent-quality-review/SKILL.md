---
name: independent-quality-review
description: Use em marcos de projeto SGDK, antes de crescimento caro ou quando uma entrega multidisciplinar precisar de crítica independente e correções priorizadas. Roteia até três revisores read-only conforme risco e estágio. Não use em toda pequena edição, como substituto do owner técnico, para aprovar o próprio trabalho ou para transformar gosto em blocker.
---

# Independent Quality Review

Atue como conselho de qualidade, não como antagonista por temperamento. O alvo é
descobrir cedo defeitos causais e oportunidades de alto retorno sem paralisar a
produção, ampliar escopo ou promover claims.

## Checkpoints

- `foundation`: depois de visão/GDD e antes de TDD ou produção cara;
- `pre_growth`: depois dos seeds de mecânica, level, inimigos e áudio;
- `vertical_slice`: depois da cena jogável e antes de expandir conteúdo;
- `release_candidate`: antes do closeout de produto.

Não rode o conselho em cada arquivo. Faça review por delta e SHA desde o último
checkpoint aceito.

## Roteamento obrigatório

Crie `quality_review_request.json` e execute:

```bash
python3 tools/sgdk_wrapper/quality_review_router.py plan \
  --request <quality_review_request.json> \
  --output <quality_review_plan.json> \
  --taskset-output <quality_review_taskset.json>
```

O roteador seleciona no máximo três domínios e reutiliza owners existentes.
Lacunas especializadas usam `gameplay-experience-reviewer`,
`narrative-design-reviewer` e `product-market-reviewer`. Mercado só é aplicável
com intenção comercial ou pedido explícito.

Quando houver dois ou mais reviews longos independentes, passe o taskset para
`harness-orchestration`. Reviewers são read-only, recebem cápsula mínima e não
veem a defesa persuasiva do produtor. O coordenador permanece único owner de
escopo, claim, promoção, integração, Git e decisão humana.

## Parecer

Consolide em `independent_quality_review.json`:

- artefatos e SHA examinados;
- reviewer diferente do produtor;
- achados como `defect`, `risk`, `opportunity` ou `taste`;
- severidade, confiança, evidência e impacto no jogador;
- menor correção causal, owner e prova de aceitação;
- no máximo três prioridades imediatas;
- decisão `proceed`, `proceed_with_tracked_risks`, `revise_before_growth` ou
  `human_scope_decision_required`.

Valide antes de encaminhar correções:

```bash
python3 tools/sgdk_wrapper/quality_review_router.py validate-report \
  --request <quality_review_request.json> \
  --plan <quality_review_plan.json> \
  --report <independent_quality_review.json>
```

## Limites

- `taste` e `opportunity` nunca bloqueiam crescimento por si;
- proposta fora do GDD exige decisão humana, não mutação silenciosa;
- gameplay não passa sem observação de ROM, captura e input trace no slice;
- market review usa fontes atuais, datadas e rastreáveis;
- parecer não prova qualidade, ROM, performance ou AAA;
- especialistas corrigem; o conselho apenas diagnostica, prioriza e revalida.
