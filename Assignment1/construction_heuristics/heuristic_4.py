
import logging
import random
import numpy as np

from framework.solution import Solution, Delta, Add, Remove, Reverse, Solution_Worthiness, Swap
from framework.constants import logger_name
from construction_heuristics.initialization_procedure import Initialization_Procedure

logger = logging.getLogger(logger_name)

class Solution_Worthiness_Insertion_Heuristic(Solution_Worthiness):
    
    def __init__(self, objective_value, max_trip_duration, performed_trips, collected_prizes, delta, reverse_delta, is_unserved_customer, unserved_customer_index):
        super().__init__(objective_value, max_trip_duration, performed_trips, collected_prizes, delta, reverse_delta)

        self._is_unserved_customer = is_unserved_customer
        self._unserved_customer_index = unserved_customer_index

    def get_is_unserved_customer(self):
        return self._is_unserved_customer

    def get_unserved_customer_index(self):
        return self._unserved_customer_index

    @classmethod
    def clone_from_worthiness(cls, worthiness, is_unserved_customer, unserved_customer_index):
        return Solution_Worthiness_Insertion_Heuristic(worthiness.get_objective_value(), worthiness.get_max_trip_duration(), worthiness.get_performed_trips(), worthiness.get_collected_prizes(), worthiness.get_delta(), worthiness.get_reverse_delta(), is_unserved_customer, unserved_customer_index)

