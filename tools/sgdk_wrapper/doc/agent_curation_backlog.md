# Backlog de Curadoria: Framework Canônico de Agentes (`.agent`)

**Data da Revisão Crítica:** 17 de Abril de 2026  
**Alvo:** `F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\.agent`  
**Status Atual:** O framework canônico está vivo e operacional, mas a análise anterior estava parcialmente superestimada em alguns pontos. A revisão honesta abaixo mantém apenas achados sustentados por evidência direta dos arquivos do wrapper.

Este documento substitui a leitura apressada anterior por um backlog mais preciso, separando:

- problemas reais do framework canônico
- contradições internas entre docs, workflows e skills
- hipóteses que ainda precisam de validação antes de virarem ação

---

## 1. Achados Confirmados

### 1.1 Contradição entre discurso anti-persona e artefatos ainda agent-centric
* **Descrição Específica**: O `ARCHITECTURE.md` afirma que o fluxo canônico "não é definido por personas fictícias", mas o próprio framework ainda contém e referencia personas e papéis nomeados. Há referências explícitas a `art-director`, `art-pipeline-operator`, `mega-drive-pixel-engineer` e outros em skills, regras e workflows.
* **Localização Exata**:
  * `tools/sgdk_wrapper/.agent/ARCHITECTURE.md`
  * `tools/sgdk_wrapper/.agent/agents/`
  * `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`
  * `tools/sgdk_wrapper/.agent/workflows/art-onboarding.md`
  * `tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md`
* **Tipo de Curadoria**: Harmonização arquitetural / revisão conceitual.
* **Prioridade**: Crítica.
* **Responsável Sugerido**: Arquiteto do Framework.
* **Prazo Estimado**: 2 a 3 horas.
* **Status Atual**: Contraditório.
* **Complexidade**: Média.
* **Dependências**: Definir se `agents/` continuará como camada pedagógica/documental ou será formalmente descontinuado.
* **Análise de Impacto**: Hoje o problema não é "deletar `agents/`". O problema real é a mensagem conflitante. Uma IA lendo o framework pode concluir tanto que personas são proibidas quanto que elas ainda são parte oficial da operação, o que aumenta ambiguidade de roteamento e de linguagem de handoff.

### 1.2 Manifesto canônico não representa toda a superfície realmente usada
* **Descrição Específica**: O `framework_manifest.json` não rastreia partes do framework que já são relevantes no funcionamento e na descoberta do contexto. Exemplos concretos: `framework_manifest.json` não rastreia a si mesmo; `lib_case/` não está em `tracked_paths`; `skills/README.md` documenta política canônica de `openai.yaml` e também não está rastreado; skills e workflows efetivamente referenciados no ecossistema, como `skills/architecture/scene-state-architect`, `skills/governance/truth-hierarchy-guard`, `skills/governance/doc-sync-audit`, `skills/operation/status-panel-maintainer`, `workflows/art-onboarding.md`, `workflows/status.md`, `workflows/plan.md` e `workflows/handoff.md`, também ficaram fora.
* **Localização Exata**:
  * `tools/sgdk_wrapper/.agent/framework_manifest.json`
  * `tools/sgdk_wrapper/.agent/skills/README.md`
  * `tools/sgdk_wrapper/.agent/workflows/`
  * `tools/sgdk_wrapper/.agent/lib_case/`
* **Tipo de Curadoria**: Atualização de manifesto / governança de bootstrap.
* **Prioridade**: Alta.
* **Responsável Sugerido**: Agente de Governança (`doc-sync-audit`).
* **Prazo Estimado**: 1 a 2 horas.
* **Status Atual**: Incompleto.
* **Complexidade**: Média.
* **Dependências**: Item 1.1, porque a decisão sobre `agents/` e `openai.yaml` afeta o que deve ou não ser rastreado.
* **Análise de Impacto**: O risco não é apenas "drift". O bootstrap local pode materializar uma cópia parcial da `.agent`, deixando de fora partes que o próprio framework considera válidas para operação, roteamento e retenção de conhecimento.

