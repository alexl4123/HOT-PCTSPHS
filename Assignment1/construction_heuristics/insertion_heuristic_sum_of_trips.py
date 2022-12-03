import logging
import random
import numpy as np

from framework.solution import Solution, Delta, Add, Remove, Reverse, Solution_Worthiness, Swap
from framework.constants import logger_name
from construction_heuristics.initialization_procedure import Initialization_Procedure

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


class Insertion_Heuristic_Sum_Of_Trips(Initialization_Procedure):
    """
    Is an insertion heuristic, that works according to the following principle:
    1.) It starts with an ''empty'' tour (i.e. 0[]0)
    2.) Tries to add as many customers as possible, s.t. constraint 1 is satisfied (the customer is chosen, s.t. the total sum of trips is minimized)
    3.) If one cannot add anymore customers without destroying constraint 1, then try to add hotels
    4.) If also adding hotels doesn't work, try swapping
    """

    def create_solution(self, random_k=0):

        self._random_k = random_k

        solution = Solution(self._instance)

        starting_hotel = self._instance.get_hotel_per_index(0)
        starting_trip_index = 0
        starting_trip_index_position = 0
        starting_trip_length = 0

        self.unserved_customers = self._instance._customers_list.copy()

        while len(self.unserved_customers) > 0 and (
                not solution.is_c1_satisfied() or not solution.is_c2_satisfied() or not solution.is_c3_satisfied()):
            cur_best = None
            cur_best_sum_of_trips = 0
            cur_best_hotel = None
            cur_best_distance_hotel = 0
            cur_best_swap = None
            cur_best_distance_swap = 0

            avg_trip_distance = 0
            for trip_index in range(len(solution._trips)):
                avg_trip_distance = avg_trip_distance + solution._trip_lengths[trip_index]
            avg_trip_distance = avg_trip_distance / len(solution._trips)

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
                                                                                 next_trip_index,
                                                                                 next_trip_index_position, next_node)

                    (worthiness_hotel, distance_hotel) = self.get_best_hotel_for_edge(solution, avg_trip_distance,
                                                                                      last_trip_index,
                                                                                      last_trip_index_position,
                                                                                      last_node, next_trip_index,
                                                                                      next_trip_index_position,
                                                                                      next_node)
                    (worthiness_swap, distance_swap) = self.get_best_swap_customer(solution, avg_trip_distance,
                                                                                   last_trip_index,
                                                                                   last_trip_index_position, last_node,
                                                                                   next_trip_index,
                                                                                   next_trip_index_position, next_node)

                    if cur_best and worthiness and cur_best_sum_of_trips > sum_of_trips:
                        cur_best = worthiness
                        cur_best_sum_of_trips = sum_of_trips
                    elif not cur_best and worthiness:
                        cur_best = worthiness
                        cur_best_sum_of_trips = sum_of_trips
                    
                    if cur_best_hotel and worthiness_hotel and distance_hotel > cur_best_distance_hotel:
                        cur_best_hotel = worthiness_hotel
                        cur_best_distance_hotel = distance_hotel
                    elif not cur_best_hotel and worthiness_hotel:
                        cur_best_hotel = worthiness_hotel
                        cur_best_distance_hotel = distance_hotel

                    if cur_best_swap and worthiness_swap and distance_swap > cur_best_distance_swap:
                        cur_best_swap = worthiness_swap
                        cur_best_distance_swap = distance_swap
                    elif not cur_best and worthiness_swap:
                        cur_best_swap = worthiness_swap
                        cur_best_distance_swap = distance_swap

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
                                                                                 next_trip_index,
                                                                                 next_trip_index_position, next_node)
                    (worthiness_hotel, distance_hotel) = self.get_best_hotel_for_edge(solution, avg_trip_distance,
                                                                                      last_trip_index,
                                                                                      last_trip_index_position,
                                                                                      last_node, next_trip_index,
                                                                                      next_trip_index_position,
                                                                                      next_node)
                    # No SWAP!
                    # worthiness_swap = self.get_best_swap_customer(solution, last_trip_index, last_trip_index_position, last_node, next_trip_index, next_trip_index_position, next_node)

                    if cur_best and worthiness and cur_best_sum_of_trips > sum_of_trips:
                        cur_best = worthiness
                        cur_best_sum_of_trips = sum_of_trips
                    elif not cur_best and worthiness:
                        cur_best = worthiness
                        cur_best_sum_of_trips = sum_of_trips

                    if cur_best_hotel and worthiness_hotel and distance_hotel > cur_best_distance_hotel:
                        cur_best_hotel = worthiness_hotel
                        cur_best_distance_hotel = distance_hotel
                    elif not cur_best_hotel and worthiness_hotel:
                        cur_best_hotel = worthiness_hotel
                        cur_best_distance_hotel = distance_hotel

                    """
                    if cur_best_hotel and worthiness_hotel and cur_best_hotel.get_objective_value() > worthiness_hotel.get_objective_value():
                        cur_best_hotel = worthiness_hotel
                    elif not cur_best_hotel and worthiness_hotel:
                        cur_best_hotel = worthiness_hotel
                    """

                    """
                    if cur_best_swap and worthiness_swap and cur_best_swap.get_objective_value() > worthiness_swap.get_objective_value():
                        cur_best_swap = worthiness_swap
                    elif not cur_best and worthiness:
                        cur_best_swap = worthiness_swap
                    """

            next_node = solution._hotels[len(solution._hotels) - 1]
            next_trip_index = len(solution._trips) - 1
            next_trip_index_position = 0

            (sum_of_trips, worthiness) = self.get_best_customer_for_edge(solution, last_trip_index,
                                                                         last_trip_index_position, last_node,
                                                                         next_trip_index, next_trip_index_position,
                                                                         next_node)
            (worthiness_hotel, distance_hotel) = self.get_best_hotel_for_edge(solution, avg_trip_distance,
                                                                              last_trip_index, last_trip_index_position,
                                                                              last_node, next_trip_index,
                                                                              next_trip_index_position, next_node)
            # NO SWAPPING HOTELS
            # worthiness_swap = self.get_best_swap_customer(solution, last_trip_index, last_trip_index_position, last_node, next_trip_index, next_trip_index_position, next_node)

            if cur_best and worthiness and cur_best_sum_of_trips > sum_of_trips:
                cur_best = worthiness
                cur_best_sum_of_trips = sum_of_trips
            elif not cur_best and worthiness:
                cur_best = worthiness
                cur_best_sum_of_trips = sum_of_trips

            if cur_best_hotel and worthiness_hotel and distance_hotel > cur_best_distance_hotel:
                cur_best_hotel = worthiness_hotel
                cur_best_distance_hotel = distance_hotel
            elif not cur_best_hotel and worthiness_hotel:
                cur_best_hotel = worthiness_hotel
                cur_best_distance_hotel = distance_hotel

            """
            if cur_best_hotel and worthiness_hotel and cur_best_hotel.get_objective_value() > worthiness_hotel.get_objective_value():
                cur_best_hotel = worthiness_hotel
            elif not cur_best_hotel and worthiness_hotel:
                cur_best_hotel = worthiness_hotel
            """

            """
            if cur_best_swap and worthiness_swap and cur_best_swap.get_objective_value() > worthiness_swap.get_objective_value():
                cur_best_swap = worthiness_swap
            elif not cur_best and worthiness:
                cur_best_swap = worthiness_swap
            """

            if cur_best:
                solution.change_from_delta(cur_best.get_delta())
                if cur_best.get_is_unserved_customer():
                    for unserved_customer_index in cur_best.get_unserved_customer_indexes():
                        del self.unserved_customers[unserved_customer_index]
            elif cur_best_swap:
                solution.change_from_delta(cur_best_swap.get_delta())
                if not cur_best_swap.get_is_unserved_customer():
                    for unserved_customer_index in cur_best_swap.get_unserved_customer_indexes():
                        self.unserved_customers.append(unserved_customer_index)
            elif cur_best_hotel:
                solution.change_from_delta(cur_best_hotel.get_delta())
                if not cur_best_hotel.get_is_unserved_customer():
                    for unserved_customer_index in cur_best_hotel.get_unserved_customer_indexes():
                        self.unserved_customers.append(unserved_customer_index)

            else:
                logger.error("Insertion Heuristic could not find a solution!")
                return False

        if solution.is_c1_satisfied() and solution.is_c2_satisfied() and solution.is_c3_satisfied():
            logger.debug("Check all constraints verified, C1: " + str(solution.is_c1_satisfied()) + ", C2:" + str(
                solution.is_c2_satisfied()) + ", C3:" + str(solution.is_c3_satisfied()))
            logger.info("Insertion found solution with obj-value of " + str(solution.get_objective_value()))
            logger.debug(
                "Insertion solution verified by slow calculation:" + str(solution.slow_objective_values_calculation()))
            logger.info(solution.to_string())
            return solution
        else:
            logger.error("Insertion Heuristic could not find a solution!")
            return False

    def get_best_customer_for_edge(self, solution, last_trip_index, last_trip_index_position, last_node,
                                   next_trip_index, next_trip_index_position, next_node):

        cur_best = None
        cur_best_total_length = 0

        for customer_index in range(len(self.unserved_customers)):
            customer = self.unserved_customers[customer_index]

            add = Add(customer, next_trip_index, next_trip_index_position)
            delta = Delta([add])

            worthiness = solution.change_from_delta(delta)

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

    def get_best_hotel_for_edge(self, solution, avg_trip_distance, last_trip_index, last_trip_index_position, last_node,
                                next_trip_index, next_trip_index_position, next_node):

        cur_best = None
        cur_best_distance = 0

        old_trip_distance = solution._trip_lengths[next_trip_index]

        for hotel_index in range(len(self._instance._hotels_list)):
            hotel = self._instance._hotels_list[hotel_index]

            # if hotel.get_id() == last_node.get_id() and hotel.get_id() == next_node.get_id():
            #    continue

            add = Add(hotel, next_trip_index, next_trip_index_position)
            delta = Delta([add])

            worthiness = solution.change_from_delta(delta)

            if solution.is_c1_satisfied() and solution.is_c2_satisfied():
                new_trip_length_1 = solution._trip_lengths[next_trip_index]
                new_trip_length_2 = solution._trip_lengths[next_trip_index + 1]

                # new_max = max([new_trip_length_1, new_trip_length_2])
                # diff_lengths = old_trip_distance - new_max
                # diff_lengths = new_trip_length_1 + new_trip_length_2
                diff_lengths = len(solution._trips[next_trip_index]) + len(solution._trips[next_trip_index + 1])

                if (len(solution._trips[next_trip_index]) > 0 or len(solution._trips[next_trip_index + 1]) > 0):

                    if cur_best and diff_lengths > cur_best_distance:
                        cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False, [])
                        cur_best_distance = diff_lengths
                    elif not cur_best:
                        cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False, [])
                        cur_best_distance = diff_lengths

            solution.change_from_delta(worthiness.get_reverse_delta())

        return (cur_best, cur_best_distance)

    def get_best_swap_customer(self, solution, avg_trip_distance, last_trip_index, last_trip_index_position, last_node,
                               next_trip_index, next_trip_index_position, next_node):

        cur_best = None
        cur_best_distance = 0

        old_trip_distance = solution._trip_lengths[next_trip_index]

        for hotel in self._instance._hotels_list:
            # print(str(cur_max_trip_value_index) + str(item_index))

            remove = Remove(next_node, next_trip_index, next_trip_index_position)
            add = Add(hotel, next_trip_index, next_trip_index_position)

            delta = Delta([remove, add])

            worthiness = solution.change_from_delta(delta)

            if solution.is_c1_satisfied() and solution.is_c2_satisfied():
                new_trip_length_1 = solution._trip_lengths[next_trip_index]
                new_trip_length_2 = solution._trip_lengths[next_trip_index + 1]

                # new_max = max([new_trip_length_1, new_trip_length_2])
                # diff_lengths = old_trip_distance - new_max
                # diff_lengths = new_trip_length_1 + new_trip_length_2
                diff_lengths = len(solution._trips[next_trip_index]) + len(solution._trips[next_trip_index + 1])

                # if new_trip_length_1 > 0 and new_trip_length_2 > 0:
                if (len(solution._trips[next_trip_index]) > 0 or len(solution._trips[next_trip_index + 1]) > 0):
                    if cur_best and diff_lengths > cur_best_distance:
                        cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False,
                                                                                                 [next_node])
                        cur_best_distance = diff_lengths
                    elif not cur_best:
                        cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False,
                                                                                                 [next_node])
                        cur_best_distance = diff_lengths

            solution.change_from_delta(worthiness.get_reverse_delta())

        if not cur_best:
            # Try removing the one before
            if next_trip_index_position > 0:
                for hotel in self._instance._hotels_list:
                    # print(str(cur_max_trip_value_index) + str(item_index))
                    remove = Remove(next_node, next_trip_index, next_trip_index_position)
                    next_node_2 = solution._trips[next_trip_index][next_trip_index_position - 1]
                    remove2 = Remove(next_node_2, next_trip_index, next_trip_index_position - 1)
                    add = Add(hotel, next_trip_index, next_trip_index_position)

                    delta = Delta([remove, remove2, add])

                    worthiness = solution.change_from_delta(delta)

                    if solution.is_c1_satisfied() and solution.is_c2_satisfied() and (
                            len(solution._trips[next_trip_index]) > 0 or len(solution._trips[next_trip_index + 1]) > 0):
                        new_trip_length_1 = solution._trip_lengths[next_trip_index]
                        new_trip_length_2 = solution._trip_lengths[next_trip_index + 1]

                        # new_max = max([new_trip_length_1, new_trip_length_2])
                        # diff_lengths = old_trip_distance - new_max

                        # diff_lengths = new_trip_length_1 + new_trip_length_2
                        diff_lengths = len(solution._trips[next_trip_index]) + len(solution._trips[next_trip_index + 1])

                        if cur_best and diff_lengths > cur_best_distance:
                            cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False,
                                                                                                     [next_node,
                                                                                                      next_node_2])
                            cur_best_distance = diff_lengths
                        elif not cur_best:
                            cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False,
                                                                                                     [next_node,
                                                                                                      next_node_2])
                            cur_best_distance = diff_lengths

                    solution.change_from_delta(worthiness.get_reverse_delta())

            # Try removing one after
            if not cur_best and next_trip_index_position < (len(solution._trips[next_trip_index]) - 1):
                for hotel in self._instance._hotels_list:
                    # print(str(cur_max_trip_value_index) + str(item_index))
                    remove = Remove(next_node, next_trip_index, next_trip_index_position)
                    next_node_2 = solution._trips[next_trip_index][next_trip_index_position + 1]
                    remove2 = Remove(next_node_2, next_trip_index, next_trip_index_position)
                    add = Add(hotel, next_trip_index, next_trip_index_position)

                    delta = Delta([remove, remove2, add])

                    worthiness = solution.change_from_delta(delta)

                    if solution.is_c1_satisfied() and solution.is_c2_satisfied() and (
                            len(solution._trips[next_trip_index]) > 0 or len(solution._trips[next_trip_index + 1]) > 0):

                        new_trip_length_1 = solution._trip_lengths[next_trip_index]
                        new_trip_length_2 = solution._trip_lengths[next_trip_index + 1]

                        # new_max = max([new_trip_length_1, new_trip_length_2])
                        # diff_lengths = old_trip_distance - new_max
                        # diff_lengths = new_trip_length_1 + new_trip_length_2
                        diff_lengths = len(solution._trips[next_trip_index]) + len(solution._trips[next_trip_index + 1])

                        if cur_best and diff_lengths > cur_best_distance:

                            cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False,
                                                                                                     [next_node,
                                                                                                      next_node_2])
                            cur_best_distance = diff_lengths
                        elif not cur_best:
                            cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False,
                                                                                                     [next_node,
                                                                                                      next_node_2])
                            cur_best_distance = diff_lengths

                    solution.change_from_delta(worthiness.get_reverse_delta())

        return (cur_best, cur_best_distance)

    """ 
        cur_max_trip_value = solution._max_trip_length
        cur_max_trip_value_index = -1

        for trip_length_index in range(len(solution._trip_lengths)):
            cur_trip_length = solution._trip_lengths[trip_length_index]

            if cur_max_trip_value == cur_trip_length:
                cur_max_trip_value_index = trip_length_index

        if cur_max_trip_value_index == -1:
            logger.error("FATAL-IN-INSERTION-HEURISTIC")
            quit()
        
        for item_index in range(len(solution._trips[cur_max_trip_value_index])):

            old_item = solution._trips[cur_max_trip_value_index][item_index]

    """