class Insertion_Heuristic(Initialization_Procedure):

    def create_solution(self, random_k = 0):

        self._random_k = random_k

        solution = Solution(self._instance)

        starting_hotel = self._instance.get_hotel_per_index(0)
        starting_trip_index = 0
        starting_trip_index_position = 0
        starting_trip_length = 0


        self.unserved_customers = self._instance._customers_list.copy()

        while len(self.unserved_customers) > 0 and (not solution.is_c1_satisfied() or not solution.is_c2_satisfied() or not solution.is_c3_satisfied()):

            cur_best = None

            """
            print(solution.to_string())
            id_list = []
            for customer in self.unserved_customers:
                id_list.append(customer.get_id())
            print(id_list)
            """
                


            for trip_index in range(len(solution._trips)):
                last_node = solution._hotels[trip_index]
                last_trip_index = trip_index
                last_trip_index_position = 0

                for trip_position_index in range(len(solution._trips[trip_index])):
                    next_node = solution._trips[trip_index][trip_position_index]
                    next_trip_index = trip_index
                    next_trip_index_position = trip_position_index

                    worthiness = self.get_best_insertion_for_edge(solution, last_trip_index, last_trip_index_position, last_node, next_trip_index, next_trip_index_position, next_node)

                    if cur_best and worthiness and cur_best.get_objective_value() > worthiness.get_objective_value():
                        cur_best = worthiness
                    elif not cur_best and worthiness:
                        cur_best = worthiness

                    last_node = next_node
                    last_trip_index = next_trip_index
                    last_trip_index_position = next_trip_index_position

                #
                if trip_index < len(solution._hotels) - 1:
                    next_node = solution._hotels[trip_index + 1]
                    next_trip_index = trip_index
                    next_trip_index_position = len(solution._trips[trip_index])

                    worthiness = self.get_best_insertion_for_edge(solution, last_trip_index, last_trip_index_position, last_node, next_trip_index, next_trip_index_position, next_node)

                    if cur_best and worthiness and cur_best.get_objective_value() > worthiness.get_objective_value():
                        cur_best = worthiness
                    elif not cur_best and worthiness:
                        cur_best = worthiness



            next_node = solution._hotels[len(solution._hotels) - 1]
            next_trip_index = len(solution._trips) - 1
            next_trip_index_position = 0

            worthiness = self.get_best_insertion_for_edge(solution, last_trip_index, last_trip_index_position, last_node, next_trip_index, next_trip_index_position, next_node)

            if cur_best and worthiness and cur_best.get_objective_value() > worthiness.get_objective_value():
                cur_best = worthiness
            elif not cur_best and worthiness:
                cur_best = worthiness

            if cur_best:
                solution.change_from_delta(cur_best.get_delta())
                if cur_best.get_is_unserved_customer():
                    del self.unserved_customers[cur_best.get_unserved_customer_index()]
            else:
                new_worthiness = self.try_swapping(solution)

                if not new_worthiness:
                    logger.error("Insertion Heuristic could not find a solution!")
                    quit()
            

        if solution.is_c1_satisfied() and solution.is_c2_satisfied() and solution.is_c3_satisfied():
            logger.debug("Check all constraints verified, C1: " + str(solution.is_c1_satisfied()) + ", C2:" + str(solution.is_c2_satisfied()) + ", C3:" + str(solution.is_c3_satisfied()))
            logger.info("Insertion found solution with obj-value of " + str(solution.get_objective_value()))
            logger.debug("Insertion solution verified by slow calculation:" + str(solution.slow_objective_values_calculation()))
            logger.info(solution.to_string())
            return solution
        else:
            logger.error("Insertion Heuristic could not find a solution!")
            quit()


                    

    def get_best_insertion_for_edge(self, solution, last_trip_index, last_trip_index_position, last_node, next_trip_index, next_trip_index_position, next_node):


        cur_best = None

        for customer_index in range(len(self.unserved_customers)):
            customer = self.unserved_customers[customer_index]

            #print("CUSTOMER:" + str(customer.get_id()) + "::" + str(next_trip_index) + "::" + str(next_trip_index_position))
            add = Add(customer, next_trip_index, next_trip_index_position)
            delta = Delta([add])

            """
            if customer.get_id() == 6:
                print("BEFORE-CUSTOMER-ADD:" + str(customer.get_id()))
                print(solution.to_string())
                print("Add at position:" + str(next_trip_index) + "::" + str(next_trip_index_position))
                print(solution.slow_objective_values_calculation())
                print(solution._max_trip_length)
            """
            
            worthiness = solution.change_from_delta(delta)

            """
            if customer.get_id() == 6:
                print(solution.to_string())
                print(solution.slow_objective_values_calculation())
                print(solution._max_trip_length)
                print("AFTER-CUSTOMER-ADD:")
            """

            if solution.is_c1_satisfied() and solution.is_c2_satisfied():
                if cur_best and cur_best.get_objective_value() > worthiness.get_objective_value():
                    cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, True, customer_index)
                elif not cur_best:
                    cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, True, customer_index)

            solution.change_from_delta(worthiness.get_reverse_delta())


        #if cur_best == None:
        for hotel_index in range(len(self._instance._hotels_list)):
            hotel = self._instance._hotels_list[hotel_index]

            #if hotel.get_id() == last_node.get_id() and hotel.get_id() == next_node.get_id():
            #    continue

            add = Add(hotel, next_trip_index, next_trip_index_position)
            delta = Delta([add])

            """
            print("BEFORE-HOTEL-ADD:" + str(hotel.get_id()))
            print(solution.slow_objective_values_calculation())
            print(solution._max_trip_length)
            """
            worthiness = solution.change_from_delta(delta)

            """
            print(solution.slow_objective_values_calculation())
            print(solution._max_trip_length)
            print("AFTER-HOTEL-ADD")
            """

            if solution.is_c1_satisfied() and solution.is_c2_satisfied():
                if cur_best and cur_best.get_objective_value() > worthiness.get_objective_value():
                    cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False, customer_index)
                elif not cur_best:
                    cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False, customer_index)
                

            solution.change_from_delta(worthiness.get_reverse_delta())

        return cur_best


    def try_swapping(self, solution):
        # TODO
        cur_max_trip_value = solution._max_trip_length
        cur_max_trip_value_index = -1

        for trip_length_index in range(len(solution._trip_lengths)):
            cur_trip_length = solution._trip_lengths[trip_length_index]

            if cur_max_trip_value == cur_trip_length:
                cur_max_trip_value_index = trip_length_index

        if cur_max_trip_value_index == -1:
            logger.error("FATAL-IN-INSERTION-HEURISTIC")
            quit()
        
        for item_index in range(len(solution._trips[cur_max_trip_value_index])):

            old_item = solution._trips[cur_max_trip_value_index][item_index]

            for hotel in self._instance._hotels_list:
                #print(str(cur_max_trip_value_index) + str(item_index))
                remove = Remove(old_item, cur_max_trip_value_index,item_index)
                add = Add(hotel, cur_max_trip_value_index,item_index)

                delta = Delta([remove,add])

                worthiness = solution.change_from_delta(delta)

                if solution.is_c1_satisfied() and solution.is_c2_satisfied():
                    return worthiness

                solution.change_from_delta(worthiness.get_reverse_delta())


        return None



                