### 1.3 Contratos explícitos faltando em skills relevantes, mas não em toda a árvore
* **Descrição Específica**: A análise anterior marcou isso de forma ampla demais. O problema real confirmado é mais específico: algumas skills importantes ainda não expõem o contrato completo exigido em `ARCHITECTURE.md` (`entrada minima`, `saida minima`, `passa quando`, `handoff para proxima etapa`), enquanto outras centrais já estão corretas. As faltantes confirmadas na revisão incluem:
  * `skills/architecture/scene-state-architect/SKILL.md`
  * `skills/governance/truth-hierarchy-guard/SKILL.md`
  * `skills/governance/doc-sync-audit/SKILL.md`
  * `skills/operation/status-panel-maintainer/SKILL.md`
  * `skills/art/visual-excellence-standards/SKILL.md`
* **Localização Exata**: `tools/sgdk_wrapper/.agent/skills/**/SKILL.md`
* **Tipo de Curadoria**: Padronização de contrato operacional.
* **Prioridade**: Alta.
* **Responsável Sugerido**: Engenheiro de Prompt / Governança.
* **Prazo Estimado**: 2 a 3 horas.
* **Status Atual**: Parcial.
* **Complexidade**: Média.
* **Dependências**: Nenhuma.
* **Análise de Impacto**: O impacto aqui é real, mas mais localizado do que o texto anterior sugeria. Essas skills continuam legíveis para humanos, porém perdem previsibilidade para orquestração entre IAs, especialmente nas etapas de diagnóstico, status e arquitetura.

### 1.4 Workflows legados não estão claramente alinhados ao modelo canônico atual
* **Descrição Específica**: O `workflows/art-onboarding.md` segue uma linguagem e uma estrutura mais antigas, ainda centradas em "agente responsável" e fluxos operacionais parcialmente diferentes da narrativa mais nova baseada em pipeline + skills + manifesto. Isso não prova obsolescência total, mas prova desalinhamento editorial.
* **Localização Exata**:
  * `tools/sgdk_wrapper/.agent/workflows/art-onboarding.md`
  * comparação com `tools/sgdk_wrapper/.agent/workflows/production-loop.md`
  * comparação com `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md`
* **Tipo de Curadoria**: Revisão editorial / alinhamento de workflow.
* **Prioridade**: Média.
* **Responsável Sugerido**: Arquiteto do Framework + dono da trilha de arte.
* **Prazo Estimado**: 1 a 2 horas.
* **Status Atual**: Desalinhado.
* **Complexidade**: Média.
* **Dependências**: Item 1.1.
* **Análise de Impacto**: Sem esse ajuste, diferentes documentos do próprio framework empurram a IA para estilos de operação diferentes, o que enfraquece consistência de execução e dificulta auditoria.

---

## 2. Pontos que a análise anterior exagerou ou concluiu cedo demais

### 2.1 `agents/` não pode ser tratado como lixo sem decisão arquitetural explícita
* **Descrição Específica**: A recomendação anterior de remover diretamente `tools/sgdk_wrapper/.agent/agents/` não é suficientemente sustentada. Embora exista tensão com o `ARCHITECTURE.md`, os arquivos ainda são referenciados indiretamente por regras, workflows e pelo vocabulário de várias skills.
* **Localização Exata**:
  * `tools/sgdk_wrapper/.agent/agents/`
  * `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`
  * `tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md`
* **Tipo de Curadoria**: Decisão arquitetural, não limpeza automática.
* **Prioridade**: Alta.
* **Responsável Sugerido**: Arquiteto do Framework.
* **Prazo Estimado**: 1 hora para decisão, mais tempo se houver migração.
* **Status Atual**: Indefinido.
* **Complexidade**: Média.
* **Dependências**: Item 1.1.
* **Análise de Impacto**: Apagar esse diretório agora pode quebrar coerência documental antes de resolver a contradição de origem.

