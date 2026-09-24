# Roteiro QA Passo-a-Passo e Checklist de Evidências para RC

**Versão:** 1.0  
**Data:** 2026-03-17  
**Público:** Testers leigos (sem conhecimento técnico de SGDK)  
**Objetivo:** Validar ROMs antes da promoção a Release Candidate (RC)

---

## 1. PRÉ-REQUISITOS

- [ ] BlastEm instalado para fechar o gate principal; BizHawk pode complementar telemetria e diagnóstico
- [ ] ROM compilada (`out/rom.bin` no diretório do projeto)
- [ ] Se não houver ROM: executar `build.bat` na pasta do projeto

---

## 2. ROTEIRO PASSO-A-PASSO (GENÉRICO)

### 2.1 Inicialização

| Passo | Ação | O que observar | Evidência |
|-------|------|----------------|-----------|
| 1 | Executar `run.bat` (ou abrir ROM no emulador) | Tela de boot/logo aparece | Screenshot: `01_boot.png` |
| 2 | Aguardar 3–5 segundos | Sem travamento, sem tela preta infinita | OK / FALHA |
| 3 | Verificar se há tela de título ou menu | Elementos visíveis e legíveis | Screenshot: `02_title.png` |

### 2.2 Controles básicos

| Passo | Ação | O que observar | Evidência |
|-------|------|----------------|-----------|
| 4 | Pressionar START (ou equivalente) | Jogo inicia ou menu responde | OK / FALHA |
| 5 | Mover D-pad (cima, baixo, esquerda, direita) | Personagem/cursor se move | OK / FALHA |
| 6 | Pressionar A, B, C (conforme mapeamento) | Ação executada (pulo, ataque, etc.) | OK / FALHA |

### 2.3 Gameplay (plataforma / ação)

| Passo | Ação | O que observar | Evidência |
|-------|------|----------------|-----------|
| 7 | Caminhar pela fase | Scroll da câmera acompanha o personagem | OK / FALHA |
| 8 | Pular em plataformas | Colisão com chão e plataformas funciona | OK / FALHA |
| 9 | Atacar inimigo (se aplicável) | Dano/efeito visível | OK / FALHA |
| 10 | Jogar por ~2 minutos | Sem crash, sem glitch grave de sprites | OK / FALHA |

### 2.4 Áudio

| Passo | Ação | O que observar | Evidência |
|-------|------|----------------|-----------|
| 11 | Verificar se há música de fundo | BGM toca (ou silêncio esperado) | OK / FALHA / N/A |
| 12 | Executar ação que gera SFX | Som de efeito é reproduzido | OK / FALHA / N/A |

### 2.5 Encerramento

| Passo | Ação | O que observar | Evidência |
|-------|------|----------------|-----------|
| 13 | Pausar (se houver) | Menu de pausa aparece | OK / FALHA / N/A |
| 14 | Sair do emulador | Fechamento normal, sem erro | OK / FALHA |

---

## 3. ROTEIRO ESPECÍFICO — SHADOW DANCER HAMOOPIG

| Passo | Ação | O que observar | Evidência |
|-------|------|----------------|-----------|
| A | Iniciar ROM | Tela Sega / boot | `sd_01_boot.png` |
| B | Selecionar modo (1P/2P) e stage | Menu responde | `sd_02_menu.png` |
| C | Controlar ninja: andar, pular, shuriken | Movimento fluido, shuriken lançado | OK / FALHA |
| D | Subir/descer entre planos (escadas, rampas) | Troca de plano funciona | OK / FALHA |
| E | Colidir com inimigo | Resposta de dano ou evasão | OK / FALHA |
| F | Usar bomba (se disponível) | Efeito visual e sonoro | OK / FALHA |
| G | Jogar até fim da fase ou 3 min | Sem crash | OK / FALHA |

---

## 4. ROTEIRO ESPECÍFICO — PEQUENO PRÍNCIPE

