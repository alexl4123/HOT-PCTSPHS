
import logging
import random
import numpy as np

from framework.solution import Solution, Delta, Add, Remove, Reverse, Solution_Worthiness, Swap
from framework.constants import logger_name
from construction_heuristics.initialization_procedure import Initialization_Procedure

logger = logging.getLogger(logger_name)

class Solution_Worthiness_Insertion_Heuristic(Solution_Worthiness):
    
    def __init__(self, objective_value, max_trip_duration, performed_trips, collected_prizes, delta, reverse_delta, is_unserved_customer, unserved_customer_indexes):
        super().__init__(objective_value, max_trip_duration, performed_trips, collected_prizes, delta, reverse_delta)

        self._is_unserved_customer = is_unserved_customer
        self._unserved_customer_indexes = unserved_customer_indexes

    def get_is_unserved_customer(self):
        return self._is_unserved_customer

    def get_unserved_customer_indexes(self):
        return self._unserved_customer_indexes

    @classmethod
    def clone_from_worthiness(cls, worthiness, is_unserved_customer, unserved_customer_index):
        return Solution_Worthiness_Insertion_Heuristic(worthiness.get_objective_value(), worthiness.get_max_trip_duration(), worthiness.get_performed_trips(), worthiness.get_collected_prizes(), worthiness.get_delta(), worthiness.get_reverse_delta(), is_unserved_customer, unserved_customer_index)

