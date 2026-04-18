# Backlog de Curadoria: METAL SLUG URBAN SUNSET

**Data da Análise:** 17 de Abril de 2026  
**Status do Projeto:** Funcional (Build OK), Viewer de Cenas Operacional.

Este documento cataloga de forma estruturada todos os pontos, seções, conteúdos e elementos do projeto que ainda necessitam de curadoria, seja para atingir o status "Elite" ou para manter a integridade operacional e documental do workspace.

---

## 1. Arte & Estética (Assets Visuais)

### 1.1 Revisão de Dithering e Textura (MISSING_DITHERING_FOR_MATERIAL)
* **Descrição Específica**: Diversos assets de cenários (BG_A) estão com baixa densidade de dithering e detalhamento por tile. O juiz estético do SGDK Wrapper aponta que não atingem o patamar mínimo esperado para "leitura de material" em um asset "Elite".
* **Localização Exata**:
  * `res/gfx/urban_default_bg_a.png`
  * `res/gfx/urban_linefirst_balanced_bg_a.png`
  * `res/gfx/urban_linefirst_cohesive_bg_a.png`
  * `res/gfx/mission1_flat_strict15_bg_a.png`
  * `res/gfx/mission1_flat_snap700_bg_a.png`
  * `res/gfx/mission1_skylift_bg_a.png`
* **Tipo de Curadoria**: Refinamento visual (adição controlada de texturas e dithering direcional para simular materialidade sem gerar ruído).
* **Prioridade**: Baixa (Não bloqueia o build atual, classificado como Warning).
* **Responsável Sugerido**: Agente de Arte (`art-translation-to-vdp`).
* **Prazo Estimado**: 2 a 3 horas por asset.
* **Status Atual**: Pendente.
* **Complexidade**: Alta.
* **Dependências**: Nenhuma técnica, mas requer aprovação de direção de arte para não quebrar a leitura da cena.
* **Análise de Impacto**: A ausência dessa curadoria mantém o projeto com um aspecto mais "flat" ou genérico. Em portões futuros mais rigorosos, a falta de detalhe pode voltar a impedir a chancela "Elite" do projeto.

### 1.2 Redução de Ruído Visual (NOISY_TEXTURE)
* **Descrição Específica**: O asset do céu da variante "linefirst_balanced" recebeu um gradiente recentemente, mas a matriz de Bayer gerou um padrão que o pipeline interpreta como ruído (`NOISY_TEXTURE`), e não como uma transição material suave.
* **Localização Exata**: `res/gfx/urban_linefirst_balanced_bg_b.png`
* **Tipo de Curadoria**: Refinamento visual / Padronização.
* **Prioridade**: Média (Afeta diretamente a qualidade do rework recém-implementado).
* **Responsável Sugerido**: Agente de Arte.
* **Prazo Estimado**: 1 hora.
* **Status Atual**: Pendente.
* **Complexidade**: Média.
* **Dependências**: Nenhuma.
* **Análise de Impacto**: Pode distrair o jogador e comprometer a separação clara entre o BG_A (cenário) e o BG_B (céu), gerando um visual poluído ("dirty look") na tela do CRT ou emuladores.

---

## 2. Operação & Validação

### 2.1 Renovação da Evidência Canônica de Emulador
* **Descrição Específica**: O build recente alterou o hash da ROM, o que invalidou a evidência rastreada pelo pipeline (`rom_identity_mismatch`). O projeto atual não possui prova canônica atualizada de que roda a 60fps constantes no BlastEm.
* **Localização Exata**: Logs de build / Ferramenta de Captura (`tools/sgdk_wrapper/run_visual_capture.ps1`).
* **Tipo de Curadoria**: Verificação Factual / Operacional.
* **Prioridade**: Crítica.
* **Responsável Sugerido**: Agente de Operação (`sgdk-build-wrapper-operator`).
* **Prazo Estimado**: 15 minutos.
* **Status Atual**: Bloqueado / Obsoleto.
* **Complexidade**: Baixa.
* **Dependências**: Nenhuma (o build atual é bem-sucedido e estável).
* **Análise de Impacto**: Fere a Regra de Ferro do workspace: *"Se não foi visto rodando no emulador, não existe"*. Sem essa curadoria, o projeto fica tecnicamente em um estado "não entregue" do ponto de vista do framework de QA.

---

## 3. Documentação & Memória

### 3.1 Atualização do Memory Bank e Changelog
* **Descrição Específica**: O arquivo de memória operacional do projeto e o changelog canônico precisam refletir as resoluções recentes de assets (queda do blocker `visual_gate_blocked`) e o novo status do projeto. O pipeline reporta: `Changelog canonico desatualizado: assets_desatualizados=2`.
* **Localização Exata**: `doc/10-memory-bank.md` e logs de auditoria do workspace.
* **Tipo de Curadoria**: Atualização de informações.
* **Prioridade**: Alta.
* **Responsável Sugerido**: Agente de Planejamento/Arquitetura.
* **Prazo Estimado**: 30 minutos.
* **Status Atual**: Desatualizado.
* **Complexidade**: Baixa.
* **Dependências**: Evidência Canônica (Item 2.1) deve ser resolvida em conjunto para fechar o ciclo.
* **Análise de Impacto**: O histórico do projeto perde rastreabilidade. Futuros agentes autônomos podem atuar com contexto incorreto, acreditando que o projeto ainda possui blockers ou tentando refazer trabalho já validado.

---

## 4. Código Fonte (Revisão Técnica)

### 4.1 Limpeza e Padronização do Viewer (`main.c`)
* **Descrição Específica**: O código do visualizador implementado recentemente (`main.c`) utiliza alguns valores engessados (magic numbers) para offsets de texto, índices de cor de fundo (ex: `VDP_setBackgroundColor(1)`) e lógica manual de preenchimento (`fillRow`).
* **Localização Exata**: `src/main.c` (especialmente no bloco da função `loadCurrentSceneVariant` a partir da linha 333).
* **Tipo de Curadoria**: Revisão técnica de código / Refatoração.
* **Prioridade**: Baixa.
* **Responsável Sugerido**: Agente de Código (`sgdk-runtime-coder`).
* **Prazo Estimado**: 1 a 2 horas.
* **Status Atual**: Funcional, não bloqueante.
* **Complexidade**: Média.
* **Dependências**: Nenhuma.
* **Análise de Impacto**: Acúmulo de débito técnico. Pode dificultar a legibilidade, inserção de novas cenas no viewer, ou expansão da arquitetura caso a equipe deseje reintroduzir lógica de sprites futuramente.
