import sys
import logging

from constants import logger_name
from load_and_parse import Input_file_parser
from solution import Solution, Delta

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

solution = Solution(instance)

def trips_printer(trips):
    string = "["
    for trip in trips:
        string = string + "["
        for obj in trip:
            string = string + str(obj.get_id()) + ","

        string = string + "]"

    string = string + "]"
    print(string)

def hotels_printer(hotels):
    string = "["
    for obj in hotels:
        string = string + str(obj.get_id()) + ","

    string = string + "]"
    print(string)


trips_printer(solution._trips)
hotels_printer(solution._hotels)

my_delta = Delta([], [(instance.get_list_of_customers()[0], 0, 0)])
solution.change_from_delta(my_delta)
trips_printer(solution._trips)
hotels_printer(solution._hotels)

my_delta = Delta([], [(instance.get_list_of_customers()[1], 0, 1)])
solution.change_from_delta(my_delta)
trips_printer(solution._trips)
hotels_printer(solution._hotels)

my_delta = Delta([], [(instance.get_hotel_per_index(1), 0, 1)])
solution.change_from_delta(my_delta)
trips_printer(solution._trips)
hotels_printer(solution._hotels)

my_delta = Delta([], [(instance.get_list_of_customers()[2], 1, 0)])
solution.change_from_delta(my_delta)
trips_printer(solution._trips)
hotels_printer(solution._hotels)


my_delta = Delta([(instance.get_hotel_per_index(1), 1, 0)], [])
solution.change_from_delta(my_delta)
trips_printer(solution._trips)
hotels_printer(solution._hotels)

my_delta = Delta([(instance.get_list_of_customers()[2], 0, 1)], [])
solution.change_from_delta(my_delta)
trips_printer(solution._trips)
hotels_printer(solution._hotels)





for hotel in instance.get_list_of_hotels():
    print("Hotel with ID: " + str(hotel.get_id()) + " has fee " + str(hotel.get_fee()))

for customer in instance.get_list_of_customers():
    print("Customer with ID: " + str(customer.get_id()) + " has prize " + str(customer.get_prize()) + " and has penalty " + str(customer.get_penalty()))

for edge in instance.get_list_of_edges():
    print("Edge with vertex_a_id: " + str(edge.get_vertex_a().get_id()) + ", vertex_b_id: " + str(edge.get_vertex_b().get_id()) + " has weight " + str(edge.get_weight()))
        

