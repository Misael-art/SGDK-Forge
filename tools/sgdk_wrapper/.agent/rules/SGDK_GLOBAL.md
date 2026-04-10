---
trigger: always_on
---

# SGDK Global Rules

Estas regras sao sempre ativas para qualquer projeto `MegaDrive_DEV` que use esta `.agent`.

## 1. Fonte de verdade

- Leia primeiro `doc/10-memory-bank.md`, `doc/11-gdd.md`, `doc/13-spec-cenas.md`, `doc/00-diretrizes-agente.md` e `doc/00-governance/08_maximalist_directive.md` quando existirem.
- Trate `.mddev/project.json` como manifesto estrutural, nao como substituto dos docs canonicos.
- Nunca trate README isolado como prova suficiente de implementacao ou validacao.
- Todos OS AGENTES DEVEM OBEDECER O **MASTER SYSTEM DIRECTOR** e aplicar a **Filosofia Maximalista**, priorizando excelencia visual e impulsionando o hardware com responsabilidade.

## 2. Restricoes nao negociaveis

- Nao usar `float` ou `double` para gameplay SGDK.
- Nao usar `malloc` ou `free` no loop de jogo.
- Nao inventar APIs do SGDK.
- Nao duplicar logica de build em scripts de projeto.
- Nao alterar budgets sem evidencia e autorizacao quando o projeto exigir.
- Nao sobrescrever `.agent` local se ela ja existir.

### 2.1 Execucao automatica da proibicao de heap

- A validacao central varre `src/` em busca de `malloc/calloc/realloc/free`.
- Para bloquear merges com uso de heap, ativar `SGDK_ENFORCE_NO_HEAP=1` no ambiente de validacao.
- Mesmo em modo permissivo (sem a variavel), ocorrencias sao reportadas como `WARNING` e devem ser justificadas.

## 3. Governanca e status

- Diferencie sempre `documentado`, `implementado`, `buildado`, `testado_em_emulador`, `validado_budget`, `placeholder`, `parcial` e `futuro_arquitetural`.
- Nao use termos como `validado`, `pronto` ou `completo` sem evidencia verificavel.
- Se encontrar conflito entre docs e codigo, sinalize a divergencia explicitamente.

## 3.1 Armadilhas SGDK que devem ser assumidas como suspeitas

- `VDP_drawTextBGFill()` no SGDK 2.11 nao trunca a string com seguranca. Se `strlen(str) > len`, a funcao pode corromper a stack e derrubar o 68000 alguns frames depois.
- Para overlays, HUDs e ferramentas de benchmark, nunca chame `VDP_drawTextBGFill()` com largura menor que o texto real. Use um wrapper local que trunque primeiro e so depois complete com espacos.
- Sintoma classico dessa corrupcao: BlastEm acusa `M68K attempted to execute code at unmapped or I/O address ...` sem apontar o overlay como origem imediata.

## 4. Operacao do wrapper

- Toda logica compartilhada deve morar em `tools/sgdk_wrapper/`.
- Melhorias genericas vao para o wrapper central, nao para wrappers locais do projeto.
- O bootstrap da `.agent` e feito apenas quando ausente.
- Se a `.agent` local existir sem `framework_manifest.json` ou com sinais de drift, trate o projeto como `bootstrap_degradado` ate auditoria explicita.
- O wrapper nao deve fingir saude canonica quando so consegue provar existencia de copia local.

## 5. Handoff

- Ao encerrar uma sessao relevante, atualize o documento de estado operacional do projeto se ele existir.
- Se a implementacao mudou e a documentacao ficou atras, nao silencie essa diferenca.
- Handoff de validacao em emulador exige sincronizar `emulator_session.json`, `validation_report.json` e memoria operacional na mesma narrativa factual.

## 6. Maximalismo Tecnico Obrigatorio

Nao basta adicionar FX isolado. O "Treasure Mindset" exige combinacao. E OBRIGATORIO:
- Combinar FX (ver `doc/05_technical/80_fx_combination_matrix.md`).
- Variar FX no tempo com uso obrigatorio de Timeline de cena e "pico".
- Reagir ao gameplay e otimizar para caber (multiplexing, blinking, streaming).
Se uma cena usa tecnicas isoladas estaticas e sem evolucao temporal, ela e considerada INCOMPLETA.

## 7. Experimental Override (A Excecao AAA)

