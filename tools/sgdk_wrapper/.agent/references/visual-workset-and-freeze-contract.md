# Contrato de workset visual e congelamento

Leia antes de produzir ou retomar arte quando o projeto possuir historico,
probes, arquivos rejeitados ou mais de uma epoca visual.

## Autoridade operacional

`doc/art/visual_workset_manifest.json` e a lista curta de arquivos autorizados
a participar da iteracao atual. Ele nao substitui proveniencia, contrato visual,
GDD, pixel gate, budget ou aprovacao humana.

- `production_sources`: unicas imagens que podem possuir pixels novos.
- `reference_only_sources`: orientam qualidade, pose ou estudo; nunca fornecem
  pixels, underlay, img2img, baseline de geracao ou cluster copiavel.
- `forbidden_source_roots`: historico, staging, evidencias e runtime que nao
  podem voltar ao grafo de producao.
- `active_epoch`: identidade imutavel da rodada atual.

Contrato e spec de geracao devem registrar o SHA do workset vigente. Caminho
encontrado por busca, semelhanca de nome ou proximidade no diretorio nao concede
elegibilidade.

Valide com:

```bash
PYTHONPATH=tools/sgdk_wrapper python3 -m forge_art workset-validate \
  --project-root "<projeto>"
```

## Projeto congelado

`state=frozen_case_study` significa:

- `production_sources` vazio;
- somente auditoria, validacao, verificacao de rota e leitura do estudo;
- nenhuma nova pose, frame, strip, conversao, shootout ou promocao;
- reativacao exige decisao humana explicita e um novo workset ativo. Editar
  somente o status, reutilizar arquivos antigos ou abrir nova pasta `vNN` nao e
  reativacao valida.

O congelamento preserva a evidencia e encerra a producao daquele caso; as
regras generalizadas vivem nas skills e validators canonicos, nao no projeto.

## Regra de alcance

Arquivo arquivado por texto mas ainda referenciado por `.res`, cena, contrato,
spec ou builder continua ativo. A quarentena so existe quando o grafo de
producao nao consegue alcanca-lo. `visual_lab_control`, `negative_evidence`,
`procedural_code_probe`, `historical_superseded` e `runtime_evidence_only`
nunca sao fontes de pixels.
