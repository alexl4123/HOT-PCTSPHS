#!/bin/bash

qsub -N aco-benchmark -r y -pe pthreads 21 -l longrun=1 -e ~/benchmark_aco_00.txt -o ~/benchmark_aco_01.txt ~/HOTWS22/Assignment1/stat_aco.sh
