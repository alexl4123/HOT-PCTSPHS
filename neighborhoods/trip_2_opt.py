
from neighborhoods.neighborhood import Neighborhood

from framework.solution import Delta, Solution_Worthiness, Reverse


class Trip_2_Opt(Neighborhood):

    def __init__(self, instance, with_delta = True):
        self._instance = instance
        self._solution = None

        self._trip_index = 0

        self._trip_position_index_1 = 0
        self._trip_position_index_2 = 1

        self._number_of_solutions = None
        self._solutions_per_trip = []
        self._current_solution_index = 0

        self._delta = with_delta

    def set_solution(self, solution):
        self._solution = solution

    def reset_indexes(self):
        self._trip_index = 0

        self._trip_position_index_1 = 0
        self._trip_position_index_2 = 1

        self._number_of_solutions = None
        self._solutions_per_trip = []
        self._current_solution_index = 0

    def get_number_possible_solutions(self):

        if not self._number_of_solutions:

            self._number_of_solutions = 0

            for trip in self._solution._trips:
                number_of_vertices = len(trip)
                number_of_edges = number_of_vertices + 1  # Due to edges from and to hotels
                number_of_relevant_edges = number_of_edges - 2

                number_of_possible_exchanges_for_trip = (number_of_relevant_edges * (number_of_relevant_edges + 1)) / 2

                self._number_of_solutions = self._number_of_solutions + number_of_possible_exchanges_for_trip
                self._solutions_per_trip.append(number_of_possible_exchanges_for_trip)

            self._number_of_solutions = int(self._number_of_solutions)

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
        first_index = 0

        while length > 1:

            possible_solutions_for_remaining_length = length - 1

            if pos < possible_solutions_for_remaining_length:
                second_index = int(first_index + 1 + pos)
                break
            else:
                first_index += 1
                pos -= possible_solutions_for_remaining_length
                length -= 1

        return self.reverse(trip, trip_index, first_index, second_index)


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


        vertex_q1 = None
        vertex_q2 = None

        while not vertex_q1 or not vertex_q2:
        
            trip = self._solution._trips[self._trip_index]

            if self._trip_position_index_2 < len(trip) and self._trip_position_index_1 < len(trip) - 1:
                vertex_q1 = trip[self._trip_position_index_1]
                vertex_q2 = trip[self._trip_position_index_2]
            elif self._trip_position_index_2 >= len(trip) and self._trip_position_index_1 < len(trip) - 1:
                self._trip_position_index_1 += 1
                self._trip_position_index_2 = self._trip_position_index_1 + 1
            elif self._trip_position_index_2 >= len(trip) and self._trip_position_index_1 >= len(trip) - 1:
                self._trip_position_index_1 = 0
                self._trip_position_index_2 = 1
                self._trip_index += 1
            else:
                print("ERROR IN 2-OPT")
                quit()

        # Calculate cost of exchange

        rev = self.reverse(trip, self._trip_index, self._trip_position_index_1, self._trip_position_index_2)

        # Set next solution
        self._current_solution_index = self._current_solution_index + 1

        self._trip_position_index_2 += 1

        return rev




    def reverse(self, trip, trip_index, trip_position_index_1, trip_position_index_2):

        vertex_q1 = trip[trip_position_index_1]
        vertex_q2 = trip[trip_position_index_2]

        if trip_position_index_1 > 0:
            vertex_p1 = trip[trip_position_index_1 - 1]
        else:
            vertex_p1 = self._solution._hotels[trip_index]

        if trip_position_index_2 < len(trip) - 1:
            vertex_p2 = trip[trip_position_index_2 + 1]
        else:
            vertex_p2 = self._solution._hotels[trip_index + 1]

        #print("<<<" + str(self._trip_position_index_1) + "::" + str(self._trip_position_index_2) + "::" + str(len(trip)) + ">>>")
        #print("|||" + str(vertex_p1.get_id()) + "::" + str(vertex_q1.get_id()) + "___" + str(vertex_q2.get_id()) + "::" + str(vertex_p2.get_id()) + "|||")

        if self._delta:
            current_length = self._instance.get_distance(vertex_p1, vertex_q1) + self._instance.get_distance(vertex_q2,
                                                                                                             vertex_p2)

            new_length = self._instance.get_distance(vertex_p1, vertex_q2) + self._instance.get_distance(vertex_q1,
                                                                                                         vertex_p2)

            #print("2-EXCH-delta_minus:" + str(current_length) + ":delta_plus:" + str(new_length))

        # Compute necessary operation
        reverse = Reverse(vertex_q1, trip_index, trip_position_index_1, vertex_q2, trip_index,
                          trip_position_index_2)
        delta = Delta([reverse])

        if self._delta:
            # Calculate new solution-worthiness
            new_trip_length = self._solution._trip_lengths[trip_index] - current_length + new_length

            if new_trip_length > self._solution._max_trip_length:
                new_max_trip_length = new_trip_length
            else:
                new_max_trip_length = self._solution._max_trip_length

            new_objective_value = self._solution.get_objective_value() - current_length + new_length
        else:
            cloned_solution = self._solution.clone()
            cloned_solution.change_from_delta(delta, False)
            values = cloned_solution.slow_objective_values_calculation()

            new_objective_value = values[0]
            new_max_trip_length = values[4]

        worthiness = Solution_Worthiness(new_objective_value, new_max_trip_length, self._solution.get_number_of_trips(),
                                         self._solution.get_prize(), delta, Delta([]))
        return worthiness


    @classmethod
    def to_string(cls):
        return "trip_2_opt"