Embora as regras de VDP e Budget sejam lei, e encorajado recorrer ao `doc/00-governance/11_experimental_override.md`. E permitida UMA quebra premeditada das regras ou limites seguros por cena (geralmente no Signature Moment) para alcancar efeitos tidos como impossiveis no Mega Drive, DESDE QUE justificado e que o motor permaneca firmemente em 60fps constantes sem latencia de input.

## 8. Inteligencia Visual e Travas de Arte (CRITICO)

A credibilidade do espetaculo vem da consistencia visual. Para gerar ou instruir criacao de qualquer asset visual de uma cena, o pipeline DEVE obrigatoriamente cumprir a "Visual Quality Bar" (`doc/03_art/00_visual_quality_bar.md`) ativando 3 travas inviolaveis:
- **Trava 1:** Sem 3 referencias visuais reais explicitas justificando a heranca -> INVALIDO.
- **Trava 2:** Sem Visual Breakdown pre-definido (paleta, material, iluminacao e profundidade) -> INVALIDO.
- **Trava 3:** Sem a aprovacao do `art-director` para validar shading/volume -> INVALIDO.
- Todo feedback corretivo de arte deve passar antes por `doc/03_art/02_visual_feedback_bank.md` e pela skill `visual-excellence-standards`.

## 9. EFEITO COLATERAL DE FX (OBRIGATORIO)

Nenhum FX age isoladamente. Todo FX principal deve gerar pelo menos 1 efeito secundario fisicamente real no ambiente:
- Chuva deve gerar reflexo no chao.
- Fogo deve espalhar fumaça ou glow na paleta adjacente.
- Impacto tem que gerar camera shake, poeira ou alteracao de estado temporal.

## 10. GAMEPLAY VISUAL LINK

Nenhum efeito pode existir sem ligacao direta com o gameplay ou o pulso narrativo. O `Scene Architect` DEVE se fazer a seguinte pergunta obrigatoria:
"Como esse efeito ajuda o jogador a sentir a mecanica de jogo?"
Se nao ajuda ou e puramente "de enfeite" sem interagir, nao gaste VRAM. Repense o fluxo.

## 11. SISTEMA DISCRETO DE CUTSCENES ("FAKE CINEMA")

A partir deste trancamento, **"Cutscene nao e Gameplay"**. Se uma animacao narrativa for requisitada, o Pipeline DEVE operar sob as regras de *Economia Inteligente* e `Fake Cinema`. E obrigatório que o projeto:
- Importe o estrito arsenal narrativo ditado pelo documento `/doc/05_technical/90_cutscene_system.md` (Usando Pans, Holds e Som).
- Cumpra intencionalmente 3 regras cinematicas do `doc/01_game_design/30_cinematic_language.md`.
- Entregue a cena obedecendo religiosamente ao "Template de Cutscene", formalizando a prioridade *Imagem Bem Feita + Truques Visuais > Animacao Complexa*. A pergunta base passa a ser: *"Como conto isso com o minímo de movimento e maximo de impacto?"*

## 12. O SGDK MASTER BUILD & VISUAL VALIDATION LOOP

O executor/agente perde o direito de declarar sucesso baseado unicamente na "teoria ou codigo C limpo". Todos os processos agora respondem primeiramente ao documento `/doc/00-governance/12_master_build_validation_loop.md`.
**A Regra Final de Ferro:** Intencao nao e validacao. Funcao na tela sim. Se o pipeline falhar em compilar a ROM final, ou se a ROM rodando no emulador nao comprovar perfeitamente os 60FPS coerentes com a integracao das rules visuais AAA e os FX interagindo, a tarefa nao ta concluida.
A operacao entra em "Bloqueio de Progresso" e deve registrar o defeito imediatamente no artefato canonico de memoria operacional do contexto atual: `doc/10-memory-bank.md` para projetos SGDK e `doc/06_AI_MEMORY_BANK.md` para governanca do workspace. Nenhum agente deve exigir ou inventar `AI_MEMORY.md` fora desse fluxo canonico. A iteracao segue em `Cycle-rebuild` ate o sucesso real e empirico. "Se não foi visto rodando, não existe."

## 13. METRICAS DE RUNTIME E QUALIDADE PERCEPTIVA (OBRIGATORIO PARA AAA)

