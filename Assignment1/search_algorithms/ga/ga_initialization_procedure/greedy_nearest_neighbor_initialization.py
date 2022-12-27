import logging
import time

from framework.result import Result
from framework.solution import Solution, Delta, Add, Remove, Reverse
from search_algorithms.ga.ga_initialization_procedure.initialization_procedure import GA_Initialization_Procedure
from search_algorithms.ga.ga_solution import GA_Solution
from framework.constants import logger_name

logger = logging.getLogger(logger_name)


class Greedy_Nearest_Neighbor_Initialization(GA_Initialization_Procedure):
    """
    Greedy nearest neighbor initialization procedure.
    1.) Constructs a greedy-nearest-neighbor-tour while ignoring all constraints
    2.) Tries to repair solution, by inserting hotels
    """

    def __init__(self, instance, alpha=1, beta=-0.5, gamma=-0.5, delta=0.5, fitness_function = None):
        super().__init__(instance, alpha = alpha, beta = beta, gamma = gamma, delta = delta, fitness_function = fitness_function)

    def create_solution(self, random_k=0, show_output=True, max_runtime = 90):
        """
        max_runtime not supported
        """

        inst = self._instance

        solution = GA_Solution(self._instance, fitness_function = self._fitness_function)

        current_location = self._instance.get_hotel_per_index(0)
        current_trip_position = 0
        current_trip_index_position = 0

        current_trip_value = 0

        starting_time = time.time()

        # Until C3 is satisfied -> insert greedily nearest neighbors
        while not solution.is_c3_satisfied():
            nearest_unserved_customer = self.get_nearest_unserved_customer(current_location, random_k, solution)
            d_n_c = inst.get_distance(current_location, nearest_unserved_customer)

            solution.change_from_delta(
                Delta([Add(nearest_unserved_customer, current_trip_position, current_trip_index_position)]))
            current_trip_index_position = current_trip_index_position + 1
            current_trip_value = current_trip_value + d_n_c
            current_location = nearest_unserved_customer

        greedy_trip = solution._trips[0].copy()

        trip_size = 0

        upper_index = len(greedy_trip)
        lower_index = 0
        index = 0

        trip_index = 0
        trip_index_position = 0

        # Try to repair the solution by inserting hotels
        # Thereby going through all customers, and if there is a customer, where it is then not fulfilled, we try to insert a hotel -> if this fails we abort
        while index <= upper_index:
            if index == lower_index:
                if index < upper_index:
                    trip_size_new = trip_size + inst.get_distance(solution._hotels[trip_index], greedy_trip[index])
                else:
                    trip_size_new = trip_size + inst.get_distance(solution._hotels[trip_index],
                                                                  solution._hotels[trip_index + 1])

            elif index == upper_index:
                trip_size_new = trip_size + inst.get_distance(greedy_trip[index - 1], solution._hotels[trip_index + 1])
            else:
                trip_size_new = trip_size + inst.get_distance(greedy_trip[index - 1], greedy_trip[index])

            if trip_size_new > inst.get_C1():

                index = index - 1

                while index >= lower_index:
                    nearest_hotel = self.get_nearest_hotel(greedy_trip[index])
                    d_n_h = inst.get_distance(greedy_trip[index], nearest_hotel)

                    if trip_size + d_n_h <= inst.get_C1():

                        solution.change_from_delta(Delta([Add(nearest_hotel, trip_index, trip_index_position)]))

                        trip_index = trip_index + 1
                        trip_index_position = 0
                        lower_index = index + 1
                        index = index + 1

                        trip_size = 0

                        break
                    else:
                        index = index - 1
                        trip_index_position = trip_index_position - 1
                        trip_size = trip_size - inst.get_distance(greedy_trip[index], greedy_trip[index + 1])

                if index < lower_index:
                    break

            else:

                index = index + 1
                trip_index_position = trip_index_position + 1
                trip_size = trip_size_new

        if show_output:
            logger.info("Check all constraints verified, C1: " + str(solution.is_c1_satisfied()) + ", C2:" + str(
                solution.is_c2_satisfied()) + ", C3:" + str(solution.is_c3_satisfied()))
            logger.info("Greedy-CH found solution with fitness-value of " + str(solution.get_fitness_value()))
            #logger.info(
            #    "Greedy-CH solution verified by slow calculation:" + str(solution.slow_objective_values_calculation()))
            #logger.debug(solution.to_string())

        duration = time.time() - starting_time

        solution.compute_fitness_value()
        return Result(solution, [solution.get_fitness_value()], duration)



    def to_string(self):
        return "pure-greedy"
