# Canonical Skill Curation Design

## Objetivo

Reduzir o framework SGDK ao melhor conjunto operacional de skills, sem
canonizar técnicas apenas para satisfazer validadores. Skills redundantes,
desatualizadas, frágeis ou sem evidência suficiente devem sair da descoberta
ativa, mas permanecer rastreáveis e reversíveis.

## Escopo

Esta curadoria cobre:

- as 26 skills associadas aos 94 achados atuais do
  `validate_skill_framework.py`;
- referências a essas skills em pipelines, workflows, manifests e metadata;
- critérios permanentes de lifecycle, descoberta e restauração;
- redução de custo de contexto das skills mantidas.

Não cobre implementação de gameplay, assets, ROM, emulação ou promoção de
qualquer claim técnico para `testado_em_emulador`.

## Princípios

1. SGDK 2.11 e os limites reais do Mega Drive têm precedência sobre texto
   legado, exemplos externos e memória do agente.
2. Técnica correta e owner único importam mais que quantidade de skills.
3. Conteúdo E1 ou candidato pode orientar investigação, mas não entra como
   regra operacional sem validação proporcional.
4. Uma skill ativa deve mudar decisões do agente. Material puramente
   explicativo pertence a referência ou `lib_case`.
5. Nenhuma skill é apagada nesta curadoria: desativação usa quarentena
   rastreável e reversível.
6. Validator verde é consequência da curadoria, não critério de promoção.

## Arquitetura

### Árvore ativa

`tools/sgdk_wrapper/.agent/skills/` conterá apenas skills descobríveis e
operacionais.

Cada skill ativa deve possuir:

- frontmatter com `name` e descrição curta de gatilhos;
- `agents/openai.yaml` válido;
- owner sem sobreposição destrutiva;
- contrato mínimo: entrada, saída, aprovação e handoff;
- técnicas compatíveis com SGDK 2.11 e hardware real;
- conteúdo conciso, orientado a decisão.

### Quarentena legado

Skills desativadas serão movidas integralmente para:

`tools/sgdk_wrapper/.agent/legacy/skills/<skill-name>/`

A pasta `legacy/` não participa da descoberta por `.agents/skills`, do
`framework_manifest.json` ativo nem dos pipelines. O conteúdo original deve ser
preservado, exceto por um marcador externo no registro de lifecycle.

### Registro de lifecycle

Será criado:

`tools/sgdk_wrapper/.agent/references/skill_lifecycle_registry.json`

Cada registro terá:

- `skill_id`;
- `lifecycle`: `active`, `merged`, `superseded`, `deprecated` ou
  `experimental`;
- `decision_reason`;
- `replacement_skill`;
- `evidence_grade`;
- `source_path`;
- `legacy_path`;
- `content_sha256`;
- `references_redirected`;
- `restore_conditions`;
- `decision_date`;
- `human_approved`.

O registro é a fonte de rastreabilidade; não será criada uma skill só para
explicar lifecycle.

## Rubrica de decisão

### Manter ativa

Manter quando:

- possui responsabilidade distinta e recorrente;
- evita erro técnico relevante;
- tem handoff claro;
- não duplica owner já mais forte;
- suas recomendações são compatíveis com headers SGDK 2.11;
- seu custo de contexto é proporcional ao valor.

### Fundir

Fundir quando:

- duas skills tomam as mesmas decisões;
- uma é subconjunto natural da outra;
- separar aumenta roteamento, contexto e risco de owners concorrentes.

O conteúdo útil é incorporado ao owner sobrevivente de forma concisa; a skill
fundida vai para legado com `replacement_skill`.

### Substituir

Substituir quando:

- a técnica é válida, mas o owner atual está errado;
- outra skill já oferece contrato mais completo ou atual;
- o nome ou escopo induz rota tecnicamente inferior.

### Deprecar

Deprecar quando:

- recomenda API antiga, inexistente ou abordagem inferior;
- depende de comportamento não comprovado;
- mistura observação de outra plataforma com contrato Mega Drive;
- promove técnica E1 como regra;
- é tão específica que custa mais contexto do que evita erros.

### Experimental

Mover para legado experimental quando a técnica pode ser útil, mas ainda
precisa de fixture, ROM, budget, header check ou evidência em emulador.

## Auditoria técnica

Para cada skill:

1. identificar claims, owner, entradas, saídas e handoff;
2. localizar sobreposição com skills ativas;
3. verificar APIs sensíveis nos headers de `sdk/sgdk-2.11/inc/`;
4. separar regra de hardware, heurística, caso de estudo e afirmação sem prova;
5. atribuir lifecycle;
6. atualizar todas as referências;
7. testar descoberta e roteamento.

Técnicas sem uso de API direta ainda devem ser verificadas contra as regras
globais de VRAM, DMA, CRAM, sprites, H-Int, VBlank, Z80 e ownership.

## Economia de tokens

### Frontmatter

- descrição apenas de gatilhos;
- sem resumo do workflow;
- sem listas extensas de técnicas.

### Corpo ativo

- alvo recomendado: até 500 palavras por skill nova ou curada;
- manter somente decisões, contrato, blockers e anti-padrões;
- remover narrativa de sessões e duplicação de regras globais;
- mover casos históricos para `lib_case`;
- mover tabelas extensas e pesquisa para referências carregadas sob demanda.

### Roteamento

- `allow_implicit_invocation=true` somente para owners seguros e claramente
  acionáveis;
- skills experimentais ou de opt-in ficam fora da árvore ativa ou usam
  invocação explícita;
- aliases e overlaps devem apontar para um único owner.

## Migração e reversão

1. Registrar o hash do conteúdo antes de mover.
2. Mover a pasta completa para `legacy/skills/`.
3. Atualizar manifest, pipeline, workflow e catálogo de owner.
4. Executar validator para garantir que legado não é descoberto.
5. Registrar substituta e referências redirecionadas.

Para restaurar:

1. validar as condições declaradas em `restore_conditions`;
2. conferir o hash legado;
3. mover de volta para `skills/`;
4. atualizar lifecycle para `active`;
5. restaurar referências;
6. executar todas as validações.

## Estratégia de testes

### Estado RED

Preservar como baseline os 94 achados atuais:

- 13 frontmatters;
- 55 campos de metadata;
- 26 contratos.

### Testes estruturais

- `validate_skill_framework.py`;
- validação individual de cada skill ativa;
- JSON parse do lifecycle registry e manifests;
- busca por referências a skills arquivadas;
- confirmação de que `.agents/skills` não expõe `legacy/`.

### Testes técnicos

- fixtures de roteamento por domínio;
- verificação de owner único;
- consulta de headers para APIs citadas;
- rejeição de termos e APIs SGDK legadas;
- teste de restauração em diretório temporário.

### Critério de conclusão

A curadoria passa quando:

- o validator global fica limpo;
- nenhuma skill ativa aponta para owner arquivado;
- cada skill ativa possui lifecycle e contrato válidos;
- todas as desativações têm hash, motivo, substituta ou condição de
  restauração;
- a contagem e o tamanho total das skills ativas não aumentam sem justificativa;
- memória e changelog registram decisões sem promover ROM, runtime ou AAA.

## Ordem de execução

1. Criar testes e registry de lifecycle.
2. Auditar arquitetura, código e hardware.
3. Auditar arte e áudio.
4. Auditar orchestrators de planejamento.
5. Redirecionar referências e mover legado.
6. Compactar skills sobreviventes.
7. Executar validações completas.
8. Atualizar memória e changelog.

