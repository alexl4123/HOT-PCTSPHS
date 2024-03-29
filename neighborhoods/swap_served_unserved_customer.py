from neighborhoods.neighborhood import Neighborhood

from framework.solution import Delta, Solution_Worthiness, Reverse, Remove, Add


class Swap_Served_Unserved_Customer(Neighborhood):

    def __init__(self, instance):
        self._instance = instance
        self._solution = None

        self._trip_index = 0
        self._trip_position_index = 0
        self._unserved_customer_index = 0
        self._unserved_customers = []

        self._current_solution_index = 0

    def set_solution(self, solution):
        self._solution = solution

    def reset_indexes(self):

        self._trip_index = 0
        self._trip_position_index = 0
        self._unserved_customer_index = 0
        self._unserved_customers = []

        self._current_solution_index = 0
        self._number_of_solutions = None

    def get_number_possible_solutions(self):
        """
            Should be in O(|unserved| * (n+1)) in the number of customers currently in the solution
        """

        if not self._number_of_solutions:

            self._unserved_customers = []
            self._number_of_solutions = 0

            for customer in self._instance.get_list_of_customers():
                if not self._solution.is_customer_served(customer):
                    self._unserved_customers.append(customer)

            number_of_possible_insertion_positions = 0
            for trip in self._solution._trips:
                number_of_possible_insertion_positions += len(trip)

            self._number_of_solutions = len(self._unserved_customers) * number_of_possible_insertion_positions

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
        add_obj = None
        rmv_obj = None
        while add_obj == None or rmv_obj == None:
            if self._trip_index >= len(self._solution._trips):
                print("FATAL ERROR IN ADD_CUSTOMER NEIGHBORHOOD")
                quit()

            cur_trip =  self._solution._trips[self._trip_index]

            if len(cur_trip) > 0 and self._trip_position_index < len(cur_trip) and self._unserved_customer_index < len(self._unserved_customers):
                add_obj = self._unserved_customers[self._unserved_customer_index]
                rmv_obj = cur_trip[self._trip_position_index]

            elif len(cur_trip) > 0 and self._trip_position_index < len(cur_trip) and self._unserved_customer_index >= len(self._unserved_customers):
                self._trip_position_index += 1
                self._unserved_customer_index = 0
            elif len(cur_trip) > 0 and self._trip_position_index >= len(cur_trip):
                self._trip_index += 1
                self._trip_position_index = 0
                self._unserved_customer_index = 0
            else:
                self._trip_index += 1
                self._trip_position_index = 0
                self._unserved_customer_index = 0



        # Compute necessary operations
        rmv = Remove(rmv_obj, self._trip_index, self._trip_position_index)
        add = Add(add_obj, self._trip_index, self._trip_position_index)
        delta = Delta([rmv, add])

        # Calculate new solution worthiness
        left = self._solution.left_neighbor_customer(self._trip_index, self._trip_position_index)
        right = self._solution.right_neighbor_customer(self._trip_index, self._trip_position_index)

        old_length = self._instance.get_distance(left, rmv_obj) + self._instance.get_distance(rmv_obj, right)
        new_length = self._instance.get_distance(left, add_obj)  + self._instance.get_distance(add_obj, right)

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
        new_prize = self._solution._prize + add_obj.get_prize() - rmv_obj.get_prize()

        new_objective_value = self._solution.get_objective_value() - old_length + new_length - add_obj.get_penalty() + rmv_obj.get_penalty()


        worthiness = Solution_Worthiness(new_objective_value, new_max_trip_length, self._solution.get_number_of_trips(), new_prize, delta, Delta([]))


        self._unserved_customer_index += 1
        self._current_solution_index += 1

        return worthiness
