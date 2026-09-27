# Prompt de continuidade: Mugenesis, tarefas pequenas e verificaveis

Voce continua o Mugenesis_Demo no workspace SGDK Forge. Sua capacidade de gerar
imagens pode ajudar o piloto de FX. Nao redesenhe o motor nem tente resolver
todas as pendencias numa rodada. Leia AGENTS.md e use os wrappers existentes.

## Estado inicial: confirmar, nao presumir

Projeto: `SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]`.
Leia seu `doc/10-memory-bank.md`, contrato em `doc/mugen/palette_contract_rule1.md`
e pacote `doc/mugen/fx_pilot_hadouken/`. Leia tambem
`tools/sgdk_wrapper/.agent/references/mugen_conversion_safety_2026_09_24.md`.
Leia as skills diretamente em `tools/sgdk_wrapper/.agent/skills/`: neste host,
`.agents/skills` foi encontrado como diretorio real divergente da ponte esperada.
Nao confie numa copia antiga nem corrija essa infraestrutura junto com o piloto.
Identifique branch, commit, arquivos modificados e PRs antes de escrever.
Nao substitua trabalho de outro agente. Use branch/worktree propria quando
necessario; nao troque a branch da sessao de outro agente.

No handoff de 2026-09-24: PR20 integrada; PR21 (proveniencia) aberta;
PR22 (Stage 3) draft. Isso deve ser consultado novamente. Protecao da PR21 NAO
esta automaticamente na branch da PR22. Nao reconverta assets de producao sem
confirmar essa protecao e seus testes. Nao faca merges apenas porque testes passam.

Baseline informada: ROM `9530c0a1…`, 70/1200 frames acima do budget. Flash-only
`595116bc…` buildada, sem captura; shake-only e ambas ainda pendentes. Prefixos
nao servem como identidade final: obtenha hashes completos dos artefatos reais.
Nao declarar 60 fps constantes, AAA ou aprovacao audiovisual a partir disso.

## Ordem de execucao

1. Registrar checkpoint inicial e executar uma vez os testes relevantes da
   branch. Comando conhecido: `python3 -m pytest tools/mugen2sgdk_forge/tests -q -ra`.
   Registrar falhas e skips; nao assumir que 70 testes e um numero permanente.
   Falha anterior nao pode ser apagada ou ter expectativa afrouxada para passar.
2. Sem alterar producao, preparar e avaliar UMA familia: hadouken, AIR 750/751.
   Use os arquivos originais e contratos do pacote, nunca o efeito vermelho
   defeituoso da ROM como alvo. Confirme hashes, mascara, pivots e duracoes.
3. Somente apos candidato aprovado e requisitos tecnicos satisfeitos, integrar
   esse piloto isoladamente pelo conversor. Nao migrar todas as familias junto.
4. Fechar as capturas pendentes da Stage 3 quando o host permitir, em rodada
   separada da integracao artistica. Nao misturar arte e flash/shake no mesmo A/B.
5. Suzaku e outras familias ficam para tarefas posteriores, com contrato proprio.

## Tarefa artistica delimitada

Verifique que sua ferramenta de imagem esta disponivel. Leia a skill imagegen
e as skills canonicas de traducao/pixel/animacao aplicaveis antes de produzir.
Se a ferramenta nao estiver disponivel, preserve o pacote e continue apenas
as verificacoes independentes; nao simule arte final com primitivas em codigo.

Paleta local: 8 slots estaveis utilizaveis, 6 slots de roupa proibidos para FX,
1 slot de FX (indice 6), indice 0 transparente. Extraia os valores EXATOS de
`palette_roles.json`; nao invente RGB, nao mude corpo ou variantes para acomodar
o efeito. A escolha da cor de FX precisa considerar todas as 15 familias.

Preserve os 8 elementos AIR, inclusive 3 vazios intencionais, duracoes, pivots,
direcao e volume percebido. Nao alterar hitboxes, escala do corpo, dano, alcance,
velocidade ou timing para fazer a imagem caber. Teto do piloto: 26 tiles e
2 sprites de hardware por frame; custo compilado e pressao de scanline exigem
medicao propria, nao estimativa por retangulos.

