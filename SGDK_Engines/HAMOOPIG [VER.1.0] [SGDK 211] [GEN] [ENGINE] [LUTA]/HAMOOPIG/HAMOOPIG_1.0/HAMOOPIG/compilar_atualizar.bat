del /Q C:\GENDK\HAMOOPIG\out\res\*.*
del /Q C:\GENDK\HAMOOPIG\out\src\*.*
del /Q C:\GENDK\HAMOOPIG\out\watchers\*.*
del /Q C:\GENDK\HAMOOPIG\out\rom.bin
del /Q C:\GENDK\HAMOOPIG\out\rom.out
del /Q C:\GENDK\HAMOOPIG\out\rom_head.bin
del /Q C:\GENDK\HAMOOPIG\out\rom_head.o
del /Q C:\GENDK\HAMOOPIG\out\sega.o
del /Q C:\GENDK\HAMOOPIG\out\sysbol.txt
C:\sgdk\bin\make -f C:\sgdk\makefile.gen
C:\GAMES\Bizhawk\EmuHawk C:\GENDK\HAMOOPIG\out\rom.bin