### 2.2 `agents/openai.yaml` não é órfão por evidência atual
* **Descrição Específica**: A análise anterior tratou `agents/openai.yaml` como resquício legado. Isso não se sustenta. O arquivo `skills/README.md` possui uma seção explícita chamada "Política de `openai.yaml`", o que indica que esses YAMLs ainda são parte formal do framework.
* **Localização Exata**:
  * `tools/sgdk_wrapper/.agent/skills/README.md`
  * `tools/sgdk_wrapper/.agent/skills/**/agents/openai.yaml`
* **Tipo de Curadoria**: Documentação de interface / validação de uso real.
* **Prioridade**: Média.
* **Responsável Sugerido**: Dono da integração de IDE/LLM.
* **Prazo Estimado**: 45 minutos.
* **Status Atual**: Válido, mas pouco explicado.
* **Complexidade**: Baixa.
* **Dependências**: Nenhuma.
* **Análise de Impacto**: O risco aqui não é "lixo de repositório". O risco real é faltar explicação sobre quem consome esse metadata e como ele convive com `SKILL.md`.

### 2.3 `lib_case` versus `references/` pede explicação, não migração automática
* **Descrição Específica**: A análise anterior sugeriu consolidar materiais de `references/` dentro de `lib_case/`. Isso também ficou forte demais. A evidência atual mostra que `lib_case/` e `references/` cumprem papéis diferentes: `lib_case/` se apresenta como few-shot reproduzível; `references/` guarda contratos e realidade operacional específicos de uma skill.
* **Localização Exata**:
  * `tools/sgdk_wrapper/.agent/lib_case/README.md`
  * `tools/sgdk_wrapper/.agent/skills/code/sgdk-runtime-coder/references/`
* **Tipo de Curadoria**: Clarificação estrutural.
* **Prioridade**: Baixa.
* **Responsável Sugerido**: Arquiteto do Framework + dono da skill de runtime.
* **Prazo Estimado**: 30 a 60 minutos.
* **Status Atual**: Subdocumentado, não necessariamente errado.
* **Complexidade**: Baixa.
* **Dependências**: Nenhuma.
* **Análise de Impacto**: Hoje o maior problema não é a coexistência dos dois diretórios, e sim a ausência de um texto simples dizendo quando consultar cada um.

---

## 3. Lacunas adicionais que faltaram na análise anterior

### 3.1 O método usado para medir drift do framework foi inadequado
* **Descrição Específica**: A execução de `doc_drift_audit.py` sobre `tools/sgdk_wrapper` como se ele fosse um projeto SGDK comum produz falsos problemas de contexto. O script foi escrito para auditar projetos com `.mddev/project.json`, `doc/11-gdd.md`, `doc/13-spec-cenas.md` e `.agent` local bootstrapada, não para auditar a fonte canônica do framework em si.
* **Localização Exata**:
  * `tools/sgdk_wrapper/.agent/scripts/doc_drift_audit.py`
* **Tipo de Curadoria**: Verificação metodológica / melhoria de auditoria.
* **Prioridade**: Alta.
* **Responsável Sugerido**: Governança + Operação do Wrapper.
* **Prazo Estimado**: 1 a 2 horas.
* **Status Atual**: Gap de ferramental.
* **Complexidade**: Média.
* **Dependências**: Nenhuma.
* **Análise de Impacto**: Sem distinguir "auditoria de projeto" de "auditoria da fonte canônica", fica fácil gerar diagnósticos errados e tomar decisões de curadoria com base em falso positivo.

### 3.2 Falta um auditor específico para a saúde da `.agent` canônica
* **Descrição Específica**: Existe auditoria de drift entre cópia local e fonte canônica, mas não há, pelo menos de forma evidente, um script dedicado a validar a coerência interna da própria fonte canônica: manifesto versus estrutura real, workflows versus skills, contratos faltantes, referências cruzadas quebradas e política de metadata.
* **Localização Exata**:
  * lacuna entre `tools/sgdk_wrapper/.agent/scripts/doc_drift_audit.py`
  * e `tools/sgdk_wrapper/.agent/scripts/project_status.py`
