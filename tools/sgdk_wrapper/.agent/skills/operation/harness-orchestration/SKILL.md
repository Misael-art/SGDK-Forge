---
name: harness-orchestration
description: Use quando uma tarefa SGDK ampla possuir dois ou mais ramos potencialmente independentes e for preciso decidir, com baixo consumo de contexto, entre execução local, subagente read-only ou produtor isolado. Não use para uma correção curta, um único blocker causal, gate humano, promoção, claim ou integração final.
---

# Harness Orchestration

Coordene trabalho paralelo sem transformar quantidade de agentes em objetivo.
O coordenador continua sendo o único owner de escopo, claims, promoção,
integração Git, memory bank final e resposta humana.

## Entrada mínima

- workspace e projeto reais;
- objetivo e claim vigente;
- blocker causal dominante;
- tarefas delimitadas com dependências;
- caminhos de leitura, escrita e proteção;
- capacidade real do harness para criar/esperar/interromper workers.

## Decisão obrigatória

Antes de delegar, gere o snapshot e o plano:

```bash
python3 tools/sgdk_wrapper/harness_orchestration.py probe \
  --workspace-root . --project-root "SGDK_projects/<projeto>" \
  --objective "<objetivo>" --surface codex_desktop \
  --subagents available --max-concurrency 4 --supports-wait \
  --supports-interrupt --permission-profile workspace_write \
  --output "SGDK_projects/<projeto>/out/logs/harness_context_snapshot.json"

python3 tools/sgdk_wrapper/harness_orchestration.py plan \
  --context "SGDK_projects/<projeto>/out/logs/harness_context_snapshot.json" \
  --taskset <taskset.json> \
  --output "SGDK_projects/<projeto>/out/logs/orchestration_plan.json"
```

Obedeça `execution_mode`; não substitua a decisão por preferência pessoal.
Escopos do taskset são relativos ao projeto; caminhos absolutos POSIX/Windows e
travessia são proibidos.

## Quando delegar

- inventário, auditoria, testes, logs, budget ou review independentes;
- tarefa com pelo menos 60 segundos estimados;
- cápsula de contexto com até 1.200 palavras;
- resultado com até 600 palavras;
- writer somente quando for longo, reversível, isolado e sem sobreposição.

Use modelo econômico para coleta determinística, modelo equilibrado para
diagnóstico e modelo de alta capacidade apenas para julgamento artístico,
arquitetura ou causalidade que realmente o exija.

## Quando não delegar

- tarefa curta ou de um arquivo simples;
- claim, promoção, gate humano, integração, commit ou memória final;
- blocker externo/capacidade ausente compartilhada;
- writers no mesmo caminho;
- mesma hipótese já falhou sem evidência nova;
- preparação e revisão custariam mais que a execução local.

## Contrato do worker

- padrão read-only;
- sem histórico completo; receber apenas a cápsula do plano;
- logs completos ficam em arquivo, nunca voltam ao coordenador;
- toda entrada e saída relevante usa SHA-256;
- output segue `agent_task_result.schema.json`;
- valide antes de integrar:

```bash
python3 tools/sgdk_wrapper/harness_orchestration.py validate-result \
  --plan "SGDK_projects/<projeto>/out/logs/orchestration_plan.json" \
  --result <result.json>
```

Resultado stale, claim divergente, escrita fora do lease, escrita em caminho
protegido ou log bruto embutido é descartado.

Ao fechar a execução, agregue custo e eficiência causal sem promover qualidade:

```bash
python3 tools/sgdk_wrapper/harness_orchestration.py metrics \
  --plan "SGDK_projects/<projeto>/out/logs/orchestration_plan.json" \
  --result <result.json> \
  --output "SGDK_projects/<projeto>/out/logs/orchestration_metrics.json"
```

## Passa quando

- o plano não possui dependência cíclica;
- tarefas locais e delegadas têm razões explícitas;
- nenhuma escrita se sobrepõe;
- gate humano bloqueia apenas descendentes;
- o coordenador revalida hashes antes de integrar;
- validação crítica final é refeita mesmo havendo cache;
- paralelismo não promove asset, runtime, ROM ou AAA.

## Handoff

Entregue `harness_context_snapshot.json`, `orchestration_plan.json`, envelopes
validados, blockers removidos, custo observado e próxima ação causal. Não
copie transcrições de workers para o handoff.
