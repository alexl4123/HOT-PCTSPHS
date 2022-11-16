
from construction_heuristics.initialization_procedure import Initialization_Procedure
from construction_heuristics.heuristic_2 import Deterministic_Greedy_Initialization
from construction_heuristics.heuristic_3 import Backtracking_Search
from construction_heuristics.heuristic_4 import Insertion_Heuristic
from construction_heuristics.heuristic_6 import Insertion_Heuristic_3

class Combination_Of_Heuristics(Initialization_Procedure):

    def create_solution(self, random_k = 0):

        procedure_1 = Deterministic_Greedy_Initialization(self._instance)
        procedure_2 = Backtracking_Search(self._instance)
        procedure_3 = Insertion_Heuristic(self._instance)
        procedure_4 = Insertion_Heuristic_3(self._instance)


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
                



