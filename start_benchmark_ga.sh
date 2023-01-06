#!/bin/bash

qsub -N ga-benchmark -r y -pe pthreads 8 -l longrun=1 -e ~/ga_benchmark_00.txt -o ~/ga_benchmark_01.txt ~/HOTWS22/Assignment1/benchmark_ga.sh
