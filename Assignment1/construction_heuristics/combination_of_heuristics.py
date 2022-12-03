from construction_heuristics.initialization_procedure import Initialization_Procedure
from construction_heuristics.greedy_nearest_neighbor_initialization import Greedy_Nearest_Neighbor_Initialization
from construction_heuristics.backtracking_search import Backtracking_Search
from construction_heuristics.insertion_heuristic_sum_of_trips import Insertion_Heuristic_Sum_Of_Trips
from construction_heuristics.insertion_diverse_hotels import Insertion_Diverse_Hotels


class Combination_Of_Heuristics(Initialization_Procedure):

    def create_solution(self, random_k=0):

        procedure_1 = Greedy_Nearest_Neighbor_Initialization(self._instance)
        procedure_2 = Backtracking_Search(self._instance)
        procedure_3 = Insertion_Heuristic_Sum_Of_Trips(self._instance)
        procedure_4 = Insertion_Diverse_Hotels(self._instance)

        if random_k == 0:

            best_solution = None

            solutions = []
            solution_1 = procedure_1.create_solution()
            solution_2 = procedure_2.create_solution()
            solution_3 = procedure_3.create_solution()
            solution_4 = procedure_4.create_solution()

            if solution_1:
                best_solution = solution_1
            if solution_2 and best_solution.get_objective_value() > solution_2.get_objective_value():
                best_solution = solution_2
            if solution_3 and best_solution.get_objective_value() > solution_3.get_objective_value():
                best_solution = solution_3
            if solution_4 and best_solution.get_objective_value() > solution_4.get_objective_value():
                best_solution = solution_4

            return best_solution
        else:
            return procedure_2.create_solution(random_k)
