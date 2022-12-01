from time import process_time

import logging

from framework.solution import Delta, Solution_Worthiness
from framework.constants import logger_name
from search_algorithms.algorithm import Algorithm, Algorithm_Result
from search_algorithms.local_search import Local_Search, Step_Function_Type

from neighborhoods.neighborhood import Neighborhood
from neighborhoods.trip_2_opt import Trip_2_Opt

from vnd import Vnd

logger = logging.getLogger(logger_name)


class Gvns(Algorithm):

    def __init__(self, instance, random_k):
        super().__init__(instance)

        self._random_k = random_k

    def start_gvns(self, initialization_procedure, neighborhood, termination_criterion=100):
        # FIXME: Here I am not sure about the implementation at all
        solution = initialization_procedure.create_solution(self._random_k)
        solution = Vnd.start_vnd(initialization_procedure, neighborhood, termination_criterion)
        k = 1
        kmax = 4
        max_runtime = 15 * 60  # max 15 minutes
        total_process_time = 0
        process_start = process_time()
        while k <= kmax and total_process_time < max_runtime:
            new_solution = Vnd.start_vnd(initialization_procedure, neighborhood, termination_criterion)
            if new_solution.get_objective_value() < solution.get_objective_value():
                solution = new_solution

            k += 1
            process_end = process_time()
            total_process_time += process_end - process_start
            process_start = process_end

        return solution
