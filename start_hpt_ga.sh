#!/bin/bash

qsub -N m-ga-hpt -l h_vmem=2G -r y -pe pthreads 11 -e ~/m_ga_00.txt -o ~/m_ga_01.txt ~/HOTWS22/Assignment1/hpt_ga.sh