Produza no maximo duas alternativas iniciais de UMA pose representativa, em
staging dentro do projeto. Escolha pela silhueta, nucleo escuro opaco, contraste
com o cenario e continuidade com as poses vizinhas. So expanda a sequencia apos
verificar viabilidade da pose na paleta contratada. Guarde fonte, prompt e hash.
Imagem gerada nao garante indexacao, grade, transparencia ou coerencia temporal.
Converta/valide pelo pipeline existente, preservando a fonte. Nao publique pixels
de terceiros no git. Qualquer aprovacao humana exigida pelo pipeline permanece
pendente ate ser recebida; enquanto isso execute apenas trabalho independente.

## Gates do piloto

- Mascara da exportacao original corresponde ao indice 0 da fonte; preto opaco
  nao vira transparente. No redesenho, avaliar silhueta deliberadamente alterada
  em vez de exigir igualdade pixel a pixel com a arte anterior.
- Slots de roupa intocados em todas as variantes; cores fora do contrato bloqueiam.
- Tempos AIR, ordem, frames vazios, pivots e hitboxes preservados.
- Brief e JSON concordam; budgets estimados e compilados identificados separadamente.
- Contact sheet em escala nativa, preview temporal e comparacao fonte/candidato.
- Proveniencia preservada e aprovacao vinculada ao hash; reconversao identica
  deve ser idempotente. Testar em copia antes de tocar producao.
- Build e BlastEm da mesma ROM para aprovar integracao. Um piloto aprovado nao
  faz o `palette-check` global de Ken passar enquanto outras familias excederem a linha.
- Depois da migracao, observar flash com projetil ativo: compartilhar linha de
  CRAM pode alterar ambos. Se houver spill, registrar e encaminhar decisao de
  paleta; nao liberar outra linha silenciosamente nem afirmar isolamento pelo stub.

## Capturas Stage 3

Use preflight e rota BlastEm ja existente, uma execucao por vez. Nao iniciar
batch sob pressao de memoria, encerrar programas do usuario ou mudar swap.
Se inviavel, registre o impedimento com medicao atual e preserve a tarefa draft.

Matriz: base, flash-only, shake-only, ambos. Mesmos inputs/estado, janela de
1200 frames, warmup, regiao, audio e configuracao de captura. Se o estado-base
nao for reproduzivel, a comparacao fica invalida; nao substituir por outro trecho.
Registrar ROM SHA-256 completo, configuracao, numerador/denominador, artefatos e
falhas. Fazer bursts para observar flash e shake; eles nao comprovam cadencia
prolongada ou audio. Preservar testes de hitstop, hits consecutivos, projetil
distante, superpause, KO, retorno de round e restauracao exata de paleta.

## Disciplina para evitar regressao e desperdicio

Uma alteracao por ciclo: reproduzir -> alterar -> teste direcionado -> comparar
-> registrar. Repetir suite completa quando a integracao justificar, nao a cada
ajuste de documento. Nao criar novo framework, novos gates genericos ou refatorar
arquitetura para fechar um piloto. Nao atualizar golden/hash para esconder falha.
Nao usar waiver como aprovacao. Nao alterar asserts para combinar com resultado ruim.

Apos duas tentativas sem progresso na mesma causa, encerrar aquele ciclo com
diagnostico, artefatos e proxima acao concreta; avance somente em tarefa independente.
Isso e checkpoint, nao entrega concluida. Nao prometa loop infinito ou ausencia
absoluta de regressao. Nao promova licoes ao canon nesta tarefa automaticamente.

Ao terminar, atualizar memoria/changelog do projeto e entregar: arquivos alterados,
hashes, testes com skips, comparacao visual realizada, ROM observada ou pendente,
pendencias e proximo comando verificavel. Declarar separadamente arte candidata,
integracao tecnica, evidencia de emulador e aprovacao artistica. A qualidade
comparavel as referencias permanece pendente enquanto esses eixos nao forem provados.
