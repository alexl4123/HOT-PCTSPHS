import logging
import random
import numpy as np
import time

from framework.solution import Solution, Delta, Add, Remove, Reverse, Solution_Worthiness, Swap
from framework.constants import logger_name
from construction_heuristics.initialization_procedure import Initialization_Procedure
from framework.result import Result

logger = logging.getLogger(logger_name)


class Solution_Worthiness_Insertion_Heuristic(Solution_Worthiness):

    def __init__(self, objective_value, max_trip_duration, performed_trips, collected_prizes, delta, reverse_delta,
                 is_unserved_customer, unserved_customer_indexes):
        super().__init__(objective_value, max_trip_duration, performed_trips, collected_prizes, delta, reverse_delta)

        self._is_unserved_customer = is_unserved_customer
        self._unserved_customer_indexes = unserved_customer_indexes

    def get_is_unserved_customer(self):
        return self._is_unserved_customer

    def get_unserved_customer_indexes(self):
        return self._unserved_customer_indexes

    @classmethod
    def clone_from_worthiness(cls, worthiness, is_unserved_customer, unserved_customer_index):
        return Solution_Worthiness_Insertion_Heuristic(worthiness.get_objective_value(),
                                                       worthiness.get_max_trip_duration(),
                                                       worthiness.get_performed_trips(),
                                                       worthiness.get_collected_prizes(), worthiness.get_delta(),
                                                       worthiness.get_reverse_delta(), is_unserved_customer,
                                                       unserved_customer_index)


