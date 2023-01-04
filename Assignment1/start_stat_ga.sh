#!/bin/bash

qsub -N ga-stat -r y -pe pthreads 8 -e ~/stat_ga_00.txt -o ~/stat_ga_01.txt ~/HOTWS22/Assignment1/stat_ga.sh
