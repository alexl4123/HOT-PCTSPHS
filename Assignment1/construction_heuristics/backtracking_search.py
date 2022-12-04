import time
import logging
import random
import numpy as np

from framework.result import Result
from framework.solution import Solution, Delta, Add, Remove, Reverse
from framework.constants import logger_name
from construction_heuristics.initialization_procedure import Initialization_Procedure

logger = logging.getLogger(logger_name)


class Backtracking_Search(Initialization_Procedure):
    """
    Tries to do a breadth limited backtracking search, thereby increasing the speed, but it may not find a solution.
    Breadth limited means in this context, that it backtracks if it cannot progress further, if it does so it only considers the (randomized) nearest neighbor and the nearest hotel, so in the worst possible outcome we have a branching factor of 2.
    """

    def __init__(self, instance, alpha=1, beta=-0.5, gamma=-0.5, delta=0.5, delta_evaluation = True):
        super().__init__(instance, alpha, beta, gamma, delta)
        self._delta = delta_evaluation

    def create_solution(self, random_k=0, output = True, max_runtime = 90):

        self._random_k = random_k

        solution = Solution(self._instance)

        starting_hotel = self._instance.get_hotel_per_index(0)
        starting_trip_index = 0
        starting_trip_index_position = 0
        starting_trip_length = 0

        starting_time = time.time()

        result = self.backtracking(solution, starting_hotel, starting_trip_index, starting_trip_index_position,
                                   starting_trip_length, starting_time, max_runtime)

        duration = time.time() - starting_time

        if result:
            if output:
                logger.debug("Check all constraints verified, C1: " + str(solution.is_c1_satisfied()) + ", C2:" + str(
                    solution.is_c2_satisfied()) + ", C3:" + str(solution.is_c3_satisfied()))
                logger.info("Backtracking found solution with obj-value of " + str(solution.get_objective_value()))
                logger.debug("Backtracking solution verified by slow calculation:" + str(
                    solution.slow_objective_values_calculation()))
                logger.info(solution.to_string())

            return Result(solution, [solution.get_objective_value()], duration)
        else:
            logger.error("Backtracking could not find a solution!")
            return Result(False, [-1], duration)

    def backtracking(self, solution, obj, trip_index, trip_index_position, current_trip_length, starting_time, max_runtime):

        if not solution.is_c3_satisfied() and solution.is_c2_satisfied():
            return self.backtracking_helper(solution, obj, trip_index, trip_index_position, current_trip_length, starting_time, max_runtime)
        elif solution.is_c2_satisfied():
            if solution.is_c1_satisfied() and solution.is_c2_satisfied() and solution.is_c3_satisfied():
                return True
            else:
                return self.backtracking_helper(solution, obj, trip_index, trip_index_position, current_trip_length, starting_time, max_runtime)
                # return False

        return False

    def backtracking_helper(self, solution, obj, trip_index, trip_index_position, current_trip_length, starting_time, max_runtime):

        inst = self._instance

        # LIMIT-BREADTH
        index = 0
        if trip_index_position == 0:
            index_upper_limit = 1
        elif trip_index_position == 1:
            index_upper_limit = 1
        else:
            index_upper_limit = 1
        # LIMIT-BREADTH

        for nearest in self.get_all_nearest_customers(obj, self._random_k):
            #print(solution.to_string())
            #print(nearest.get_id())

            if time.time() - starting_time > max_runtime:
                #print("TIMEOUT")
                return False

            # LIMIT-BREADTH
            if index >= index_upper_limit:
                break
            # LIMIT-BREADTH

            if self._delta:
                new_dist = inst.get_distance(obj, nearest)
                if not solution.is_customer_served(nearest) and new_dist > 0:

                    # LIMIT-BREADTH
                    index = index + 1
                    # LIMIT-BREADTH

                    new_trip_length = new_dist + current_trip_length

                    if new_trip_length <= inst.get_C1():
                        delta = Delta([Add(nearest, trip_index, trip_index_position)])

                        worthiness = solution.change_from_delta(delta)

                        # For Customer
                        result = self.backtracking(solution, nearest, trip_index, trip_index_position + 1, new_trip_length, starting_time, max_runtime)

                        if result:
                            return result
                        else:
                            solution.change_from_delta(worthiness.get_reverse_delta())

                    else:
                        break
            else: #not self._delta
                if not solution.is_customer_served(nearest) and obj.get_id() != nearest.get_id():

                    cloned_solution = solution.clone()

                    index = index + 1

                    delta = Delta([Add(nearest, trip_index, trip_index_position)])
                    cloned_solution.change_from_delta(delta, False) 
                    values = cloned_solution.slow_objective_values_calculation()

                    if values[4] <= inst.get_C1():
                        delta = Delta([Add(nearest, trip_index, trip_index_position)])
                        worthiness = solution.change_from_delta(delta, False)
                        solution.update_values_from_slow_calculation(values)

                        trip_lengths = values[7]
                        new_trip_length = trip_lengths[len(trip_lengths) - 1]

                        # For Customer
                        result = self.backtracking(solution, nearest, trip_index, trip_index_position + 1, new_trip_length, starting_time, max_runtime)

                        if result:
                            return result
                        else:
                            solution.change_from_delta(worthiness.get_reverse_delta())

                    else:
                        break


        # LIMIT-BREADTH
        index = 0
        index_upper_limit = 1
        # LIMIT-BREADTH

        if current_trip_length > 0:
            for nearest in self.get_all_nearest_hotels(obj):
                if time.time() - starting_time > max_runtime:
                    #print("TIMEOUT")
                    return False


                # LIMIT-BREADTH
                if index >= index_upper_limit:
                    break
                # LIMIT-BREADTH

                if self._delta:
                    new_dist = inst.get_distance(obj, nearest)
                    if new_dist > 0:

                        # LIMIT-BREADTH
                        index = index + 1
                        # LIMIT-BREADTH
                        new_trip_length = new_dist + current_trip_length

                        if new_trip_length <= inst.get_C1():
                            delta = Delta([Add(nearest, trip_index, trip_index_position)])

                            worthiness = solution.change_from_delta(delta)

                            # For Hotel
                            result = self.backtracking(solution, nearest, trip_index + 1, 0, 0, starting_time, max_runtime)

                            if result:
                                return result
                            else:
                                solution.change_from_delta(worthiness.get_reverse_delta())
                        else:
                            break
                else: # not delta

                    if obj.get_id() != nearest.get_id():
                        cloned_solution = solution.clone()

                        index = index + 1

                        delta = Delta([Add(nearest, trip_index, trip_index_position)])
                        cloned_solution.change_from_delta(delta, False) 
                        values = cloned_solution.slow_objective_values_calculation()

                        if values[4] <= inst.get_C1():
                            delta = Delta([Add(nearest, trip_index, trip_index_position)])
                            worthiness = solution.change_from_delta(delta, False)
                            solution.update_values_from_slow_calculation(values)

                            trip_lengths = values[7]
                            new_trip_length = trip_lengths[len(trip_lengths) - 1]

                            # For Hotel
                            result = self.backtracking(solution, nearest, trip_index + 1, 0, 0, starting_time, max_runtime)

                            if result:
                                return result
                            else:
                                solution.change_from_delta(worthiness.get_reverse_delta())

                        else:
                            break

        return False



    def to_string(self):
        return "backtracking"





