
import logging
from solution import Solution, Delta
from initialization_procedure import Initialization_Procedure
from constants import logger_name

logger = logging.getLogger(logger_name)

class Deterministic_Greedy_Initialization(Initialization_Procedure):

    def create_solution(self):

        inst = self._instance

        solution = Solution(self._instance)

        current_location = self._instance.get_hotel_per_index(0)
        current_trip_position = 0
        current_trip_index_position = 0

        current_trip_value = 0

        safe_state = (solution.clone(), current_location, current_trip_position, current_trip_index_position, current_trip_value)
        safe_state_2 = None

        while not solution.is_c3_satisfied():
            
            nearest_unserved_customer = solution.get_nearest_unserved_customer(current_location)
            d_n_c = inst.get_distance(current_location, nearest_unserved_customer) 
            if d_n_c == 0:
                nearest_unserved_customer = solution.get_nearest_unserved_customer(current_location, 1)
                d_n_c = inst.get_distance(current_location, nearest_unserved_customer) 


            solution.change_from_delta(Delta([],[(nearest_unserved_customer, current_trip_position, current_trip_index_position)]))
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

        i_2 = 0

        print(solution.to_string())


        while index <= upper_index and i_2 < 6:
            print("Outer-" + str(index))
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

                index = index - 1
                print(index)

                while index >= lower_index:
                    nearest_hotel = inst.get_nearest_hotel(greedy_trip[index])
                    d_n_h = inst.get_distance(greedy_trip[index], nearest_hotel)

                    print(trip_size)
                    print(d_n_h)

                    if trip_size + d_n_h <= inst.get_C1():
                        # Good Case :-)

                        print("GOOD:" + str(index) + "::" + str(trip_index) + "::" + str(trip_index_position))
                        solution.change_from_delta(Delta([],[(nearest_hotel, trip_index, trip_index_position)]))

                        trip_index = trip_index + 1
                        trip_index_position = 0
                        lower_index = index + 1
                        index = index + 1
                        trip_size = 0

                        break
                    else:
                        print("BAD:" + str(index))
                        index = index - 1
                        trip_index_position = trip_index_position - 1
                        trip_size = trip_size - inst.get_distance(greedy_trip[index], greedy_trip[index + 1])

                if index < lower_index:
                    logger.error("deterministic procedure could not find valid path, quitting")
                    quit()

            else:
                index = index + 1
                trip_index_position = trip_index_position + 1
                trip_size = trip_size_new

            i_2 = i_2 + 1




        print(solution.to_string())

        logger.info("Deterministic greedy found solution with obj-value of " + str(solution.get_objective_value()))
        logger.info(solution.to_string())
        
        return solution



        















