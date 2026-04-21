# Prompt de Handoff Para Implementacao do Ecossistema AAA

Copie o texto abaixo e use como prompt inicial para o proximo agente de IA.

---

Voce vai atuar **somente** em `F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper` para implementar novas capacidades no ecossistema de agentes e automacao SGDK.

## Missao

Implemente, com seguranca e sem regressao, a expansao do ecossistema AAA descrita nos documentos abaixo:

- `F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\doc\aaa_agent_feature_roadmap.md`
- `F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\doc\aaa_agent_feature_implementation_spec.md`
- `F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\doc\aaa_agent_feature_handoff_checklist.md`

## Regra Maxima

**Nao pode haver regressao no comportamento atual do wrapper.**

Isso significa:

- nao quebrar nem alterar silenciosamente o comportamento default de:
  - `build.bat`
  - `build_inner.bat`
  - `run.bat`
  - `validate_resources.ps1`
  - `run_runtime_capture.ps1`
  - `run_visual_capture.ps1`
  - `generate_scene_regression_report.ps1`
- nao introduzir gate novo por default
- nao mudar formato de artefato legado sem compatibilidade explicita
- nao editar `src/`, `res/`, `doc/` de projetos SGDK nem `out/rom.bin`
- nao integrar nada no wrapper principal sem flag `SGDK_*`

Se surgir qualquer necessidade de quebrar contrato atual do wrapper, **pare**, registre a dependencia como decisao arquitetural pendente e nao improvise.

## Ordem de Trabalho Obrigatoria

Siga exatamente esta ordem:

1. ler `aaa_agent_feature_roadmap.md`
2. ler `aaa_agent_feature_implementation_spec.md`
3. ler `aaa_agent_feature_handoff_checklist.md`
4. executar **Sprint 0**
5. executar **Sprint 1**
6. executar **Sprint 2**
7. seguir sprint por sprint, sem pular etapas

Nao comecar por integracao no wrapper principal.
Nao comecar por gate.
Nao comecar por feature que depende de outra ainda nao pronta.

## Prioridades Tecnicas

Implemente nesta ordem:

1. fundacao comum
2. capturador canonico de evidencia BlastEm
3. linter de contrato de cena
4. runner deterministico de regressao por cena
5. auditor de budget por frame/cena
6. inspector visual de VRAM/paleta/sprites
7. integracoes opt-in

## Modo de Implementacao

Toda feature nova deve nascer assim:

1. script isolado
2. schema JSON versionado
3. artefato novo em `out/logs`, `out/evidence` ou `out/reports`
4. validacao local
5. piloto em projeto laboratorio
6. integracao opt-in por flag

Por default:

- falhas novas devem degradar para warning
- scripts novos nao devem afetar build legado
- o wrapper atual deve continuar funcionando igual com as flags desligadas

## O Que Voce Deve Criar

Siga os nomes exatos e interfaces definidos em:

- `aaa_agent_feature_implementation_spec.md`

Isso inclui:

- scripts `.ps1`
- modulos `.psm1`
- schemas `.schema.json`
- um renderer `.py` para o inspector VDP

Nao invente nomes alternativos sem necessidade real.

## O Que Voce Nao Pode Inventar

Se algum destes pontos aparecer, nao chute:

- formato final do dump VDP se nao estiver documentado
- contrato definitivo de bootstrap deterministico de cena
- thresholds canonicos de budget por tipo de cena
- politica oficial de comparacao tolerante versus exata
- obrigatoriedade universal dos manifests para todos os projetos

Nesses casos:

1. documente o bloqueio
2. proponha a menor implementacao segura possivel
3. mantenha a feature em modo observacao

## Entrega Esperada por Sprint

Antes de encerrar cada sprint:

- confirme que os arquivos previstos para a sprint foram criados
- valide schemas e artefatos gerados
- rode diagnosticos dos arquivos editados
- confirme explicitamente que nao houve regressao no fluxo default
- registre riscos restantes e proximos passos

## Formato de Progresso Esperado

Em cada ciclo de trabalho:

1. diga qual sprint esta executando
2. diga quais arquivos vai criar ou alterar
3. implemente apenas o necessario para a sprint atual
4. valide
5. reporte:
   - arquivos criados
   - arquivos alterados
   - testes executados
   - riscos
   - se o comportamento default foi preservado

## Primeiro Passo Obrigatorio

Comece pela **Sprint 0 - Preflight** do arquivo:

- `F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\doc\aaa_agent_feature_handoff_checklist.md`

Depois avance para a **Sprint 1 - Fundacao Comum**.

Se tudo estiver claro, inicie sem modificar o wrapper principal.

---

Fim do prompt.
