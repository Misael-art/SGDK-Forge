# Plano priorizado de robustecimento — proposta

O objetivo é tornar perdas e custos verificáveis antes de expandir o jogo. A curadoria não implementa estas mudanças. Cada implementação exige atualizar a memória do projeto, testes e evidência proporcional; alterar skills/regras requer aprovação humana explícita do patch.

## Três quick wins para decisão imediata

|Ordem|Tipo/escopo|Impacto÷esforço e owner|Aceite|
|---|---|---|---|
|Q1|Ferramenta/contrato: sanear proveniência e falso positivo lógico (G01/G02)|Alto: elimina bloqueio real e ruído em2–4dias; guardian+reviewer|Schema válido e registros por símbolo; fixture lógico passa, pixel procedural real continua bloqueado; permissão não verificada continua declarada|
|Q2|Teste/rota: SuperPause e capacidades (G09/G04)|Alto: evita regressões e conversão truncada em2,5–4dias; runtime-coder|Posição/facing/timing verificados em C; fronteiras255/256,160/161,32/33 ebitmap8words rejeitam overflow sem alterar corpus válido|
|Q3|Rota/índice: intake MUGEN para owners existentes (G12 parcial)|Alto: reduz deriva em1–2dias; learning-loop+doc-sync|Um índice com lição/fonte/commit/hash/owner/status; README e paths reconciliados; catálogo não duplica status nem promove candidato|

Estas são três unidades de decisão, não justificativa para adiar P0 de performance. Q1/Q2 podem ser feitos antes de nova arte; G03 é primeira frente da onda seguinte. Ordem global considera dependência: não medir uma ROM cujos dados estão mudando sem congelar identidade.

## Onda1 — custo e semântica confiáveis

1. **G03: gate de CPU antes de FX (gate+ferramenta;3–6dias).** Congelar baseline e inputs; medir reconhecedor, VM, física/colisão, render, fila DMA e áudio, separando startup. Repetir cenário adversarial com dois lutadores, supers/HUD/voz/BGM. Registrar máximos, distribuição, deadlines e trecho observável. Aceite: nenhum deadline perdido no corpus fechado; falha é finding, não motivo para reduzir silenciosamente qualidade ou trocar limiar. O corpus não prova todas as partidas possíveis.
2. **G05: cobertura nominal/semântica (ferramenta+endurecimento;4–7dias).** Listar126estados e796controladores como população observada da fonte; marcar quais foram exercitados e com qual oráculo. Asserções de input/cancel/throw/juggle/trade/re-hit. Cobertura de casos críticos100% do escopo declarado; geral nunca inventada por contagem de estados distintos.
3. **G08: manifesto de perdas (ferramenta+contrato;2–4dias).** Antes de assets finais, reconciliar50sem-sheet,46blend, mirror4 e limites; preservar fonte e outputhash. Cada aproximação visível exige comparação e veredito, sem sobrecarregar acceptance_status com enum inventado.

Dependências: Q2 estabiliza limites antes do corpus; Q1 permite proveniência válida; Q3 torna resultados encontráveis. Se custo continuar alto, otimizar hotspots com traços diferenciais; não reescrever tudo em Assembly sem evidência de necessidade.

## Onda2 — composição e avaliação audiovisual

4. **G06/G07 (ferramentas+rotas;5–9dias):** SAT/rescomp e palette ownership temporal. Medir contagem e pixels/linha, VRAM e DMA do conjunto com fonte de geometria real. Preservar entradas/JSON/resultados; medir degrau seguinte. Gate bloqueia conflito/overflow, não reprova estilo leve com justificativa explícita.
5. **G10 (rota+endurecimento áudio;3–5dias):** mapear SND canais/interrupções, capturar driver real com áudio e ouvir cenários sincronizados. Report RMS não é qualidade; driver dummy bloqueia aprovação sonora. Qualidade de resample é julgada no sample convertido, não só no WAV fonte.
6. **G11 (integração+gate;4–6dias):** ligar sequência determinística de ROM ao audiovisual_review existente. Exportar frames consecutivos e PTS; verificar loss de captura separado de cadence do jogo; comparar ROIs movimento, sparks, HUD e restore. Definir janelas de hitstop intencionais para não classificá-las automaticamente como stall. Revisão qualificada registra capacidades e intervalos efetivamente vistos/ouvidos. Se ferramenta não permite playback/áudio, manter esses eixos pendentes e encaminhar a quem consegue revisar.

## Onda3 — reuso e expansão controlada

7. **G12/G13/G14 (bootstrap, tooling e rota;5–8dias):** corpus sintético redistribuível, pacote privado por hash e manifesto local, clean checkout sem caminhos externos; separar skips de passed; lições herdadas não se tornam prova local; pacotes ambíguos são recusados.
8. **Skills (propostas da matriz;2–4dias para preparar patches, validação adicional conforme caso):** corrigir header inexistente, qualificar referências centrais e acrescentar handoffs de MUGEN aos owners. Primeiro runbook de tradução; skill nova apenas se segundo personagem demonstrar reuso e fronteira clara.
9. **Segundo personagem e estágio E4:** trabalho de produto separado, não parte desta curadoria. Aceite em dois rosters distintos e palco completo reabre paleta/DMA/scanline/CPU; não reutilizar aprovação Ken×Ken como aprovação de tudo. Multiplexação/S-H somente se benefício e custo forem demonstrados.

## Ordem de dependências e regra de saída

Q1/Q2/Q3 → baseline congelada → G03+G05+G08 → G06/G07/G10 → G11 → corpus independente e segundo personagem. Performance pode exigir nova rodada após estágio/roster. Estimativas não são cumulativas exatas nem compromisso de calendário.

Encerrar uma tarefa técnica é permitido quando seu aceite foi demonstrado; não chamar essa tarefa de jogo concluído. Claim do jogo só avança com build, validação, BlastEm, gameplay, cadência, áudio e memória, além dos gates artísticos aplicáveis. `execution_status=passed` nunca substitui veredito por eixo. Bloqueio requer causa/owner/próximo experimento; repetição sem informação nova não é progresso.

## Prompt para executar uma onda aprovada

Leia este pacote e a matriz de fidelidade na fonte/commit declarados. Selecione apenas os IDs da onda autorizada; escreva aceite e baseline antes de mudar código. Consulte owners existentes e o GDD/contexto. Para cada ID: reproduza → isole causa → teste hipótese → implemente no owner canônico → rode regressão → gere ROM pelo wrapper quando runtime/arte mudarem → capture BlastEm no mesmoSHA → revise o eixo pertinente → registre memória/limites. Não altere limiar nem schema para esconder perda. Não use screenshot como prova de movimento ou sampleRMS como aprovação sonora. Não promova lição/skill sem revisão humana. Entregue diff, testes, evidência e pendências exatas; não anuncieAAA pela soma de tarefas verdes.
