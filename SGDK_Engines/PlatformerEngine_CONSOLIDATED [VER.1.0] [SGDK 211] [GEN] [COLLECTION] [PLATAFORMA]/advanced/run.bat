@echo off
REM =========================================================================
REM advanced/run.bat - Delegacao canonica para tools\\sgdk_wrapper
REM NUNCA adicione logica aqui. Centralize no wrapper.
REM =========================================================================
call "%~dp0..\..\.\tools\sgdk_wrapper\run.bat" "%~dp0"
exit /b %errorlevel%
