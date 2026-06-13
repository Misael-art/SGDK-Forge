#!/usr/bin/env pwsh
# imagegen_tool.ps1
# Wrapper PowerShell para imagegen_tool.py
# Uso: .\imagegen_tool.ps1 [status|install|route|generate|convert|healthcheck] [args]

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Base = & python -c "import sys; print(sys.executable)"

# Forward all arguments to Python script
& python "$ScriptDir\imagegen_tool.py" @args
