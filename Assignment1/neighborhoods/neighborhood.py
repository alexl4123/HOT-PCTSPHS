from framework.solution import Delta, Solution_Worthiness


class Neighborhood:

    def __init__(self, instance):
        self._instance = instance

    def reset_indexes(self):
        pass

    def set_solution(self, solution):
        self._solution = solution

    def get_number_possible_solutions(self):
        return 0

    def next_solution(self):
        pass


    def calc_solution(self):
        return Solution_Worthiness(self._solution.get_objective_value(), self._solution.get_max_trip_length(),
                                   self._solution.get_number_of_trips(), self._solution.get_prize(), Delta([], []), Delta([], []))
