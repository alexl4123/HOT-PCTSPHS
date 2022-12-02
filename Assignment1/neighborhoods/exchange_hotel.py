
from neighborhoods.neighborhood import Neighborhood
from framework.solution import Delta, Solution_Worthiness, Reverse, Remove, Add


class Exchange_Hotel(Neighborhood):

    def __init__(self, instance):
        self._instance = instance
        self._solution = None

        self._trip_index = 1
        self._hotel_index = 0
        self._hotels = instance.get_list_of_hotels()

        self._current_solution_index = 0
        
        # Just needed for the Delta-Remove functionality of framework.solution
        self._trip_position_index = 0

    def set_solution(self, solution):
        self._solution = solution
        self._hotels = solution._hotels

    def reset_indexes(self):

        self._trip_index = 1
        self._hotel_index = 0
        self._current_solution_index = 0
        self._number_of_solutions = None

    def get_number_possible_solutions(self):
        """
            Should be in O(h * h_t) in the number of hotels currently in the solution (h) times the total number of hotels available (h_t)
        """


        if not self._number_of_solutions:
            self._number_of_solutions = 0
           
            sol_hotels = self._solution._hotels

            self._number_of_solutions = (len(sol_hotels) - 2) * len(self._hotels)

        return self._number_of_solutions


    def next_solution(self):

        if not self._number_of_solutions:
            val = self.get_number_possible_solutions()
            if val == 0:
                print("NO EXCHANGE-HOTEL-Solutions possible")
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

        while hotel == None:
            if self._trip_index >= len(sol_hotels) - 1:
                print("FATAL ERROR IN EXCHANGE-HOTEL")
                quit()

            if self._hotel_index > len(self._hotels) - 1:
                self._trip_index += 1
                self._hotel_index = 0
            elif self._hotel_index <= len(self._hotels) - 1:
                hotel = self._hotels[self._hotel_index]

        old_hotel = sol_hotels[self._trip_index]

        # Compute necessary operations
        if hotel.get_id() != old_hotel.get_id():
            add = Add(hotel, self._trip_index, 0)
            rmv = Remove(old_hotel, self._trip_index, self._trip_position_index)
            delta = Delta([add,rmv])
        else:
            delta = Delta([])

        # Calculate new solution worthiness
        left = self._solution.left_neighbor_hotel(self._trip_index)
        right = self._solution.right_neighbor_hotel(self._trip_index)

        old_length_0 = self._instance.get_distance(left, old_hotel) 
        old_length_1 = self._instance.get_distance(old_hotel, right)
        old_length = old_length_0 + old_length_1

        new_length_0 = self._instance.get_distance(left, hotel)
        new_length_1 = self._instance.get_distance(hotel, right)
        new_length = new_length_0 + new_length_1

        # Recalculate max_trip_length
        left_trip = self._solution._trip_lengths[self._trip_index - 1]
        right_trip = self._solution._trip_lengths[self._trip_index]

        new_left_trip = left_trip - old_length_0 + new_length_0

        new_right_trip = right_trip - old_length_1 + new_length_1


        new_max_trip_length = self._solution._max_trip_length

        if new_left_trip > new_max_trip_length and new_left_trip >= new_right_trip:
            new_max_trip_length = new_left_trip
        elif new_right_trip > new_max_trip_length and new_right_trip >= new_left_trip:
            new_max_trip_length = new_right_trip

        # Recalculate new prize
        new_prize = self._solution._prize

        new_objective_value = self._solution.get_objective_value() - old_length + new_length - old_hotel.get_fee() + hotel.get_fee()


        worthiness = Solution_Worthiness(new_objective_value, new_max_trip_length, self._solution.get_number_of_trips(), new_prize, delta, Delta([]))

        self._hotel_index += 1
        self._current_solution_index += 1

        return worthiness
