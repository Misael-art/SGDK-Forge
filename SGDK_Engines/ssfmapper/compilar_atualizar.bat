del /Q C:\GENDK\_project01_template\out\res\*.*
del /Q C:\GENDK\_project01_template\out\src\*.*
del /Q C:\GENDK\_project01_template\out\watchers\*.*
del /Q C:\GENDK\_project01_template\out\rom.bin
del /Q C:\GENDK\_project01_template\out\rom.out
del /Q C:\GENDK\_project01_template\out\rom_head.bin
del /Q C:\GENDK\_project01_template\out\rom_head.o
del /Q C:\GENDK\_project01_template\out\sega.o
del /Q C:\GENDK\_project01_template\out\sysbol.txt
C:\sgdk\bin\make -f C:\sgdk\makefile.gen
copy /y .\out\rom.bin .\rom.bin

C:\GENDK\emuladores\Blastem\Blastem.exe "./rom.bin" 



pause