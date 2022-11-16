import sys
import logging

from framework.constants import logger_name, file_path_to_solutions
from framework.load_and_parse import Input_file_parser
from framework.solution import Solution, Delta
from framework.test_instances import Tester

from search_algorithms.local_search import Local_Search, Step_Function_Type

from construction_heuristics.heuristic_2 import Deterministic_Greedy_Initialization
from construction_heuristics.heuristic_3 import Backtracking_Search
from construction_heuristics.heuristic_4 import Insertion_Heuristic
from construction_heuristics.heuristic_5 import Insertion_Heuristic_2
from construction_heuristics.heuristic_6 import Insertion_Heuristic_3
from construction_heuristics.heuristic_deterministic import Combination_Of_Heuristics

from neighborhoods.neighborhood import Neighborhood
from neighborhoods.trip_2_opt import Trip_2_Opt

logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("[%(levelname)s][%(asctime)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


argv = len(sys.argv)

if argv != 2:
    logger.critical("SYNOPSIS: python start.py filepath")
    quit()

args = sys.argv
file_name = args[1]

my_object = Input_file_parser(file_name)
instance = my_object.load_and_parse_input_file()
instance.precompute_all_nearest_neighbors()

if instance.is_instance_not_computable():
    logger.error("The given instance is not computable according to the necessary constraints!")
    quit()


#initialization_procedure = Deterministic_Greedy_Initialization(instance)
#initialization_procedure = Insertion_Heuristic_3(instance)
initialization_procedure = Combination_Of_Heuristics(instance)
result = initialization_procedure.create_solution(0)
result.write_solution_to_file(file_path_to_solutions)

"""
neighborhood = Trip_2_Opt(instance)

randomization_k = 0
search_alg = Local_Search(instance, randomization_k)
result = search_alg.start_search(initialization_procedure, Step_Function_Type.FIRST, neighborhood)

logger.info("Trace of objective values: " + str(result.get_trace()))
logger.info(result.get_best_solution().to_string())

#result.get_best_solution().write_solution_to_file(file_path_to_solutions)


#tester = Tester(instance)
#tester.test_solution_class()
"""

"""
for hotel in instance.get_list_of_hotels():
    print("Hotel with ID: " + str(hotel.get_id()) + " has fee " + str(hotel.get_fee()))

for customer in instance.get_list_of_customers():
    print("Customer with ID: " + str(customer.get_id()) + " has prize " + str(customer.get_prize()) + " and has penalty " + str(customer.get_penalty()))

for edge in instance.get_list_of_edges():
    print("Edge with vertex_a_id: " + str(edge.get_vertex_a().get_id()) + ", vertex_b_id: " + str(edge.get_vertex_b().get_id()) + " has weight " + str(edge.get_weight()))
"""      

