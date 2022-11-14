
import logging

from .solution import Solution, Delta
from .constants import logger_name

logger = logging.getLogger(logger_name)

class Tester:

    def __init__(self, instance):
        self._instance = instance



    def trips_printer(self, trips):
        string = "["
        for trip in trips:
            string = string + "["
            for obj in trip:
                string = string + str(obj.get_id()) + ","

            string = string + "]"

        string = string + "]"
        print(string)

    def hotels_printer(self, hotels):
        string = "["
        for obj in hotels:
            string = string + str(obj.get_id()) + ","

        string = string + "]"
        print(string)



    def _mini_test(self, solution, removes, adds, should_objective_value, should_max_trip_length, should_number_of_trips, should_prize):
        my_delta = Delta(removes, adds)

        prev_obj_val = solution.get_objective_value()
        prev_max_trip_length = solution.get_max_trip_length()
        prev_number_of_trips = solution.get_number_of_trips()
        prev_prize = solution.get_prize()

        reverse_delta = solution.change_from_delta(my_delta)

        works = True

        if solution.get_objective_value() != should_objective_value:
            logger.error("Should and Is objective_value do not correspond: SHOULD: " + str(should_objective_value) + " IS:" + str(solution.get_objective_value()))
            works = False

        if solution.get_max_trip_length() != should_max_trip_length:
            logger.error("Should and Is max_trip_length do not correspond: SHOULD: " + str(should_max_trip_length) + " IS:" + str(solution.get_max_trip_length()))
            works = False

        if solution.get_number_of_trips() != should_number_of_trips:
            logger.error("Should and Is number_of_trips do not correspond: SHOULD: " + str(should_number_of_trips) + " IS:" + str(solution.get_number_of_trips()))
            works = False

        if solution.get_prize() != should_prize:
            logger.error("Should and Is prize do not correspond: SHOULD: " + str(should_prize) + " IS:" + str(solution.get_prize()))
            works = False

        print(solution.get_objective_value())
        print(solution.get_max_trip_length())
        print(solution.get_number_of_trips())
        print(solution.get_prize())

        self.trips_printer(solution._trips)
        self.hotels_printer(solution._hotels)

        # ------ TESTS REVERSE ---------

        reverse_reverse = solution.change_from_delta(reverse_delta.get_reverse_delta())

        if solution.get_objective_value() != prev_obj_val:
            logger.error("REVERSE: Should and Is objective_value do not correspond: SHOULD: " + str(should_objective_value) + " IS:" + str(solution.get_objective_value()))
            works = False

        if solution.get_max_trip_length() != prev_max_trip_length:
            logger.error("REVERSE: Should and Is max_trip_length do not correspond: SHOULD: " + str(should_max_trip_length) + " IS:" + str(solution.get_max_trip_length()))
            works = False

        if solution.get_number_of_trips() != prev_number_of_trips:
            logger.error("REVERSE: Should and Is number_of_trips do not correspond: SHOULD: " + str(should_number_of_trips) + " IS:" + str(solution.get_number_of_trips()))
            works = False

        if solution.get_prize() != prev_prize:
            logger.error("REVERSE: Should and Is prize do not correspond: SHOULD: " + str(should_prize) + " IS:" + str(solution.get_prize()))
            works = False

        # -------- TESTS REVERSE REVERSE ----------

        solution.change_from_delta(reverse_reverse.get_reverse_delta())

        if solution.get_objective_value() != should_objective_value:
            logger.error("Should and Is objective_value do not correspond: SHOULD: " + str(should_objective_value) + " IS:" + str(solution.get_objective_value()))
            works = False

        if solution.get_max_trip_length() != should_max_trip_length:
            logger.error("Should and Is max_trip_length do not correspond: SHOULD: " + str(should_max_trip_length) + " IS:" + str(solution.get_max_trip_length()))
            works = False

        if solution.get_number_of_trips() != should_number_of_trips:
            logger.error("Should and Is number_of_trips do not correspond: SHOULD: " + str(should_number_of_trips) + " IS:" + str(solution.get_number_of_trips()))
            works = False

        if solution.get_prize() != should_prize:
            logger.error("Should and Is prize do not correspond: SHOULD: " + str(should_prize) + " IS:" + str(solution.get_prize()))
            works = False

        return works


    def test_solution_class(self):

        solution = Solution(self._instance)
        # Simple customer insertion operations (I0-I3)
        works = self._mini_test(solution, [], [], 2150, 0, 1, 0)
        works = works and self._mini_test(solution, [], [(self._instance.get_customer_per_index(2), 0, 0)], 1880, 480, 1, 1000)
        works = works and self._mini_test(solution, [], [(self._instance.get_customer_per_index(3), 0, 0)], 1840, 740, 1, 1900)
        works = works and self._mini_test(solution, [], [(self._instance.get_customer_per_index(4), 0, 2)], 1650, 1050, 1, 2000)
        works = works and self._mini_test(solution, [], [(self._instance.get_customer_per_index(5), 0, 1)], 1750, 1750, 1, 2500)
        print("SIMPLE CUSTOMER INSERTION COMPLETE")
        # Simple customer deletion operations (DC0-DC3)
        works = works and self._mini_test(solution, [(self._instance.get_customer_per_index(5), 0, 1)], [], 1650, 1050, 1, 2000)
        works = works and self._mini_test(solution, [(self._instance.get_customer_per_index(4), 0, 2)], [], 1840, 740, 1, 1900)
        works = works and self._mini_test(solution, [(self._instance.get_customer_per_index(3), 0, 0)], [], 1880, 480, 1, 1000)
        works = works and self._mini_test(solution, [(self._instance.get_customer_per_index(2), 0, 0)], [], 2150, 0, 1, 0)
        print("SIMPLE CUSTOMER REMOVAL COMPLETE")
        # Simple hotel insertion operations (H0-H3 + necessary customer ops)
        works = works and self._mini_test(solution, [], [(self._instance.get_hotel_per_index(1), 0, 0)], 3090, 420, 2, 0)
        works = works and self._mini_test(solution, [], [(self._instance.get_customer_per_index(2), 0, 0)], 2560, 640, 2, 1000)
        works = works and self._mini_test(solution, [], [(self._instance.get_hotel_per_index(1), 0, 0)], 3240, 800, 3, 1000)
        works = works and self._mini_test(solution, [], [(self._instance.get_hotel_per_index(1), 1, 1)], 3340, 800, 4, 1000)
        works = works and self._mini_test(solution, [], [(self._instance.get_customer_per_index(3), 1, 1)], 3000, 760, 4, 1900)
        works = works and self._mini_test(solution, [], [(self._instance.get_hotel_per_index(1), 1, 1)], 3660, 800, 5, 1900)
        print("SIMPLE HOTEL INSERTION COMPLETE")
        works = works and self._mini_test(solution, [(self._instance.get_hotel_per_index(1), 2, 0)], [], 3000, 760, 4, 1900)
        works = works and self._mini_test(solution, [(self._instance.get_customer_per_index(3), 1, 1)], [], 3340, 800, 4, 1000)
        works = works and self._mini_test(solution, [(self._instance.get_hotel_per_index(1), 2, 0)], [], 3240, 800, 3, 1000)
        works = works and self._mini_test(solution, [(self._instance.get_hotel_per_index(1), 1, 0)], [], 2560, 640, 2, 1000)
        works = works and self._mini_test(solution, [(self._instance.get_customer_per_index(2), 0, 0)], [], 3090, 420, 2, 0)
        works = works and self._mini_test(solution, [(self._instance.get_hotel_per_index(1), 1, 0)], [], 2150, 0, 1, 0)
        print("SIMPLE HOTEL REMOVAL COMPLETE")

        print("ALL TESTS WORKED (TRUE = YES/FALSE = NO): " + str(works))
        print("Further note: test may only be invoked with the test_2.txt instance!")

        """
        # Simple insertion operations (H1-H4)
        solution = Solution(self._instance)
        self._mini_test(solution, [], [], 2150, 0, 1, 0)
        self._mini_test(solution, [], [(self._instance.get_customer_per_index(2), 0, 0)], 1880, 480, 1, 1000)
        self._mini_test(solution, [], [(self._instance.get_customer_per_index(3), 0, 0)], 1840, 740, 1, 1900)
        self._mini_test(solution, [], [(self._instance.get_customer_per_index(4), 0, 2)], 1650, 1050, 1, 2000)
        self._mini_test(solution, [], [(self._instance.get_customer_per_index(5), 0, 1)], 1750, 1750, 1, 2500)
        """



