#!/bin/bash

qsub -N aco-hpt -r y -pe pthreads 21 -l longrun=1 -e ~/stat_aco_00.txt -o ~/stat_aco_01.txt ~/HOTWS22/Assignment1/stat_aco.sh
