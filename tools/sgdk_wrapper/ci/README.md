# CI sugerido — SGDK wrapper

## Pre-flight e validacao em projeto de referencia

Script local (Windows / PowerShell):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\ci\run_golden_validate.ps1"
```

- Executa `preflight_host.ps1` (exit code **2** = avisos opcionais apenas, tratado como sucesso).
- Executa `validate_resources.ps1` com `-WorkDir` no projeto dourado definido no proprio script.

Ajuste a variavel `$GoldenProjectRelative` em `run_golden_validate.ps1` se o projeto de referencia mudar.

## GitLab CI (opcional)

Runner **Windows** com MSYS2/SGDK no PATH. Job de exemplo:

```yaml
sgdk_preflight:
  stage: test
  tags:
    - windows
  script:
    - powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_golden_validate.ps1
```

Sem runner Windows, mantenha a validacao via script local ou pipeline propria.
