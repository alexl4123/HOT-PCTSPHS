import time
import logging

from framework.solution import Delta, Solution_Worthiness
from framework.constants import logger_name
from framework.result import Result

from search_algorithms.algorithm import Algorithm
from search_algorithms.local_search import Local_Search, Step_Function_Type

from neighborhoods.neighborhood import Neighborhood
from neighborhoods.trip_2_opt import Trip_2_Opt

logger = logging.getLogger(logger_name)


class Vnd(Algorithm):

    def __init__(self, instance, random_k):
        super().__init__(instance)

        self._random_k = random_k

    def start_search(self, init_solution, step_function_type, neighborhoods, max_runtime, termination_criterion=1000, starting_time = None):

        neighborhood_number = 0
        max_neighborhood_number = len(neighborhoods) - 1 

        solution = init_solution

        trace = []

        if not starting_time:
            starting_time = time.time()

        old_objective_value = solution.get_objective_value()

        while neighborhood_number <= max_neighborhood_number:

            cur_neighborhood = neighborhoods[neighborhood_number]
            local_search = Local_Search(self._instance, 0)
            result = local_search.start_search(solution, step_function_type, [cur_neighborhood], termination_criterion, int(max_runtime/10))

            if result.get_best_solution().get_objective_value() < old_objective_value:
                neighborhood_number = 0
                old_objective_value = result.get_best_solution().get_objective_value()
            else: 
                neighborhood_number += 1

            trace.append(result.get_best_solution().get_objective_value())



            current_time = time.time()
            delta = current_time - starting_time
            if delta > max_runtime:
                break

        duration = time.time() - starting_time
        if duration > max_runtime:
            logger.info("Runtime limit reached, actual runtime: " + max_runtime)

            duration = max_runtime

        checked_values = solution.slow_objective_values_calculation()

        logger.info("VND search found solution with objective value: " + str(solution.get_objective_value()))
        logger.info("VND search solution verfification with slow calculation: " + str(checked_values))
        logger.info("VND Trace:" + str(trace))

        if checked_values[0] != solution.get_objective_value():
            logger.error("Likely error in delta-evaluation!")
            quit()
        if checked_values[0] != trace[len(trace) - 1]:
            logger.error("Likely error in neighborhood-evaluation!")
            quit()

        return Result(solution, trace, duration)
