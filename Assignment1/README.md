# Prize Collecting Travelling Salesperson Problem with Hotel Selection (PCTSPHS)

The implementation of the programming assignments of the lecture Heuristic Optimization Techniques (192.137), which uses metaheuristics to tackle the PCTSPHS problem.

## How to execute the framework?

You need to have python and type `python start.py`

Note that you HAVE TO BE in the top lvl. directory to execute it, otherwise it won't work due to imports.

## Help/Arguments

By typing `python start.py --help` you can access the help page, although it is noted, that in the current version (hand-in 1) not all possible commands are shown, but generally the following options exist:

- Mode: Specifies which experiment/algorithm to run (e.g. --mode 5 for GVNS)

- Instance: To specify which instance shall be executed (instances are located in `tsp_instances/`), (e.g. `--instance tsp_instances/00_test.txt`  OR `--instance benchmark` to run all instances)

- Randomization factor: Only available for the randomized construction heuristic and the grasp (by `--randomization-factor`, e.g. `--randomization-factor 5`)

## Where are the files necessary for the hand in?

Inside the `hand_in` folder one can find the best solutions for each instance and each experiment/algorithm and further the data-analysis (Jupyter-Notebooks).

## Other general structure of the source files:

### start

The start.py file is the entry point into the program,

### Framework

The framework folder contains the `heart` of the project, i.e. the loading, parsing, etc. of the instnaces, the instance representation, the solution representation, the delta evaluation, the slow-solution-evaluation, etc.

### construction_heuristics

This folder contains everything that can be related to the construction heuristics, for instance our backtracking.

### search_algorithms

This folder contains our meta-heuristics.

### neighborhoods

This folder contains all used neighborhoods (with the exception of the ''shaking'' neighborhood for GVNS)

### tsp_instances

This folder contains all the instances, sorted by instance size.

### stp_instances_solutions

After execution the results are printed to this folder.

### hand_in

Hand in folder and experiment analysis.

# Requirements

We do not provide a full list of requirements, at the moment you have to have ''luck'' that all are installed, if not python will complain anyway and you can install them by carefully reading the error message and then installing them via `pip`.

