from time import process_time

import logging

from framework.solution import Delta, Solution_Worthiness
from framework.constants import logger_name
from search_algorithms.algorithm import Algorithm, Algorithm_Result

logger = logging.getLogger(logger_name)


class Grasp(Algorithm):

    def __init__(self, instance, random_k):
        super().__init__(instance)

        self._random_k = random_k

    def start_grasp(self, initialization_procedure, step_function_type, neighborhood, termination_criterion=100):
        solution = None
        max_runtime = 15 * 60  # max 15 minutes
        step1 = 0
        total_process_time = 0
        process_start = process_time()
        while total_process_time < max_runtime and step1 < termination_criterion:
            # here I simply copy from local_search.py start_search method just with additional runtime criterion
            initial_randomized_solution = initialization_procedure.create_solution(self._random_k)
            current_best_worthiness = Solution_Worthiness(initial_randomized_solution.get_objective_value(),
                                                          initial_randomized_solution.get_max_trip_length(),
                                                          initial_randomized_solution.get_number_of_trips(),
                                                          initial_randomized_solution.get_prize(),
                                                          Delta([]),
                                                          Delta([]))
            trace = [initial_randomized_solution.get_objective_value()]

            step2 = 0

            last_objective_value = 0
            current_objective_value = current_best_worthiness.get_objective_value()

            while step2 < termination_criterion and last_objective_value != current_objective_value:
                new_worthiness = self._step_function(neighborhood, initial_randomized_solution, step_function_type)

                last_objective_value = current_objective_value
                current_objective_value = new_worthiness.get_objective_value()

                if new_worthiness.get_objective_value() < current_best_worthiness.get_objective_value():
                    # If it is better, apply changes
                    initial_randomized_solution.change_from_delta(new_worthiness.get_delta())
                    current_best_worthiness = new_worthiness

                trace.append(current_best_worthiness.get_objective_value())

                step2 = step2 + 1

            solution = initial_randomized_solution
            step1 += 1
            process_end = process_time()
            total_process_time += process_end - process_start
            process_start = process_end

        logger.info("GRASP found solution with objective value: " + str(solution.get_objective_value()))
        logger.info("GRASP solution verfification with slow calculation: " + str(
            solution.slow_objective_values_calculation()))

        return Algorithm_Result(initial_randomized_solution, trace)
