# 00 - Project Brief - TAIKETSU ULTRA HERO GENESIS [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

Este documento e o contrato curto de intencao. Ele existe para impedir que o agente comece arte, codigo ou curadoria sem entender o tipo de trabalho.

## Contexto

- Tipo de trabalho: technical_demo (porta direta de engine externa)
- Teto de promessa: prototype
- Frase do projeto: manter a engine de luta TaiketsuUltraHeroGenesis compilando e rodando em SGDK 2.11 no pipeline canonico deste workspace, preservada sob GPL-3.0 e com creditos.
- Publico alvo: mantenedores do workspace e estudo de engine de luta no Mega Drive
- Plataforma alvo: Mega Drive / SGDK 2.11

## Origem e creditos

- TaiketsuUltraHeroGenesis e fork da engine HAMOOPIG (by GameDevBoss / Daniel Moura, 2015-2022), upstream `github.com/guilhermesousa03/TaiketsuUltraHeroGenesis`, licenca GPL-3.0.
- **Creditos obrigatorios a GameDevBoss (Daniel Moura)** em qualquer uso ou redistribuicao (exigencia do cabecalho do codigo).
- Origem local preservada: `SGDK_Engines/TaiketsuUltraHeroGenesis` (nao modificada por esta porta).
- Nota: o workspace ja carrega o derivado curado `TAIKETSU ULTRA REBIRTH [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]`; este projeto e a porta direta da engine, distinto por tag [ENGINE].

## Escopo desta porta

Dentro do escopo:
- Materializar o upstream na estrutura canonica (modelo) com src/res completos.
- Garantir build pelo wrapper canonico (SDK `sdk/sgdk-2.11`).
- Boot no BlastEm com evidencia; corrigir apenas o que impede o boot (fix minimo documentado).
- Placeholders documentados para o que o upstream nao traz (PCM de audio, 28 sprites fora de sincronia).

Fora do escopo (nao-metas):
- Reautoral arte, audio ou mecanica da engine.
- Promover para jogo AAA ou cumprir a barra viva de cena AAA.
- Portar o header de ROM upstream (rom_head segue o do template).

## Pilares

1. Preservacao: codigo upstream byte-fiel, exceto fixes minimos documentados no memory bank/changelog.
2. Honestidade de status: placeholder e prototype declarados onde verdadeiros.
3. Pipeline canonico: nenhuma logica de build no projeto; wrapper centraliza.

## Sucesso

ROM gerada em `out/rom.bin` + boot registrado no BlastEm (atingido em 2026-09-10); memory bank e changelog refletindo exatamente o estado real.
