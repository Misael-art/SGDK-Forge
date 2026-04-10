# SGDK Wrapper - Build Automation System

Sistema centralizado de build para projetos SGDK com validacao, auto-fix e preparacao automatica de assets.

## Solucao canonica

O fluxo oficial deste workspace e:

1. guardar os assets brutos em `res/data/`;
2. deixar o wrapper preparar a versao final em `res/`;
3. usar `res/data/backup/` como trilha de seguranca antes de qualquer correcao ou sobrescrita;
4. manter o projeto derivado de `tools/sgdk_wrapper/modelo`.

Esse padrao existe para separar origem bruta e saida final, permitir repetibilidade em projetos humanos e assistidos por IA, e evitar que um build "conserte" imagens sem deixar rastro.

## O que ele faz

1. Centraliza a logica de build em um unico lugar.
2. Configura o ambiente automaticamente via `env.bat`.
3. Detecta e corrige erros comuns de recurso e migracao.
4. Pode preparar assets brutos a partir de `res/data/`, espelhando para `res/`.
5. Pode mover backups automaticamente para `res/data/backup/` antes de sobrescrever ou corrigir arquivos.
6. Pode sanitizar imagens ja geradas em `res/`.
7. Mantem o pipeline reutilizavel entre projetos.

## Modelo oficial

`tools/sgdk_wrapper/modelo` e a base de referencia para novos projetos.

Ele entrega:
- worktree completo e copiavel;
- wrappers locais prontos para localizar o `sgdk_wrapper`;
- `res/data/` e `res/data/backup/` ja criados;
- codigo C inicial, pedagogico e compilavel;
- documentacao explicando arquitetura, build e pipeline de assets.

Se a ideia for iniciar um projeto novo, copie o conteudo de `modelo` para `SGDK_projects/<nome-do-projeto>` e trabalhe a partir dali.

## Modos de operacao

### Build normal

```bat
call "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\build.bat"
```

### Preparacao automatica de assets

Ative quando o projeto tiver imagens brutas em `res/data/` ou, em projetos legados, em `data/`.

```bat
set SGDK_AUTO_PREPARE_ASSETS=1
call "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\build.bat"
```

Fluxo:
1. Escaneia `res/` e corrige imagens incompativeis, salvando o original em `res/data/backup/`.
2. Escaneia `res/data/` recursivamente, ignorando `res/data/backup/`.
3. Converte e espelha os arquivos para `res/`, mantendo subpastas e nomes.
4. Se `res/data/` estiver vazio, faz fallback para o modo legado baseado em `data/` + `res/*.res`.
5. Salva `out/logs/asset_preparation_report.json`.
6. Salva `out/logs/asset_preparation.log`.
7. Salva `out/logs/asset_preparation_preview.png`.
8. Se a confianca da extracao for baixa, o build falha cedo com diagnostico.

Com isso, o wrapper deixa de atuar apenas como "sanitizador final" e passa a operar como uma esteira de preparo de assets com backup, relatorio e rastreabilidade.

### Sanitizacao proativa

Ative quando quiser que o wrapper corrija conformidade tecnica dos PNGs em `res/` antes do `make`.

```bat
set SGDK_AUTO_FIX_RESOURCES=1
call "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\build.bat"
```

## Logs importantes

- `out/logs/build_output.log`: saida completa do `make` e do `rescomp`.
- `out/logs/build_debug.log`: acoes executadas pelos scripts do wrapper.
- `out/logs/validation_report.json`: resultado estruturado da validacao.
- `out/logs/asset_preparation_report.json`: relatorio estruturado da preparacao automatica.
- `out/logs/asset_preparation.log`: log textual, pedagogico e cronologico da preparacao.
- `out/logs/asset_preparation_preview.png`: previa visual dos recortes/crops escolhidos.

## Scripts principais

- `build.bat`: ponto de entrada do wrapper.
- `build_inner.bat`: orquestracao do pipeline.
- `prepare_assets.py`: extracao automatica de sprite sheets e backgrounds.
- `validate_resources.ps1`: validacao de `SPRITE` e `IMAGE`.
- `ensure_safe_image.ps1`: sanitizacao final sem heuristica destrutiva de `(0,0)`.
- `fix_transparency.ps1`: correcao reativa usando o sanitizador central.

## Observacoes

- O wrapper nao tenta adivinhar assets com baixa confianca: nesse caso ele falha e gera diagnostico.
- `SGDK_AUTO_PREPARE_ASSETS=1` e `SGDK_AUTO_FIX_RESOURCES=1` podem ser usados juntos.
- O caminho recomendado para novos projetos e deixar os brutos em `res/data/` e o wrapper gerar a saida final em `res/`.
- O diretorio `res/data/backup/` e reservado para snapshots dos arquivos antigos antes da correcao ou sobrescrita.
