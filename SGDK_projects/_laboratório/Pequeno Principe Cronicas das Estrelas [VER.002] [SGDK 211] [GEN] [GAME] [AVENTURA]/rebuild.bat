@echo off
REM =========================================================================
REM rebuild.bat - Delegacao canonica para tools\sgdk_wrapper
REM NUNCA adicione logica aqui. Centralize no wrapper.
REM =========================================================================
call "%~dp0..\..\tools\sgdk_wrapper\rebuild.bat" "%~dp0"
exit /b %errorlevel%
