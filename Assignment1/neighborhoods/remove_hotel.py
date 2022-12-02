
from neighborhoods.neighborhood import Neighborhood
from framework.solution import Delta, Solution_Worthiness, Reverse, Remove


class Remove_Hotel(Neighborhood):

    def __init__(self, instance):
        self._instance = instance
        self._solution = None

        self._trip_index = 1
        self._current_solution_index = 0
        
        # Just needed for the Delta-Remove functionality of framework.solution
        self._trip_position_index = 0

    def set_solution(self, solution):
        self._solution = solution

    def reset_indexes(self):

        self._trip_index = 1
        self._current_solution_index = 0
        self._number_of_solutions = None

    def get_number_possible_solutions(self):
        """
            Should be in O(h) in the number of hotels currently in the solution
        """


        if not self._number_of_solutions:
            self._number_of_solutions = 0
           
            hotels = self._solution._hotels

            self._number_of_solutions = len(hotels) - 2


        return self._number_of_solutions


    def next_solution(self):

        if not self._number_of_solutions:
            val = self.get_number_possible_solutions()
            if val == 0:
                print("NO 2-OPT-Solutions possible")
                return Solution_Worthiness(self._solution.get_objective_value(), self._solution.get_max_trip_length(),
                                           self._solution.get_number_of_trips(), self._solution.get_prize(), Delta([]),
                                           Delta([]))

        if self._current_solution_index >= self._number_of_solutions:
            print("NO MORE SOLUTIONS AVAILABLE")
            return Solution_Worthiness(self._solution.get_objective_value(), self._solution.get_max_trip_length(),
                                       self._solution.get_number_of_trips(), self._solution.get_prize(), Delta([]),
                                       Delta([]))


        hotels = self._solution._hotels
        # Get hotel
        hotel = None

        if self._trip_index >= len(hotels) - 1:
            print("FATAL ERROR IN RMV HOTEL")
            quit()

        hotel = hotels[self._trip_index]


        # Compute necessary operations
        rmv = Remove(hotel, self._trip_index, self._trip_position_index)
        delta = Delta([rmv])


        # Calculate new solution worthiness
        left = self._solution.left_neighbor_hotel(self._trip_index)
        right = self._solution.right_neighbor_hotel(self._trip_index)

        old_length = self._instance.get_distance(left, hotel) + self._instance.get_distance(hotel, right)
        new_length = self._instance.get_distance(left, right)

        # Recalculate max_trip_length
        left_trip = self._solution._trip_lengths[self._trip_index - 1]
        right_trip = self._solution._trip_lengths[self._trip_index]

        new_cur_trip_length = left_trip + right_trip - old_length + new_length

        new_max_trip_length = self._solution._max_trip_length

        if new_cur_trip_length > new_max_trip_length:
            new_max_trip_length = new_cur_trip_length

        # Recalculate new prize
        new_prize = self._solution._prize

        new_objective_value = self._solution.get_objective_value() - old_length + new_length - hotel.get_fee()


        worthiness = Solution_Worthiness(new_objective_value, new_max_trip_length, self._solution.get_number_of_trips(), new_prize, delta, Delta([]))

        self._trip_index += 1
        self._current_solution_index += 1

        return worthiness
