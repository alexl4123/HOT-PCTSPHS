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


def mini_solution_tester(instance):

    def mini_test(instance, solution, removes, adds, should_objective_value, should_max_trip_length, should_number_of_trips, should_prize):
        my_delta = Delta(removes, adds)
        solution.change_from_delta(my_delta)
    
        if solution.get_objective_value() != should_objective_value:
            logger.error("Should and Is objective_value do not correspond: SHOULD: " + str(should_objective_value) + " IS:" + str(solution.get_objective_value()))

        if solution.get_max_trip_length() != should_max_trip_length:
            logger.error("Should and Is max_trip_length do not correspond: SHOULD: " + str(should_max_trip_length) + " IS:" + str(solution.get_max_trip_length()))

        if solution.get_number_of_trips() != should_number_of_trips:
            logger.error("Should and Is number_of_trips do not correspond: SHOULD: " + str(should_number_of_trips) + " IS:" + str(solution.get_number_of_trips()))

        if solution.get_prize() != should_prize:
            logger.error("Should and Is prize do not correspond: SHOULD: " + str(should_prize) + " IS:" + str(solution.get_prize()))
 
        print(solution.get_objective_value())
        print(solution.get_max_trip_length())
        print(solution.get_number_of_trips())
        print(solution.get_prize())

        trips_printer(solution._trips)
        hotels_printer(solution._hotels)

    solution = Solution(instance)

    mini_test(instance, solution, [], [], 0, 0, 1, 0)
    mini_test(instance, solution, [], [(instance.get_customer_per_index(2), 0, 0)], 480, -270, 1, 1000)

    """
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
    """


mini_solution_tester(instance)


"""
for hotel in instance.get_list_of_hotels():
    print("Hotel with ID: " + str(hotel.get_id()) + " has fee " + str(hotel.get_fee()))

for customer in instance.get_list_of_customers():
    print("Customer with ID: " + str(customer.get_id()) + " has prize " + str(customer.get_prize()) + " and has penalty " + str(customer.get_penalty()))

for edge in instance.get_list_of_edges():
    print("Edge with vertex_a_id: " + str(edge.get_vertex_a().get_id()) + ", vertex_b_id: " + str(edge.get_vertex_b().get_id()) + " has weight " + str(edge.get_weight()))
"""      

