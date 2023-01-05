import sys
import logging
import argparse
import os
from os.path import isfile, join

from pathlib import Path

from framework.constants import logger_name, file_path_to_solutions
from framework.input_file_parser import Input_File_Parser
from framework.solution import Solution, Delta
from framework.test_instances import Tester

from construction_heuristics.greedy_nearest_neighbor_initialization import Greedy_Nearest_Neighbor_Initialization
from construction_heuristics.backtracking_search import Backtracking_Search
from construction_heuristics.combination_of_heuristics import Combination_Of_Heuristics

from neighborhoods.neighborhood import Neighborhood
from neighborhoods.trip_2_opt import Trip_2_Opt
from neighborhoods.remove_customer import Remove_Customer
from neighborhoods.add_customer import Add_Customer
from neighborhoods.swap_served_unserved_customer import Swap_Served_Unserved_Customer
from neighborhoods.interchange_customers import Interchange_Customers
from neighborhoods.insert_customer import Insert_Customer
from neighborhoods.remove_hotel import Remove_Hotel
from neighborhoods.add_hotel import Add_Hotel
from neighborhoods.exchange_hotel import Exchange_Hotel
from neighborhoods.move_hotel import Move_Hotel

from search_algorithms.local_search import Local_Search, Step_Function_Type
from search_algorithms.vnd import Vnd
from search_algorithms.grasp import Grasp
from search_algorithms.gvns import Gvns
from search_algorithms.ant_colony_optimization import Ant_Colony_Optimization
from search_algorithms.ga.genetic_algorithm import Genetic_Algorithm
from search_algorithms.ga.fitness_function import Fitness_Function
from search_algorithms.ga.constant_weights import Constant_Weights
from search_algorithms.ga.linear_weights import Linear_Weights
from search_algorithms.ga.linear_sequence_weights import Linear_Sequence_Weights
from search_algorithms.ga.ga_initialization_procedure.construction_builder import Construction_Builder

from hyper_parameter_tuning.hyper_parameter_tuning import Hyper_Parameter_Tuning
from statistical_test.statistical_test import Statistical_Test
from benchmark.benchmark import Benchmark

