@echo off
setlocal

REM Obtém o caminho completo do diretório atual
set "current_path=%cd%"

REM Extrai apenas o nome do diretório atual
for %%F in ("%current_path%") do set "current_directory=%%~nF"

REM Extrai o caminho anterior
for %%F in ("%current_path%") do set "base_path=%%~dpF"

REM Remove a barra final do caminho base (se necessário)
set "BASE_GAME_PATH=%%~dpF"

REM Remove a barra final do caminho base (se necessário)
set "base_path=%base_path:~0,-1%"

REM Define o diretório de requisitos como o caminho do diretório atual
set "REQUIREMENTS_DIR=%~dp0"
set "COMPILE_NAME=%~n0"

set "EMULADOR_GENS=C:\GENDK\_emuladores\GensKMod\gens.exe"
set "EMULADOR_BIZHAWK=C:\GENDK\_emuladores\Bizhawk\EmuHawk"
set "EMULADOR_GENS=C:\GENDK\_emuladores\Blastem\Blastem.exe"
set "EMULADOR_GENS=C:\GENDK\_emuladores\Exodus_2.1\Exodus.exe"

echo --------------------  -------------------- 
echo "                                        "
echo ROM COPILADA EM : %REQUIREMENTS_DIR%out\rom.bin 
echo COMANDO PARA COPILAR : %GDK_WIN%\bin\make -f %GDK_WIN%\makefile.gen
echo "                                        "


echo --------------------  -------------------- 
REM Exibe os resultados
echo APP   : %COMPILE_NAME%
echo LOCAL : %current_directory%
echo BASE  : %base_path%
echo --------------------  -------------------- 
echo "                                        "

echo CLEAR  : APAGANDO INFORMAÇÕES DA COPILAÇÃO ANTERIOR SE HOUVER
echo "                                        "

REM Limpa os arquivos do diretório "out"
del /Q "%REQUIREMENTS_DIR%\out\res\*.*" >nul 2>&1
del /Q "%REQUIREMENTS_DIR%\out\src\*.*" >nul 2>&1
del /Q "%REQUIREMENTS_DIR%\out\watchers\*.*" >nul 2>&1
del /Q "%REQUIREMENTS_DIR%\out\rom_head.bin" >nul 2>&1
del /Q "%REQUIREMENTS_DIR%\out\rom_head.o" >nul 2>&1
del /Q "%REQUIREMENTS_DIR%\out\sega.o" >nul 2>&1
del /Q "%REQUIREMENTS_DIR%\out\sysbol.txt" >nul 2>&1

echo BACKUP  : FAZENDO BACKUP DE SEGURANÇA DA ROM ANTERIOR CASO EXISTA

REM Verifica se o arquivo rom.bin já existe e salva versões se necessário 
set "latest_rom=%REQUIREMENTS_DIR%out\rom.bin" 
if exist "%REQUIREMENTS_DIR%out\rom.bin" (
 setlocal enabledelayedexpansion
 set /a version=1 
 
 REM Obtém a data atual no formato YYYYMMDD 
 for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set "datetime=%%I"
 set "date_str=!datetime:~0,8!"
 
 REM Loop para encontrar a próxima versão disponível 
 :loop 
 if exist "%REQUIREMENTS_DIR%out\rom_v!version!_!date_str!.bin" (
 set /a version+=1 goto loop ) 
 REM Renomeia o arquivo rom.bin para a versão encontrada com a data 
 rename "%REQUIREMENTS_DIR%out\rom.bin" "rom_v!version!_!date_str!.bin" endlocal )


echo COPILAÇÃO  : INICIANDO COPILAÇÃO DA ROM DE MEGA DRIVE
echo "                                        "


REM Executa o comando de compilação
%GDK_WIN%\bin\make -f %GDK_WIN%\makefile.gen

REM Verifica se um novo rom.bin foi criado e define como o arquivo mais recente
if exist "%REQUIREMENTS_DIR%out\rom.bin" (
    set "latest_rom=%REQUIREMENTS_DIR%out\rom.bin"
)

echo --------------------  -------------------- 
echo "                                        "

echo LANÇANDO ROM  : "%latest_rom%"
echo EMULADOR USADO : "%EMULADOR_BIZHAWK%"

REM Executa o último arquivo ROM criado no emulador
%EMULADOR_BIZHAWK% "%latest_rom%"