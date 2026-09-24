# Reavaliação individual das12 lições E0–E3

Fonte: commit33722d76; revisão contra 12c63349d72fb8d96ecd16148fcfe9a9bde5965c. Nenhuma candidata foi promovida. Confirmar no escopo significa evidência delimitada, não regra universal.

|ID|Parecer|Evidência/limite e próxima ação|
|---|---|---|
|md_68000_loop_cost|qualificar|Hotspots e melhora são observações locais. Rejeitar “cada iteração custa centenas de ciclos”; depende de código gerado, memória e trabalho. Exigir trace/profiler por etapa e estado. G03|
|measure_on_hardware_not_host|qualificar|Host serve para localizar hotspots; fator10x não é constante. Header timer.h confirma76.800subticks/s, não prova frames estáveis. Hardware físico não foi testado nesta revisão. G03|
|semantics_harness_before_rom|confirmar_no_escopo|39testes atuais incluem host real/stubs; correções semânticas têm testes. Isso não substitui ROM nem prova que todos os sete defeitos têm regressão focal independente. G05|
|exact_gates_equivalence|qualificar|Preservar ordem e portões necessários derivados de AST é boa proposta; trace98/1/86 sozinho não prova equivalência universal. Ampliar seeds/inputs e divergências nominais. G05|
|mugen_state_label_is_not_owner|confirmar_no_escopo|Parser usa último Statedef; teste com rótulo divergente existe e passou. Candidata forte de domínio. G05|
|mugen_case_sensitive_keys|confirmar_no_escopo|Parser diferencia B/b e teste unitário mais movimento host passam. Não confundir nome de comando com símbolo do botão. G05|
|mugen_engine_rules_outside_cns|qualificar|Engine rules fora CNS existem; common_forge/runtime é subset. Não elevar todos os comportamentos de pouso/negativos/custom state a equivalentes sem corpus. G05|
|ai_activates_commands|contestar_generalizacao|Ativar comandos é estratégia local; não descrever como definição universal da IA MUGEN nem como mesmo input humano. Melhora histórica não elimina27% do P5. G03|
|third_party_outputs_gitignored|qualificar|Outputs estão separados/ignorados, mas manifesto atual falha schema. Gitignore não prova ausência no histórico nem autorização de distribuição. G01|
|worktree_build_and_capture_paths|qualificar|Flatpak/mounts e .d stale são dependentes do host. Worktree é suportável com rota/montagem correta; não canonizar obrigação universal de build na árvore principal. G13|
|template_inherits_foreign_learning|confirmar_ocorrencia_local|Projeto contém the_forge_opening_lessons e histórico herdado. Quantidade28 não foi recontada como origem integral; separar inherited de local e testar bootstrap limpo. G12|
|screenshot_gate_without_scene|contestar_remedio|Edge-density não é oráculo estético. Não adicionar estágio para satisfazer heurística de captura de uma fatia técnica; classificar cena/expectativa e manter gate de estágio completo separado. G11|
