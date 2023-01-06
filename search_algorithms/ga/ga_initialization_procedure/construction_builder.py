
import time

from search_algorithms.ga.ga_initialization_procedure.initialization_procedure import GA_Initialization_Procedure
from search_algorithms.ga.ga_initialization_procedure.ga_insertion_heuristic import GA_Insertion_Heuristic, Shortest_Path_Criterion, Best_Objective_Value_Criterion, Farthest_Distance_Criterion
from search_algorithms.ga.ga_initialization_procedure.ga_greedy import GA_Greedy
from search_algorithms.ga.ga_initialization_procedure.ga_mst import GA_MST
from search_algorithms.ga.ga_initialization_procedure.ga_repair import GA_Repair

class Construction_Builder(GA_Initialization_Procedure):


    def __init__(self, instance, alpha=1, beta=-0.5, gamma=-0.5, delta=0.5, fitness_function = None):
        super().__init__(instance, alpha = alpha, beta = beta, gamma = gamma, delta = delta, fitness_function = fitness_function)


    def create_solution(self, iteration, random_k = 0, show_output = True, max_runtime = 90):

        if iteration % 50 == 0:
            ga_mst = GA_MST(self._instance, alpha = self._alpha, beta = self._beta, gamma = self._gamma, delta = self._delta_param, fitness_function = self._fitness_function)

            result = ga_mst.create_solution(random_k = random_k, show_output = show_output, max_runtime = max_runtime)
        elif iteration % 2 == 0:
            ga_greedy = GA_Greedy(self._instance, alpha = self._alpha, beta = self._beta, gamma = self._gamma, delta = self._delta_param, fitness_function = self._fitness_function)

            result = ga_greedy.create_solution(random_k = random_k, show_output = show_output, max_runtime = max_runtime)
        elif iteration % 2 == 1:
            if iteration % 6 == 1:
                ga_insertion = GA_Insertion_Heuristic(self._instance, alpha = self._alpha, beta = self._beta, gamma = self._gamma, delta = self._delta_param, insertion_criterion = Shortest_Path_Criterion, fitness_function = self._fitness_function)
            elif iteration % 6 == 3:
                ga_insertion = GA_Insertion_Heuristic(self._instance, alpha = self._alpha, beta = self._beta, gamma = self._gamma, delta = self._delta_param, insertion_criterion = Best_Objective_Value_Criterion, fitness_function = self._fitness_function)
            elif iteration % 6 == 5:
                ga_insertion = GA_Insertion_Heuristic(self._instance, alpha = self._alpha, beta = self._beta, gamma = self._gamma, delta = self._delta_param, insertion_criterion = Farthest_Distance_Criterion, fitness_function = self._fitness_function)
            else:
                print("ILLEGAL-VALUE!!!")
                quit()
            
            result = ga_insertion.create_solution(random_k = random_k, show_output = show_output, max_runtime = max_runtime)


        #print(f"Needed time:{result.get_time()}")
        result = GA_Repair.repair(result.get_best_solution()._instance, result.get_best_solution())

        return result


