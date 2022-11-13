
import logging
from solution import Solution, Delta, Add, Remove, Reverse
from initialization_procedure import Initialization_Procedure
from constants import logger_name

logger = logging.getLogger(logger_name)

class Backtracking_Search(Initialization_Procedure):

    def create_solution(self, random_k = 0):

        solution = Solution(self._instance)

        starting_hotel = self._instance.get_hotel_per_index(0)
        starting_trip_index = 0
        starting_trip_index_position = 0
        starting_trip_length = 0

        result = self.backtracking(solution, starting_hotel, starting_trip_index, starting_trip_index_position, starting_trip_length)


        if result:
            print(solution.is_c1_satisfied())
            print(solution.is_c2_satisfied())
            print(solution.is_c3_satisfied())
            print(solution._max_trip_length)

            print("SLOW-CALC:")
            print(solution.slow_objective_values_calculation())

            logger.info("Backtracking found solution with obj-value of " + str(solution.get_objective_value()))
            logger.info(solution.to_string())
            
            return solution
        else:
            logger.error("Backtracking could not find a solution!")
            quit()


    def backtracking(self, solution, obj, trip_index, trip_index_position, current_trip_length):

        if not solution.is_c3_satisfied() and solution.is_c2_satisfied():
            return self.backtracking_helper(solution,obj, trip_index, trip_index_position, current_trip_length)
        elif solution.is_c2_satisfied():
            if solution.is_c1_satisfied() and solution.is_c2_satisfied() and solution.is_c3_satisfied():
                return True
            else:
                return self.backtracking_helper(solution,obj, trip_index, trip_index_position, current_trip_length)

        return False

    def backtracking_helper(self, solution,obj, trip_index, trip_index_position, current_trip_length):

        inst = self._instance

        # LIMIT-BREADTH
        index = 0
        if trip_index_position == 0:
            index_upper_limit = 4
        elif trip_index_position == 1:
            index_upper_limit = 2
        else:
            index_upper_limit = 1
        # LIMIT-BREADTH


        for nearest in self._instance.get_all_nearest_customers(obj):

            new_dist = inst.get_distance(obj, nearest)
            if not solution.is_customer_served(nearest) and new_dist > 0:
                # LIMIT-BREADTH
                if index >= index_upper_limit:
                    break
                index = index + 1
                # LIMIT-BREADTH

                new_trip_length = new_dist + current_trip_length

                if new_trip_length <= inst.get_C1():
                    delta = Delta([Add(nearest, trip_index, trip_index_position)])

                    worthiness = solution.change_from_delta(delta)

                    # For Customer
                    result = self.backtracking(solution, nearest, trip_index, trip_index_position + 1, new_trip_length)

                    if result:
                        return result
                    else:
                        solution.change_from_delta(worthiness.get_reverse_delta())

                else:
                    # Note that this is a massive speedup, but comes at the cost, that the ''nearest'' can only be attributed to ''distance'' and not to function value
                    break

       
        # LIMIT-BREADTH
        index = 0
        index_upper_limit = 1
        # LIMIT-BREADTH

        if current_trip_length > 0:
            for nearest in self._instance.get_all_nearest_hotels(obj):
                new_dist = inst.get_distance(obj, nearest)
                if new_dist > 0:
                    # LIMIT-BREADTH
                    if index >= index_upper_limit:
                        break
                    index = index + 1
                    # LIMIT-BREADTH
                    new_trip_length = new_dist + current_trip_length

                    if new_trip_length <= inst.get_C1():
                        delta = Delta([Add(nearest, trip_index, trip_index_position)])

                        worthiness = solution.change_from_delta(delta)

                        # For Hotel
                        result = self.backtracking(solution, nearest, trip_index + 1, 0, 0)

                        if result:
                            return result
                        else:
                            solution.change_from_delta(worthiness.get_reverse_delta())
                    else:
                        # Note that this is a massive speedup, but comes at the cost, that the ''nearest'' can only be attributed to ''distance'' and not to function value
                        break

        return False





        















