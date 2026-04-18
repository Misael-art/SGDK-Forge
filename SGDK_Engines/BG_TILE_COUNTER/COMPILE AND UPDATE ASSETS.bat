del /Q C:\GENDK\BG_TILE_COUNTER\out\res\*.*
del /Q C:\GENDK\BG_TILE_COUNTER\out\src\*.*
del /Q C:\GENDK\BG_TILE_COUNTER\out\watchers\*.*
del /Q C:\GENDK\BG_TILE_COUNTER\out\rom.bin
del /Q C:\GENDK\BG_TILE_COUNTER\out\rom.out
del /Q C:\GENDK\BG_TILE_COUNTER\out\rom_head.bin
del /Q C:\GENDK\BG_TILE_COUNTER\out\rom_head.o
del /Q C:\GENDK\BG_TILE_COUNTER\out\sega.o
del /Q C:\GENDK\BG_TILE_COUNTER\out\sysbol.txt
C:\sgdk\bin\make -f C:\sgdk\makefile.gen
C:\GAMES\Bizhawk\EmuHawk C:\GENDK\BG_TILE_COUNTER\out\rom.bin