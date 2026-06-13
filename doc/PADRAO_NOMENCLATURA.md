# Padrão de Nomenclatura de Projetos e Material Ativo

Este documento descreve o padrão oficial de nomenclatura de diretórios para projetos e engines de Mega Drive nesta organização.

## O Padrão

O formato padrão usa um nome livre seguido por **5 tags obrigatórias** delimitadas por colchetes:

`NOME_DO_PROJETO [VER.XXX] [SGDK YYY] [PLATAFORMA] [TIPO] [GENERO]`

> **Atenção:** o nome principal não usa colchetes. Depois dele, os 5 blocos são obrigatórios e mantêm esta ordem.

### Estrutura Detalhada:

1. **`NOME_DO_PROJETO`**: O nome principal da engine, jogo ou projeto (sem colchetes).
   - *Exemplo:* `BLAZE_ENGINE`, `HAMOOPIG`, `Mega Snake`

2. **`[VER.XXX]`**: A versão atual do projeto.
   - Sempre deve usar o prefixo `VER.`.
   - *Exemplo:* `[VER.001]`, `[VER.1.0]`, `[VER.1.2]`

3. **`[SGDK YYY]`**: A versão da biblioteca SGDK utilizada no projeto.
   - Define o SDK compilado alvo.
   - *Exemplo:* `[SGDK 160]`, `[SGDK 200]`

4. **`[PLATAFORMA]`**: O sistema hardware alvo do projeto.
   - *Exemplo:* `[GEN]` (para Sega Genesis / Mega Drive), `[SMS]` (para Master System).

5. **`[TIPO]`**: A classificação da natureza do projeto.
   - Define se é uma Engine base, um Jogo fechado, ou projeto de Teste.
   - *Valores comuns:* `[ENGINE]`, `[GAME]`, `[TEMPLATE]`, `[ESTUDO]`.

6. **`[GENERO]`**: A categorização ou gênero principal do jogo/engine.
   - *Valores comuns:* `[BRIGA DE RUA]`, `[LUTA]`, `[PLATAFORMA]`, `[RPG]`, `[AUDIO]`, `[TESTE]`.

---

## Exemplo Completo

`BLAZE_ENGINE [VER.001] [SGDK 160] [GEN] [ENGINE] [BRIGA DE RUA]`

### Quebrando o exemplo:
- **BLAZE_ENGINE**: O nome do projeto.
- **[VER.001]**: Versão número 001.
- **[SGDK 160]**: Compilado na versão 1.60 do SGDK.
- **[GEN]**: Plataforma Sega Genesis (Mega Drive).
- **[ENGINE]**: Trata-se de uma Engine base.
- **[BRIGA DE RUA]**: Gênero "Beat 'em up" (Briga de Rua).

---

## Regras Importantes

1. Todo novo projeto deve seguir estritamente esse padrão ao ser criado dentro de `SGDK_projects` ou `SGDK_Engines`.
2. Mantenha os espaços simples e evite underscores `_` desnecessários se possível (os underscores são aceitáveis apenas se estritamente necessários no `NOME_DO_PROJETO`).
3. Siga sempre as `[Caixas Altas]` dentro das chaves quando for uma tag padrão (`[GEN]`, `[ENGINE]`, etc).

## Enforcement

- `tools/sgdk_wrapper/validate_project_name.ps1` e a fonte executavel do padrao.
- `new_project.bat` e `new_project.sh` rejeitam nomes novos fora do formato antes de criar qualquer diretorio.
- `validate_project_methodology.ps1` bloqueia projetos `new`/`reseed` fora do padrao e bloqueia divergencia entre diretorio, `.mddev/project.json` e manifesto metodologico.
- Projetos antigos nao sao renomeados automaticamente; sua identidade deve ser normalizada com curadoria humana antes do closeout.

## Material ativo dentro do projeto

O perfil executavel `portable_descriptive_v1`, declarado em
`doc/project_hygiene_manifest.json`, vale para codigo, headers, scripts, assets,
manifestos, documentacao e diretorios ativos:

- usar ASCII e evitar espacos;
- usar nomes descritivos em minusculas;
- preferir `snake_case` para codigo, scripts, assets e JSON;
- preferir `kebab-case` ou prefixo numerico + `kebab-case` para documentacao;
- manter sufixos explicitos quando uteis, como `_v003`, `_64x80`, `_strip` e `_report`;
- excecoes convencionais permitidas: `README.md`, `LICENSE`, `LICENSE.md`,
  `COPYING` e `Makefile`;
- material externo bruto preservado em `rascunho/` pode manter o nome original.

`validate_project_hygiene.ps1` bloqueia `project_naming_policy_invalid` e
`noncanonical_project_entry_name`. O agente nao renomeia automaticamente
material legado: primeiro registra impacto, referencias e plano de migracao.
