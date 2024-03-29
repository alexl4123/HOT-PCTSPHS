
from neighborhoods.neighborhood import Neighborhood
from framework.solution import Delta, Solution_Worthiness, Reverse, Remove, Add


class Add_Hotel(Neighborhood):

    def __init__(self, instance):
        self._instance = instance
        self._solution = None

        self._trip_index = 0
        self._trip_position_index = 0
        self._hotels_index = 0
        self._hotels = instance.get_list_of_hotels()

        self._current_solution_index = 0
        self._number_of_solutions = None
        self._solutions_per_trip = []


    def set_solution(self, solution):
        self._solution = solution

    def reset_indexes(self):

        self._trip_index = 0
        self._trip_position_index = 0
        self._hotels_index = 0

        self._current_solution_index = 0
        self._number_of_solutions = None
        self._solutions_per_trip = []

    def get_number_possible_solutions(self):
        """
            Should be in O(sum(n+1)) in the number of customers currently per trip
        """

        if not self._number_of_solutions:

            self._number_of_solutions = 0

            number_of_possible_insertion_positions = 0
            for trip in self._solution._trips:
                number_of_possible_insertion_positions += len(trip) + 1

                self._solutions_per_trip.append((len(trip)+1) * len(self._hotels))

            self._number_of_solutions = len(self._hotels) * number_of_possible_insertion_positions

        return self._number_of_solutions


    def get_specific_solution(self, position):
 
        trip_index = 0

        pos = position
        for tmp_trip_index in range(len(self._solutions_per_trip)):

            pos -= self._solutions_per_trip[tmp_trip_index]

            if pos < 0:
                trip_index = tmp_trip_index
                pos += self._solutions_per_trip[tmp_trip_index]
                break


        trip = self._solution._trips[trip_index]
        length = len(trip)

        trip_position_index = int(pos / len(self._hotels))
        obj_index = int(pos % len(self._hotels))
        obj = self._hotels[obj_index]

        worthiness = self.add_hotel(trip_index, trip_position_index, obj)

        return worthiness

    def next_solution(self):

        if not self._number_of_solutions:
            val = self.get_number_possible_solutions()
            if val == 0:
                print("NO ADD_HOTEL-Solutions possible")
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
                print("FATAL ERROR IN ADD_HOTEL NEIGHBORHOOD")
                quit()

            cur_trip =  self._solution._trips[self._trip_index]


            if len(cur_trip) >= 0 and self._trip_position_index <= len(cur_trip) and self._hotels_index < len(self._hotels):
                obj = self._hotels[self._hotels_index]
            elif len(cur_trip) >= 0 and self._trip_position_index <= len(cur_trip) and self._hotels_index >= len(self._hotels):
                self._trip_position_index += 1
                self._hotels_index = 0
            elif len(cur_trip) >= 0 and self._trip_position_index >= len(cur_trip):
                self._trip_index += 1
                self._trip_position_index = 0
                self._hotels_index = 0
            else:
                print("FATAL - SHOULD NOT HAPPEN IN ADD_HOTELS NEIGHBORHOOD")
                quit()

        worthiness = self.add_hotel(self._trip_index, self._trip_position_index, obj)

        self._hotels_index += 1
        self._current_solution_index += 1

        return worthiness

    def add_hotel(self, trip_index, trip_position_index, obj):

        # Compute necessary operations
        add = Add(obj, trip_index, trip_position_index)
        delta = Delta([add])


        # Calculate new solution worthiness
        trip = self._solution._trips[trip_index]

        # Calculate new solution worthiness
        if trip_position_index < len(trip) - 1:
            left = self._solution.left_neighbor_customer(trip_index, trip_position_index)
        else: 
            left = self._solution.left_neighbor_hotel(trip_index + 1)

        if trip_position_index > 0:
            right = self._solution.right_neighbor_customer(trip_index, trip_position_index - 1)
        else:
            right = self._solution.right_neighbor_hotel(trip_index)

        old_length = self._instance.get_distance(left, right)
        new_length_0 = self._instance.get_distance(left, obj)
        new_length_1 = self._instance.get_distance(obj, right)

        new_length = new_length_0 + new_length_1

        (new_left_trip_length, new_right_trip_length) = self._solution.get_left_right_length_of_trip(trip_index, trip_position_index, obj)

        # Recalculate max_trip_length
        cur_trip_length = self._solution._trip_lengths[trip_index]

        new_cur_trip_length = cur_trip_length - old_length + new_length

        new_max_trip_length = self._solution._max_trip_length

        if new_left_trip_length >= new_right_trip_length and new_left_trip_length > new_max_trip_length:
            new_max_trip_length = new_left_trip_length
        elif new_left_trip_length < new_right_trip_length and new_right_trip_length > new_max_trip_length:
            new_max_trip_length = new_right_trip_length

        # Recalculate new prize
        new_prize = self._solution._prize

        new_objective_value = self._solution.get_objective_value() - old_length + new_length + obj.get_fee()

        worthiness = Solution_Worthiness(new_objective_value, new_max_trip_length, self._solution.get_number_of_trips() + 1, new_prize, delta, Delta([]))

        return worthiness


    @classmethod
    def to_string(cls):
        return "add_hotel"

