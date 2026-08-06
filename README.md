# SGDK Forge

Framework de código aberto para iniciar, organizar e validar projetos de Mega Drive
com **SGDK 2.11**. Ele reúne um template de projeto, um wrapper de build, regras
para agentes de IA e contratos que evitam resultados tecnicamente enganosos.

> Esta é uma distribuição de **código-fonte e ferramentas**. Não é uma coleção de
> ROMs prontas nem a entrega de um jogo. Uma ROM só é considerada entregue após
> build, validação e evidência recente no BlastEm.

## Baixar

Escolha uma das opções:

- [Release estável mais recente](https://github.com/Misael-art/SGDK-Forge/releases/latest): arquivo ZIP/TAR gerado pelo GitHub para a tag publicada.
- [Código da main](https://github.com/Misael-art/SGDK-Forge/archive/refs/heads/main.zip): versão em desenvolvimento.
- Clone com Git:

```bash
git clone https://github.com/Misael-art/SGDK-Forge.git
cd SGDK-Forge
```

## O que vem no repositório

| Componente | Para que serve |
|---|---|
| `tools/sgdk_wrapper/` | Ponto central de build, validação e criação de projetos. |
| `tools/sgdk_wrapper/modelo/` | Template copiável para um novo projeto SGDK. |
| `tools/sgdk_wrapper/.agent/` | Regras, workflows e skills canônicas para agentes. |
| `SGDK_projects/FORGE_REFERENCE.../` | Fixture técnica neutra que demonstra contratos de telemetria. |
| `doc/` | Diretrizes, memória operacional e referências de produção. |
| `sdk/README.md` | Como disponibilizar o SDK SGDK 2.11 no seu computador. |

Os binários do SGDK e emuladores não fazem parte desta release de fonte. A pasta
`sdk/` explica como apontar `GDK` para uma instalação local ou instalar o SGDK
2.11 em `sdk/sgdk-2.11`.

## Início rápido

### 1. Prepare o ambiente

Para executar os checks desta release, instale:

- Python 3.10 ou superior;
- PowerShell 7 (`pwsh`) para o runner integrado;
- Git.

Para compilar uma ROM, instale também uma distribuição válida do **SGDK 2.11** e
configure `GDK` para sua pasta. Confirme que `makefile.gen` existe dentro dela.
Leia [sdk/README.md](sdk/README.md) antes de tentar o primeiro build.

No Windows, a rota de build documentada pelo wrapper usa `cmd` e caminho absoluto:

```bat
cmd /c "C:\caminho\para\SGDK-Forge\tools\sgdk_wrapper\build.bat C:\caminho\para\meu-projeto"
```

No Linux, esta release permite executar os checks de framework. A rota de build
portável para SGDK ainda não foi certificada nesta `main`; não a trate como prova
de ROM, desempenho ou compatibilidade com emulador.

### 2. Valide a instalação baixada

Execute estes comandos na raiz do repositório:

```bash
python3 tools/sgdk_wrapper/ci/test_canonical_fixture_contracts.py
python3 tools/sgdk_wrapper/ci/test_project_learning_loop.py
pwsh -NoProfile -File tools/sgdk_wrapper/ci/run_canonical_fixture_gates.ps1
```

O resultado esperado é **10/10** nos contratos de fixture e **36/36** nos checks
de vínculo de evidência. Esses testes usam apenas a biblioteca padrão do Python.

### 3. Crie um projeto

No Windows, use o template canônico:

```bat
tools\sgdk_wrapper\new_project.bat "MEU_JOGO [VER.001] [SGDK 211] [GEN] [GAME] [ACAO]"
```

Depois, abra o diretório criado em `SGDK_projects/`, revise
`.mddev/project.json` e `doc/10-memory-bank.md`, e mantenha assets brutos em
`res/data/`. A convenção completa de nomes está em
[doc/PADRAO_NOMENCLATURA.md](doc/PADRAO_NOMENCLATURA.md).

## Como ler os status corretamente

| Status | O que significa |
|---|---|
| `documentado` | Existe em documentação; ainda não há execução. |
| `implementado` | Código existe, mas não foi compilado. |
| `buildado` | Compilou; ainda não prova runtime. |
| `testado_em_emulador` | A ROM correspondente foi observada com evidência rastreável. |
| `validado_budget` | VRAM, DMA e pressão de sprites foram medidos. |

Regra principal: **“Se não foi visto rodando no emulador, não existe.”** Build
verde, screenshot isolada ou documentação não substituem evidência de runtime.

## Contratos de fixture incluídos

O `FORGE_REFERENCE` e `canonical_fixture_gate.py` protegem sete pontos comuns de
falso verde:

1. amostragem vazia não passa;
2. telemetria obrigatória ausente falha;
3. playtest mede estado observado pela ROM;
4. legalidade de cor usa CRAM, não apenas screenshot;
5. evidências precisam apontar para o mesmo SHA-256 da ROM;
6. tabelas estáticas não podem refazer trabalho ou DMA sem mudança;
7. contrato estático não pode alegar readiness de feature.

Uma fixture aprovada continua com `ready_for_aaa=false`. Veja
[canonical_fixture_contracts.md](tools/sgdk_wrapper/.agent/references/canonical_fixture_contracts.md)
e o [README da referência](SGDK_projects/FORGE_REFERENCE%20[VER.001]%20[SGDK%20211]%20[GEN]%20[LAB]%20[TECHDEMO]/README.md).

## Antes de entregar uma ROM

O fluxo de produção exige, no mínimo:

1. build concluído e `out/rom.bin` identificado;
2. relatório de validação limpo;
3. boot da mesma ROM no BlastEm;
4. gameplay, desempenho e áudio observados;
5. orçamento VDP/VRAM/DMA revisado quando aplicável;
6. `doc/10-memory-bank.md` e changelog atualizados.

Os workflows canônicos ficam em
[`tools/sgdk_wrapper/.agent/workflows/`](tools/sgdk_wrapper/.agent/workflows/).

## Escopo da release v0.1.0

`v0.1.0` distribui o framework, o template, o `FORGE_REFERENCE` e os testes de
contratos. Ela não contém ROM distribuível, evidência BlastEm, benchmark de 60 fps
ou selo AAA. O gate rastreável está em
[doc/releases/v0.1.0-source-release-gate.md](doc/releases/v0.1.0-source-release-gate.md).

## Licença

Consulte [LICENSE](LICENSE).