* **Tipo de Curadoria**: Automação de governança.
* **Prioridade**: Média.
* **Responsável Sugerido**: Governança / manutenção do wrapper.
* **Prazo Estimado**: 2 a 4 horas.
* **Status Atual**: Ausente.
* **Complexidade**: Média.
* **Dependências**: Item 1.2.
* **Análise de Impacto**: Enquanto a fonte canônica não tiver um self-check próprio, a curadoria do framework continuará dependendo de leitura manual e ficará mais sujeita a deriva silenciosa.

---

## 4. Matriz Forense de Sustentação

Esta matriz reclassifica o backlog em quatro níveis objetivos:

- `confirmado`: sustentado diretamente por arquivos, texto explícito ou ausência objetiva em estrutura canônica
- `provavel`: fortemente sugerido por múltiplos indícios, mas ainda depende de decisão arquitetural ou validação de intenção
- `hipotese`: plausível, mas ainda sem base suficiente para virar ação concreta
- `nao sustentado`: a leitura anterior não se mantém diante da evidência disponível

| Item | Classificação | Evidência objetiva | Leitura operacional |
|---|---|---|---|
| Contradição entre discurso anti-persona e artefatos ainda agent-centric | `confirmado` | `ARCHITECTURE.md` rejeita personas como eixo do fluxo; `SGDK_GLOBAL.md`, `art-onboarding.md`, `visual-excellence-standards/SKILL.md` e `agents/` ainda usam esse vocabulário | Há inconsistência interna real de linguagem e modelo mental |
| `framework_manifest.json` não representa toda a superfície realmente usada | `confirmado` | O manifesto omite `skills/README.md`, `lib_case/`, `scene-state-architect`, `truth-hierarchy-guard`, `doc-sync-audit`, `status-panel-maintainer`, `art-onboarding.md`, `handoff.md`, `plan.md` e `status.md`, embora esses arquivos existam e sejam canônicos ou operacionalmente relevantes | O bootstrap e a auditoria podem enxergar uma `.agent` parcial como suficiente |
| Contratos explícitos faltando em skills relevantes | `confirmado` | `ARCHITECTURE.md` exige `entrada minima`, `saida minima`, `passa quando` e `handoff`; isso falta em `scene-state-architect`, `truth-hierarchy-guard`, `doc-sync-audit`, `status-panel-maintainer` e `visual-excellence-standards` | O problema é localizado, mas real, e afeta handoff confiável entre IAs |
| `art-onboarding.md` desalinhado ao modelo canônico atual | `confirmado` | O workflow usa `Agente responsavel` e uma narrativa mais antiga, enquanto `production-loop.md` e `aaa-scene-pipeline.md` privilegiam pipeline + skills | Há desalinhamento editorial, ainda que o arquivo continue útil |
| `agents/` exige decisão arquitetural explícita antes de qualquer limpeza | `provavel` | O diretório conflita com o discurso arquitetural, mas ainda conversa com o ecossistema por terminologia e referências indiretas | A tensão é real, mas a ação correta ainda depende de decisão formal |
| `openai.yaml` precisa de status oficial definido | `provavel` | `skills/README.md` define política para `openai.yaml`, mas o framework não explica claramente quem consome esse metadata e como ele convive com `SKILL.md` | Não é lixo óbvio; precisa de enquadramento oficial |
| `doc_drift_audit.py` é inadequado para auditar a fonte canônica da `.agent` | `confirmado` | O script pressupõe projeto SGDK com `.mddev/project.json`, docs de projeto e `.agent` local bootstrapada | Usá-lo contra o wrapper central gera falso positivo metodológico |
| Falta um auditor específico para a saúde da `.agent` canônica | `provavel` | Há auditores para projeto e para drift entre cópia local e fonte canônica, mas não aparece um self-check dedicado da fonte central | A lacuna é forte, embora tecnicamente ainda possa existir fora da área inspecionada |
| `lib_case/` e `references/` precisam ser fundidos | `nao sustentado` | A evidência atual mostra papéis diferentes: `lib_case` como few-shot reproduzível e `references/` como suporte de skill | Não há base suficiente para reorganização estrutural |
| `agents/openai.yaml` são arquivos órfãos/legados | `nao sustentado` | `skills/README.md` possui política formal de `openai.yaml` | O problema é documentação insuficiente, não orfandade comprovada |
| `agents/` pode ser removido imediatamente | `nao sustentado` | Não há prova de que a remoção seja segura hoje; há, sim, prova de contradição conceitual | Excluir agora seria precipitado |
| Todos os workflows auxiliares ausentes do manifesto são obrigatoriamente críticos | `hipotese` | Eles existem e são úteis, mas nem todos estão explicitamente marcados como críticos na arquitetura | Precisam de triagem antes de entrar no `tracked_paths` |

