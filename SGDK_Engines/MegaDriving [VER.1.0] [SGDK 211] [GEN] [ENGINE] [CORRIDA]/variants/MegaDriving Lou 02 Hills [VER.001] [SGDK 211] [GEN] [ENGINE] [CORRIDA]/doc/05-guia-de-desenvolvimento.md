# Guia de Desenvolvimento

## Ciclo diario sugerido

1. Ler a tarefa do dia
2. Abrir `../../upstream/lou/02_hills/src/main.c` ou o modulo alvo
3. Ajustar recurso em `../../upstream/lou/02_hills/res/`, se necessario
4. Rodar `build.bat`
5. Rodar `run.bat`
6. Registrar aprendizados e decisoes tecnicas

## Checklist antes de mexer

- Entendi em qual modulo a mudanca pertence?
- Existe documentacao previa sobre isso em `doc/`?
- A alteracao e especifica do projeto ou generica do wrapper?

## Checklist antes de concluir

- O projeto compila?
- O comportamento foi validado no emulador?
- A documentacao ficou atualizada?
- Nao deixei arquivos soltos, logs ou scripts ambiguos na raiz?

## Quando parar e reorganizar

Se voce notar mais de um destes sinais, vale abrir uma tarefa de organizacao:

- scripts duplicados com nomes diferentes
- recursos sem pasta definida
- arquivos gerados misturados com codigo
- varias notas soltas fora de `doc/`
