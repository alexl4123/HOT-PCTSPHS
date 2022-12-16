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

from search_algorithms.local_search import Local_Search, Step_Function_Type
from search_algorithms.vnd import Vnd
from search_algorithms.grasp import Grasp
from search_algorithms.gvns import Gvns

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

from search_algorithms.ga.fitness_function import Fitness_Function


class Start_PCTSPHS:

    def __init__(self):

        self._instances = []
        self._benchmark_instances_path = 'tsp_instances/'
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
        parser.add_argument('--instance',type=str, help='Either choose \'benchmark\' to run all instances or specify the file path for the instance', default='tsp_instances/00_test.txt')
        parser.add_argument('--mode',choices = ['0','construction','1','rand-construction','2','local-search','3','GRASP','4','VND','5','GVNS', '6', 'GA'], help='Choose the mode, exactly one of (either the int or the name) {0=construction,1=rand-construction,2=local-search,3=GRASP,4=VND,5=GVNS, 6=GA}.\n If mode is (1) or (3), then one can also specify the \'randomization-factor\'; If mode is (2) or (3) one can also specify the \'neighborhood-structure\'; If mode is (2),(4), or (5) one can also specify the \'preload-starting-solutions-from-path\'.', default='construction')
        
        

        args,_ = parser.parse_known_args()

        if (args.mode == '1' or args.mode == 'rand-construction') or (args.mode == '3' or args.mode == 'GRASP'):
            parser.add_argument('--randomization-factor',type=int, help='randomization-factor=0 means NO randomization, whereas the higher it is set the higher the randomization', default=0)
        if (args.mode == '1' or args.mode == 'rand-construction') or (args.mode == '3' or args.mode == 'GRASP') or (args.mode == '5' or args.mode == 'GVNS'):
            parser.add_argument('--runs',type=int, help='specify how many runs shall be made (how often for each instance the algorithm shall be executed)', default=1)

        if (args.mode == '2' or args.mode == 'local-search') or (args.mode == '3' or args.mode == 'GRASP'):
            parser.add_argument('--neighborhood-structure',choices=['remove_customer','add_customer','insert_customer','swap_served_unserved_customer','interchange_customers','trip_2_opt','remove_hotel','add_hotel','exchange_hotel','move_hotel'], help='Choose a neighborhood structure for local search.', default='trip_2_opt')

        if (args.mode == '2' or args.mode == 'local-search') or (args.mode == '4' or args.mode == 'VND') or (args.mode == '5' or args.mode == 'GVNS' or (args.mode == '6' or args.mode == 'GA')):
            parser.add_argument('--preload-starting-solutions-from-path', help='Do you want to preload the starting solution? If so specify a path, where the files are (file name(s) must be exactly as in the instance files!).')

        if (args.mode == '2' or args.mode == 'local-search'):
            parser.add_argument('--benchmark-all-local-search', help='Do you want to run all benchmarking instances for local search?', action='store_true')
            parser.add_argument('--step-function', choices=['first','best','random'], default='first', help='Which step-function?')

        if args.instance != "benchmark":
            parser.add_argument('--instance-check-necessary-constraints', action='store_true', help='Set this flag to enable a necessary condition check on the instances, i.e. if this test fails the instance cannot be computed.')

        args = parser.parse_args()


        if args.instance != "benchmark":
            logger.info(args.instance)
            path = Path(args.instance)
            if not path.is_file():
                logger.fatal("The path:<" + str(args.instance) + "> does not point to a file!")
                quit()

            if args.instance_check_necessary_constraints:
                parsed_file = Input_file_Parser(args.instance)
                instance = parsed_file.load_and_parse_input_file()
                instance.precompute_all_nearest_neighbors()

                if instance.is_instance_not_computable():
                    logger.error("The given instance is not computable according to the necessary constraints!")
                    quit()

            input_file_parser = Input_File_Parser(args.instance)
            self._instances = [input_file_parser.load_and_parse_input_file()]

        else:
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

        if args.mode == '0' or args.mode == 'construction':
            self.start_construction_heuristics()

        elif args.mode == '1' or args.mode == 'rand-construction':
            self.start_random_construction_heuristics(args.randomization_factor, args.runs)

        elif args.mode == '2' or args.mode == 'local-search':

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
            self.start_grasp_search(args.randomization_factor,args.neighborhood_structure, args.runs)

        elif args.mode == '4' or args.mode =='VND':
            self.start_vnd_search(args.preload_starting_solutions_from_path)

        elif args.mode == '5' or args.mode == 'GVNS':
            self.start_gvns_search(args.preload_starting_solutions_from_path, args.runs)
        elif args.mode == '6' or args.mode == 'GA':
            self.start_ga_search(args.preload_starting_solutions_from_path)





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


    def start_grasp_search(self, random_k, neighborhood, trial_runs):
        print("start-grasp-search..." + str(random_k) + "::" + str(neighborhood))


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

            neighborhoods = [Interchange_Customers(instance),Insert_Customer(instance), Trip_2_Opt(instance), Swap_Served_Unserved_Customer(instance), Remove_Customer(instance), Add_Customer(instance), Remove_Hotel(instance), Add_Hotel(instance),Exchange_Hotel(instance), Move_Hotel(instance)]
            
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


        for instance in self._instances:

            if pre_load:
                solution = self.pre_load_solution_from_path(instance, pre_load, instance_base_name, pre_load_files)
            else:
                initialization_procedure = Backtracking_Search(instance)
                solution = initialization_procedure.create_solution().get_best_solution()

            print(solution.to_string())

            ff = Fitness_Function(instance, 1, 1, 1)

            ff.compute_fitness(solution)



    def pre_load_solution_from_path(self, instance, pre_load, instance_base_name, pre_load_files):

        pre_load_file_name = pre_load_files[instance_base_name]

        pre_load_file = open(pre_load + pre_load_file_name, "r")

        # first line is instance name
        pre_load_file.readline()

        solution_str = pre_load_file.readline()

        pre_load_file.close()

        solution = Solution(instance)
        solution.parse_from_str(solution_str)
        print("LOADED SOLUTION for: " + str(instance_base_name))
        print(solution.to_string())

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