| Passo | Ação | O que observar | Evidência |
|-------|------|----------------|-----------|
| A | Iniciar ROM | Boot e tela de título | `pp_01_boot.png` |
| B | Iniciar jogo | Transição para planeta (B-612, Rei, etc.) | OK / FALHA |
| C | Andar pelo planeta | Scroll, tiles, efeitos visuais | OK / FALHA |
| D | Interagir com NPC (diálogo) | Janela de diálogo aparece | OK / FALHA |
| E | Viajar para próximo planeta | Transição de viagem | OK / FALHA |
| F | Abrir Codex (se desbloqueado) | Tela de codex exibida | OK / FALHA |

---

## 5. CHECKLIST DE EVIDÊNCIAS PARA PROMOÇÃO RC

Preencher antes de aprovar um build como Release Candidate.

### 5.1 Build

| Item | Status | Notas |
|------|--------|-------|
| `build.bat` executa sem erro | ☐ OK ☐ FALHA | |
| ROM gerada em `out/rom.bin` | ☐ OK ☐ FALHA | Tamanho: _____ KB |
| `validation_report.json` sem erros críticos | ☐ OK ☐ FALHA ☐ N/A | |

### 5.2 Execução

| Item | Status | Notas |
|------|--------|-------|
| ROM inicia no emulador com evidência rastreável | ☐ OK ☐ FALHA | BlastEm fecha gate |
| Sem crash em 5 min de gameplay | ☐ OK ☐ FALHA | |
| Controles respondem corretamente | ☐ OK ☐ FALHA | |
| Colisão e física coerentes | ☐ OK ☐ FALHA | |
| Áudio (BGM/SFX) conforme esperado | ☐ OK ☐ FALHA ☐ N/A | |

### 5.3 Artefatos a coletar

| Artefato | Obrigatório | Descrição |
|----------|-------------|-----------|
| Screenshot da tela de boot | Sim | `01_boot.png` |
| Screenshot da tela de título/menu | Sim | `02_title.png` |
| Screenshot de gameplay (1–2 cenas) | Sim | `03_gameplay.png`, `04_gameplay2.png` |
| `validation_report.json` | Se disponível | Em `out/logs/` |
| `runtime_metrics.json` | Recomendado | Sustenta performance e budget percebido |
| `emulator_session.json` | Recomendado | Registra boot, emulador observado e eixos QA |
| Log de build (em caso de falha) | Se aplicável | `out/logs/build_debug.log` |

### 5.4 Critérios de bloqueio (NÃO promover a RC se)

- [ ] ROM não inicia ou trava na boot
- [ ] Crash recorrente em menos de 2 min
- [ ] Controles não respondem
- [ ] Colisão quebrada (personagem atravessa paredes)
- [ ] Glitch grave de sprites (flickering excessivo, sprites duplicados)
- [ ] Build falha ou ROM não é gerada

---

## 6. TEMPLATE DE RELATÓRIO QA

```
Projeto: ___________________________
Build: _____________________________ (data/hash se disponível)
Emulador: __________________________
Tester: _____________________________
Data: _______________________________

Resumo: ☐ APROVADO para RC  ☐ REPROVADO

Evidências anexadas:
- [ ] 01_boot.png
- [ ] 02_title.png
- [ ] 03_gameplay.png
- [ ] validation_report.json (se houver)

Problemas encontrados:
1. _________________________________
2. _________________________________

Observações:
_____________________________________
_____________________________________
```

---

## 7. REFERÊNCIAS

- **Build:** `build.bat` (delega a `tools/sgdk_wrapper/build.bat`)
- **Execução:** `run.bat` (abre ROM no emulador detectado)
- **Validação:** `tools/sgdk_wrapper/validate_resources.ps1`
- **Memory Bank:** `doc/10-memory-bank.md` no projeto ou `doc/06_AI_MEMORY_BANK.md` no workspace
