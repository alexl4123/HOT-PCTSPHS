import time
import logging

from construction_heuristics.combination_of_heuristics import Combination_Of_Heuristics

from framework.solution import Delta, Solution_Worthiness
from framework.result import Result
from framework.constants import logger_name

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


class Grasp(Algorithm):

    def __init__(self, instance, random_k):
        super().__init__(instance)

        self._random_k = random_k

    def start_search(self, init_solution, step_function_type, neighborhoods, max_runtime, termination_criterion=10, starting_time = None, output=True):
        solution = None
        iteration = 0

        trace = []

        if not starting_time:
            starting_time = time.time()


        instance = self._instance

        while iteration < termination_criterion:


            randomized_procedure = Combination_Of_Heuristics(instance)
            retry = 0
            while retry < 10:
                result = randomized_procedure.create_solution(self._random_k, False)
                if result.get_best_solution():
                    break

            if not result.get_best_solution():
                continue


            neighborhoods = [Interchange_Customers(instance),Insert_Customer(instance), Trip_2_Opt(instance), Swap_Served_Unserved_Customer(instance), Remove_Customer(instance), Add_Customer(instance), Remove_Hotel(instance), Add_Hotel(instance),Exchange_Hotel(instance), Move_Hotel(instance)]

            vnd = Vnd(instance, 0)
            result = vnd.start_search(result.get_best_solution(), Step_Function_Type.FIRST, neighborhoods,  max_runtime, output = False)

            if not solution or result.get_best_solution().get_objective_value() < solution.get_objective_value():
                solution = result.get_best_solution()

            trace.append(result.get_best_solution().get_objective_value())

            iteration += 1

            current_time = time.time()
            delta = current_time - starting_time
            if delta > max_runtime:
                break


        duration = time.time() - starting_time
        if duration > max_runtime:
            logger.info("Runtime limit reached, actual runtime: " + max_runtime)

            duration = max_runtime

        checked_values = solution.slow_objective_values_calculation()
        if output:
            logger.info("GRASP found solution with objective value: " + str(solution.get_objective_value()))
            logger.info("GRASP solution verfification with slow calculation: " + str(checked_values[0]))
            logger.info("GRASP Trace:" + str(trace))

        if checked_values[0] != solution.get_objective_value():
            logger.error("Likely error in delta-evaluation!")
            quit()

        return Result(solution, trace, duration)