---

## 5. Próximo Passo Mais Seguro

### Ordem recomendada

1. **Curar `framework_manifest.json` e definir oficialmente o status de `agents/` e `openai.yaml`.**
2. **Padronizar os contratos das skills relevantes antes de qualquer limpeza estrutural.**

### Justificativa

- O manifesto é hoje o ponto de controle mais objetivo do bootstrap, do drift e da leitura de saúde da `.agent`.
- Sem uma decisão oficial sobre `agents/` e `openai.yaml`, qualquer limpeza estrutural corre o risco de apagar algo que o próprio framework ainda considera válido.
- Sem contratos consistentes nas skills-chave, o framework continua frágil para orquestração entre IAs mesmo que a árvore de arquivos fique mais "bonita".

### Sequência segura de execução

#### Passo 1 — Curadoria do manifesto

- revisar `tracked_paths` em [framework_manifest.json](file:///F:/Projects/MegaDrive_DEV/tools/sgdk_wrapper/.agent/framework_manifest.json)
- classificar cada item ausente em uma destas classes:
  - `canonico_critico`
  - `canonico_auxiliar`
  - `pedagogico`
  - `experimental`
- declarar explicitamente o status de:
  - `tools/sgdk_wrapper/.agent/agents/`
  - `tools/sgdk_wrapper/.agent/skills/**/agents/openai.yaml`
- só então expandir ou não o manifesto

#### Passo 2 — Contratos das skills

- padronizar primeiro:
  - [scene-state-architect](file:///F:/Projects/MegaDrive_DEV/tools/sgdk_wrapper/.agent/skills/architecture/scene-state-architect/SKILL.md)
  - [truth-hierarchy-guard](file:///F:/Projects/MegaDrive_DEV/tools/sgdk_wrapper/.agent/skills/governance/truth-hierarchy-guard/SKILL.md)
  - [doc-sync-audit](file:///F:/Projects/MegaDrive_DEV/tools/sgdk_wrapper/.agent/skills/governance/doc-sync-audit/SKILL.md)
  - [status-panel-maintainer](file:///F:/Projects/MegaDrive_DEV/tools/sgdk_wrapper/.agent/skills/operation/status-panel-maintainer/SKILL.md)
  - [visual-excellence-standards](file:///F:/Projects/MegaDrive_DEV/tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md)
- usar exatamente os quatro campos canônicos exigidos em [ARCHITECTURE.md](file:///F:/Projects/MegaDrive_DEV/tools/sgdk_wrapper/.agent/ARCHITECTURE.md):
  - `entrada minima`
  - `saida minima`
  - `passa quando`
  - `handoff para proxima etapa`

#### Passo 3 — Só depois decidir limpeza estrutural

- reavaliar `agents/`
- reavaliar `art-onboarding.md`
- decidir se algum workflow auxiliar entra no manifesto
- decidir se vale criar auditor específico da `.agent` canônica

### O que evitar agora

- não remover `agents/` antes da decisão oficial
- não apagar `openai.yaml` antes de confirmar seu consumidor
- não migrar `references/` para `lib_case/` sem prova de ganho operacional
- não usar `doc_drift_audit.py` como prova principal contra a fonte canônica do wrapper
