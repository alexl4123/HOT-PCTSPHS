from neighborhoods.neighborhood import Neighborhood

from framework.solution import Delta, Solution_Worthiness, Reverse, Remove, Add


class Insert_Customer(Neighborhood):

    def __init__(self, instance):
        self._instance = instance
        self._solution = None

        self._trip_index = 0
        self._trip_position_index_0 = 0
        self._trip_position_index_1 = 0

        self._current_solution_index = 0

    def set_solution(self, solution):
        self._solution = solution

    def reset_indexes(self):

        self._trip_index = 0
        self._trip_position_index_0 = 0
        self._trip_position_index_1 = 0

        self._current_solution_index = 0
        self._number_of_solutions = None

    def get_number_possible_solutions(self):
        """
            Should be in O(sum(n*(n-1)) in the number of customers currently in the solution (n is the amount of customers per trip, i.e. the sum is over the trips)
        """

        if not self._number_of_solutions:
            self._trip_position_index_0 = 0
            self._trip_position_index_1 = 0


            self._number_of_solutions = 0

            number_of_possible_interchanges = 0
            for trip in self._solution._trips:
                number_of_possible_interchanges += len(trip) * (len(trip) - 1)

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
        obj = None
        while obj == None:
            if self._trip_index >= len(self._solution._trips):
                print("FATAL ERROR IN ADD_CUSTOMER NEIGHBORHOOD")
                quit()

            cur_trip =  self._solution._trips[self._trip_index]

            if self._trip_position_index_0 == self._trip_position_index_1 or self._trip_position_index_0 + 1 == self._trip_position_index_1:
                self._trip_position_index_1 += 1
            elif len(cur_trip) > 0 and self._trip_position_index_1 <= len(cur_trip) and self._trip_position_index_0 < len(cur_trip):
                obj = cur_trip[self._trip_position_index_0]
            elif len(cur_trip) > 0 and self._trip_position_index_1 > len(cur_trip) and self._trip_position_index_0 < len(cur_trip):
                self._trip_position_index_0 += 1
                self._trip_position_index_1 = 0
            elif len(cur_trip) > 0 and self._trip_position_index_1 > len(cur_trip) and self._trip_position_index_0 >= len(cur_trip) - 1:
                self._trip_index += 1
                self._trip_position_index_0 = 0
                self._trip_position_index_1 = 0
            else:
                self._trip_index += 1
                self._trip_position_index_0 = 0
                self._trip_position_index_1 = 0

        # Compute necessary operations
        rmv = Remove(obj, self._trip_index, self._trip_position_index_0)

        insert_pos = -1
        if self._trip_position_index_0 < self._trip_position_index_1:
            insert_pos = self._trip_position_index_1 - 1
        else:
            insert_pos = self._trip_position_index_1 

        add = Add(obj, self._trip_index, insert_pos)

        delta = Delta([rmv, add])

        # Calculate new solution worthiness
        left_0 = self._solution.left_neighbor_customer(self._trip_index, self._trip_position_index_0)
        right_0 = self._solution.right_neighbor_customer(self._trip_index, self._trip_position_index_0)

        cur_trip = self._solution._trips[self._trip_index]

        if self._trip_position_index_1 > 0 and self._trip_position_index_1 < len(cur_trip):
            left_1 = cur_trip[self._trip_position_index_1 - 1]
            right_1 = cur_trip[self._trip_position_index_1]
        elif self._trip_position_index_1 == 0 and self._trip_position_index_1 < len(cur_trip):
            left_1 = self._solution._hotels[self._trip_index]
            right_1 = cur_trip[self._trip_position_index_1]
        elif self._trip_position_index_1 > 0 and self._trip_position_index_1 >= len(cur_trip):
            left_1 = cur_trip[self._trip_position_index_1 - 1]
            right_1 = self._solution._hotels[self._trip_index + 1]

        old_length = self._instance.get_distance(left_0, obj) + self._instance.get_distance(obj, right_0) + self._instance.get_distance(left_1, right_1)
        new_length = self._instance.get_distance(left_1, obj)  + self._instance.get_distance(obj, right_1) + self._instance.get_distance(left_0, right_0)

        """
        print("<<<" + str(self._trip_position_index_0) + "::" + str(self._trip_position_index_1) + ">>>")
        print("<<<" + str(left_0.get_id()) + "::" + str(obj.get_id()) + "::" + str(right_0.get_id())  + ">>>")
        print("<<<" + str(left_1.get_id()) + "::" + str(obj.get_id()) + "::" + str(right_1.get_id())  + ">>>")
        print("<<<" + str(self._solution.to_string()) + ">>>")
        print("<<<" + str(self._solution.slow_objective_values_calculation()) + ">>>")
        print("<<<" + str(self._instance.get_distance(left_0, obj)) + ";;" + str(self._instance.get_distance(obj, right_0)) + ";;" + str(self._instance.get_distance(left_1, right_1)) + ">>>")
        print("<<<" + str(self._instance.get_distance(left_1, obj)) + ";;" + str(self._instance.get_distance(obj, right_1))  + ";;" + str(self._instance.get_distance(left_0, right_0))+ ">>>")
        """

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
