from neighborhoods.neighborhood import Neighborhood

from framework.solution import Delta, Solution_Worthiness, Reverse, Remove, Add


class Interchange_Customers(Neighborhood):

    def __init__(self, instance):
        self._instance = instance
        self._solution = None

        self._trip_index = 0
        self._trip_position_index_0 = 0
        self._trip_position_index_1 = 1

        self._current_solution_index = 0

    def set_solution(self, solution):
        self._solution = solution

    def reset_indexes(self):

        self._trip_index = 0
        self._trip_position_index_0 = 0
        self._trip_position_index_1 = 1

        self._current_solution_index = 0
        self._number_of_solutions = None

    def get_number_possible_solutions(self):
        """
            Should be in O(sum((n*(n-1))/2) in the number of customers currently in the solution (n is the amount of customers per trip, i.e. the sum is over the trips)
        """

        if not self._number_of_solutions:

            self._unserved_customers = []
            self._number_of_solutions = 0

            number_of_possible_interchanges = 0
            for trip in self._solution._trips:
                number_of_possible_interchanges += int((len(trip) * (len(trip) - 1)) / 2)

            self._number_of_solutions = number_of_possible_interchanges
            print(self._number_of_solutions)

        return self._number_of_solutions


    def next_solution(self):

        if not self._number_of_solutions:
            val = self.get_number_possible_solutions()
            if val == 0:
                print("NO ADD_CUSTOMER-Solutions possible")
                return Solution_Worthiness(self._solution.get_objective_value(), self._solution.get_max_trip_length(),
                                           self._solution.get_number_of_trips(), self._solution.get_prize(), Delta([]),
                                           Delta([]))

        if self._current_solution_index >= self._number_of_solutions:
            print("NO MORE SOLUTIONS AVAILABLE")
            return Solution_Worthiness(self._solution.get_objective_value(), self._solution.get_max_trip_length(),
                                       self._solution.get_number_of_trips(), self._solution.get_prize(), Delta([]),
                                       Delta([]))


        # Get next customer
        first_obj = None
        second_obj = None
        while first_obj == None or second_obj == None:
            if self._trip_index >= len(self._solution._trips):
                print("FATAL ERROR IN ADD_CUSTOMER NEIGHBORHOOD")
                quit()

            cur_trip =  self._solution._trips[self._trip_index]

            if len(cur_trip) > 0 and self._trip_position_index_1 < len(cur_trip):
                first_obj = cur_trip[self._trip_position_index_0]
                second_obj = cur_trip[self._trip_position_index_1]
            elif len(cur_trip) > 0 and self._trip_position_index_1 >= len(cur_trip) and self._trip_position_index_0 < len(cur_trip) - 1:
                self._trip_position_index_0 += 1
                self._trip_position_index_1 = self._trip_position_index_0 + 1
            elif len(cur_trip) > 0 and self._trip_position_index_1 >= len(cur_trip) and self._trip_position_index_0 >= len(cur_trip) - 1:
                self._trip_index += 1
                self._trip_position_index_0 = 0
                self._trip_position_index_1 = self._trip_position_index_0 + 1
            else:
                self._trip_index += 1
                self._trip_position_index_0 = 0
                self._trip_position_index_1 = self._trip_position_index_0 + 1


        # Compute necessary operations
        rmv_0 = Remove(first_obj, self._trip_index, self._trip_position_index_0)
        rmv_1 = Remove(second_obj, self._trip_index, self._trip_position_index_1)
        add_0 = Add(second_obj, self._trip_index, self._trip_position_index_0)
        add_1 = Add(first_obj, self._trip_index, self._trip_position_index_1)

        delta = Delta([rmv_1, rmv_0, add_0, add_1])

        # Calculate new solution worthiness
        left_0 = self._solution.left_neighbor_customer(self._trip_index, self._trip_position_index_0)
        right_0 = self._solution.right_neighbor_customer(self._trip_index, self._trip_position_index_0)

        left_1 = self._solution.left_neighbor_customer(self._trip_index, self._trip_position_index_1)
        right_1 = self._solution.right_neighbor_customer(self._trip_index, self._trip_position_index_1)

        if (self._trip_position_index_1 - self._trip_position_index_0) > 1:
            old_length_0 = self._instance.get_distance(left_0, first_obj) + self._instance.get_distance(first_obj, right_0)
            old_length_1 = self._instance.get_distance(left_1, second_obj) + self._instance.get_distance(second_obj, right_1)
            new_length_0 = self._instance.get_distance(left_0, second_obj)  + self._instance.get_distance(second_obj, right_0)
            new_length_1 = self._instance.get_distance(left_1, first_obj)  + self._instance.get_distance(first_obj, right_1)
        else: 
            old_length_0 = self._instance.get_distance(left_0, first_obj) + self._instance.get_distance(first_obj, right_0)
            old_length_1 = self._instance.get_distance(left_1, second_obj) + self._instance.get_distance(second_obj, right_1)
            new_length_0 = self._instance.get_distance(left_0, second_obj)  + self._instance.get_distance(second_obj, first_obj)
            new_length_1 = self._instance.get_distance(second_obj, first_obj)  + self._instance.get_distance(first_obj, right_1)

        old_length = old_length_0 + old_length_1
        new_length = new_length_0 + new_length_1

        # Recalculate max_trip_length
        cur_trip_length = self._solution._trip_lengths[self._trip_index]

        new_cur_trip_length = cur_trip_length - old_length + new_length

        new_max_trip_length = self._solution._max_trip_length

        if cur_trip_length >= new_max_trip_length and new_cur_trip_length < new_max_trip_length:
            correct_calculation = False

            if not correct_calculation:
                # If this is executed (can be set above), then the new_max_trip_length is just approximated (leads to a speedup, but only works for valid solution)
                pass
            else:
                # Correct recalculation of max trip length, but at reduced speed
                # Get new max trip length
                new_max_trip_length = new_cur_trip_length
                for trip_length_index in range(self._solution._trip_lengths):
                    if trip_length_index == self._trip_index:
                        continue
                    elif self._solution._trip_lengths[trip_length_index] > new_max_trip_length:
                        new_max_trip_length = self._solution._trip_lengths[trip_length_index]
        elif new_cur_trip_length > new_max_trip_length:
            new_max_trip_length = new_cur_trip_length

        # Recalculate new prize
        new_prize = self._solution._prize

        new_objective_value = self._solution.get_objective_value() - old_length + new_length


        worthiness = Solution_Worthiness(new_objective_value, new_max_trip_length, self._solution.get_number_of_trips(), new_prize, delta, Delta([]))

        self._current_solution_index += 1
        self._trip_position_index_1 += 1

        return worthiness
