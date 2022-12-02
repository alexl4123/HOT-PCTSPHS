
from neighborhoods.neighborhood import Neighborhood
from framework.solution import Delta, Solution_Worthiness, Reverse, Remove, Add


class Move_Hotel(Neighborhood):

    def __init__(self, instance):
        self._instance = instance
        self._solution = None

        self._trip_index = 1

        self._is_left = True
        self._hotel_left_index = 0
        self._hotel_right_index = 0

        self._current_solution_index = 0
        
        # Just needed for the Delta-Remove functionality of framework.solution
        self._trip_position_index = 0

    def set_solution(self, solution):
        self._solution = solution

    def reset_indexes(self):

        self._trip_index = 1

        self._is_left = True
        self._hotel_left_index = 0
        self._hotel_right_index = 0

        self._current_solution_index = 0
        self._number_of_solutions = None

    def get_number_possible_solutions(self):
        """
            Should be in about O(2 * h * insert) in the number of hotels currently in the solution (h), and available insertion positions (insert)
        """


        if not self._number_of_solutions:
            self._number_of_solutions = 0

            available_insertion_positions = 0

            for hotel_index in range(1, len(self._solution._hotels) - 1):
                left_trip = self._solution._trips[hotel_index - 1]
                right_trip = self._solution._trips[hotel_index]

                available_insertion_positions += len(left_trip) + len(right_trip)
           
            self._number_of_solutions = available_insertion_positions

        return self._number_of_solutions


    def next_solution(self):

        if not self._number_of_solutions:
            val = self.get_number_possible_solutions()
            if val == 0:
                print("NO MOVE-HOTEL-Solutions possible")
                return Solution_Worthiness(self._solution.get_objective_value(), self._solution.get_max_trip_length(),
                                           self._solution.get_number_of_trips(), self._solution.get_prize(), Delta([]),
                                           Delta([]))

        if self._current_solution_index >= self._number_of_solutions:
            print("NO MORE SOLUTIONS AVAILABLE")
            return Solution_Worthiness(self._solution.get_objective_value(), self._solution.get_max_trip_length(),
                                       self._solution.get_number_of_trips(), self._solution.get_prize(), Delta([]),
                                       Delta([]))


        sol_hotels = self._solution._hotels
        # Get hotel
        hotel = None

        trip_index = -1
        trip_position_index = -1

        while trip_index < 0 and trip_position_index < 0:

            if trip_index > len(self._solution._hotels) - 1:
                print("SHOULD-NOT-HAPPEN")
                quit()
                
            left_trip = self._solution._trips[self._trip_index - 1]
            right_trip = self._solution._trips[self._trip_index]

            left_trip_position_index = len(left_trip) - 1 - self._hotel_left_index
            right_trip_position_index = 1 + self._hotel_right_index

            if left_trip_position_index < 0 and right_trip_position_index > len(right_trip):
                self._hotel_left_index = 0
                self._hotel_right_index = 0
                self._is_left = True
                self._trip_index += 1
            elif self._is_left and left_trip_position_index >= 0:
                trip_position_index = left_trip_position_index
                trip_index = self._trip_index - 1
            elif not self._is_left and right_trip_position_index <= len(right_trip):
                trip_position_index = right_trip_position_index
                trip_index = self._trip_index
            elif self._is_left and left_trip_position_index < 0:
                self._is_left = False
                trip_position_index = right_trip_position_index
                trip_index = self._trip_index
            elif not self._is_left and right_trip_position_index > len(right_trip):
                self._is_left = True
                trip_position_index = left_trip_position_index
                trip_index = self._trip_index - 1
            else:
                print("ERROR IN MOVE HOTEL")
                quit()

        

        hotel = sol_hotels[self._trip_index]

        # Compute necessary operations
        rmv = Remove(hotel, self._trip_index, trip_position_index)

        if self._is_left:
            add = Add(hotel, trip_index, trip_position_index)
        else:
            add = Add(hotel, trip_index - 1, len(self._solution._trips[trip_index - 1]) + trip_position_index)

        delta = Delta([rmv, add])

        # Calculate new solution worthiness
        old_left = self._solution.left_neighbor_hotel(self._trip_index)
        old_right = self._solution.right_neighbor_hotel(self._trip_index)

        new_left = self._solution.left_neighbor_customer(trip_index, trip_position_index)
        if trip_position_index > 0:
            new_right = self._solution.right_neighbor_customer(trip_index, trip_position_index - 1)
        else: 
            new_right = self._solution._trips[trip_index][0]

        """
        print("<<<" + str(hotel.get_id()) + ">>>")
        print("<<<" + str(old_left.get_id()) + "::" + str(old_right.get_id()) + "::" + str(new_left.get_id()) + "::" + str(new_right.get_id()) + ">>>")
        """

        old_length_0 = self._instance.get_distance(old_left, hotel) 
        old_length_1 = self._instance.get_distance(hotel, old_right)
        old_length_2 = self._instance.get_distance(new_left, new_right)
        old_length = old_length_0 + old_length_1 + old_length_2

        new_length_0 = self._instance.get_distance(new_left, hotel)
        new_length_1 = self._instance.get_distance(hotel, new_right)
        new_length_2 = self._instance.get_distance(old_left, old_right)
        new_length = new_length_0 + new_length_1 + new_length_2

        # Recalculate max_trip_length


        (new_left_trip_length, new_right_trip_length) = self._solution.get_left_right_length_of_trip(trip_index, trip_position_index, hotel)

        if self._is_left:
            new_left_trip = new_left_trip_length
            new_right_trip = new_right_trip_length - old_length_0 - old_length_1 + new_length_2 + self._solution._trip_lengths[trip_index + 1]
        else:
            new_right_trip = new_right_trip_length
            new_left_trip = new_left_trip_length - old_length_0 - old_length_1 + new_length_2 + self._solution._trip_lengths[trip_index - 1]


        new_max_trip_length = self._solution._max_trip_length

        if new_left_trip > new_max_trip_length and new_left_trip >= new_right_trip:
            new_max_trip_length = new_left_trip
        elif new_right_trip > new_max_trip_length and new_right_trip >= new_left_trip:
            new_max_trip_length = new_right_trip

        # Recalculate new prize
        new_prize = self._solution._prize

        new_objective_value = self._solution.get_objective_value() - old_length + new_length
        
        """
        print("<<<" + str(hotel.get_id()) + "<>" + str(self._current_solution_index) + ">>>")
        print("<<<" + str(trip_index) + "::" + str(trip_position_index) + ">>>")
        print("<<<" + str(new_objective_value) + "::" + str(new_max_trip_length) + "::" + str(new_left_trip) + "::" + str(new_right_trip) + ">>>")
        print("!!!!" + str(self._instance.get_C1()) + "::" + str(self._instance.get_C2()) + "::" + str(self._instance.get_C3()) + "!!!!")
        """

        worthiness = Solution_Worthiness(new_objective_value, new_max_trip_length, self._solution.get_number_of_trips(), new_prize, delta, Delta([]))

        if self._is_left:
            self._is_left = False
            self._hotel_left_index += 1
        else: 
            self._is_left = True
            self._hotel_right_index += 1
        
        self._current_solution_index += 1

        return worthiness
