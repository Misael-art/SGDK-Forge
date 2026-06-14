# 00 - Project Brief - [ESTUDO]_mugen_sff_showdown_v1

Este documento e o contrato curto de intencao. Ele existe para impedir que o agente comece arte, codigo ou curadoria sem entender o tipo de trabalho.

## Contexto

- Tipo de trabalho: exercise
- Teto de promessa: exercise
- Frase do projeto: estudo controlado para avaliar conversao MUGEN SFF/DEF em viewer SGDK sem perder composicao, camera e vitalidade cromatica.
- Publico alvo: agentes SGDK Forge em treinamento e curadoria humana do pipeline visual.
- Plataforma alvo: Mega Drive / SGDK 2.11

## Pilares

- Pilar 1: preservar a logica de camera horizontal e vertical do stage, incluindo bounds, zoffset e verticalfollow.
- Pilar 2: preservar a separacao de planos de BG0/BG1/BG2/BG3 em vez de achatar deltas como uma imagem unica.
- Pilar 3: manter cores vibrantes e papeis de material, com paleta curada por plano/material e nao por nearest-color massivo.
- Pilar 4: tratar a ROM como prova de laboratorio ate existir dump VDP, budget validado e visual delivery gate aprovado.

## Escopo

### Dentro

- Extrair e reconstruir fixture SFF/DEF.
- Auditar composicao, camera, paleta, tilemap, budget e evidencia BlastEm.
- Registrar falhas e regras de prevencao para o agente.

### Fora

- Promover o stage como asset autoral de jogo final.
- Declarar `ready_for_aaa`.
- Corrigir runtime ou gerar nova ROM sem pedido explicito.

## Primeiro Resultado Valido

- Entrega minima: parecer curatorial com evidencias, blockers e contrato de rework.
- Evidencia minima: comparacao entre reconstrucoes, bins/export, captura BlastEm e relatorios de conversao.
- Criterio de sucesso: o estudo identifica por que a cena ficou achatada/opaca e impede que esse resultado seja tratado como sucesso visual.

## Riscos Principais

- Risco: converter um stage com deltas de parallax em um unico plano BG_A.
  Mitigacao: exigir `parallax_layer_contract`, `camera_motion_contract` e rota multi-plano ou `compare_flat` honestamente bloqueada.
- Risco: reduzir paleta por bandas e nearest-color ate perder vibracao.
  Mitigacao: exigir `palette_vitality_check` com comparacao source/export/BlastEm.
- Risco: usar o nome de benchmarks ou IP como autorizacao visual.
  Mitigacao: tratar referencias como eixo tecnico de qualidade, nunca como fonte autoral.

## Decisao de Abertura

- Data: 2026-06-13
- Decisor humano: solicitacao de curadoria do estudo
- Decisao: exercise
- Motivo: o projeto vive em `_agent_training`, declara `lab_not_delivery=true` e existe para treinar o agente em conversao visual, nao para entregar jogo.