class Insertion_Heuristic_2(Initialization_Procedure):

    def create_solution(self, random_k = 0):

        self._random_k = random_k

        solution = Solution(self._instance)

        starting_hotel = self._instance.get_hotel_per_index(0)
        starting_trip_index = 0
        starting_trip_index_position = 0
        starting_trip_length = 0


        self.unserved_customers = self._instance._customers_list.copy()

        base_mode = False
        base_mode_reverse_delta = None

        change_base_mode = False
        change_base_index = 1
        change_base_mode_reverse_delta = None

        change_hotel_index = 1
        change_hotel_index_2 = 0
        change_hotel_reverse_delta = None

        while len(self.unserved_customers) > 0 and (not solution.is_c1_satisfied() or not solution.is_c2_satisfied() or not solution.is_c3_satisfied()):

            print(len(self.unserved_customers))
            #print(solution.to_string())
            print(solution.get_objective_value())
            #print(solution.slow_objective_values_calculation())


            cur_best = self.get_best_customer(solution)

            failed = True



            if cur_best:
                base_mode = False
                base_mode_reverse_delta = None

                change_base_mode = False
                change_base_index = 1
                change_base_mode_reverse_delta = None

                change_hotel_index = 1
                change_hotel_index_2 = 0
                change_hotel_reverse_delta = None

                failed = False

                solution.change_from_delta(cur_best.get_delta())
                if cur_best.get_is_unserved_customer():
                    for unserved_customer_index in cur_best.get_unserved_customer_indexes():
                        del self.unserved_customers[unserved_customer_index]       
            elif not base_mode:
                base_mode = True
                failed = False

                trip_index = len(solution._hotels) - 2
                second_to_last_hotel = solution._hotels[trip_index]

                add = Add(second_to_last_hotel, trip_index, len(solution._trips[trip_index]))

                delta = Delta([add])

                worthiness = solution.change_from_delta(delta)

                if not solution.is_c1_satisfied() or not solution.is_c2_satisfied():
                    solution.change_from_delta(worthiness.get_reverse_delta())
                    base_mode_reverse_delta = None
                else: 
                    base_mode_reverse_delta = worthiness.get_reverse_delta()
            elif base_mode and change_base_index < len(self._instance._hotels_list):
                change_base_mode = True
                base_mode = False
                failed = False
            
                if base_mode_reverse_delta:
                    solution.change_from_delta(base_mode_reverse_delta)
                if change_base_mode_reverse_delta:
                    solution.change_from_delta(change_base_mode_reverse_delta)

                trip_index = len(solution._hotels) - 2
                second_to_last_hotel = solution._hotels[trip_index]

                next_hotels = self._instance.get_all_nearest_hotels(second_to_last_hotel)
                next_hotel = next_hotels[change_base_index]

                add = Add(next_hotel, trip_index, len(solution._trips[trip_index]))
                delta = Delta([add])

                worthiness = solution.change_from_delta(delta)

                change_base_index = change_base_index + 1

                if not solution.is_c1_satisfied() or not solution.is_c2_satisfied():
                    solution.change_from_delta(worthiness.get_reverse_delta())
                    change_base_mode_reverse_delta = None
                else: 
                    change_base_mode_reverse_delta = worthiness.get_reverse_delta()

            elif change_hotel_index < len(solution._trips):
                failed = False

                if change_base_mode_reverse_delta:
                    solution.change_from_delta(change_base_mode_reverse_delta)
                    change_base_mode_reverse_delta = None

                if change_hotel_reverse_delta:
                    solution.change_from_delta(change_hotel_reverse_delta)

                hotel_to_change = solution._hotels[change_hotel_index]

                new_hotel = solution._hotels[change_hotel_index_2]

                add = Add(new_hotel, change_hotel_index, 0)
                rmv = Remove(hotel_to_change, change_hotel_index, 0)
                
                delta = Delta([add,rmv])

                
                # Construct reverse-delta by hand due to efficiency speeup 
                rmv_2 = Remove(new_hotel, change_hotel_index, 0)
                add_2 = Add(hotel_to_change, change_hotel_index, 0)
                reverse_delta = Delta([add_2, rmv_2])

                solution.change_from_delta(delta)

                change_hotel_index_2 = change_hotel_index_2 + 1
                if change_hotel_index_2 == len(solution._hotels):
                    change_hotel_index_2 = 0
                    change_hotel_index = change_hotel_index + 1


                if not solution.is_c1_satisfied() or not solution.is_c2_satisfied():
                    solution.change_from_delta(reverse_delta)
                    change_hotel_reverse_delta = None
                else: 
                    change_hotel_reverse_delta = reverse_delta











            if failed:
                logger.error("Insertion Heuristic could not find a solution!")
                quit()
        

        if solution.is_c1_satisfied() and solution.is_c2_satisfied() and solution.is_c3_satisfied():
            logger.info("Check all constraints verified, C1: " + str(solution.is_c1_satisfied()) + ", C2:" + str(solution.is_c2_satisfied()) + ", C3:" + str(solution.is_c3_satisfied()))
            logger.info("Insertion found solution with obj-value of " + str(solution.get_objective_value()))
            logger.info("Insertion solution verified by slow calculation:" + str(solution.slow_objective_values_calculation()))
            logger.info(solution.to_string())
            return solution
        else:
            logger.error("Insertion Heuristic could not find a solution!")
            quit()

    def get_best_customer(self, solution):
        cur_best = None
        cur_best_sum_of_trips = 0

        for trip_index in range(len(solution._trips)):
            last_node = solution._hotels[trip_index]
            last_trip_index = trip_index
            last_trip_index_position = 0

            for trip_position_index in range(len(solution._trips[trip_index])):
                next_node = solution._trips[trip_index][trip_position_index]
                next_trip_index = trip_index
                next_trip_index_position = trip_position_index

                (sum_of_trips, worthiness) = self.get_best_customer_for_edge(solution, last_trip_index, last_trip_index_position, last_node, next_trip_index, next_trip_index_position, next_node)

                if cur_best and worthiness and cur_best_sum_of_trips > sum_of_trips:
                    cur_best = worthiness
                    cur_best_sum_of_trips = sum_of_trips
                elif not cur_best and worthiness:
                    cur_best = worthiness
                    cur_best_sum_of_trips = sum_of_trips

                last_node = next_node
                last_trip_index = next_trip_index
                last_trip_index_position = next_trip_index_position

            #
            if trip_index < len(solution._hotels) - 1:
                next_node = solution._hotels[trip_index + 1]
                next_trip_index = trip_index
                next_trip_index_position = len(solution._trips[trip_index])

                (sum_of_trips, worthiness) = self.get_best_customer_for_edge(solution, last_trip_index, last_trip_index_position, last_node, next_trip_index, next_trip_index_position, next_node)

                if cur_best and worthiness and cur_best_sum_of_trips > sum_of_trips:
                    cur_best = worthiness
                    cur_best_sum_of_trips = sum_of_trips
                elif not cur_best and worthiness:
                    cur_best = worthiness
                    cur_best_sum_of_trips = sum_of_trips

        next_node = solution._hotels[len(solution._hotels) - 1]
        next_trip_index = len(solution._trips) - 1
        next_trip_index_position = 0

        (sum_of_trips, worthiness) = self.get_best_customer_for_edge(solution, last_trip_index, last_trip_index_position, last_node, next_trip_index, next_trip_index_position, next_node)
        if cur_best and worthiness and cur_best_sum_of_trips > sum_of_trips:
            cur_best = worthiness
            cur_best_sum_of_trips = sum_of_trips
        elif not cur_best and worthiness:
            cur_best = worthiness
            cur_best_sum_of_trips = sum_of_trips

        return cur_best




    def get_best_customer_for_edge(self, solution, last_trip_index, last_trip_index_position, last_node, next_trip_index, next_trip_index_position, next_node):

        cur_best = None
        cur_best_total_length = 0

        for customer_index in range(len(self.unserved_customers)):
            customer = self.unserved_customers[customer_index]

            #print("CUSTOMER:" + str(customer.get_id()) + "::" + str(next_trip_index) + "::" + str(next_trip_index_position))
            add = Add(customer, next_trip_index, next_trip_index_position)
            delta = Delta([add])

            """
            print("BEFORE-CUSTOMER-ADD:" + str(customer.get_id()))
            print(solution.to_string())
            print("Add at position:" + str(next_trip_index) + "::" + str(next_trip_index_position))
            print(solution.slow_objective_values_calculation())
            print(solution._max_trip_length)
            print(self._instance.get_C1())
            """
        
            worthiness = solution.change_from_delta(delta)

            """
            print("-----------------------------------")
            print(solution.to_string())
            print(solution.slow_objective_values_calculation())
            print(solution._max_trip_length)
            print(self._instance.get_C1())
 
            print("AFTER-CUSTOMER-ADD:")
            """

            if solution.is_c1_satisfied() and solution.is_c2_satisfied():
                if cur_best and cur_best_total_length > solution._sum_of_trips:
                    cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, True, [customer_index])
                    cur_best_total_length = solution._sum_of_trips
                elif not cur_best:
                    cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, True, [customer_index])
                    cur_best_total_length = solution._sum_of_trips

                #if solution.is_c3_satisfied():
                #    return worthiness

            solution.change_from_delta(worthiness.get_reverse_delta())

        return (cur_best_total_length, cur_best)

    def get_best_hotel_for_edge(self, solution, avg_trip_distance, last_trip_index, last_trip_index_position, last_node, next_trip_index, next_trip_index_position, next_node):

        cur_best = None
        cur_best_distance = 0

        old_trip_distance = solution._trip_lengths[next_trip_index]

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
                new_trip_length_1 = solution._trip_lengths[next_trip_index]
                new_trip_length_2 = solution._trip_lengths[next_trip_index + 1]

                #new_max = max([new_trip_length_1, new_trip_length_2])
                #diff_lengths = old_trip_distance - new_max
                #diff_lengths = new_trip_length_1 + new_trip_length_2
                diff_lengths = len(solution._trips[next_trip_index]) + len(solution._trips[next_trip_index + 1])

                if (len(solution._trips[next_trip_index]) > 0 or len(solution._trips[next_trip_index + 1]) > 0):
                    
                    if cur_best and diff_lengths > cur_best_distance:
                        cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False, [])
                        cur_best_distance = diff_lengths
                    elif not cur_best:
                        cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False, [])
                        cur_best_distance = diff_lengths
                    

            solution.change_from_delta(worthiness.get_reverse_delta())

        return (cur_best, cur_best_distance)


    def get_best_swap_customer(self, solution, avg_trip_distance, last_trip_index, last_trip_index_position, last_node, next_trip_index, next_trip_index_position, next_node):

        cur_best = None 
        cur_best_distance = 0

        old_trip_distance = solution._trip_lengths[next_trip_index]

        for hotel in self._instance._hotels_list:
            #print(str(cur_max_trip_value_index) + str(item_index))

            remove = Remove(next_node, next_trip_index, next_trip_index_position)
            add = Add(hotel, next_trip_index, next_trip_index_position)

            delta = Delta([remove,add])

            worthiness = solution.change_from_delta(delta)




            if solution.is_c1_satisfied() and solution.is_c2_satisfied():
                new_trip_length_1 = solution._trip_lengths[next_trip_index]
                new_trip_length_2 = solution._trip_lengths[next_trip_index + 1]

                #new_max = max([new_trip_length_1, new_trip_length_2])
                #diff_lengths = old_trip_distance - new_max
                #diff_lengths = new_trip_length_1 + new_trip_length_2
                diff_lengths = len(solution._trips[next_trip_index]) + len(solution._trips[next_trip_index + 1])


                #if new_trip_length_1 > 0 and new_trip_length_2 > 0:
                if (len(solution._trips[next_trip_index]) > 0 or len(solution._trips[next_trip_index + 1]) > 0):
                    if cur_best and diff_lengths > cur_best_distance:
                        cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False, [next_node])
                        cur_best_distance = diff_lengths
                    elif not cur_best:
                        cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False, [next_node])
                        cur_best_distance = diff_lengths

            solution.change_from_delta(worthiness.get_reverse_delta())

        if not cur_best: 
            # Try removing the one before
            if next_trip_index_position > 0:
                for hotel in self._instance._hotels_list:
                    #print(str(cur_max_trip_value_index) + str(item_index))
                    remove = Remove(next_node, next_trip_index, next_trip_index_position)
                    next_node_2 = solution._trips[next_trip_index][next_trip_index_position - 1]
                    remove2 = Remove(next_node_2, next_trip_index, next_trip_index_position - 1)
                    add = Add(hotel, next_trip_index, next_trip_index_position)

                    delta = Delta([remove, remove2, add])

                    worthiness = solution.change_from_delta(delta)


                    if solution.is_c1_satisfied() and solution.is_c2_satisfied() and (len(solution._trips[next_trip_index]) > 0 or len(solution._trips[next_trip_index + 1]) > 0):
                        new_trip_length_1 = solution._trip_lengths[next_trip_index]
                        new_trip_length_2 = solution._trip_lengths[next_trip_index + 1]

                        #new_max = max([new_trip_length_1, new_trip_length_2])
                        #diff_lengths = old_trip_distance - new_max


                        #diff_lengths = new_trip_length_1 + new_trip_length_2
                        diff_lengths = len(solution._trips[next_trip_index]) + len(solution._trips[next_trip_index + 1])
                    
                        if cur_best and diff_lengths > cur_best_distance:
                            cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False, [next_node, next_node_2])
                            cur_best_distance = diff_lengths
                        elif not cur_best:
                            cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False, [next_node, next_node_2])
                            cur_best_distance = diff_lengths
                        
                    solution.change_from_delta(worthiness.get_reverse_delta())

            # Try removing one after
            if not cur_best and next_trip_index_position < (len(solution._trips[next_trip_index]) - 1):
                for hotel in self._instance._hotels_list:
                        #print(str(cur_max_trip_value_index) + str(item_index))
                        remove = Remove(next_node, next_trip_index, next_trip_index_position)
                        next_node_2 = solution._trips[next_trip_index][next_trip_index_position + 1]
                        remove2 = Remove(next_node_2, next_trip_index, next_trip_index_position)
                        add = Add(hotel, next_trip_index, next_trip_index_position)

                        delta = Delta([remove, remove2, add])

                        worthiness = solution.change_from_delta(delta)
    

                        if solution.is_c1_satisfied() and solution.is_c2_satisfied() and (len(solution._trips[next_trip_index]) > 0 or len(solution._trips[next_trip_index + 1]) > 0):

                            new_trip_length_1 = solution._trip_lengths[next_trip_index]
                            new_trip_length_2 = solution._trip_lengths[next_trip_index + 1]

                            #new_max = max([new_trip_length_1, new_trip_length_2])
                            #diff_lengths = old_trip_distance - new_max
                            #diff_lengths = new_trip_length_1 + new_trip_length_2
                            diff_lengths = len(solution._trips[next_trip_index]) + len(solution._trips[next_trip_index + 1])

                            if cur_best and diff_lengths > cur_best_distance:

                                cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False, [next_node, next_node_2])
                                cur_best_distance = diff_lengths
                            elif not cur_best:
                                cur_best = Solution_Worthiness_Insertion_Heuristic.clone_from_worthiness(worthiness, False, [next_node, next_node_2])
                                cur_best_distance = diff_lengths

                            
                        solution.change_from_delta(worthiness.get_reverse_delta())

        return (cur_best, cur_best_distance)



    """ 
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

    """           
