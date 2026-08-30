# Failure Patterns

Registre aqui falhas, falsos positivos, tentativas ruins e decisoes que nao devem ser repetidas sem nova evidencia.

| Data | Classificacao | Contexto | Falha observada | Causa provavel | Mitigacao | Evidencia |
|---|---|---|---|---|---|---|
| [DATA] | `local_note` | [cena/sistema] | [o que falhou] | [causa] | [como evitar] | [log/screenshot/hash] |

## Regras

- Falha sem evidencia deve ser marcada como hipotese.
- Solucao nao comprovada nao vira recomendacao.
- Se a falha indicar risco canonico, classifique como `needs_human_review`.


## L02 proporcao estilizada ignorada por modelos de imagem

- Data: 2026-07-03
- Contexto: prompts pediram explicitamente proporcao arcade 3.5 heads para sprites de 44-56px
- Falha observada: modelos entregaram anatomia realista (~6.5 heads) em todos os sheets de personagem; o downscale direto para altura de jogo vira borrao (provado no contact sheet)
- Causa provavel: modelos de imagem generalistas nao obedecem instrucao textual de proporcao estilizada com confiabilidade
- Mitigacao: pedir anatomia realista de proposito (identidade, roupa, pose) e declarar a compressao para 3-4 heads como etapa pixel autoral obrigatoria; atualizar template de prompt pack e concept_art_direction_system
- Evidencia: data/source_art/taina_model_sheet/taina_turnaround_v01.png e data/processed/contact_sheets/vdp_survival_contact_sheet_v01.png
- Classificacao: candidato_canonico
- Candidato: regra de prompts de personagem no concept-art-direction

## L03 texto diegetico emergente apesar do negative prompt

- Data: 2026-07-03
- Contexto: prompts de cenario com negative prompt 'no text'
- Falha observada: modelo inseriu texto diegetico (fita 'interditado por sindicato', selo de uniao em caixote) no painel da arena 3
- Causa provavel: elementos textuais fazem parte do vocabulario visual de docas/interdicao no treino do modelo
- Mitigacao: gate de concept classificar texto emergente como aceito_diegetico ou rejeitado em vez de reprovar automaticamente; neste caso foi ACEITO como narrativa ambiental do GDD; conversao a tiles precisa de politica para texto legivel
- Evidencia: data/source_art/cais_world/cais_arena3_beirada_ringout_v01.png
- Classificacao: candidato_canonico
- Candidato: politica de texto diegetico nos gates de arte

## L05 nomes de arquivo humanos quebram higiene

- Data: 2026-07-03
- Contexto: humano salvou os concepts gerados manualmente
- Falha observada: nomes com espacos, acentos e dois-pontos (invalido em Windows) e dois arquivos na pasta errada, apesar do padrao declarado no prompt pack
- Causa provavel: prompt pack declarou o padrao de pasta mas nao o nome exato de arquivo por prompt
- Mitigacao: prompt pack deve dar o nome de arquivo exato por prompt; agente normaliza para portable_descriptive_v1 no recebimento como rotina
- Evidencia: renomeacao registrada no changelog de 2026-07-03
- Classificacao: local_note

## L06 incompatibilidades do framework em pwsh linux

- Data: 2026-07-03
- Contexto: primeira producao completa do framework num host Manjaro Linux com pwsh 7.6
- Falha observada: OrderedDictionary rejeitado pelo Test-JsonSchema; ConvertFrom-Json converte datas ISO em DateTime sem -DateKind String; .agent local precisa ser symlink absoluto; heuristica do GDD nao le acentos; higiene acusa literais de caminho em texto historico; validate_resources usa -WorkDir; audit_project_learning chama py
- Causa provavel: framework desenvolvido e testado apenas em Windows PowerShell
- Mitigacao: fix ja commitado no validador do brawler; varrer validadores irmaos e adicionar CI multiplataforma (chips de curadoria abertos)
- Evidencia: doc/changelog/changelog.md de 2026-07-03 e commit do fix no wrapper
- Classificacao: candidato_canonico
- Candidato: varredura pwsh linux nos validadores (chips task_0721942b task_7b255b45 task_1e7be1cf)

## L07 falso verde de contrato em fase de planejamento

- Data: 2026-07-03
- Contexto: cadeia de contratos de design 100 por cento valida com projeto sem ROM nem arte
- Falha observada: audit_game_design_contracts emitiu ready_for_aaa=true em pre-producao, criando impressao de prontidao
- Causa provavel: auditor nao cruza evidencia de runtime antes de conceder o status maximo
- Mitigacao: slice_scope_contract como guarda anti-falso-verde local; no canonico, emitir design_contracts_ready em planejamento e reservar ready_for_aaa para quando houver evidencia
- Evidencia: doc/contracts/slice_scope_contract.json e parecer curatorial de 2026-07-03
- Classificacao: candidato_canonico
- Candidato: novo status design_contracts_ready no auditor (chip task_1e7be1cf)

## L08 ledger e derivado dos markdowns e nao editavel a mao

- Data: 2026-07-03
- Contexto: agente escreveu licoes estruturadas direto em learning_ledger.json
- Falha observada: audit_project_learning -Mode Capture regenerou o ledger a partir dos markdowns e sobrescreveu as licoes escritas a mao
- Causa provavel: o ledger e artefato DERIVADO (extract_project_learning.py parseia success/failure patterns por secoes ## com campos '- Campo: valor'); escrever nele viola o contrato da ferramenta
- Mitigacao: curar licoes SEMPRE nos markdowns no formato do parser (Data, Contexto, Falha observada/Padrao observado, Causa provavel, Mitigacao, Evidencia, Classificacao, Candidato) e deixar o capture derivar o ledger
- Evidencia: doc/agent_learning/learning_ledger.json regenerado em 2026-07-03
- Classificacao: local_note