class Start_PCTSPHS:

    def __init__(self):

        self._instances = []

        self._benchmark_instances_path = 'tsp_instances/00_batch_1_2/'
        self._default_instance = 'tsp_instances/00_batch_1_2/00_test.txt'

        self._max_runtime = 15*60 #seconds

    def start(self):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(levelname)s][%(asctime)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        self._logger = logger

        parser = argparse.ArgumentParser(description="The problem ''Prize Collecting Traveling Salesperson Problem with Hotel Selection'' (PCTSPHS) is tackled with several heurstic solving techniques, like local search or variable neighborhood descent.", add_help=True, formatter_class=argparse.RawTextHelpFormatter)  

        subparsers = parser.add_subparsers(help="sub-command help", dest='subparser_name')

        self.initialize_construction_parser(subparsers)
        self.initialize_random_construction_parser(subparsers)
        self.initialize_local_search_parser(subparsers)
        self.initialize_grasp_parser(subparsers)
        self.initialize_vnd_parser(subparsers)
        self.initialize_gvns_parser(subparsers)
        self.initialize_ga_parser(subparsers)
        self.initialize_aco_parser(subparsers)
        self.initialize_evaluate_solution_parser(subparsers)
        
        args = parser.parse_args()

        if not args.subparser_name:
            print("You must specify which algorithm you want to use, by adding one of the following choices (the integer or name, both work): {0=construction,1=rand-construction,2=local-search,3=GRASP,4=VND,5=GVNS, 6=GA, 7=ACO}. E.g. use: 'start.py 0' for the construction heuristic.")
            quit()


        self.algorithm_selector(args)




    def initialize_construction_parser(self, subparsers):
        construction_0 = subparsers.add_parser("CONSTRUCTION",help="construction-heuristic")
        construction_1 = subparsers.add_parser("0",help="construction-heuristic")

        self.add_instance_arg(construction_0)
        self.add_instance_arg(construction_1)

    def initialize_random_construction_parser(self, subparsers):
        random_construction_0 = subparsers.add_parser("RAND-CONSTRUCTION",help="randomized construction-heuristic")
        random_construction_1 = subparsers.add_parser("1",help="randomized construction-heuristic")

        self.add_instance_arg(random_construction_0)
        self.add_randomization_factor_arg(random_construction_0)
        self.add_runs_arg(random_construction_0)
        self.add_instance_arg(random_construction_1)
        self.add_randomization_factor_arg(random_construction_1)
        self.add_runs_arg(random_construction_1)
    

    def initialize_local_search_parser(self, subparsers):
        local_search_0 = subparsers.add_parser("LOCAL-SEARCH",help="Start Local Search")
        local_search_1 = subparsers.add_parser("2",help="Start Local Search")

        self.add_instance_arg(local_search_0)
        self.add_neighborhood_arg(local_search_0)
        self.add_preload_starting_solutions_from_file_arg(local_search_0)
        self.add_special_local_search_args(local_search_0)

        self.add_instance_arg(local_search_1)
        self.add_neighborhood_arg(local_search_1)
        self.add_preload_starting_solutions_from_file_arg(local_search_1)
        self.add_special_local_search_args(local_search_1)


    def initialize_grasp_parser(self, subparsers):
        grasp_0 = subparsers.add_parser("GRASP",help="GRASP Search")
        grasp_1 = subparsers.add_parser("3",help="GRASP Search")

        self.add_instance_arg(grasp_0)
        self.add_randomization_factor_arg(grasp_0)
        self.add_runs_arg(grasp_0)

        self.add_instance_arg(grasp_1)
        self.add_randomization_factor_arg(grasp_1)
        self.add_runs_arg(grasp_1)




    def initialize_vnd_parser(self, subparsers):
        vnd_0 = subparsers.add_parser("VND",help="VND Search")
        vnd_1 = subparsers.add_parser("4",help="VND Search")

        self.add_instance_arg(vnd_0)
        self.add_preload_starting_solutions_from_file_arg(vnd_0)

        self.add_instance_arg(vnd_1)
        self.add_preload_starting_solutions_from_file_arg(vnd_1)

   
    def initialize_gvns_parser(self, subparsers):
        gvns_0 = subparsers.add_parser("GVNS",help="GVNS Search")
        gvns_1 = subparsers.add_parser("5",help="GVNS Search")

        self.add_instance_arg(gvns_0)
        self.add_runs_arg(gvns_0)
        self.add_preload_starting_solutions_from_file_arg(gvns_0)

        self.add_instance_arg(gvns_1)
        self.add_runs_arg(gvns_1)
        self.add_preload_starting_solutions_from_file_arg(gvns_1)


    def initialize_ga_parser(self, subparsers):
        ga_0 = subparsers.add_parser("GA",help="GA Search")
        ga_1 = subparsers.add_parser("6",help="GA Search")

        self.add_instance_arg(ga_0)
        self.add_hpt_arg(ga_0)
        self.add_hpt_init_arg(ga_0)
        self.add_stat_diff_arg(ga_0)
        self.add_benchmark_population_style(ga_0)
        self.add_path_to_repository(ga_0)
        self.add_preload_starting_solutions_from_file_arg(ga_0)

        self.add_instance_arg(ga_1)
        self.add_hpt_arg(ga_1)
        self.add_hpt_init_arg(ga_1)
        self.add_path_to_repository(ga_1)
        self.add_stat_diff_arg(ga_1)
        self.add_benchmark_population_style(ga_1)
        self.add_preload_starting_solutions_from_file_arg(ga_1)

    def initialize_aco_parser(self, subparsers):
        aco_0 = subparsers.add_parser("ACO",help="ACO Search")
        aco_1 = subparsers.add_parser("7",help="ACO Search")

        self.add_instance_arg(aco_0)
        self.add_hpt_arg(aco_0)
        self.add_path_to_repository(aco_0)
        self.add_stat_diff_arg(aco_0)
        self.add_benchmark_population_style(aco_0)
        self.add_preload_starting_solutions_from_file_arg(aco_0)

        self.add_instance_arg(aco_1)
        self.add_hpt_arg(aco_1)
        self.add_path_to_repository(aco_1)
        self.add_stat_diff_arg(aco_1)
        self.add_benchmark_population_style(aco_1)
        self.add_preload_starting_solutions_from_file_arg(aco_1)

    def initialize_evaluate_solution_parser(self, subparsers):
        eval_0 = subparsers.add_parser("EVAL", help="Evaluate Solution")

        self.add_must_specify_instance_path(eval_0)
        self.add_must_specify_starting_solutions(eval_0)

    def add_must_specify_starting_solutions(self, parser):
        parser.add_argument('solutions', help='Specify a path, where the files are (file name(s) must be exactly as in the instance files!).')

    def add_must_specify_instance_path(self, parser):
        parser.add_argument('instance',type=str, help='Either choose \'benchmark\' to run all instances or specify the file path for the instance', default=self._default_instance)

    def add_neighborhood_arg(self, parser):
        parser.add_argument('--neighborhood-structure',choices=['remove_customer','add_customer','insert_customer','swap_served_unserved_customer','interchange_customers','trip_2_opt','remove_hotel','add_hotel','exchange_hotel','move_hotel'], help='Choose a neighborhood structure for local search.', default='trip_2_opt')

    def add_preload_starting_solutions_from_file_arg(self, parser):
        parser.add_argument('--preload-starting-solutions-from-path', help='Do you want to preload the starting solution? If so specify a path, where the files are (file name(s) must be exactly as in the instance files!).')

    def add_special_local_search_args(self, parser):
        parser.add_argument('--benchmark-all-local-search', help='Do you want to run all benchmarking instances for local search?', action='store_true')
        parser.add_argument('--step-function', choices=['first','best','random'], default='first', help='Which step-function?')


    def add_instance_arg(self, parser):
        parser.add_argument('--instance',type=str, help='Either choose \'benchmark\' to run all instances or specify the file path for the instance', default=self._default_instance)
        parser.add_argument('--instance_check_necessary_constraints', help='Do you want to check, whether some necessary constraints are fulfilled for this instance?', action='store_true')

    def add_randomization_factor_arg(self, parser):
        parser.add_argument('--randomization-factor',type=int, help='randomization-factor=0 means NO randomization, whereas the higher it is set the higher the randomization', default=0)

    def add_runs_arg(self, parser):
        parser.add_argument('--runs',type=int, help='specify how many runs shall be made (how often for each instance the algorithm shall be executed)', default=1)

    def add_hpt_arg(self, parser):
        parser.add_argument('--perform-hyper-parameter-tuning', help='Do you want to run hyper-parameter-tuning on this algorithm?', action='store_true')

    def add_stat_diff_arg(self, parser):
        parser.add_argument('--perform-statistical-test', help='Do you want to run "generate data for statistical tests" on this algorithm?', action='store_true')

    def add_benchmark_population_style(self, parser):
        parser.add_argument('--perform-benchmark-population-style', help='Do you want to run the benchmark instances and report on the best found data?', action='store_true')

 
    def add_hpt_init_arg(self, parser):
        parser.add_argument('--perform-hyper-parameter-tuning-for-initialization-procedure', help='Do you want to run hyper-parameter-tuning on the initialization-procedure for GA? -> This command overules all others', action='store_true')
 
    def add_path_to_repository(self, parser):
        parser.add_argument('--path-to-repository', help='Specify a path to the repository, if e.g. one executes this on the cluster.', default='./')

       
        
    def algorithm_selector(self, args):
        logger = self._logger
        print(args)

        args.mode = args.subparser_name


        if not args.mode == 'EVAL' and args.instance != "benchmark":
            logger.info(args.instance)
            path = Path(args.instance)
            if not path.is_file():
                logger.fatal("The path:<" + str(args.instance) + "> does not point to a file!")
                quit()

            if args.instance_check_necessary_constraints:
                parsed_file = Input_file_Parser(args.instance)
                instance = parsed_file.load_and_parse_input_file()

                if instance.is_instance_not_computable():
                    logger.error("The given instance is not computable according to the necessary constraints!")
                    quit()

            input_file_parser = Input_File_Parser(args.instance)
            self._instances = [input_file_parser.load_and_parse_input_file()]

        elif not args.mode == 'EVAL':
            logger.info("BENCHMARKING")
            benchmark_files = []
            for f in os.listdir(self._benchmark_instances_path):
                benchmark_files.append(f)

            benchmark_files.sort()

            for f in benchmark_files:
                path = Path(join(self._benchmark_instances_path, f))

                if path.is_file():
                    str_path = self._benchmark_instances_path + f
                    input_file_parser = Input_File_Parser(str_path)
                    self._instances.append(input_file_parser.load_and_parse_input_file())
        else:
            benchmark_files = []
            instances = args.instance
            for f in os.listdir(instances):
                benchmark_files.append(f)

            benchmark_files.sort()

            for f in benchmark_files:
                path = Path(join(instances, f))

                if path.is_file():
                    str_path = instances + f
                    input_file_parser = Input_File_Parser(str_path)
                    self._instances.append(input_file_parser.load_and_parse_input_file())


        if args.mode == '0' or args.mode == 'CONSTRUCTION':
            self.start_construction_heuristics()

        elif args.mode == '1' or args.mode == 'RAND-CONSTRUCTION':
            self.start_random_construction_heuristics(args.randomization_factor, args.runs)

        elif args.mode == '2' or args.mode == 'LOCAL-SEARCH':

            if args.step_function == 'first':
                step_function = Step_Function_Type.FIRST
            elif args.step_function == 'best':
                step_function = Step_Function_Type.BEST
            elif args.step_function == 'random':
                step_function = Step_Function_Type.RANDOM

            if not args.benchmark_all_local_search:
                self.start_local_search(args.neighborhood_structure, args.preload_starting_solutions_from_path, step_function)
            else:

                step_functions = [Step_Function_Type.FIRST, Step_Function_Type.BEST, Step_Function_Type.RANDOM]
                neighborhoods = ['remove_customer','add_customer','insert_customer','swap_served_unserved_customer','interchange_customers','trip_2_opt','remove_hotel','add_hotel','exchange_hotel','move_hotel']
                        

                for step_function in step_functions:
                    for neighborhood in neighborhoods:

                        print("<<<<<<<<<<<<" + str(step_function) + ":::" + str(neighborhood) + ">>>>>>")
                        self.start_local_search(neighborhood, args.preload_starting_solutions_from_path, step_function)


                
        elif args.mode == '3' or args.mode == 'GRASP':
            self.start_grasp_search(args.randomization_factor, args.runs)

        elif args.mode == '4' or args.mode =='VND':
            self.start_vnd_search(args.preload_starting_solutions_from_path)

        elif args.mode == '5' or args.mode == 'GVNS':
            self.start_gvns_search(args.preload_starting_solutions_from_path, args.runs)
        elif args.mode == '6' or args.mode == 'GA':
            if args.perform_benchmark_population_style:
                self.start_ga_benchmark_population_style(args.path_to_repository)
            if args.perform_statistical_test:
                self.start_ga_test_statistical_difference(args.path_to_repository)
            if args.perform_hyper_parameter_tuning_for_initialization_procedure:
                self.start_ga_init_hpt(args.path_to_repository)
            if args.perform_hyper_parameter_tuning:
                self.start_ga_hpt(args.path_to_repository)

            if not args.perform_hyper_parameter_tuning and not args.perform_hyper_parameter_tuning_for_initialization_procedure and not args.perform_statistical_test and not args.perform_benchmark_population_style:
                self.start_ga_search(args.preload_starting_solutions_from_path)
        elif args.mode == '7' or args.mode == 'ACO':
            if args.perform_benchmark_population_style:
                self.start_aco_benchmark_population_style(args.path_to_repository)
            if args.perform_statistical_test:
                self.start_aco_test_statistical_difference(args.path_to_repository)
            if args.perform_hyper_parameter_tuning:
                self.start_aco_hpt(args.path_to_repository)

            if not args.perform_hyper_parameter_tuning and not args.perform_statistical_test and not args.perform_benchmark_population_style:
                self.start_aco_search(args.preload_starting_solutions_from_path)
        elif args.mode == 'EVAL':
            print('EVALUATE SOLUTION')
            print(args)
            self.start_evaluate_solution(args.solutions)

    def start_evaluate_solution(self, pre_load):
        print("START EVAL")

        pre_load_files = {}
        for f in os.listdir(pre_load):
            basename_stem = Path(pre_load + f).stem
            pre_load_files[basename_stem] = f

        for instance in self._instances:

            instance_base_name = instance.get_basename()

            solution = self.pre_load_solution_from_path(instance, pre_load, instance_base_name, pre_load_files)


            print("<<<<<<>>>>>>>")
            print(instance.get_instance_name())
            print(solution.get_objective_value())
            print(solution.is_c1_satisfied())
            print(solution.is_c2_satisfied())
            print(solution.is_c3_satisfied())
            print(solution.to_string())
            
 
            
    def start_construction_heuristics(self):
        print("start-construction")

        # These should not be set by the user, only for report purposes (effect of delta vs. no delta)
        benchmarking = False
        with_delta_evaluation = True

        for instance in self._instances:

            initialization_procedure = Combination_Of_Heuristics(instance, with_delta_evaluation)
            result = initialization_procedure.create_solution(random_k = 0, benchmarking = benchmarking, max_runtime = 10)
            if result.get_best_solution():
                result.get_best_solution().write_solution_to_file(file_path_to_solutions + "construction_heuristic")

            solution = result.get_best_solution()

            if solution:
                objective_value = solution._objective_value
                sum_of_trips = solution._sum_of_trips
                penalties = solution._penalties
                hotel_fees = solution._hotel_fees
                max_trip_length = solution._max_trip_length
                trips = len(solution._trips)
                prize = solution._prize
                trip_lengths = solution._trip_lengths
            else:
                objective_value = -1
                sum_of_trips = -1
                penalties = -1
                hotel_fees = -1
                max_trip_length = -1
                trips = -1
                prize = -1
                trip_lengths = []

            instance_name = instance.get_instance_name()
            related_statistics = self.compute_related_statistics(instance, solution)

            header_line = ["Instance_Name","Number_Of_Customers","Number_Of_Hotels","Objective_Value","Sum_of_Trips","Penalties","Hotel_Fees","Max_Trip_Length","Number_Of_Trips","Prize","Time","Trace","Trip_Lengths", "Percentate-of-collected-prizes","uses-delta-evaluation"]

            content_line = [str(instance_name), str(len(instance._customers_list)), str(len(instance._hotels_list)), str(objective_value), str(sum_of_trips), str(penalties), str(hotel_fees), str(max_trip_length), str(trips), str(prize), str(result.get_time()), str(result.get_trace()), str(trip_lengths), str(related_statistics[0]),str(with_delta_evaluation)]

            for key in result.get_additional_params().keys():
                header_line.append(str(key))
                content_line.append(str(result.get_additional_params()[key]))



            result.write_result_metadata_to_file(file_path_to_solutions + "construction_heuristic", header_line, content_line, instance)


    def start_random_construction_heuristics(self, random_k, trial_runs):
        print("start-random-const..." + str(random_k))

        max_runtime = 4
        for instance in self._instances:

            best_result = None

            for index in range(trial_runs):

                instance_name = instance.get_instance_name()

                
                initialization_procedure = Combination_Of_Heuristics(instance)
                retry = 0
                while retry < 10:
                    result = initialization_procedure.create_solution(random_k = random_k, max_runtime = max_runtime)
                    if result.get_best_solution():
                        break


                solution = result.get_best_solution()

                if not best_result or best_result.get_best_solution()._objective_value > solution._objective_value:
                    best_result = result

                header_line = ["Instance_Name","Index","Number_Of_Customers","Number_Of_Hotels","Objective_Value","Sum_of_Trips","Penalties","Hotel_Fees","Max_Trip_Length","Number_Of_Trips","Prize","Time","Trace"]

                content_line = [str(instance_name), str(index), str(len(instance._customers_list)), str(len(instance._hotels_list)), str(solution._objective_value), str(solution._sum_of_trips), str(solution._penalties), str(solution._hotel_fees), str(solution._max_trip_length), str(len(solution._trips)), str(solution._prize), str(result.get_time()), str(result.get_trace())]


                for key in result.get_additional_params().keys():
                    header_line.append(str(key))
                    content_line.append(str(result.get_additional_params()[key]))




                result.write_result_metadata_to_file(file_path_to_solutions + "random_construction_heuristic", header_line, content_line)

            best_result.get_best_solution().write_solution_to_file(file_path_to_solutions + "random_construction_heuristic")


    def start_local_search(self, neighborhood_str, pre_load, step_function):
        print("start-local-search..." + str(neighborhood_str))

        # Trip_2_Opt can be used for delta vs. no delta measurements
        with_delta = True
        delta_measurements = False
        #max_runtime = self._max_runtime
        max_runtime = 60

        if pre_load:
            pre_load_files = {}
            for f in os.listdir(pre_load):
                basename_stem = Path(pre_load + f).stem
                pre_load_files[basename_stem] = f

        for instance in self._instances:

            instance_base_name = instance.get_basename()

            if pre_load:
                solution = self.pre_load_solution_from_path(instance, pre_load, instance_base_name, pre_load_files)
            else:
                initialization_procedure = Backtracking_Search(instance)
                solution = initialization_procedure.create_solution().get_best_solution()

            if neighborhood_str == 'remove_customer':
                neighborhood = Remove_Customer(instance)
            elif neighborhood_str == 'add_customer':
                neighborhood = Add_Customer(instance)
            elif neighborhood_str == 'insert_customer':
                neighborhood = Insert_Customer(instance)
            elif neighborhood_str == 'swap_served_unserved_customer':
                neighborhood = Swap_Served_Unserved_Customer(instance)
            elif neighborhood_str == 'interchange_customers':
                neighborhood = Interchange_Customers(instance)
            elif neighborhood_str == 'trip_2_opt':
                neighborhood = Trip_2_Opt(instance, with_delta)
            elif neighborhood_str == 'remove_hotel':
                neighborhood = Remove_Hotel(instance)
            elif neighborhood_str == 'add_hotel':
                neighborhood = Add_Hotel(instance)
            elif neighborhood_str == 'exchange_hotel':
                neighborhood = Exchange_Hotel(instance)
            elif neighborhood_str == 'move_hotel':
                neighborhood = Move_Hotel(instance)

            randomization_k = 0
            search_alg = Local_Search(instance, randomization_k)
            result = search_alg.start_search(solution, step_function, [neighborhood], max_runtime)

            solution = result.get_best_solution()

            # Necessary e.g. for timeouts!
            if solution:
                objective_value = solution._objective_value
                sum_of_trips = solution._sum_of_trips
                penalties = solution._penalties
                hotel_fees = solution._hotel_fees
                max_trip_length = solution._max_trip_length
                trips = len(solution._trips)
                prize = solution._prize
                trip_lengths = solution._trip_lengths
            else:
                objective_value = -1
                sum_of_trips = -1
                penalties = -1
                hotel_fees = -1
                max_trip_length = -1
                trips = -1
                prize = -1
                trip_lengths = []

            if solution:
                result.get_best_solution().write_solution_to_file(file_path_to_solutions + "local_search", neighborhood_str + "_" + str(step_function))

            if not delta_measurements:
                header_line = ["Instance_Name","Number_Of_Customers","Number_Of_Hotels","Objective_Value","Sum_of_Trips","Penalties","Hotel_Fees","Max_Trip_Length","Number_Of_Trips","Prize","Time","Trace", "Neighborhood", "Step_Function"]

                solution = result.get_best_solution()
                instance_name = instance.get_instance_name()

                content_line = [str(instance_name), str(len(instance._customers_list)), str(len(instance._hotels_list)), str(solution._objective_value), str(solution._sum_of_trips), str(solution._penalties), str(solution._hotel_fees), str(solution._max_trip_length), str(len(solution._trips)), str(solution._prize), str(result.get_time()), str(result.get_trace()), neighborhood_str, str(step_function)]

                for key in result.get_additional_params().keys():
                    header_line.append(str(key))
                    content_line.append(str(result.get_additional_params()[key]))

            else:
                header_line = ["Instance_Name","Number_Of_Customers","Number_Of_Hotels","Objective_Value","Sum_of_Trips","Penalties","Hotel_Fees","Max_Trip_Length","Number_Of_Trips","Prize","Time","Trace", "Neighborhood", "Step_Function","Delta-Evaluation"]

                solution = result.get_best_solution()
                instance_name = instance.get_instance_name()

                content_line = [str(instance_name), str(len(instance._customers_list)), str(len(instance._hotels_list)), str(solution._objective_value), str(solution._sum_of_trips), str(solution._penalties), str(solution._hotel_fees), str(solution._max_trip_length), str(len(solution._trips)), str(solution._prize), str(result.get_time()), str(result.get_trace()), neighborhood_str, str(step_function), str(with_delta)]





            result.write_result_metadata_to_file(file_path_to_solutions + "local_search", header_line, content_line)


    def start_grasp_search(self, random_k, trial_runs):

        for instance in self._instances:

            best_result = None

            for index in range(trial_runs):

                instance_base_name = instance.get_basename()

                grasp = Grasp(instance, random_k)
                result = grasp.start_search(None, None, None, self._max_runtime)

                result.get_best_solution().write_solution_to_file(file_path_to_solutions + "grasp")

                if not best_result or best_result.get_best_solution()._objective_value > solution._objective_value:
                    best_result = result

                header_line = ["Instance_Name","Number_Of_Customers","Number_Of_Hotels","Objective_Value","Sum_of_Trips","Penalties","Hotel_Fees","Max_Trip_Length","Number_Of_Trips","Prize","Time","Trace"]

                solution = result.get_best_solution()
                instance_name = instance.get_instance_name()

                content_line = [str(instance_name), str(len(instance._customers_list)), str(len(instance._hotels_list)), str(solution._objective_value), str(solution._sum_of_trips), str(solution._penalties), str(solution._hotel_fees), str(solution._max_trip_length), str(len(solution._trips)), str(solution._prize), str(result.get_time()), str(result.get_trace())]


                for key in result.get_additional_params().keys():
                    header_line.append(str(key))
                    content_line.append(str(result.get_additional_params()[key]))



                result.write_result_metadata_to_file(file_path_to_solutions + "grasp", header_line, content_line)






    def start_vnd_search(self, pre_load):
        print("start-vnd-search")


        if pre_load:
            pre_load_files = {}
            for f in os.listdir(pre_load):
                basename_stem = Path(pre_load + f).stem
                pre_load_files[basename_stem] = f

        for instance in self._instances:

            instance_base_name = instance.get_basename()

            if pre_load:
                solution = self.pre_load_solution_from_path(instance, pre_load, instance_base_name, pre_load_files)
            else:
                initialization_procedure = Backtracking_Search(instance)
                solution = initialization_procedure.create_solution().get_best_solution()

            #neighborhoods = [Interchange_Customers(instance),Insert_Customer(instance), Trip_2_Opt(instance), Swap_Served_Unserved_Customer(instance), Remove_Customer(instance), Add_Customer(instance), Remove_Hotel(instance), Add_Hotel(instance),Exchange_Hotel(instance), Move_Hotel(instance)]
            neighborhoods = [Interchange_Customers(instance),Insert_Customer(instance), Trip_2_Opt(instance), Swap_Served_Unserved_Customer(instance), Remove_Customer(instance), Add_Customer(instance),Exchange_Hotel(instance), Move_Hotel(instance), Add_Hotel(instance), Remove_Hotel(instance)]
            
            vnd = Vnd(instance, 0)
            #vnd = Local_Search(instance, 0)
            result = vnd.start_search(solution, Step_Function_Type.BEST, neighborhoods, self._max_runtime)

            result.get_best_solution().write_solution_to_file(file_path_to_solutions + "vnd")

            header_line = ["Instance_Name","Number_Of_Customers","Number_Of_Hotels","Objective_Value","Sum_of_Trips","Penalties","Hotel_Fees","Max_Trip_Length","Number_Of_Trips","Prize","Time","Trace"]

            solution = result.get_best_solution()
            instance_name = instance.get_instance_name()

            content_line = [str(instance_name), str(len(instance._customers_list)), str(len(instance._hotels_list)), str(solution._objective_value), str(solution._sum_of_trips), str(solution._penalties), str(solution._hotel_fees), str(solution._max_trip_length), str(len(solution._trips)), str(solution._prize), str(result.get_time()), str(result.get_trace())]

            for key in result.get_additional_params().keys():
                header_line.append(str(key))
                content_line.append(str(result.get_additional_params()[key]))




            result.write_result_metadata_to_file(file_path_to_solutions + "vnd", header_line, content_line)


    def start_gvns_search(self, pre_load, trial_runs):
        print("start-gvns-search")


        iterations = 10

        if pre_load:
            pre_load_files = {}
            for f in os.listdir(pre_load):
                basename_stem = Path(pre_load + f).stem
                pre_load_files[basename_stem] = f


            """
            for instance in self._instances:
                instance_base_name = instance.get_basename()
                solution = self.pre_load_solution_from_path(instance, pre_load, instance_base_name, pre_load_files)
    

                print(solution.get_objective_value())
            quit()
            """

        for instance in self._instances:

            best_result = None

            instance_base_name = instance.get_basename()

            for index in range(trial_runs):


                if pre_load:
                    solution = self.pre_load_solution_from_path(instance, pre_load, instance_base_name, pre_load_files)
                else:
                    initialization_procedure = Backtracking_Search(instance)
                    solution = initialization_procedure.create_solution().get_best_solution()


                gvns = Gvns(instance, 0)
                result = gvns.start_search(solution, None, None, 10, termination_criterion = iterations)

                if not best_result or best_result.get_best_solution()._objective_value > result.get_best_solution().get_objective_value():
                    best_result = result

                header_line = ["Instance_Name","Number_Of_Customers","Number_Of_Hotels","Objective_Value","Sum_of_Trips","Penalties","Hotel_Fees","Max_Trip_Length","Number_Of_Trips","Prize","Time","Trace"]

                solution = result.get_best_solution()
                instance_name = instance.get_instance_name()

                content_line = [str(instance_name), str(len(instance._customers_list)), str(len(instance._hotels_list)), str(solution._objective_value), str(solution._sum_of_trips), str(solution._penalties), str(solution._hotel_fees), str(solution._max_trip_length), str(len(solution._trips)), str(solution._prize), str(result.get_time()), str(result.get_trace())]

                for key in result.get_additional_params().keys():
                    header_line.append(str(key))
                    content_line.append(str(result.get_additional_params()[key]))
            
                result.write_result_metadata_to_file(file_path_to_solutions + "gvns", header_line, content_line)
            
            print("<<<<<<<<<<<Best for INSTANCE: " + str(instance_base_name) + ">>>>>>>>>>>>>>>")
            print(best_result.get_best_solution().get_objective_value())
            print(best_result.get_best_solution().slow_objective_values_calculation())
            print("--------------------------------------------")

            best_result.get_best_solution().write_solution_to_file(file_path_to_solutions + "gvns")


    def start_ga_search(self, pre_load):

        if pre_load:
            pre_load_files = {}
            for f in os.listdir(pre_load):
                basename_stem = Path(pre_load + f).stem
                pre_load_files[basename_stem] = f

        random_k = 15
        population_size = 75
        tournament_k = 7
        percentage_replaced = 0.1
        #neighborhoods_round_robin = [Trip_2_Opt, Add_Customer]
        #neighborhoods_round_robin = [Trip_2_Opt]
        #neighborhoods_round_robin = [Interchange_Customers,Insert_Customer, Trip_2_Opt, Swap_Served_Unserved_Customer, Remove_Customer, Add_Customer, Remove_Hotel, Add_Hotel,Exchange_Hotel, Move_Hotel]
        #neighborhoods_round_robin = [Trip_2_Opt, Remove_Customer, Add_Customer, Remove_Hotel, Add_Hotel]
        #neighborhoods_round_robin = [Add_Customer]
        neighborhoods_round_robin = [Trip_2_Opt, Remove_Customer, Add_Customer, Remove_Hotel, Add_Hotel]


        #saw_policy = Linear_Sequence_Weights(1.5,1.5,1.5,0.1,0.1,0.1,300)
        saw_policy = Constant_Weights(3,3,3)
        iterations = 300


        for instance in self._instances:

            instance_base_name = instance.get_basename()

            """
            if pre_load:
                solution = self.pre_load_solution_from_path(instance, pre_load, instance_base_name, pre_load_files)
            else:
                initialization_procedure = Backtracking_Search(instance)
                solution = initialization_procedure.create_solution().get_best_solution()
            """
            solution = None

            ga = Genetic_Algorithm(instance, random_k)
            result = ga.start_search(solution, None, neighborhoods_round_robin, 10, population_size = population_size, tournament_k = tournament_k, percentage_replaced = percentage_replaced, saw_policy = saw_policy, termination_criterion = iterations, compute_distance_analysis = False)
            
            print("<<<<<<<<<<<Best for INSTANCE: " + str(instance_base_name) + ">>>>>>>>>>>>>>>")
            print(result.get_best_solution().get_objective_value())
            print(result.get_best_solution().slow_objective_values_calculation())
            print(result.get_best_solution().is_c1_satisfied())
            print(result.get_best_solution().is_c2_satisfied())
            print(result.get_best_solution().is_c3_satisfied())
            print(result.get_trace())
            print(result.get_best_solution().to_string())
            print("--------------------------------------------")
            
            header_line = ["Instance_Name","Number_Of_Customers","Number_Of_Hotels","Objective_Value","Sum_of_Trips","Penalties","Hotel_Fees","Max_Trip_Length","Number_Of_Trips","Prize","Time","Trace"]

            solution = result.get_best_solution()
            instance_name = instance.get_instance_name()

            content_line = [str(instance_name), str(len(instance._customers_list)), str(len(instance._hotels_list)), str(solution._objective_value), str(solution._sum_of_trips), str(solution._penalties), str(solution._hotel_fees), str(solution._max_trip_length), str(len(solution._trips)), str(solution._prize), str(result.get_time()), str(result.get_trace())]

            for key in result.get_additional_params().keys():
                header_line.append(str(key))
                content_line.append(str(result.get_additional_params()[key]))
        
            result.write_result_metadata_to_file(file_path_to_solutions + "ga", header_line, content_line)

            result.get_best_solution().write_solution_to_file(file_path_to_solutions + "ga")

    def start_ga_init_hpt(self, path_to_repository):
        hpt = Hyper_Parameter_Tuning(path_to_repository = path_to_repository, output_path = "m_init.csv")

        arguments = {}
        arguments["type"] = ["initialization"]
        arguments["saw_policy"] = [Constant_Weights(3,3,3)]
        arguments["termination_criterion"] = [0]
        #arguments["random_k"] = [5,10]
        arguments["random_k"] = [5]
        arguments["population_size"] = [100]
        arguments["show_output"] = [False]
        #arguments["alpha"] = [0,0.5,1]
        arguments["alpha"] = [0.5]
        #arguments["beta"] = [0,-0.5,-1,0.5]
        arguments["beta"] = [-1]
        arguments["gamma"] = [-1]
        arguments["delta"] = [0.5,-0.5]

        hpt.perform(Construction_Builder, arguments)

    def start_ga_hpt(self, path_to_repository):
        hpt = Hyper_Parameter_Tuning(path_to_repository = path_to_repository, output_path = "m_ga.csv")


        neighborhoods_round_robin = [Trip_2_Opt, Remove_Customer, Add_Customer, Remove_Hotel, Add_Hotel]

        """
                                                                  perc._repl                                                                 tournament_k
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.05,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],50,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:08:09:55
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.05,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],81,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:08:16:29
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.05,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],95,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:08:23:03
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.1,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],27,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:08:29:40
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.1,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],50,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:08:36:07
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.1,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],81,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:08:42:38
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.1,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],95,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:08:49:09
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.2,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],27,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:08:55:42
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.2,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],50,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:09:02:16
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.2,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],81,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:09:08:50
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.2,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],95,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:09:15:30
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.4,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],50,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:09:21:59
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.4,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],81,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:09:28:32
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.4,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],95,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:09:34:57
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.9,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],27,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:09:41:29
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.9,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],50,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:09:47:53
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.9,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],81,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:09:54:27
        algorithm,Constant-Weights(Gamma-1:3;Gamma-2:3;Gamma-3:3),0.9,100,[trip_2_opt;remove_customer;add_customer;remove_hotel;add_hotel;],95,5,400,0.5,-1.0,-0.5,0.5,8,rand_test_14,20230103:10:00:57
        """


        arguments = {}
        arguments["type"] = ["algorithm"]
        arguments["saw_policy"] = [Constant_Weights(3,3,3)]
        #arguments["percentage_replaced"] = [0.05,0.1,0.2,0.4,0.9]
        arguments["percentage_replaced"] = [0.05,0.1,0.2,0.4,0.9]
        arguments["population_size"] = [100]
        arguments["neighborhoods"] = [neighborhoods_round_robin]
        #arguments["tournament_k"] = [3,9,27,50,81,95]
        arguments["tournament_k"] = [27,50,81,95]
        arguments["random_k"] = [5]
        arguments["termination_criterion"] = [400]
        arguments["alpha"] = [0.5]
        arguments["beta"] = [-1.0]
        arguments["gamma"] = [-0.5]
        arguments["delta"] = [0.5]
        


        hpt.perform(Genetic_Algorithm, arguments)

    def start_ga_test_statistical_difference(self, path_to_repository):
        print("ga-test-stat-diff")
        print(path_to_repository)

        stat = Statistical_Test(path_to_repository, "stat_ga.csv")

        """
        arguments = {}
        arguments["type"] = "algorithm"
        arguments["saw_policy"] = Constant_Weights(3,3,3)
        arguments["population_size"] = 50
        arguments["random_k"] = 5
        arguments["alpha"] = 1
        arguments["beta"] = 1
        arguments["rho"] = 0.24
        arguments["p"] = 0.25 # For min-max-ants

        arguments["local_information"] = "objective_value" # For different local information

        arguments["min_max_ant_system"] = True
        arguments["termination_criterion"] = 400
        """
        
        neighborhoods_round_robin = [Trip_2_Opt, Remove_Customer, Add_Customer, Remove_Hotel, Add_Hotel]
 
        arguments = {}
        arguments["type"] = "algorithm"
        arguments["saw_policy"] = Constant_Weights(3,3,3)
        arguments["percentage_replaced"] = 0.2
        arguments["population_size"] = 100
        arguments["neighborhoods"] = neighborhoods_round_robin
        arguments["tournament_k"] = 50
        arguments["random_k"] = 5
        arguments["termination_criterion"] = 400
        arguments["alpha"] = 0.5
        arguments["beta"] = -1.0
        arguments["gamma"] = -0.5
        arguments["delta"] = 0.5
       
        stat.perform(Genetic_Algorithm, arguments)

    def start_ga_benchmark_population_style(self, path_to_repository):
        print("ga-benchmark-pop-style")
        print(path_to_repository)

        benchmark = Benchmark(path_to_repository, "ga_benchmark.csv")

        """
        arguments = {}
        arguments["type"] = "algorithm"
        arguments["saw_policy"] = Constant_Weights(3,3,3)
        arguments["population_size"] = 50
        arguments["random_k"] = 5
        arguments["alpha"] = 1
        arguments["beta"] = 1
        arguments["rho"] = 0.24
        arguments["p"] = 0.25 # For min-max-ants

        arguments["local_information"] = "objective_value" # For different local information

        arguments["min_max_ant_system"] = True
        arguments["termination_criterion"] = 400
        """
        



        neighborhoods_round_robin = [Trip_2_Opt, Remove_Customer, Add_Customer, Remove_Hotel, Add_Hotel]
 
        arguments = {}
        arguments["type"] = "algorithm"
        arguments["saw_policy"] = Constant_Weights(3,3,3)
        arguments["percentage_replaced"] = 0.2
        arguments["population_size"] = 100
        arguments["neighborhoods"] = neighborhoods_round_robin
        arguments["tournament_k"] = 50
        arguments["random_k"] = 5
        arguments["termination_criterion"] = 400
        arguments["alpha"] = 0.5
        arguments["beta"] = -1.0
        arguments["gamma"] = -0.5
        arguments["delta"] = 0.5


        benchmark.perform(Genetic_Algorithm, arguments, "ga")
 

    def start_aco_search(self, pre_load):

        if pre_load:
            pre_load_files = {}
            for f in os.listdir(pre_load):
                basename_stem = Path(pre_load + f).stem
                pre_load_files[basename_stem] = f

        #tournament_k = 5
        #percentage_replaced = 0.05
        #saw_policy = Linear_Sequence_Weights(0.1,0.1,1,0.1,0.1,0.1, 10)

        """
        random_k = 5
        population_size = 25
        saw_policy = Constant_Weights(2,2,2)
        iterations = 100
        """


        for instance in self._instances:

            instance_base_name = instance.get_basename()

            """
            if pre_load:
                solution = self.pre_load_solution_from_path(instance, pre_load, instance_base_name, pre_load_files)
            else:
                initialization_procedure = Backtracking_Search(instance)
                solution = initialization_procedure.create_solution().get_best_solution()
            """
            solution = None
 
            saw_policy = Constant_Weights(3,3,3)
            population_size = 50
            random_k = 5
            alpha = 1
            beta = 1
            rho = 0.24
            p = 0.25 # For min-max-ants

            local_information = "objective_value" # For different local information

            min_max_ant_system = True
            termination_criterion = 400
               
            aco = Ant_Colony_Optimization(instance, random_k)
            result = aco.start_search(solution, None, None, 100, population_size = population_size, saw_policy = saw_policy, termination_criterion = termination_criterion, compute_distance_analysis = False, alpha = alpha, beta = beta, rho = rho, p = p, local_information = local_information, min_max_ant_system = min_max_ant_system)
            
            print("<<<<<<<<<<<Best for INSTANCE: " + str(instance_base_name) + ">>>>>>>>>>>>>>>")
            print(result.get_best_solution().get_objective_value())
            print(result.get_best_solution().slow_objective_values_calculation())
            print(result.get_best_solution().is_c1_satisfied())
            print(result.get_best_solution().is_c2_satisfied())
            print(result.get_best_solution().is_c3_satisfied())
            print(result.get_trace())
            print("--------------------------------------------")
            
            header_line = ["Instance_Name","Number_Of_Customers","Number_Of_Hotels","Objective_Value","Sum_of_Trips","Penalties","Hotel_Fees","Max_Trip_Length","Number_Of_Trips","Prize","Time","Trace"]

            solution = result.get_best_solution()
            instance_name = instance.get_instance_name()

            content_line = [str(instance_name), str(len(instance._customers_list)), str(len(instance._hotels_list)), str(solution._objective_value), str(solution._sum_of_trips), str(solution._penalties), str(solution._hotel_fees), str(solution._max_trip_length), str(len(solution._trips)), str(solution._prize), str(result.get_time()), str(result.get_trace())]

            for key in result.get_additional_params().keys():
                header_line.append(str(key))
                content_line.append(str(result.get_additional_params()[key]))
        
            result.write_result_metadata_to_file(file_path_to_solutions + "aco", header_line, content_line)

            result.get_best_solution().write_solution_to_file(file_path_to_solutions + "aco")

    def start_aco_hpt(self, path_to_repository):
        hpt = Hyper_Parameter_Tuning(path_to_repository = path_to_repository, output_path = "aco.csv")

        arguments = {}
        arguments["type"] = ["algorithm"]
        arguments["saw_policy"] = [Constant_Weights(3,3,3)]
        arguments["population_size"] = [50,100]
        arguments["random_k"] = [5]
        #arguments["alpha"] = [1,10,0.10,0.5,2]
        arguments["alpha"] = [1]
        #arguments["beta"] = [1,10,0.10,0.5,2]
        arguments["beta"] = [1]
        #arguments["rho"] = [0.02,0.07,0.20,0.50]
        arguments["rho"] = [0.24]
        #arguments["p"] = [0.5,0.75,0.25] # For min-max-ants
        #arguments["p"] = [0.5,0.75,0.25] # For min-max-ants
        arguments["p"] = [0.5,0.25] # For min-max-ants

        arguments["local_information"] = ["objective_value"] # For different local information

        arguments["min_max_ant_system"] = [True]
        arguments["termination_criterion"] = [200]
        
        hpt.perform(Ant_Colony_Optimization, arguments)

    def start_aco_test_statistical_difference(self, path_to_repository):
        print("ACO test-stat-diff")
        print(path_to_repository)

        stat = Statistical_Test(path_to_repository, "stat_aco.csv")

        arguments = {}
        arguments["type"] = "algorithm"
        arguments["saw_policy"] = Constant_Weights(3,3,3)
        arguments["population_size"] = 50
        arguments["random_k"] = 5
        arguments["alpha"] = 1
        arguments["beta"] = 1
        arguments["rho"] = 0.24
        arguments["p"] = 0.25 # For min-max-ants

        arguments["local_information"] = "objective_value" # For different local information

        arguments["min_max_ant_system"] = True
        arguments["termination_criterion"] = 400
        
        stat.perform(Ant_Colony_Optimization, arguments)

    def start_aco_benchmark_population_style(self, path_to_repository):
        print("aco-benchmark")
        print(path_to_repository)


        benchmark = Benchmark(path_to_repository, "n_aco_benchmark.csv")

        arguments = {}
        arguments["type"] = "algorithm"
        arguments["saw_policy"] = Constant_Weights(3,3,3)
        arguments["population_size"] = 50
        arguments["random_k"] = 5
        arguments["alpha"] = 1
        arguments["beta"] = 1
        arguments["rho"] = 0.24
        arguments["p"] = 0.25 # For min-max-ants

        arguments["local_information"] = "objective_value" # For different local information

        arguments["min_max_ant_system"] = True
        arguments["termination_criterion"] = 400
        
        benchmark.perform(Ant_Colony_Optimization, arguments, "n_aco")



    def pre_load_solution_from_path(self, instance, pre_load, instance_base_name, pre_load_files):

        pre_load_file_name = pre_load_files[instance_base_name]

        pre_load_file = open(pre_load + pre_load_file_name, "r")

        # first line is instance name
        pre_load_file.readline()

        solution_str = pre_load_file.readline()

        pre_load_file.close()

        solution = Solution(instance)
        solution.parse_from_str(solution_str)

        return solution

    def compute_related_statistics(self, instance, solution):

        total_prizes = 0

        for customer in instance.get_list_of_customers():
            total_prizes += customer.get_prize()

        if not solution:
            return [0]
        else:
            return [solution._prize/total_prizes]


main = Start_PCTSPHS()
main.start()

quit()

"""
argv = len(sys.argv)

if argv != 2:
    logger.critical("SYNOPSIS: python start.py filepath")
    quit()

args = sys.argv
file_name = args[1]

#tester = Tester(instance)
#tester.test_solution_class()

for hotel in instance.get_list_of_hotels():
    print("Hotel with ID: " + str(hotel.get_id()) + " has fee " + str(hotel.get_fee()))

for customer in instance.get_list_of_customers():
    print("Customer with ID: " + str(customer.get_id()) + " has prize " + str(customer.get_prize()) + " and has penalty " + str(customer.get_penalty()))

for edge in instance.get_list_of_edges():
    print("Edge with vertex_a_id: " + str(edge.get_vertex_a().get_id()) + ", vertex_b_id: " + str(edge.get_vertex_b().get_id()) + " has weight " + str(edge.get_weight()))
"""
