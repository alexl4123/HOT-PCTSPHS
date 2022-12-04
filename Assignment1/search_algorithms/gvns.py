import time
import logging
import random

from framework.solution import Delta, Solution_Worthiness
from framework.constants import logger_name
from framework.result import Result

from search_algorithms.algorithm import Algorithm
from search_algorithms.local_search import Local_Search, Step_Function_Type
from search_algorithms.vnd import Vnd

from neighborhoods.neighborhood import Neighborhood
from neighborhoods.trip_2_opt import Trip_2_Opt
from neighborhoods.remove_customer import Remove_Customer
from neighborhoods.add_customer import Add_Customer
from neighborhoods.swap_served_unserved_customer import Swap_Served_Unserved_Customer
from neighborhoods.interchange_customers import Interchange_Customers
from neighborhoods.insert_customer import Insert_Customer
from neighborhoods.remove_hotel import Remove_Hotel
from neighborhoods.add_hotel import Add_Hotel
from neighborhoods.exchange_hotel import Exchange_Hotel
from neighborhoods.move_hotel import Move_Hotel


logger = logging.getLogger(logger_name)


class Gvns(Algorithm):

    def __init__(self, instance, random_k):
        super().__init__(instance)

        self._random_k = random_k

    def start_search(self, init_solution, step_function_type, neighborhoods, max_runtime, termination_criterion=3, starting_time = None, output = True):


        instance = self._instance
        iteration = 0

        neighborhoods = [Interchange_Customers(instance),Insert_Customer(instance),Trip_2_Opt(instance), Swap_Served_Unserved_Customer(instance), Remove_Customer(instance), Add_Customer(instance), Remove_Hotel(instance), Add_Hotel(instance),Exchange_Hotel(instance), Move_Hotel(instance)]

        solution = init_solution

        trace = []
        trace.append(solution.get_objective_value())

        vnd = Vnd(instance, 0)
        result = vnd.start_search(solution, Step_Function_Type.FIRST, neighborhoods,  max_runtime, output = False, allow_invalid_solutions = True)

        cur_best_result = Result(result.get_best_solution().clone(), result.get_trace(), result.get_time(), result.get_additional_params())
        trace.append(result.get_best_solution().get_objective_value())

        if not starting_time:
            starting_time = time.time()


        while iteration < termination_criterion:


            solution = self.shaking(solution, iteration)



            neighborhoods = [Interchange_Customers(instance),Insert_Customer(instance), Trip_2_Opt(instance), Swap_Served_Unserved_Customer(instance), Remove_Customer(instance), Add_Customer(instance), Remove_Hotel(instance), Add_Hotel(instance),Exchange_Hotel(instance), Move_Hotel(instance)]

            vnd = Vnd(instance, 0)
            result = vnd.start_search(solution, Step_Function_Type.BEST, neighborhoods,  max_runtime, output = False, allow_invalid_solutions = True)


            if not cur_best_result or result.get_best_solution().get_objective_value() < cur_best_result.get_best_solution().get_objective_value():
                cur_best_result = Result(result.get_best_solution().clone(), result.get_trace(), result.get_time(), result.get_additional_params())

                iteration = 0

            else:
                iteration += 1
               
            print(iteration)
            trace.append(result.get_best_solution().get_objective_value()) 


            current_time = time.time()
            delta = current_time - starting_time
            if delta > max_runtime:
                break

        duration = time.time() - starting_time
        if duration > max_runtime:
            logger.info("Runtime limit reached, actual runtime: " + str(max_runtime))

            duration = max_runtime

        solution = cur_best_result.get_best_solution()

        checked_values = solution.slow_objective_values_calculation()
        if output:
            logger.info("GVNS found solution with objective value: " + str(solution.get_objective_value()))
            logger.info("GVNS solution verfification with slow calculation: " + str(checked_values[0]))
            logger.info("GVNS Trace:" + str(trace))

        if checked_values[0] != solution.get_objective_value():
            logger.error("GVNS Likely error in delta-evaluation!")
            quit()

        return Result(solution, trace, duration)

    def shaking(self, solution, iteration):

        possible_positions = 0
        for trip in solution._trips:
            possible_positions += len(trip) + 1

        for index in range(iteration + 1):
            position = random.randint(0, possible_positions - 1)
            hotel = self._instance.get_list_of_hotels()[random.randint(0,len(self._instance.get_list_of_hotels()) - 1)]
            trip_index = 0
            trip_position_index = 0

            for trip in solution._trips:
                positions_trip = len(trip) + 1

                if position < positions_trip:
                    # Current trip
                    trip_position_index = position
                    break

                elif position >= positions_trip:
                    trip_index += 1
                    position = position - positions_trip

            old_trip = solution._trips[trip_index]

            new_left = old_trip[:trip_position_index]
            new_right = old_trip[trip_position_index:]


            solution._trips[trip_index] = new_left
            solution._trips.insert(trip_index + 1, new_right)

            solution._hotels.insert(trip_index + 1, hotel)
            solution._trips_size += 1
            possible_positions += 1

        solution.update_values_from_slow_calculation()


        return solution























        
