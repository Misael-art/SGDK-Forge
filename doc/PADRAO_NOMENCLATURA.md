# Padrão de Nomenclatura de Projetos

Este documento descreve o padrão oficial de nomenclatura de diretórios para projetos e engines de Mega Drive nesta organização.

## O Padrão

O formato padrão para os nomes dos diretórios é composto por **5 partes obrigatórias**, delimitadas por colchetes, no seguinte formato:

`[NOME_DO_PROJETO] [VER.XXX] [SGDK YYY] [PLATAFORMA] [TIPO] [GENERO]`

> **Atenção:** Embora a regra exija 5 blocos de colchetes fixos após o Nome, a estrutura original fornecida pelo usuário possui a seguinte leitura pedagógica prática:

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
