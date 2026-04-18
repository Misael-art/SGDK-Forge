@echo off
REM Override local para evitar estouro do ResComp em maquinas com pagefile mais restrito.
REM O wrapper global continua defaultando para 2g quando nenhum projeto pedir ajuste.
set "JAVA_OPTS=-Xmx1024m"
