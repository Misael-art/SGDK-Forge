Title ISGDK - AFSBLOOD
Color 1F
@echo off
cls

cd\
cd "C:\GENDK\project01_sgdk-ssfmapper\src\"
CLS
ECHO ================================================================================
ECHO                             ISGDK - AFSBLOOD - 2020
ECHO                        ARQUIVO TEMPORARIO DE COMPILACAO
Echo.
ECHO ================================================================================
ECHO DATA DO ARQUIVO: 29/08/2022 - 12:09:57
Echo.
ECHO ================================================================================
ECHO --------------------------------------------------------------------------------
%GDK_WIN%\bin\make -f %GDK_WIN%\makefile.gen
Echo.
ECHO   ----------------------------------------------------------------------------
ECHO   ROM = C:\GENDK\project01_sgdk-ssfmapper\src\out\rom.bin
ECHO   ----------------------------------------------------------------------------
Echo.
Pause
DEL compilar.bat
