#!/bin/bash

qsub -N n-aco-benchmark -r y -pe pthreads 8 -l longrun=1 -e ~/n_aco_benchmark_00.txt -o ~/n_aco_benchmark_01.txt ~/HOTWS22/Assignment1/benchmark_aco.sh