Para qualquer cena que queira alegar nivel AAA, nao basta "rodar". E obrigatorio declarar, quando houver instrumentacao ou checklist de QA:
- `frame_stability`: estabilidade de frame/jitter
- `sprite_pressure`: pressao de sprite/scanline
- `fx_load`: carga simultanea de FX
- `perceptual_quality`: julgamento perceptivo objetivo da cena

Se esses campos estiverem `nao_medido`, a cena pode estar funcional, mas nao deve ser vendida como validacao AAA completa.

Quando o wrapper central rodar com `SGDK_RUNTIME_CAPTURE=1`, o artefato `out/logs/runtime_metrics.json` passa a ser evidencia obrigatoria do estado observado em emulador e deve ser refletido em `out/logs/validation_report.json`, que se torna a fonte primaria do status panel junto com as metricas de runtime.

## 14. CRITERIO UNICO DE QA E EVIDENCIA EM EMULADOR

- **BlastEm** e o emulador de referencia obrigatorio para `boot_emulador` e gate de entrega.
- **BizHawk** com Genesis Plus GX e aceito como evidencia complementar para telemetria, frame advance e captura de `runtime_metrics.json`, mas nao substitui o gate obrigatorio em BlastEm.
- **Exodus** e aceito apenas para diagnostico de edge cases.
- **Gens KMod** e aceito somente para analise exploratoria de VRAM/registradores, nunca como evidencia de aprovacao.
- `testado_em_emulador` so pode ser promovido a verdadeiro quando houver evidencia rastreavel em `validation_report.json` e/ou artefato de sessao de emulador, sempre respeitando BlastEm como referencia de entrega.

### 14.1 Vinculo obrigatorio com a ROM validada

- Toda evidencia de emulador deve estar ligada a uma ROM identificavel por caminho e, quando possivel, hash, tamanho e timestamp.
- Abrir o emulador sem provar qual ROM estava em execucao nao fecha gate.
- Se a ROM for rebuildada depois da captura, a evidencia anterior vira obsoleta e os eixos de QA devem ser rebaixados ate nova validacao.

### 14.2 Ciclo de vida da sessao de emulador

- `emulator_session.json` nao pode parar em `launch_status=started` quando a sessao de QA foi usada como evidencia.
- O ciclo esperado e `started -> captured -> closed`, ou equivalente mais detalhado definido pelo wrapper.
- `boot_emulador` nao deve ser marcado como `ok` sem uma sessao ao menos capturada.
- `gameplay_basico` nao deve ser marcado como funcional se a sessao nao provar entrada, leitura de estado ou resposta visual coerente.

### 14.3 Captura dedicada e nao ambigua

- Screenshot para gate deve ser captura dedicada da janela do BlastEm ou screenshot interno do proprio emulador.
- Captura global da area de trabalho, IDE ou monitor errado nao conta como evidencia valida.
- Quando houver mais de uma janela candidata, o processo de QA deve verificar titulo da janela, PID ou outro identificador confiavel antes de salvar a evidencia.
- O framework deve preservar os arquivos de captura usados no gate em `source_artifacts` do `validation_report.json`.

### 14.3.1 Regra canonica para evidencia de VDP

- Quando o projeto ou laboratorio emitir um bloco de evidencia visual em SRAM auditavel, o gate pode ser fechado com o trio: `benchmark_visual.png` (ou screenshot equivalente da janela do BlastEm) + `save.sram` + `visual_vdp_dump.bin`.
- Nessa configuracao, o quicksave nativo do BlastEm passa a ser **evidencia redundante opcional**, nao requisito bloqueante.
- O `visual_vdp_dump.bin` deve ser derivado de um bloco assinado e limitado ao frame/estado relevante, nunca de inferencia textual ou de memoria inventada pelo agente.
- Se o projeto nao tiver emissao canônica de dump visual em SRAM, a regra acima nao se aplica; nesse caso o gate continua dependendo da evidencia padrao registrada pelo wrapper e pelo `emulator_session.json`.

### 14.4 Perfil minimo observacional quando nao houver telemetria forte

- Na ausencia de `runtime_metrics.json`, ainda e obrigatorio registrar um perfil observacional honesto com `frame_stability`, `sprite_pressure`, `fx_load` e `perceptual_quality`.
- Campos observacionais devem usar linguagem explicita como `observado`, `estimado` ou `nao_medido`, nunca fingir precisionismo inexistente.
- Silencio intencional tambem e evidência valida de audio, desde que sustentado pela ausencia rastreavel de assets e rotinas sonoras no slice.
