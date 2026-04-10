# AGENTS.md – Diretrizes para Agentes de IA

Este documento define propósitos, métodos e regras para agentes de IA que atuam no projeto MegaDrive_DEV, garantindo consistência, portabilidade e respeito à arquitetura existente.

---

## 1. Propósito do Projeto

O **MegaDrive_DEV** é um repositório de engines e jogos para **Mega Drive / Genesis**, desenvolvidos com **SGDK** (Sega Genesis Development Kit). O foco é **pedagógico**: permitir que iniciantes aprendam a programar para o Mega Drive através de exemplos funcionais, documentados e resilientes.

- **Engines:** BLAZE_ENGINE (briga de rua), HAMOOPIG (luta), state machine RPG, etc.
- **Jogos:** Mega Snake, mega genius, entre outros.
- **Migração em curso:** Projetos SGDK 160 → SGDK 211 para compatibilidade com a versão atual do SDK.

---

## 2. Arquitetura Canônica

### 2.1 Scripts-Wrapper Centralizados

Toda a lógica de build, limpeza, execução e configuração de ambiente está centralizada em:

```
tools/sgdk_wrapper/
├── build.bat              # Entry point: converte para short path, delega a build_inner
├── build_inner.bat        # Logica de build (executada em contexto short path)
├── clean.bat              # Limpeza de artefatos
├── run.bat                # Execução da ROM no emulador
├── env.bat                # Configuração de GDK, PATH, Java
├── fix_migration_issues.ps1   # Pré-processamento para migração SGDK
├── validate_resources.ps1     # Validação de recursos antes do build
├── autofix_sprite_res.ps1    # Correção de sprite.res (dimensões, paths, duplicatas)
├── fix_transparency.ps1      # Correção de transparência em PNG
└── ...

### 2.2 Delegação Obrigatória
Todo projeto de categoria Elite DEVE conter na sua raiz os 3 scripts de delegação:
1. `build.bat`: `call "..\..\tools\sgdk_wrapper\build.bat" "%~dp0"`
2. `clean.bat`: `call "..\..\tools\sgdk_wrapper\clean.bat" "%~dp0"`
3. `run.bat`:   `call "..\..\tools\sgdk_wrapper\run.bat" "%~dp0"`

Essa triade é mandatória para garantir a compatibilidade com ferramentas de automação e agentes de IA.
```

### 2.2 Delegação pelos Projetos

Cada projeto possui scripts **canônicos** que apenas delegam ao wrapper:

```batch
REM build.bat (em cada projeto)
call "%~dp0..\..\tools\sgdk_wrapper\build.bat" "%~dp0"
```

- **Nenhuma lógica de build** deve ser duplicada nos projetos.
- O número de `..` varia conforme a profundidade do projeto (2 ou 3 níveis).
- Qualquer melhoria, correção de bug ou nova funcionalidade é feita **apenas** nos arquivos do wrapper.

### 2.3 Variáveis de Ambiente

- `%GDK%` ou `$env:GDK`: Caminho da instalação SGDK (ex.: `sgdk-2.11`).
- `%MD_ROOT%`: Raiz do repositório MegaDrive_DEV.

---

## 3. Fluxo de Migração SGDK 160 → 211

1. **fix_migration_issues.ps1** (pré-processamento)
   - Detecta projetos `[SGDK 211]` e localiza versão `[SGDK 160]` no mesmo diretório pai.
   - Usa `res/sprite.res` da versão 160 como fonte para recuperação.
   - Migra APIs deprecadas no código C:
     - `VDP_setPalette` → `PAL_setPalette`, `VDP_setPaletteColors` → `PAL_setColors`
     - `PAL_setColorsDMA` → `PAL_setColors(..., DMA)`, `PAL_setPaletteDMA` → `PAL_setPalette(..., DMA)`
     - `SPR_addSpriteEx` com 6 args → 5 args (remove sprIndex)
     - `SPR_FLAG_AUTO_SPRITE_ALLOC` → `SPR_FLAG_AUTO_VRAM_ALLOC`

2. **autofix_sprite_res.ps1** (recuperação de sprite.res)
   - Corrige dimensões W/H usando o sprite.res da versão 160 como referência.
   - Corrige paths incorretos (ex.: ninja char02 → char03, enemy05 → enemy01).
   - Remove duplicatas de definições SPRITE.
   - Aplica `opt_type=1` (SPRITE) para sprites que excedem o limite de 16 sprites internos do VDP.

3. **validate_resources.ps1** (validação)
   - Verifica existência de arquivos, dimensões, limite VDP (16 sprites internos), alinhamento de pixels.
   - Gera `validation_report.json` com diagnóstico estruturado.

---

## 4. Regras para o Agente de IA

### 4.1 Modificações

- **Correções genéricas:** Modificar apenas em `tools/sgdk_wrapper`.
- **Correções específicas de projeto:** Documentar em relatório em `doc/migrations/` e não duplicar lógica no wrapper.
- **Nunca criar cópias ou forks** de arquivos existentes; preferir correções in-place.

