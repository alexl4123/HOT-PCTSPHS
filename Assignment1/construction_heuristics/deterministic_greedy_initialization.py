
import logging
from solution import Solution, Delta
from initialization_procedure import Initialization_Procedure
from constants import logger_name

logger = logging.getLogger(logger_name)

class Deterministic_Greedy_Initialization(Initialization_Procedure):
    """
    Deprecated and not working, use Backtracking_Search instead
    """

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
            nearest_hotel = self._instance.get_nearest_hotel(current_location)
            d_n_h = inst.get_distance(current_location, nearest_hotel)
            if d_n_h == 0:
                nearest_hotel = self._instance.get_nearest_hotel(current_location, 1)
                d_n_h = inst.get_distance(current_location, nearest_hotel)


            nearest_unserved_customer = solution.get_nearest_unserved_customer(current_location)
            d_n_c = inst.get_distance(current_location, nearest_unserved_customer) 
            if d_n_c == 0:
                nearest_unserved_customer = solution.get_nearest_unserved_customer(current_location, 1)
                d_n_c = inst.get_distance(current_location, nearest_unserved_customer) 


            if ((current_trip_value + d_n_h) <= inst.get_C1()) and ((current_trip_value + d_n_c) <= inst.get_C1()):
                print("V1")
                print(d_n_c)
                safe_state = (solution.clone(), current_location, current_trip_position, current_trip_index_position, current_trip_value)

                solution.change_from_delta(Delta([],[(nearest_unserved_customer, current_trip_position, current_trip_index_position)]))
                current_trip_index_position = current_trip_index_position + 1
                current_trip_value = current_trip_value + d_n_c
                current_location = nearest_unserved_customer

            elif ((current_trip_value + d_n_h) <=  inst.get_C1()) and d_n_h > 0 and ((current_trip_value + d_n_c) > inst.get_C1()):
                print("2")
                solution.change_from_delta(Delta([],[(nearest_hotel, current_trip_position, current_trip_position_index)]))
                current_trip_value = current_trip_value + d_n_h
                current_trip_index_position = 0
                current_trip_position = current_trip_position + 1
                current_trip_value = 0
                current_location = nearest_hotel
                safe_state = (solution.clone(), current_location, current_trip_position, current_trip_index_position, current_trip_value)
            elif ((current_trip_value + d_n_h) > inst.get_C1()) and ((current_trip_value + d_n_c) <= inst.get_C1()):
                print("3")
                solution.change_from_delta(Delta([],[(nearest_unserved_customer, current_trip_position, current_trip_index_position)]))
                current_trip_index_position = current_trip_index_position + 1
                current_trip_value = current_trip_value + d_n_c
                current_location = nearest_unserved_customer
            elif ((current_trip_value + d_n_h) > inst.get_C1()) and ((current_trip_value + d_n_c) > inst.get_C1()):
                print("4")
                # Load safe state and go to last hotel


                solution = safe_state[0]
                current_location = safe_state[1]
                current_trip_position = safe_state[2]
                current_trip_index_position = safe_state[3]
                current_trip_value = safe_state[4]



                nearest_hotel = self._instance.get_nearest_hotel(current_location)
                d_n_h = inst.get_distance(current_location, nearest_hotel)

                if (current_trip_value + d_n_h) > inst.get_C1():
                    logger.error(solution.to_string())
                    logger.error("Deterministic greedy initialization procedure could not find a solution")
                    quit()


                solution.change_from_delta(Delta([],[(nearest_hotel, current_trip_position, current_trip_index_position)]))
                current_trip_value = current_trip_value + d_n_h
                current_trip_index_position = 0
                current_trip_position = current_trip_position + 1
                current_trip_value = 0
                current_location = nearest_hotel
                safe_state = (solution.clone(), current_location, current_trip_position, current_trip_index_position, current_trip_value)
            else:
                logger.error("Should be unreachable position")
                quit()

            if solution.is_c3_satisfied() and not solution.is_c1_satisfied():
                print("V5")
                solution = safe_state[0]
                current_location = safe_state[1]
                current_trip_position = safe_state[2]
                current_trip_index_position = safe_state[3]
                current_trip_value = safe_state[4]
                print("Current-location:" + str(current_location.get_id()))
                print(solution.to_string())

                nearest_hotel = self._instance.get_nearest_hotel(current_location)
                d_n_h = inst.get_distance(current_location, nearest_hotel)
                if d_n_h == 0:
                    nearest_hotel = self._instance.get_nearest_hotel(current_location, 1)
                    d_n_h = inst.get_distance(current_location, nearest_hotel)

                if (current_trip_value + d_n_h) > inst.get_C1():
                    logger.error(solution.to_string())
                    logger.error("Deterministic greedy initialization procedure could not find a solution")
                    quit()


                solution.change_from_delta(Delta([],[(nearest_hotel, current_trip_position, current_trip_index_position)]))
                current_trip_value = current_trip_value + d_n_h
                current_trip_index_position = 0
                current_trip_position = current_trip_position + 1
                current_trip_value = 0
                current_location = nearest_hotel
                safe_state = (solution.clone(), current_location, current_trip_position, current_trip_index_position, current_trip_value)


        logger.info("Deterministic greedy found solution with obj-value of " + str(solution.get_objective_value()))
        logger.info(solution.to_string())
        
        return solution



        















