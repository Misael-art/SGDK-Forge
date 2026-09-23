# SGDK MASTER BUILD & VISUAL VALIDATION LOOP

O Sistema de Agentes NÃO ESTÁ AUTORIZADO a considerar qualquer implementação concluída ou válida até que ela compile, rode em emulador e seja visualmente aprovada na prática. Intenção não é validação. Código limpo não é validação. **"Se não foi visto rodando, não existe."**

---

## 🔁 CICLO OBRIGATÓRIO (NÃO PODE SER PULADO)

### PASSO 1 — BUILD REAL (SGDK)
- Compilar o projeto usando a toolchain oficial.
- Se houver erros (compilação, assets ou LTO), o agente deve buscar a correção ou reportar o erro ambiental até que a ROM (`.bin`) seja gerada 100% livre de falhas.
- **PROIBIDO:** Assumir que o código funciona e pular o log de sucesso de compilação.

### PASSO 2 — EXECUÇÃO EM EMULADOR
- Executar a ROM resultante com evidência rastreável de emulador. BlastEm fecha o gate principal; BizHawk pode complementar telemetria e captura.
- A validação exige provas: Screenshot da cena base e captura observável da funcionalidade e do impacto das mecânicas.
- Quando o projeto emitir um bloco visual canônico em SRAM, a prova mínima aceita passa a ser: screenshot dedicado do BlastEm + `save.sram` + `visual_vdp_dump.bin`.
- Nessa modalidade, o quicksave nativo do BlastEm é redundância opcional e não pode bloquear sozinho o gate se o trio acima estiver íntegro e ligado à ROM validada.
- Sempre que possível, registrar também `out/logs/emulator_session.json`, `out/logs/runtime_metrics.json` e `out/logs/validation_report.json`.
- **✋ LIMITAÇÃO DE AGENTE (Pipeline Honesto):** Como a IA nativa via terminal geralmente não possui os "olhos" diretos num emulador gráfico, caso ela não tenha ferramentas de integração CI que mastiguem pixels/GIFs, ela é OBRIGADA a PARAR e demandar a prova do usuário: *"Humano, instancie o emulador e julgue estes critérios abaixo. Me devolva o resultado fotográfico/perceptual."*

### PASSO 3 — BREAKDOWN VISUAL (PROVA)
Decompor a evidência gráfica:
- Paleta observada batendo com a desenhada?
- Sprites ativos estouram o limite de scanline sem flickering?
- As camadas (Plano A, B, Sprites) mantêm profundidade?

### PASSO 4 — PROVA DE COERÊNCIA & INTEGRAÇÃO
A prova real de que o `Visual Cohesion System` foi implementado não é o `main.c`, é o jogo na tela:
- O FX de chuva, fogo ou vento AFETA o horizonte e o player?
- A iluminação global altera os blocos físicos simultaneamente ao acontecer na nuvem?
- Efeito sem interação detectada no emulador → **INVALIDAR.**

### PASSO 5 — PERFORMANCE CAPTURE
- O Counter do emulador deve registrar 60 frames por segundo estáveis (60Hz NTSC).
- `runtime_metrics.json` deve capturar amostras válidas e sustentar o eixo de performance.
- Qualquer detecção de *lag frame* devido a processamento exagerado de colisões ou DMA excedente durante o `Signature Moment` → **INVALIDAR.**

### PASSO 6 — AVALIAÇÃO AAA
A chancela final de Quality Assurance. Responda: *"Isso parece tecnicamente um jogo top-tier Sega/Treasure de 1994?"*

---

# 🚫 BLOQUEIO DE PROGRESSO

Se QUALQUER passo acima for reprovado no ambiente real, o sistema aciona o Loop Penal:
1. É PROIBIDO marcar a tarefa como resolvida.
2. O agente deve registrar o estado imediatamente no artefato canônico de memória operacional: `doc/10-memory-bank.md` no projeto ou `doc/06_AI_MEMORY_BANK.md` no workspace. Formato exigido:

```md
## Falha: [nome da cena/versão]
### Motivo
- [Ex: Faltou splash na chuva / Queda pra 55fps / Erro de compilação LTO]
### Ação necessária
- [Ex: Reduzir tamanho dos sprites / Fix no Palette DMA]
### Status
REPROVADO
```

### 🔁 LOOP DE CORREÇÃO
Mudar o código, reconstruir as ferramentas visuais, refazer o Build e submeter novamente. Só se transborda desse ciclo fechado quando as `CONDIÇÕES DE SUCESSO` (Roda, Impacta, É Coeso, Integra Hardware e Bate 60fps) marcarem OK.
