#!/bin/bash

# compilation

# https://github.com/Franticware/SGDK_wine
# git clone https://github.com/Franticware/SGDK_wine.git
# cp SGDK_wine/generate_wine.sh ./
# git clone https://github.com/Stephane-D/SGDK.git




# PATH_TO_SGDK=/run/media/mmcblk0p1/steamapps/dev/SGDK
#cp generate_wine.sh $PATH_TO_SGDK/bin
# cd $PATH_TO_SGDK/bin
# sh generate_wine.sh
make GDK=$PATH_TO_SGDK -f $PATH_TO_SGDK/makefile_wine.gen


 # --------------


# cd /home/gustavo/apps/sgdk/bin
# sh generate_wine.sh
# cd /home/gustavo/apps/sgdk/bin/sample/sprite
# make GDK=/home/gustavo/apps/sgdk -f /home/gustavo/apps/sgdk/makefile_wine.gen

