# Migração Shadow Dancer Hamoopig [SGDK 160] → [SGDK 211]

**Data:** 2026-03-09  
**Projeto:** Shadow Dancer Hamoopig [VER.1.0] [SGDK 211] [GEN] [ENGINE] [PLATAFORMA]  
**Status:** Concluído

---

## Para quem não é técnico – O que é este projeto

Este projeto é uma **engine de jogo de plataforma** no estilo Shadow Dancer (ninja, ação) para **Mega Drive**, desenvolvida com o **SGDK** (Sega Genesis Development Kit). A “conversão” aqui significa **alinhar o projeto às ferramentas centrais do repositório MegaDrive_DEV**: assim você pode **compilar e rodar o jogo com um duplo clique**, sem precisar configurar manualmente o SDK nem o Makefile.

---

## O que foi alterado

| Antes | Depois |
|-------|--------|
| Makefile próprio apontando para `../_sgdk200` | Uso do **wrapper** centralizado em [tools/sgdk_wrapper](../tools/sgdk_wrapper) |
| Compilação manual com `make` e caminho local do SDK | SDK central: `sdk/sgdk-2.11` (definido em [tools/sgdk_wrapper/env.bat](../tools/sgdk_wrapper/env.bat)) |
| Sem scripts de build no projeto | **build.bat**, **clean.bat**, **run.bat**, **rebuild.bat** na raiz do projeto, que apenas chamam o wrapper |

Nenhuma lógica de build foi duplicada no projeto: toda a lógica está no wrapper.

---

## Como compilar e rodar (passo a passo)

1. **Abrir a pasta do projeto**  
   Navegue até:  
   `Shadow Dancer Hamoopig [VER.1.0] [SGDK 211] [GEN] [ENGINE] [PLATAFORMA]`.

2. **Compilar**  
   Dê **duplo clique** em **`build.bat`**.  
   (Se não existir ROM ainda, você pode usar **`run.bat`**: ele compila e depois abre o emulador.)

3. **Rodar a ROM**  
   Dê **duplo clique** em **`run.bat`** para abrir o emulador com a ROM gerada.

4. **Limpar e recompilar**  
   Execute **`clean.bat`** e em seguida **`build.bat`**.  
   Ou use **`rebuild.bat`**, que faz os dois em sequência.

---

## Estrutura do projeto após conversão

```
Shadow Dancer Hamoopig [VER.1.0] [SGDK 211] [GEN] [ENGINE] [PLATAFORMA]/
├── build.bat          # Atalho para o wrapper (compilar)
├── clean.bat          # Atalho para o wrapper (limpar)
├── run.bat            # Atalho para o wrapper (rodar ROM)
├── rebuild.bat        # clean + build
├── README.md
├── Makefile.old       # Makefile antigo (renomeado; o wrapper usa makefile.gen do SDK)
├── src/               # Código-fonte C
│   └── boot/
│       ├── rom_head.c
│       └── sega.s.old # Boot antigo (incompatível com SGDK 2.11); o build usa o sega.s do SDK
├── res/               # Recursos
│   ├── gfx.res
│   ├── sprite.res
│   └── sound.res
└── out/               # ROM gerada (rom.bin) após build
```

O wrapper está em `..\..\tools\sgdk_wrapper` (dois níveis acima da pasta do projeto).

---

## Pré-requisitos

- **Java** instalado (necessário para o ResComp, que compila recursos).
- **Ambiente configurado:** na raiz do MegaDrive_DEV, execute **`setup-env.bat`** na primeira vez (ou se aparecer erro “GDK not defined”).

---

## Problemas comuns

| Problema | Solução |
|----------|---------|
| **“GDK not defined”** | Execute `setup-env.bat` na raiz do MegaDrive_DEV e reabra o terminal. |
| **Erros de sprite / transparência em PNG** | O wrapper tenta correção automática (fix_transparency, autofix_sprite_res). Se falhar, consulte [tools/sgdk_wrapper/README.md](../../tools/sgdk_wrapper/README.md) e [doc/AGENTS.md](../AGENTS.md) (checklist de migração). |
| **APIs deprecadas (VDP_setPalette, etc.)** | O script `fix_migration_issues.ps1` é executado no build e substitui por PAL_* e SPR_FLAG_AUTO_VRAM_ALLOC. Se ainda aparecer erro em `build_output.log`, aplicar correção pontual no código e documentar aqui. |

---

## Referências

- [doc/README.md](../README.md) – Índice da documentação  
- [doc/AGENTS.md](../AGENTS.md) – Checklist de migração e fila de projetos  
- [tools/sgdk_wrapper/README.md](../../tools/sgdk_wrapper/README.md) – Wrapper e troubleshooting  
- [MIGRATION_MSU_EXAMPLE.md](MIGRATION_MSU_EXAMPLE.md) – Exemplo de migração com scripts canônicos  
- [BLAZE_ENGINE_FIX_REPORT.md](BLAZE_ENGINE_FIX_REPORT.md) – Relatório de correção (sprite.res, paleta, migração SGDK 211)

---

## Notas de build e validação

### Correção aplicada: `src/boot/sega.s` incompatível com SGDK 2.11

O projeto trazia um `sega.s` customizado que referencia callbacks de exceção (`privilegeViolationCB`, `traceCB`, `line1x1xCB`, `errorExceptionCB`, etc.) não presentes na biblioteca do SGDK 2.11, gerando erros de link:

```
undefined reference to `privilegeViolationCB'
undefined reference to `traceCB'
undefined reference to `line1x1xCB'
undefined reference to `errorExceptionCB'
```

**Solução:** O arquivo `src/boot/sega.s` do projeto foi renomeado para `src/boot/sega.s.old` (cópia mantida para referência). O makefile do SDK passa a usar o `sega.s` padrão do SGDK 2.11 (copiado de `sdk/sgdk-2.11/src/boot/sega.s` quando ausente no projeto), compatível com `libmd.a`.

### Resultado da compilação (2026-03-09)

- **clean.bat** e **build.bat** executados com sucesso.
- **out/rom.bin** gerado.
- Wrapper aplicou correções automáticas em `gfx.res` (opt_type para `spr_element_lvl12A`); `sprite.res` e `sound.res` sem alterações adicionais.
- **run.bat** e **rebuild.bat** validados: rebuild (clean + build) conclui sem erro; **out/rom.bin** gerado.

Para restaurar o boot antigo (não recomendado): renomear `sega.s.old` de volta para `sega.s`; o link voltará a falhar sem as rotinas correspondentes na lib do SGDK 2.11.
