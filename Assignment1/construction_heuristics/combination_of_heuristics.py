import logging
import time

from framework.constants import logger_name

from construction_heuristics.initialization_procedure import Initialization_Procedure
from construction_heuristics.greedy_nearest_neighbor_initialization import Greedy_Nearest_Neighbor_Initialization
from construction_heuristics.backtracking_search import Backtracking_Search
from construction_heuristics.insertion_heuristic_sum_of_trips import Insertion_Heuristic_Sum_Of_Trips
from construction_heuristics.insertion_diverse_hotels import Insertion_Diverse_Hotels

from framework.result import Result

logger = logging.getLogger(logger_name)


class Combination_Of_Heuristics(Initialization_Procedure):

    def __init__(self, instance, delta = True):
        super().__init__(instance)
        self._delta = delta


    def create_solution(self, random_k=0, show_output = True, benchmarking = False, max_runtime = 90):

        delta = self._delta

        procedure_1 = Greedy_Nearest_Neighbor_Initialization(instance = self._instance, delta = delta)
        procedure_2 = Backtracking_Search(self._instance, delta)
        procedure_3 = Insertion_Heuristic_Sum_Of_Trips(self._instance, delta)
        procedure_4 = Insertion_Diverse_Hotels(self._instance, delta)

        if random_k == 0 and not benchmarking and self._delta:

            best_result = None

            starting_time = time.time()

            result_1 = procedure_1.create_solution(show_output, max_runtime)
            result_2 = procedure_2.create_solution(show_output, max_runtime)
            result_3 = procedure_3.create_solution(show_output, max_runtime)
            result_4 = procedure_4.create_solution(show_output, max_runtime)

            if result_1.get_best_solution():
                best_result = result_1
            if result_2.get_best_solution() and best_result.get_best_solution().get_objective_value() > result_2.get_best_solution().get_objective_value():
                best_result = result_2
            if result_3.get_best_solution() and best_result.get_best_solution().get_objective_value() > result_3.get_best_solution().get_objective_value():
                best_result = result_3
            if result_4.get_best_solution() and best_result.get_best_solution().get_objective_value() > result_4.get_best_solution().get_objective_value():
                best_result = result_4

            duration = time.time() - starting_time

            return Result(best_result.get_best_solution(), [best_result.get_best_solution().get_objective_value()], duration)
        elif random_k > 0 and not benchmarking and self._delta:
            return procedure_2.create_solution(random_k, show_output, max_runtime)
        elif benchmarking:
            return procedure_2.create_solution(random_k, show_output, max_runtime)
        else:
            logger.error("Illegal configuration for combination of heuristics!")
            quit()


