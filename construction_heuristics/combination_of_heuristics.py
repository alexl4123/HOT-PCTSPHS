import logging
import time

import numpy as np

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

        show_output = True

        delta = self._delta

        procedures = []
        procedures.append(Greedy_Nearest_Neighbor_Initialization(instance = self._instance, alpha = 1, beta = 0, gamma = 0, delta = 0, delta_evaluation = delta))

        # Pretty good for rc101_3 (but not good enough...)
        procedures.append(Greedy_Nearest_Neighbor_Initialization(instance = self._instance, alpha = 2, beta = -0.25, gamma = 0.05, delta = 0.5, delta_evaluation = delta))

        #procedures.append(Backtracking_Search(self._instance, alpha = 0.1, beta = 1, gamma = 0, delta = 0.5, delta_evaluation = delta))
        # GENERALLY GOOD
        procedures.append(Backtracking_Search(self._instance, alpha = 1, beta = -0.5, gamma = -0.5, delta = 0.5, delta_evaluation = delta))

        # Not that bad for e.g. gil262
        procedures.append(Backtracking_Search(self._instance, alpha = 1, beta = 0, gamma = 0, delta = 0, delta_evaluation = delta))

        # FOR gil262 
        procedures.append(Backtracking_Search(self._instance, alpha = 1, beta = 0, gamma = 0, delta = 0.5, delta_evaluation = delta))
        # FOR test
        procedures.append(Backtracking_Search(self._instance, alpha = 1, beta = 0.2, gamma = 0.2, delta = 0.2, delta_evaluation = delta))
        # FOR berlin51_2
        procedures.append(Backtracking_Search(self._instance, alpha = 0.5, beta = -1, gamma = -1, delta = 1, delta_evaluation = delta))

        # FOR gil250 (not that bad for rc101_3)
        procedures.append(Backtracking_Search(self._instance, alpha = 1, beta = -0.4, gamma = -0.1, delta = 1, delta_evaluation = delta))


        procedures.append(Insertion_Heuristic_Sum_Of_Trips(self._instance, delta_evaluation = delta, alpha = 1, beta = 0, gamma = 0, delta = 0))
        procedures.append(Insertion_Heuristic_Sum_Of_Trips(self._instance, delta_evaluation = delta, alpha = 1, beta = -0.5, gamma = -0.5, delta = 0.5))
        procedures.append(Insertion_Diverse_Hotels(self._instance, delta_evaluation = delta,alpha = 1, beta = 0, gamma = 0, delta = 0))
        procedures.append(Insertion_Diverse_Hotels(self._instance, delta_evaluation = delta,alpha = 1, beta = -0.5, gamma = -0.5, delta = 0.5))

        if random_k == 0 and not benchmarking and self._delta:

            best_result = None
            best_parameters = {}

            starting_time = time.time()

            for procedure in procedures:
                result = procedure.create_solution(random_k = 0, output = show_output, max_runtime = max_runtime)

                if (not best_result and result.get_best_solution()) or (result.get_best_solution() and best_result.get_best_solution().get_objective_value() > result.get_best_solution().get_objective_value()):
                    best_result = result

                    best_parameters = {}
                    best_parameters['procedure-type'] = procedure.to_string()
                    best_parameters['alpha'] = procedure._alpha
                    best_parameters['beta'] = procedure._beta 
                    best_parameters['gamma'] = procedure._gamma
                    best_parameters['delta'] = procedure._delta_param

                    print(best_parameters)

            """
            result_1 = procedure_1.create_solution(show_output, max_runtime)
            result_2 = procedure_2.create_solution(show_output, max_runtime)
            result_3 = procedure_3.create_solution(show_output, max_runtime)
            result_4 = procedure_4.create_solution(show_output, max_runtime)

            if result_1.get_best_solution():
                best_result = result_1
            if (not best_result and result_3.get_best_solution()) or (result_3.get_best_solution() and best_result.get_best_solution().get_objective_value() > result_3.get_best_solution().get_objective_value()):
                best_result = result_3
            if (not best_result and result_4.get_best_solution()) or (result_4.get_best_solution() and best_result.get_best_solution().get_objective_value() > result_4.get_best_solution().get_objective_value()):
                best_result = result_4
            """

            duration = time.time() - starting_time

            return Result(best_result.get_best_solution(), [best_result.get_best_solution().get_objective_value()], duration, additional_params = best_parameters)
        elif random_k > 0 and not benchmarking and self._delta:

            mean_alpha = 0.5
            sd_alpha = 1

            mean_beta = -0.5
            sd_beta = 1

            mean_gamma = -0.5
            sd_gamma = 1

            mean_delta = 0.5
            sd_delta = 1


            alpha = np.random.normal(mean_alpha, sd_alpha)
            beta = np.random.normal(mean_beta, sd_beta)
            gamma = np.random.normal(mean_gamma, sd_gamma)
            delta = np.random.normal(mean_delta, sd_delta)

            params = {}
            params['alpha'] = alpha
            params['beta'] = beta
            params['gamma'] = gamma
            params['delta'] = delta

            procedure_2 = Backtracking_Search(self._instance, delta_evaluation = self._delta, alpha = alpha, beta = beta, gamma = gamma, delta = delta)
            #max_runtime = 2
            result = procedure_2.create_solution(random_k, show_output, max_runtime)

            return Result(result.get_best_solution(), result.get_trace(), result.get_time(), additional_params = params)

        elif benchmarking:
            procedure_2 = Backtracking_Search(self._instance, delta_evaluation = self._delta, alpha = 1, beta = -0.5, gamma = -0.5, delta = 0.5)
            return procedure_2.create_solution(random_k, show_output, max_runtime)

        else:
            logger.error("Illegal configuration for combination of heuristics!")
            quit()


