# Fechamento da curadoria — 2026-09-23

**Entregue: diagnóstico e propostas para revisão humana.** Nenhuma alteração de runtime, parser, conversor, skill ou regra neste PR. Nenhuma promoção de qualidade do jogo. A escrita destas propostas e a atualização da memória foram autorizadas pelo direcionador; implementar as propostas é decisão posterior.

## Execução e resultados

|Operação|Resultado|Alcance|
|---|---|---|
|Guard de ambiente|ready, exit0|Logs em validation/environment.txt; Graphify consultivo não foi usado como verdade|
|Adoção metodológica|exit0, manifests preservados|Não sobrescreveu classificação nem higiene|
|Contexto|exit1, unclassified|Bloqueio existente de produção; auditoria registra reprovação, não entrega aprovada|
|Higiene|exit1, blocked|out_prof/out_test/.gitignore não classificados; sem alteração fora do escopo|
|Pytest conversor|39 passed, sem skips, 7,78s|Reexecutado na fonte auditada; inclui integração privada disponível neste host|
|Scanline self-check|exit0|Contagem e pixels/linha, H32, geometry/headroom; não valida automaticamente probe C|
|Proveniência self-check|exit0|Fixtures existentes passam; falso positivo de tabela lógica continua finding real|
|Meta-medição self-check|exit0|Valida o mecanismo do meta-gate, não equivale a executar toda ferramenta do workspace|
|Selo de captura self-check|exit0|Decodificação e identidade; não demonstra qualidade do jogo|
|Proveniência do projeto|exit1, BLOCKED|Enum inválido e achados em cascata; neg1_masks é falso positivo fundamentado por seus usos lógicos|
|CLI audiovisual --self-check|exit2, opção não disponível|Tentativa preservada; não usada como aprovação ou medição|
|Learning Audit|exit0|Consulta local registrada|
|Learning Capture|exit0, captured|45 lições/29 candidatos no ledger existente, não 45 descobertas deste parecer; canonical_promotion_performed=false|
|Bundle P5|5/5 hashes coincidem|ROM, screenshot, SRAM, bloco VDP e runtime_metrics; histórico, sem nova execução|
|Reparse do pacote Ken|2 ausências +48 elementos BGFX =50|Mesmo SHA do pacote do report; leitura sem gerar/distribuir assets|

Logs e reports estão em [validation](validation/) e [evidence](evidence/). O Capture informou escrita apenas de `doc/agent_learning/learning_ledger.json` e `out/logs/project_learning_report.json` dentro do projeto fonte. Esses arquivos não são transportados ao PR documental; a operação não promoveu nenhuma candidata. A árvore fonte não apresentou diff versionado após a execução.

## Limites mantidos

- A fonte é a feature em `12c63349...`, enquanto a base do PR é main `caf10a2d...`. Links de código/skills fixam o commit auditado. O PR não incorpora as features por acidente.
- A imagem P5 foi vista; vídeo e áudio não foram reproduzidos nesta auditoria. Burst de0,4s não permite julgar animação quadro a quadro. Qualidade artística global permanece pendente.
- O report P5 contém591 overbudget e pico158, mas o denominador inclui warmup na fonte da probe atual. Não extrair uma taxa precisa de slowdown nem validar60fps do título da janela.
- Números de P3/P5 em memos foram classificados conforme sua evidência. O diagnóstico diferencia prova local, estimativa e tese. Os JSON de entrada do experimento P3 não estão vinculados pelo memo a um artefato reproduzível.
- Skill audit é documental: notas não equivalem a benchmarks de proficiência. Referências que são outputs de projeto não foram tratadas automaticamente como arquivos quebrados.
- Os12 pareceres de lições são propostas. O ledger original não foi reescrito para canonizá-los, e os padrões de governança não foram relaxados.

## Próxima decisão

Revisar os três quick wins e as ondas no [roadmap](robustness_roadmap.md). Performance, semântica, proveniência e avaliação audiovisual precisam de correções demonstradas antes de expandir efeitos/roster/estágio. O material já é concreto para revisão: cada gap tem owner, esforço estimado, evidência e aceite.
