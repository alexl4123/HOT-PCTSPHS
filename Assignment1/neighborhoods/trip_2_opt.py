
from neighborhoods.neighborhood import Neighborhood

from framework.solution import Delta, Solution_Worthiness, Reverse


class Trip_2_Opt(Neighborhood):

    def __init__(self, instance):
        self._instance = instance
        self._solution = None

        self._trip_index = 0

        self._edge_1_vertex_index = 0
        self._edge_2_vertex_index = 2

        self._number_of_solutions = None
        self._current_solution_index = 0

    def set_solution(self, solution):
        self._solution = solution

    def reset_indexes(self):
        self._trip_index = 0

        self._edge_1_vertex_index = 0
        self._edge_2_vertex_index = 2

        self._number_of_solutions = None
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

            self._number_of_solutions = int(self._number_of_solutions)

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

        # Calculate cost of exchange

        trip = self._solution._trips[self._trip_index]

        if self._edge_1_vertex_index > 0:
            vertex_p1 = trip[self._edge_1_vertex_index - 1]
        else:
            vertex_p1 = self._solution._hotels[self._trip_index]
        vertex_q1 = trip[self._edge_1_vertex_index]

        if self._edge_2_vertex_index < len(trip):
            vertex_p2 = trip[self._edge_2_vertex_index]
        else:
            vertex_p2 = self._solution._hotels[self._trip_index + 1]
        vertex_q2 = trip[self._edge_2_vertex_index - 1]

        current_length = self._instance.get_distance(vertex_p1, vertex_q1) + self._instance.get_distance(vertex_q2,
                                                                                                         vertex_p2)

        new_length = self._instance.get_distance(vertex_p1, vertex_q2) + self._instance.get_distance(vertex_q1,
                                                                                                     vertex_p2)

        # print("2-EXCH-delta_minus:" + str(current_length) + ":delta_plus:" + str(new_length))

        # Compute necessary operation
        reverse = Reverse(vertex_q1, self._trip_index, self._edge_1_vertex_index, vertex_q2, self._trip_index,
                          self._edge_2_vertex_index - 1)
        delta = Delta([reverse])

        # Calculate new solution-worthiness
        new_trip_length = self._solution._trip_lengths[self._trip_index] - current_length + new_length

        if new_trip_length > self._solution._max_trip_length:
            new_max_trip_length = new_trip_length
        else:
            new_max_trip_length = self._solution._max_trip_length

        new_objective_value = self._solution.get_objective_value() - current_length + new_length

        worthiness = Solution_Worthiness(new_objective_value, new_max_trip_length, self._solution.get_number_of_trips(),
                                         self._solution.get_prize(), delta, Delta([]))

        # Set next solution
        self._current_solution_index = self._current_solution_index + 1

        if self._edge_2_vertex_index < len(trip):
            self._edge_2_vertex_index = self._edge_2_vertex_index + 1
        elif self._edge_2_vertex_index == len(trip) and self._edge_1_vertex_index < (len(trip) - 2):
            self._edge_1_vertex_index = self._edge_1_vertex_index + 1
            self._edge_2_vertex_index = self._edge_1_vertex_index + 2
        elif self._edge_2_vertex_index == len(trip) and self._edge_1_vertex_index == (len(trip) - 2):
            self._edge_1_vertex_index = 0
            self._edge_2_vertex_index = 2

            new_trip_index = self._trip_index

            for index in range(new_trip_index + 1, len(self._solution._trips)):
                if len(self._solution._trips[index]) > 1:
                    self._trip_index = index
                    break

        return worthiness