class Insertion_Diverse_Hotels(Initialization_Procedure):
    """
    Basically is a hybrid between insertion and greedy heuristic
    1.) It starts with the empty solution (i.e. 0[]0)
    2.) It then adds customers until constraint 1 is violated
    3.) It then tries to add a best fitting hotel at the very last position at the last trip.
    """

    def __init__(self, instance, delta = True):
        super().__init__(instance)
        self._delta = delta



    def create_solution(self, random_k=0, output = True):

        self._random_k = random_k

        solution = Solution(self._instance)

        starting_hotel = self._instance.get_hotel_per_index(0)
        starting_trip_index = 0
        starting_trip_index_position = 0
        starting_trip_length = 0

        self.unserved_customers = self._instance._customers_list.copy()

        base_mode = False
        base_mode_reverse_delta = None

        change_base_mode = False
        change_base_index = 0
        change_base_index_2 = 1
        change_base_mode_reverse_delta = None

        change_hotel_index = 0
        change_hotel_index_2 = 0
        change_hotel_reverse_delta = None

        starting_time = time.time()

        while len(self.unserved_customers) > 0 and (
                not solution.is_c1_satisfied() or not solution.is_c2_satisfied() or not solution.is_c3_satisfied()):

            cur_best = self.get_best_customer(solution)

            failed = True

            if cur_best:
                # Adding customers

                base_mode = False
                base_mode_reverse_delta = None

                change_base_mode = False
                # change_base_index = 1
                change_base_index_2 = 0
                change_base_mode_reverse_delta = None

                change_hotel_index = 1
                change_hotel_index_2 = 0
                change_hotel_reverse_delta = None

                failed = False

                solution.change_from_delta(cur_best.get_delta())
                if cur_best.get_is_unserved_customer():
                    for unserved_customer_index in cur_best.get_unserved_customer_indexes():
                        del self.unserved_customers[unserved_customer_index]
            elif change_base_index_2 < len(self._instance._hotels_list):
                # Adding hotels
                # Tries to add a hotel, but only looks at the very last trip

                failed = False

                if change_base_mode_reverse_delta:
                    solution.change_from_delta(change_base_mode_reverse_delta)

                trip_index = len(solution._hotels) - 2
                second_to_last_hotel = solution._hotels[trip_index]

                next_hotels = self._instance.get_all_nearest_hotels(second_to_last_hotel)
                next_hotel = next_hotels[change_base_index]

                add = Add(next_hotel, trip_index, len(solution._trips[trip_index]))
                delta = Delta([add])

                worthiness = solution.change_from_delta(delta)

                change_base_index = change_base_index + 1
                if change_base_index >= len(self._instance._hotels_list) - 1:
                    change_base_index = 0
                change_base_index_2 = change_base_index_2 + 1

                if not solution.is_c1_satisfied() or not solution.is_c2_satisfied():
                    solution.change_from_delta(worthiness.get_reverse_delta())
                    change_base_mode_reverse_delta = None
                else:
                    change_base_mode_reverse_delta = worthiness.get_reverse_delta()

            if failed:
                logger.error("Insertion Heuristic-3 could not find a solution!")
                duration = time.time() - starting_time
                return Result(False, [-1], duration)

        duration = time.time() - starting_time

        if solution.is_c1_satisfied() and solution.is_c2_satisfied() and solution.is_c3_satisfied():
            if output:
                logger.debug("Check all constraints verified, C1: " + str(solution.is_c1_satisfied()) + ", C2:" + str(
                    solution.is_c2_satisfied()) + ", C3:" + str(solution.is_c3_satisfied()))
                logger.info("Insertion-3 found solution with obj-value of " + str(solution.get_objective_value()))
                logger.debug("Insertion-3 solution verified by slow calculation:" + str(
                    solution.slow_objective_values_calculation()))
                logger.info(solution.to_string())
            return Result(solution, [solution.get_objective_value()], duration)
        else:
            logger.error("Insertion-3 Heuristic could not find a solution!")
            return Result(False, [solution.get_objective_value()], duration)

    def get_best_customer(self, solution):
        cur_best = None
        cur_best_sum_of_trips = 0

        for trip_index in range(len(solution._trips)):
            last_node = solution._hotels[trip_index]
            last_trip_index = trip_index
            last_trip_index_position = 0

            for trip_position_index in range(len(solution._trips[trip_index])):
                next_node = solution._trips[trip_index][trip_position_index]
                next_trip_index = trip_index
                next_trip_index_position = trip_position_index

                (sum_of_trips, worthiness) = self.get_best_customer_for_edge(solution, last_trip_index,
                                                                             last_trip_index_position, last_node,
                                                                             next_trip_index, next_trip_index_position,
                                                                             next_node)

                if cur_best and worthiness and cur_best_sum_of_trips > sum_of_trips:
                    cur_best = worthiness
                    cur_best_sum_of_trips = sum_of_trips
                elif not cur_best and worthiness:
                    cur_best = worthiness
                    cur_best_sum_of_trips = sum_of_trips

                last_node = next_node
                last_trip_index = next_trip_index
                last_trip_index_position = next_trip_index_position

            #
            if trip_index < len(solution._hotels) - 1:
                next_node = solution._hotels[trip_index + 1]
                next_trip_index = trip_index
                next_trip_index_position = len(solution._trips[trip_index])

                (sum_of_trips, worthiness) = self.get_best_customer_for_edge(solution, last_trip_index,
                                                                             last_trip_index_position, last_node,
                                                                             next_trip_index, next_trip_index_position,
                                                                             next_node)

                if cur_best and worthiness and cur_best_sum_of_trips > sum_of_trips:
                    cur_best = worthiness
                    cur_best_sum_of_trips = sum_of_trips
                elif not cur_best and worthiness:
                    cur_best = worthiness
                    cur_best_sum_of_trips = sum_of_trips

        next_node = solution._hotels[len(solution._hotels) - 1]
        next_trip_index = len(solution._trips) - 1
        next_trip_index_position = 0

        (sum_of_trips, worthiness) = self.get_best_customer_for_edge(solution, last_trip_index,
                                                                     last_trip_index_position, last_node,
                                                                     next_trip_index, next_trip_index_position,
                                                                     next_node)
        if cur_best and worthiness and cur_best_sum_of_trips > sum_of_trips:
            cur_best = worthiness
            cur_best_sum_of_trips = sum_of_trips
        elif not cur_best and worthiness:
            cur_best = worthiness
            cur_best_sum_of_trips = sum_of_trips

        return cur_best

    def get_best_customer_for_edge(self, solution, last_trip_index, last_trip_index_position, last_node,
                                   next_trip_index, next_trip_index_position, next_node):

        cur_best = None
        cur_best_total_length = 0

        for customer_index in range(len(self.unserved_customers)):
            customer = self.unserved_customers[customer_index]

            # print("CUSTOMER:" + str(customer.get_id()) + "::" + str(next_trip_index) + "::" + str(next_trip_index_position))
            add = Add(customer, next_trip_index, next_trip_index_position)
            delta = Delta([add])

            """
            print("BEFORE-CUSTOMER-ADD:" + str(customer.get_id()))
            print(solution.to_string())
            print("Add at position:" + str(next_trip_index) + "::" + str(next_trip_index_position))
            print(solution.slow_objective_values_calculation())
            print(solution._max_trip_length)
            print(self._instance.get_C1())
            """

            worthiness = solution.change_from_delta(delta)

            """
            print("-----------------------------------")
            print(solution.to_string())
            print(solution.slow_objective_values_calculation())
            print(solution._max_trip_length)
            print(self._instance.get_C1())
 
            print("AFTER-CUSTOMER-ADD:")
            """

            if solution.is_c1_satisfied() and solution.is_c2_satisfied():
                if cur_best and cur_best_total_length > solution._sum_of_trips:
                    cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, True,
                                                                                             [customer_index])
                    cur_best_total_length = solution._sum_of_trips
                elif not cur_best:
                    cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, True,
                                                                                             [customer_index])
                    cur_best_total_length = solution._sum_of_trips

                # if solution.is_c3_satisfied():
                #    return worthiness

            solution.change_from_delta(worthiness.get_reverse_delta())

        return (cur_best_total_length, cur_best)
