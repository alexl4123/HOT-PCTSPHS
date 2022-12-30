#!/bin/bash

qsub -N init-hpt -l longrun=1 -r y -pe pthreads 11 -e ~/init_00.txt -o ~/init_01.txt ~/HOTWS22/Assignment1/hpt_ga_init.sh
