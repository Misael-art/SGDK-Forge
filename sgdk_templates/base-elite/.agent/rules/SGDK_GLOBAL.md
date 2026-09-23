---
trigger: always_on
---

# SGDK Global Rules

Estas regras sao sempre ativas para qualquer projeto `MegaDrive_DEV` que use esta `.agent`.

## 1. Fonte de verdade

- Leia primeiro `doc/10-memory-bank.md`, `doc/11-gdd.md`, `doc/13-spec-cenas.md` e `doc/00-diretrizes-agente.md` quando existirem.
- Trate `.mddev/project.json` como manifesto estrutural, nao como substituto dos docs canonicos.
- Nunca trate README isolado como prova suficiente de implementacao ou validacao.

## 2. Restricoes nao negociaveis

- Nao usar `float` ou `double` para gameplay SGDK.
- Nao usar `malloc` ou `free` no loop de jogo.
- Nao inventar APIs do SGDK.
- Nao duplicar logica de build em scripts de projeto.
- Nao alterar budgets sem evidencia e autorizacao quando o projeto exigir.
- Nao sobrescrever `.agent` local se ela ja existir.

## 3. Governanca e status

- Diferencie sempre `documentado`, `implementado`, `buildado`, `testado_em_emulador`, `validado_budget`, `placeholder`, `parcial` e `futuro_arquitetural`.
- Nao use termos como `validado`, `pronto` ou `completo` sem evidencia verificavel.
- Se encontrar conflito entre docs e codigo, sinalize a divergencia explicitamente.

## 4. Operacao do wrapper

- Toda logica compartilhada deve morar em `tools/sgdk_wrapper/`.
- Melhorias genericas vao para o wrapper central, nao para wrappers locais do projeto.
- O bootstrap da `.agent` e feito apenas quando ausente.

## 5. Handoff

- Ao encerrar uma sessao relevante, atualize o documento de estado operacional do projeto se ele existir.
- Se a implementacao mudou e a documentacao ficou atras, nao silencie essa diferenca.
