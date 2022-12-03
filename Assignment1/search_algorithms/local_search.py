import logging
import random
import time

from enum import Enum

from framework.solution import Delta, Solution_Worthiness
from framework.constants import logger_name
from search_algorithms.algorithm import Algorithm
from framework.result import Result

logger = logging.getLogger(logger_name)


class Local_Search(Algorithm):

    def __init__(self, instance, random_k):
        super().__init__(instance)

        self._random_k = random_k

    def start_search(self, init_solution, step_function_type, neighborhoods, max_runtime, termination_criterion=1000, starting_time = None, output=True):

        neighborhood = neighborhoods[0]

        #solution = initialization_procedure.create_solution(self._random_k)
        solution = init_solution
        current_best_worthiness = Solution_Worthiness(solution.get_objective_value(), solution.get_max_trip_length(),
                                                      solution.get_number_of_trips(), solution.get_prize(), Delta([]),
                                                      Delta([]))

        trace = [solution.get_objective_value()]

        step = 0

        last_objective_value = 0
        current_objective_value = current_best_worthiness.get_objective_value()

        if not starting_time:
            starting_time = time.time()

        while step < termination_criterion and (last_objective_value != current_objective_value or step_function_type == Step_Function_Type.RANDOM):
            new_worthiness = self._step_function(neighborhood, solution, step_function_type)

            last_objective_value = current_objective_value
            current_objective_value = new_worthiness.get_objective_value()

            if new_worthiness.get_objective_value() < current_best_worthiness.get_objective_value():
                # If it is better, apply changes
                solution.change_from_delta(new_worthiness.get_delta())
                current_best_worthiness = new_worthiness

            trace.append(current_best_worthiness.get_objective_value())

            step = step + 1

            current_time = time.time()
            delta = current_time - starting_time

            if delta > max_runtime:
                break

        duration = time.time() - starting_time
        if duration > max_runtime:
            logger.info("Runtime limit reached, actual runtime: " + max_runtime)

            duration = max_runtime


        checked_values = solution.slow_objective_values_calculation()

        if output:
            logger.info("Local search found solution with objective value: " + str(solution.get_objective_value()))
            logger.info("Local search solution verfification with slow calculation: " + str(checked_values))
            logger.info("Trace:" + str(trace))

        if checked_values[0] != solution.get_objective_value():
            logger.error("Likely error in delta-evaluation!")
            quit()
        if checked_values[0] != trace[len(trace) - 1]:
            logger.error("Likely error in neighborhood-evaluation!")
            quit()


        return Result(solution, trace, duration)

    def _step_function(self, neighborhood, solution, step_function_type):

        neighborhood.set_solution(solution)
        neighborhood.reset_indexes()

        if step_function_type == Step_Function_Type.RANDOM:
            # Inefficient, but does the job
            upper = neighborhood.get_number_possible_solutions() - 1
            sol = solution
            if upper > 0:
                k = random.randint(0, upper)
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
