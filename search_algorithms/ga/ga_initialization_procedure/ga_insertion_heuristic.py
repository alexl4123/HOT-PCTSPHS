import logging
import random
import numpy as np
import time

from framework.result import Result
from framework.solution import Solution, Delta, Add, Remove, Reverse, Solution_Worthiness, Swap
from framework.constants import logger_name

from search_algorithms.ga.ga_solution import GA_Solution
from search_algorithms.ga.ga_initialization_procedure.initialization_procedure import GA_Initialization_Procedure

logger = logging.getLogger(logger_name)

class Insertion_Criterion:

    def evaluate(self, solution):
        return False

class Shortest_Path_Criterion(Insertion_Criterion):

    def __init__(self):
        self.best_length = 0
        self.current_best = None

    def evaluate(self, solution):
        evaluate = False

        if not self.current_best:
            self.current_best = solution
            self.best_length = solution._sum_of_trips
            evaluate = True
        elif solution._sum_of_trips < self.best_length:
            self.current_best = solution
            self.best_length = solution._sum_of_trips
            evaluate = True

        return evaluate

class Best_Objective_Value_Criterion(Insertion_Criterion):

    def __init__(self):
        self.best_value = 0
        self.current_best = None

    def evaluate(self, solution):
        evaluate = False

        if not self.current_best:
            self.current_best = solution
            self.best_value = solution._objective_value
            evaluate = True
        elif solution._objective_value < self.best_value:
            self.current_best = solution
            self.best_value = solution._objective_value
            evaluate = True

        return evaluate

class Farthest_Distance_Criterion(Insertion_Criterion):

    def __init__(self):
        self.best_length = 0
        self.current_best = None

    def evaluate(self, solution):
        evaluate = False

        if not self.current_best:
            self.current_best = solution
            self.best_length = solution._sum_of_trips
            evaluate = True
        elif solution._sum_of_trips > self.best_length:
            self.current_best = solution
            self.best_length = solution._sum_of_trips
            evaluate = True

        return evaluate



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

class GA_Insertion_Heuristic(GA_Initialization_Procedure):
    """
    Is an insertion heuristic
    """

    def __init__(self, instance, alpha=1, beta=-0.5, gamma=-0.5, delta=0.5, fitness_function = None, insertion_criterion = Shortest_Path_Criterion):
        super().__init__(instance, alpha = alpha, beta = beta, gamma = gamma, delta = delta, fitness_function = fitness_function)

        self._insertion_criterion = insertion_criterion

    def create_solution(self, random_k=0, show_output=True, max_runtime = 90):
        """
        max_runtime not supported
        """

        self._random_k = random_k

        solution = GA_Solution(self._instance, fitness_function = self._fitness_function)

        starting_hotel = self._instance.get_hotel_per_index(0)
        starting_trip_index = 0
        starting_trip_index_position = 0
        starting_trip_length = 0

        self.unserved_customers = self._instance._customers_list.copy()

        starting_time = time.time()

        while len(self.unserved_customers) > 0 and not solution.is_c3_satisfied():
            cur_best = None
            cur_best_sum_of_trips = 0


            first_index = random.randint(-1,len(solution._trips[0]) - 1)
            second_index = first_index + 1

            if first_index == -1:
                first_node = solution._hotels[0]
            else:
                first_node = solution._trips[0][first_index]

            if second_index == len(solution._trips[0]):
                second_node = solution._hotels[1] # As we know, that in this step only two hotels are present
            else:
                first_node = solution._trips[0][second_index]
                

            (sum_of_trips, worthiness) = self.get_best_customer_for_edge(solution,
                                                                        first_index, first_node,
                                                                        second_index, second_node)

            solution.change_from_delta(worthiness.get_delta())
            if worthiness.get_is_unserved_customer():
                for unserved_customer_index in worthiness.get_unserved_customer_indexes():
                    del self.unserved_customers[unserved_customer_index]
            else:
                logger.error("CRITICAL -> CUR BEST IS SERVED CUSTOMER!")
                quit()

        if show_output:
            logger.debug("Check all constraints verified, C1: " + str(solution.is_c1_satisfied()) + ", C2:" + str(
                solution.is_c2_satisfied()) + ", C3:" + str(solution.is_c3_satisfied()))
            logger.info("Insertion found solution with obj-value of " + str(solution.get_objective_value()))
            logger.debug(
                "Insertion solution verified by slow calculation:" + str(solution.slow_objective_values_calculation()))
            logger.info(solution.to_string())

        duration = time.time() - starting_time

        solution.compute_fitness_value()
        return Result(solution, [solution.get_objective_value()], duration)



    def get_best_customer_for_edge(self, solution, last_trip_index_position, last_node,
                                   next_trip_index_position, next_node):

        cur_best = None

        insertion_criterion = self._insertion_criterion()

        for customer_index in range(len(self.unserved_customers)):
            customer = self.unserved_customers[customer_index]

            add = Add(customer, 0, next_trip_index_position)
            delta = Delta([add])

            worthiness = solution.change_from_delta(delta)

            if cur_best and insertion_criterion.evaluate(solution):
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

    def to_string(self):
        return "insertion-heuristic-sum-of-trips"



