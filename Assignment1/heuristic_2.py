
import logging
from solution import Solution, Delta, Add, Remove, Reverse
from initialization_procedure import Initialization_Procedure
from constants import logger_name

logger = logging.getLogger(logger_name)

class Deterministic_Greedy_Initialization(Initialization_Procedure):

    def create_solution(self, random_k = 0):

        inst = self._instance

        solution = Solution(self._instance)

        current_location = self._instance.get_hotel_per_index(0)
        current_trip_position = 0
        current_trip_index_position = 0

        current_trip_value = 0

        while not solution.is_c3_satisfied():
           
            nearest_unserved_customer = solution.get_nearest_unserved_customer(current_location, random_k)
            d_n_c = inst.get_distance(current_location, nearest_unserved_customer) 

            solution.change_from_delta(Delta([Add(nearest_unserved_customer, current_trip_position, current_trip_index_position)]))
            current_trip_index_position = current_trip_index_position + 1
            current_trip_value = current_trip_value + d_n_c
            current_location = nearest_unserved_customer
    
        """
        print(solution.slow_objective_values_calculation())

        print(solution.is_c1_satisfied())
        print(solution.is_c2_satisfied())
        print(solution.is_c3_satisfied())
        """

        greedy_trip = solution._trips[0].copy()

        trip_size = 0

        upper_index = len(greedy_trip)
        lower_index = 0
        index = 0

        trip_index = 0
        trip_index_position = 0


        while index <= upper_index:
            if index == lower_index:
                if index < upper_index:
                    trip_size_new = trip_size + inst.get_distance(solution._hotels[trip_index], greedy_trip[index])
                else:
                    trip_size_new = trip_size + inst.get_distance(solution._hotels[trip_index], solution._hotels[trip_index + 1])

            elif index == upper_index:
                trip_size_new = trip_size + inst.get_distance(greedy_trip[index-1], solution._hotels[trip_index + 1])
            else:
                trip_size_new = trip_size + inst.get_distance(greedy_trip[index - 1], greedy_trip[index])

            if trip_size_new > inst.get_C1():

                #print("Error-Case:" + str(greedy_trip[index].get_id()) + ":INDEX:" + str(index) + ":TRIP-SIZE:" + str(trip_size) + ":TRIP-SIZE-NEW:" + str(trip_size_new) + ":SOLUTION_MAX_VALUE:" + str(solution._max_trip_length))

                index = index - 1

                while index >= lower_index:
                    nearest_hotel = inst.get_nearest_hotel(greedy_trip[index])
                    d_n_h = inst.get_distance(greedy_trip[index], nearest_hotel)

                    #print("Error-REPAIR-Case:" + str(greedy_trip[index].get_id()) + ":INDEX:" + str(index) + ":TRIP-SIZE:" + str(trip_size) + ":TRIP-SIZE-NEW:" + str(trip_size + d_n_h) + ":TRIP_INDEX:" + str(trip_index) + ":TRIP_INDEX_POSITION:" + str(trip_index_position) + ":SOLUTION_MAX_VALUE:" + str(solution._max_trip_length))
                    if trip_size + d_n_h <= inst.get_C1():

                        solution.change_from_delta(Delta([Add(nearest_hotel, trip_index, trip_index_position)]))

                        trip_index = trip_index + 1
                        trip_index_position = 0
                        lower_index = index + 1
                        index = index + 1
                        """
                        print(trip_size)
                        print(d_n_h)
                        print(inst.get_C1())
                        """
                        trip_size = 0

                        break
                    else:
                        index = index - 1
                        trip_index_position = trip_index_position - 1
                        trip_size = trip_size - inst.get_distance(greedy_trip[index], greedy_trip[index + 1])

                if index < lower_index:
                    logger.error("deterministic procedure could not find valid path, quitting")
                    quit()

            else:
                """
                if index < upper_index:
                    print("Valid-Case:" + str(greedy_trip[index].get_id()) + ":INDEX:" + str(index) + ":TRIP-SIZE:" + str(trip_size) + ":TRIP-SIZE-NEW:" + str(trip_size_new) + ":SOLUTION_MAX_VALUE:" + str(solution._max_trip_length))
                """

                index = index + 1
                trip_index_position = trip_index_position + 1
                trip_size = trip_size_new

        print(solution.is_c1_satisfied())
        print(solution.is_c2_satisfied())
        print(solution.is_c3_satisfied())
        print(solution._max_trip_length)

        print("SLOW-CALC:")
        print(solution.slow_objective_values_calculation())

        logger.info("Deterministic greedy found solution with obj-value of " + str(solution.get_objective_value()))
        logger.info(solution.to_string())
        
        return solution



        















