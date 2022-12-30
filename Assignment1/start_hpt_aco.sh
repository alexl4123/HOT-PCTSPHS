#!/bin/bash

qsub -N aco-hpt -r y -pe pthreads 11 -l longrun=1 -e ~/aco_00.txt -o ~/aco_01.txt ~/HOTWS22/Assignment1/hpt_aco.sh
