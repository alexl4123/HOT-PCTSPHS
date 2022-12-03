import logging
import random

from enum import Enum

from framework.solution import Delta, Solution_Worthiness
from framework.constants import logger_name
from search_algorithms.algorithm import Algorithm, Algorithm_Result

logger = logging.getLogger(logger_name)


class Local_Search(Algorithm):

    def __init__(self, instance, random_k):
        super().__init__(instance)

        self._random_k = random_k

    def start_search(self, initialization_procedure, step_function_type, neighborhood, termination_criterion=100):

        solution = initialization_procedure.create_solution(self._random_k)
        current_best_worthiness = Solution_Worthiness(solution.get_objective_value(), solution.get_max_trip_length(),
                                                      solution.get_number_of_trips(), solution.get_prize(), Delta([]),
                                                      Delta([]))

        trace = [solution.get_objective_value()]

        step = 0

        last_objective_value = 0
        current_objective_value = current_best_worthiness.get_objective_value()

        while step < termination_criterion and last_objective_value != current_objective_value:
            new_worthiness = self._step_function(neighborhood, solution, step_function_type)

            last_objective_value = current_objective_value
            current_objective_value = new_worthiness.get_objective_value()

            if new_worthiness.get_objective_value() < current_best_worthiness.get_objective_value():
                # If it is better, apply changes
                solution.change_from_delta(new_worthiness.get_delta())
                current_best_worthiness = new_worthiness

            trace.append(current_best_worthiness.get_objective_value())

            step = step + 1

        logger.info("Local search found solution with objective value: " + str(solution.get_objective_value()))
        logger.info("Local search solution verfification with slow calculation: " + str(
            solution.slow_objective_values_calculation()))

        return Algorithm_Result(solution, trace)

    def _step_function(self, neighborhood, solution, step_function_type):

        neighborhood.set_solution(solution)
        neighborhood.reset_indexes()

        if step_function_type == Step_Function_Type.RANDOM:
            # Inefficient, but does the job
            k = random.randint(0, neighborhood.get_number_possible_solutions() - 1)
            for i in range(0, k):
                sol = neighborhood.next_solution()

            if k == 0 and neighborhood.get_number_possible_solutions() > 0:
                sol = neighborhood.next_solution()

            return sol
        else:
            current_solution = solution
            current_worthiness = Solution_Worthiness(solution.get_objective_value(), solution.get_max_trip_length(),
                                                     solution.get_number_of_trips(), solution.get_prize(), Delta([]),
                                                     Delta([]))

            k = 0
            number = neighborhood.get_number_possible_solutions()
            while k < number:
                new_worthiness = neighborhood.next_solution()

                if new_worthiness.get_max_trip_duration() <= self._instance.get_C1() and new_worthiness.get_performed_trips() <= self._instance.get_C2() and new_worthiness.get_collected_prizes() >= self._instance.get_C3():
                    if new_worthiness.get_objective_value() < current_worthiness.get_objective_value() and step_function_type == Step_Function_Type.FIRST:
                        return new_worthiness
                    elif new_worthiness.get_objective_value() < current_worthiness.get_objective_value():
                        current_worthiness = new_worthiness

                k = k + 1

            return current_worthiness


class Step_Function_Type(Enum):
    FIRST = 1
    BEST = 2
    RANDOM = 3
