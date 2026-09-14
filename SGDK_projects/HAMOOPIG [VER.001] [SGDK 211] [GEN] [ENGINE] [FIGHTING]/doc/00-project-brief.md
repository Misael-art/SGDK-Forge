# 00 - Project Brief - HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

Este documento e o contrato curto de intencao. Ele existe para impedir que o agente comece arte, codigo ou curadoria sem entender o tipo de trabalho.

## Contexto

- Tipo de trabalho: technical_demo (porta direta de engine externa)
- Teto de promessa: prototype
- Frase do projeto: manter a engine de luta HAMOOPIG compilando e rodando em SGDK 2.11 no pipeline canonico deste workspace, preservada e com creditos.
- Publico alvo: mantenedores do workspace e estudo de engine de luta no Mega Drive
- Plataforma alvo: Mega Drive / SGDK 2.11

## Origem e creditos

- HAMOOPIG e a implementacao da engine HAMOOPI (by GameDevBoss / Daniel Moura, 2015-2022) para Mega Drive, portada para SGDK por humbertodias (`github.com/humbertodias/sgdk-HAMOOPIG`).
- **Creditos obrigatorios a GameDevBoss (Daniel Moura)** em qualquer uso ou redistribuicao (exigencia do cabecalho do codigo).
- Origem local preservada: `SGDK_Engines/HAMOOPIG-SGDK` (nao modificada por esta porta).

## Escopo desta porta

Dentro do escopo:
- Materializar o upstream na estrutura canonica (modelo) com src/inc/res completos.
- Garantir build pelo wrapper canonico (`tools/sgdk_wrapper/build.sh`, SDK `sdk/sgdk-2.11`).
- Boot no BlastEm com evidencia.
- Placeholders documentados para o que o upstream nao traz (PCM de audio).

Fora do escopo (nao-metas):
- Reautoral arte, audio ou mecânica da engine (completar com material GPL do proprio HAMOOPI e permitido).
- Promover para jogo AAA ou cumprir a barra viva de cena AAA.
- Validadar budgets VRAM/DMA da engine (migracao fiel, nao re-engenharia).

## Pilares

1. Preservacao: codigo e assets upstream byte-fieis, sem reescrita criativa.
2. Honestidade de status: placeholder e prototype declarados onde verdadeiros.
3. Pipeline canonico: nenhuma logica de build no projeto; wrapper centraliza.

## Sucesso

ROM gerada em `out/rom.bin` + boot registrado no BlastEm; memory bank e changelog refletindo exatamente o estado real.
