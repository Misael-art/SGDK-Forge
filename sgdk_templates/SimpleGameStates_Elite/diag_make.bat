@echo off
setlocal
call "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\env.bat"
echo --- GDK: %GDK% ---
echo --- GDK_WIN: %GDK_WIN% ---
echo --- PATH: %PATH% ---
echo.
echo Running make with debug info...
make -f "%GDK%/makefile.gen" -p | findstr "SRC_C = OBJS ="
echo.
echo Checking src directory...
dir src /s /b
endlocal