### 4.2 Tratamento de Erros

- Manter filosofia de **erro explícito**: try/catch, mensagens descritivas.
- Explicar: o que falhou, por que falhou, como corrigir (quando aplicável).
- Evitar tratamento genérico ou silencioso de exceções.

### 4.3 Qualidade e Segurança

- Evitar workarounds temporários que comprometam escalabilidade ou segurança.
- Entregar soluções completas, sem simplificações excessivas.
- Não alterar ou remover código sem permissão; explicar mudanças antes.

### 4.4 Documentação

- Incluir comentários claros nos scripts.
- Documentar propósitos e métodos para fins pedagógicos.
- Garantir que a documentação técnica seja completa e sem duplicação.
- Documentação centralizada em `doc/`.

---

## 5. Checklist de Migração SGDK 160 → 211

Ao migrar um projeto, verificar:

| Item | Ferramenta / Ação |
|------|-------------------|
| **sprite.res – paths** | `autofix_sprite_res.ps1` com `sourceResFile` da versão 160 |
| **sprite.res – dimensões** | Recuperar do sprite.res 160 ou validar com ImageMagick |
| **sprite.res – limite 16 sprites** | Adicionar `NONE 1 1` (opt_type=SPRITE, opt_level=MEDIUM) ou reduzir dimensões |
| **sprite.res – duplicatas** | Remover definições SPRITE duplicadas (manter primeira ocorrência) |
| **APIs deprecadas** | `fix_migration_issues.ps1` (VDP_* → PAL_*, PAL_*DMA → PAL_*(...,DMA), SPR_addSpriteEx 6→5 args, SPR_FLAG_AUTO_SPRITE_ALLOC → SPR_FLAG_AUTO_VRAM_ALLOC) |
| **Transparência PNG** | `fix_transparency.ps1` (correção automática em caso de erro) |
| **Scripts de build** | `migrate_projects.py` para padronizar build.bat, clean.bat, run.bat |

---

## 6. Fila de Migração SGDK 160 → 211

Todos os engines e jogos possuem agora uma versao SGDK 211:

| Projeto | Tipo | Status |
|---------|------|--------|
| BLAZE_ENGINE [SGDK 211] | Briga de rua | Migrado (sprite.res corrigido) |
| Shadow Dancer Hamoopig [SGDK 211] [PLATAFORMA] | Plataforma | Migrado (boot sega.s alinhado) |
| HAMOOPIG [VER.001] [SGDK 211] | Luta | Migrado em lote |
| HAMOOPIG [VER.1.0] [SGDK 211] | Luta | Migrado anteriormente |
| HAMOOPIG [VER.1.0 CPU6.2] [SGDK 211] | Luta | Migrado (nomenclatura corrigida) |
| HAMOOPIG main [VER.001] [SGDK 211] | Luta | Migrado anteriormente |
| KOF94 HAMOOPIG MINIMALIST [SGDK 211] | Luta | Migrado em lote |
| MUSIC [SGDK 211] | Audio | Migrado em lote |
| Super Monaco GP [SGDK 211] | Corrida | Migrado em lote |
| mega genius [SGDK 211] | Puzzle | Migrado em lote |
| msu-example [SGDK 211] | Audio | Migrado em lote |
| Mega Snake [SGDK 211] | Arcade | Migrado em lote (de SGDK 200) |
| flip [SGDK 211] | Teste | Migrado em lote (de SGDK 200) |
| state machine RPG [SGDK 211] | RPG | Migrado em lote (de SGDK 200) |

> **Status de build validado:** 13/13 projetos compiláveis geram ROM com sucesso.
> 1 projeto (HAMOOPIG main) é referência sem recursos — documentado em `NOTA_COMPILACAO.md`.
> Consulte `doc/migrations/MIGRATION_BATCH_211.md` para detalhes completos.

## 7. Referências Rápidas

- **Documentação:** [doc/README.md](README.md)
- **Template de Projeto:** `templates/project-template/` (template canonico)
- **Wrapper:** [tools/sgdk_wrapper/README.md](../tools/sgdk_wrapper/README.md)
- **Resiliência:** [tools/sgdk_wrapper/RESILIENCE.md](../tools/sgdk_wrapper/RESILIENCE.md)
- **Relatório BLAZE_ENGINE:** [doc/migrations/BLAZE_ENGINE_FIX_REPORT.md](migrations/BLAZE_ENGINE_FIX_REPORT.md)
- **Migração Shadow Dancer:** [doc/migrations/MIGRATION_SHADOW_DANCER_HAMOOPIG.md](migrations/MIGRATION_SHADOW_DANCER_HAMOOPIG.md)
- **Migração msu-example:** [doc/migrations/MIGRATION_MSU_EXAMPLE.md](migrations/MIGRATION_MSU_EXAMPLE.md)
- **Migração em lote:** [doc/migrations/MIGRATION_BATCH_211.md](migrations/MIGRATION_BATCH_211.md)
- **Engines:** `SGDK_Engines/`
- **Projetos:** `SGDK_projects/`
