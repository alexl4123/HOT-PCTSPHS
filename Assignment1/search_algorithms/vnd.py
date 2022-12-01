from time import process_time

import logging

from framework.solution import Delta, Solution_Worthiness
from framework.constants import logger_name
from search_algorithms.algorithm import Algorithm, Algorithm_Result
from search_algorithms.local_search import Local_Search, Step_Function_Type

from neighborhoods.neighborhood import Neighborhood
from neighborhoods.trip_2_opt import Trip_2_Opt

logger = logging.getLogger(logger_name)


class Vnd(Algorithm):

    def __init__(self, instance, random_k):
        super().__init__(instance)

        self._random_k = random_k

    def start_vnd(self, initialization_procedure, neighborhood, termination_criterion=100):
        solution = initialization_procedure.create_solution(self._random_k)

        # TODO: currently we have only one neighborhood structure. For more variety implement other ones
        neighborhood_number = 1
        max_neighborhood_number = 3
        max_runtime = 15 * 60  # max 15 minutes
        total_process_time = 0
        process_start = process_time()
        while neighborhood_number <= max_neighborhood_number and total_process_time < max_runtime:
            if neighborhood_number == 1:
                step_function_type = Step_Function_Type.FIRST
                algoritm_result = Local_Search.start_search(initialization_procedure, step_function_type, neighborhood,
                                                            termination_criterion)
                new_solution = algoritm_result.get_best_solution()
                if new_solution.get_objective_value() < solution.get_objective_value():
                    solution = new_solution
            elif neighborhood_number == 2:
                step_function_type = Step_Function_Type.BEST
                algoritm_result = Local_Search.start_search(initialization_procedure, step_function_type, neighborhood,
                                                            termination_criterion)
                new_solution = algoritm_result.get_best_solution()
                if new_solution.get_objective_value() < solution.get_objective_value():
                    solution = new_solution
            elif neighborhood_number == 3:
                step_function_type = Step_Function_Type.RANDOM
                algoritm_result = Local_Search.start_search(initialization_procedure, step_function_type, neighborhood,
                                                            termination_criterion)
                new_solution = algoritm_result.get_best_solution()
                if new_solution.get_objective_value() < solution.get_objective_value():
                    solution = new_solution

            neighborhood_number += 1
            process_end = process_time()
            total_process_time += process_end - process_start
            process_start = process_end

        return solution
