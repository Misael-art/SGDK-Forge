del /Q C:\GENDK\TaiketsuUltraHeroGenesis\out\res\*.*
del /Q C:\GENDK\TaiketsuUltraHeroGenesis\out\src\*.*
del /Q C:\GENDK\TaiketsuUltraHeroGenesis\out\watchers\*.*
del /Q C:\GENDK\TaiketsuUltraHeroGenesis\out\rom.bin
del /Q C:\GENDK\TaiketsuUltraHeroGenesis\out\rom.out
del /Q C:\GENDK\TaiketsuUltraHeroGenesis\out\rom_head.bin
del /Q C:\GENDK\TaiketsuUltraHeroGenesis\out\rom_head.o
del /Q C:\GENDK\TaiketsuUltraHeroGenesis\out\sega.o
del /Q C:\GENDK\TaiketsuUltraHeroGenesis\out\sysbol.txt
C:\sgdk\bin\make -f C:\sgdk\makefile.gen
C:\GAMES\Bizhawk\EmuHawk C:\GENDK\TaiketsuUltraHeroGenesis\out\rom.bin