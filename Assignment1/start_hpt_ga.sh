#!/bin/bash

qsub -N ga-hpt -l h_vmem=2G -r y -pe pthreads 11 -e ~/ga_00.txt -o ~/ga_01.txt ~/HOTWS22/Assignment1/hpt_ga.sh
