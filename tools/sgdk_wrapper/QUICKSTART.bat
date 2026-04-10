@echo off
REM Quick reference for SGDK Wrapper usage
REM
REM IMPORTANT: Each project's build.bat should call the sgdk_wrapper
REM
REM Usage Examples:
REM
REM   1. From project directory:
REM      cd your_project_dir
REM      call "%~dp0build.bat"
REM
REM   2. From any directory with project path:
REM      call "%~dp0build.bat" "your_project_dir"
REM
REM   3. Clean build:
REM      call "%~dp0clean.bat"
REM      call "%~dp0build.bat"
REM
REM   4. Manutencao - garantir que todos os .bat deleguem ao wrapper:
REM      call "%~dp0ensure_bats.bat"        (auditoria)
REM      call "%~dp0ensure_bats.bat" -Fix  (corrigir desalinhamentos)
REM
REM For full documentation, see:
REM   tools/sgdk_wrapper/README.md
REM   tools/image-tools/README.md
