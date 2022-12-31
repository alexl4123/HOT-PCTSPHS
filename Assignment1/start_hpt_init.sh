#!/bin/bash

qsub -N m-init-hpt -l longrun=1 -r y -pe pthreads 11 -e ~/m_init_00.txt -o ~/m_init_01.txt ~/HOTWS22/Assignment1/hpt_ga_init.sh
