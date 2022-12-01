from framework.solution import Delta, Solution_Worthiness


class Neighborhood:

    def __init__(self, instance):
        self._instance = instance

    def get_number_possible_solutions(self):
        return 0

    def calc_solution(self, base_solution, permutation_index):
        return Solution_Worthiness(base_solution.get_objective_value(), base_solution.get_max_trip_length(),
                                   base_solution.get_number_of_trips(), base_solution.get_prize(), Delta([], []), Delta([], []))
