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

class Start_PCTSPHS:

    def __init__(self):

        self._instances = []
        self._benchmark_instances_path = 'tsp_instances/'

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
        parser.add_argument('--mode',choices = ['0','construction','1','rand-construction','2','local-search','3','GRASP','4','VND','5','GVNS'], help='Choose the mode, exactly one of (either the int or the name) {0=construction,1=rand-construction,2=local-search,3=GRASP,4=VND,5=GVNS}.\n If mode is (1) or (3), then one can also specify the \'randomization-factor\'; If mode is (2) or (3) one can also specify the \'neighborhood-structure\'; If mode is (2),(4), or (5) one can also specify the \'preload-starting-solutions-from-path\'.', default='construction')
        
        

        args,_ = parser.parse_known_args()

        if (args.mode == '1' or args.mode == 'rand-construction') or (args.mode == '3' or args.mode == 'GRASP'):
            parser.add_argument('--randomization-factor',type=int, help='randomization-factor=0 means NO randomization, whereas the higher it is set the higher the randomization', default=0)

        if (args.mode == '2' or args.mode == 'local-search') or (args.mode == '3' or args.mode == 'GRASP'):
            parser.add_argument('--neighborhood-structure',choices=['trip_2_opt', 'swap_served_unserved_customer', 'interchange_customers', 'exchange_hotel', 'move_hotel'], help='Choose a neighborhood structure for local search.', default='trip_2_opt')

        if (args.mode == '2' or args.mode == 'local-search') or (args.mode == '4' or args.mode == 'VND') or (args.mode == '5' or args.mode == 'GVNS'):
            parser.add_argument('--preload-starting-solutions-from-path', help='Do you want to preload the starting solution? If so specify a path, where the files are (file name(s) must be exactly as in the instance files!).')

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
            self.start_random_construction_heuristics(args.randomization_factor)
        elif args.mode == '2' or args.mode == 'local-search':
            self.start_local_search(args.neighborhood_structure, args.preload_starting_solutions_from_path)
        elif args.mode == '3' or args.mode == 'GRASP':
            self.start_grasp_search(args.randomization_factor,args.neighborhood_structure)
        elif args.mode == '4' or args.mode =='VND':
            self.start_vnd_search(args.preload_starting_solutions_from_path)
        elif args.mode == '5' or args.mode == 'GVNS':
            self.start_gvns_search(args.preload_starting_solutions_from_path)


    def start_construction_heuristics(self):
        print("start-construction")

        for instance in self._instances:

            initialization_procedure = Combination_Of_Heuristics(instance)
            result = initialization_procedure.create_solution(0)
            result.write_solution_to_file(file_path_to_solutions + "construction_heuristic")


    def start_random_construction_heuristics(self, random_k):
        print("start-random-const..." + str(random_k))

    def start_local_search(self, neighborhood_str, pre_load):
        print("start-local-search..." + str(neighborhood_str))

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
                solution = initialization_procedure.create_solution()

            if neighborhood_str == 'trip_2_opt':
                neighborhood = Trip_2_Opt(instance)
            elif neighborhood_str == 'swap_served_unserved_customer':
                neighborhood = Swap_Served_Unserved_Customer(instance)
            elif neighborhood_str == 'interchange_customers':
                neighborhood = Interchange_Customers(instance)
            elif neighborhood_str == 'exchange_hotel':
                neighborhood = Exchange_Hotel(instance)
            elif neighborhood_str == 'move_hotel':
                neighborhood = Move_Hotel(instance)

            #neighborhood = Remove_Customer(instance)
            #neighborhood = Add_Customer(instance)
            #neighborhood = Insert_Customer(instance)

            #neighborhood = Remove_Hotel(instance)
            #neighborhood = Add_Hotel(instance)


            randomization_k = 0
            search_alg = Local_Search(instance, randomization_k)
            result = search_alg.start_search(solution, Step_Function_Type.FIRST, neighborhood)

            self._logger.info("Trace of objective values: " + str(result.get_trace()))
            self._logger.info(result.get_best_solution().to_string())



    def start_grasp_search(self, random_k, neighborhood):
        print("start-grasp-search..." + str(random_k) + "::" + str(neighborhood))

    def start_vnd_search(self, pre_load):
        print("start-vnd-search")

    def start_gvns_search(self, pre_load):
        print("start-gvns-search")

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
