import sys
import logging

from constants import logger_name
from load_and_parse import Input_file_parser
from solution import Solution, Delta
from local_search import Local_Search, Step_Function_Type
from initialization_procedure import Initialization_Procedure
from neighborhood import Neighborhood

from test_instances import Tester

logger = logging.getLogger(logger_name)

argv = len(sys.argv)

if argv != 2:
    logger.critical("LOL")
    quit()
else:
    logger.info("ZZZ")

args = sys.argv
file_name = args[1]

my_object = Input_file_parser(file_name)
instance = my_object.load_and_parse_input_file()
instance.precompute_all_nearest_neighbors()


initialization_procedure = Initialization_Procedure(instance)
neighborhood = Neighborhood(instance)

search_alg = Local_Search(instance)
result = search_alg.start_search(initialization_procedure, Step_Function_Type.FIRST, neighborhood)

print("Trace of objective values: " + str(result.get_trace()))
print(result.get_best_solution().to_string())


#tester = Tester(instance)
#tester.test_solution_class()


"""
for hotel in instance.get_list_of_hotels():
    print("Hotel with ID: " + str(hotel.get_id()) + " has fee " + str(hotel.get_fee()))

for customer in instance.get_list_of_customers():
    print("Customer with ID: " + str(customer.get_id()) + " has prize " + str(customer.get_prize()) + " and has penalty " + str(customer.get_penalty()))

for edge in instance.get_list_of_edges():
    print("Edge with vertex_a_id: " + str(edge.get_vertex_a().get_id()) + ", vertex_b_id: " + str(edge.get_vertex_b().get_id()) + " has weight " + str(edge.get_weight()))
"""      

