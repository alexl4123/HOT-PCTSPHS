import random

from solution import Delta, Solution_Worthiness
from algorithm import Algorithm, Algorithm_Result

from enum import Enum


class Local_Search(Algorithm):

    def __init__(self, instance):
        super().__init__(instance)

    def start_search(self, initialization_procedure, step_function_type, neighborhood, termination_criterion = 10):

        solution = initialization_procedure.create_solution()
        current_best_worthiness = Solution_Worthiness(solution.get_objective_value(), solution.get_max_trip_length(), solution.get_number_of_trips(), solution.get_prize(), Delta([]), Delta([]))

        trace = []
        trace.append(solution.get_objective_value())

        step = 0

        while step < termination_criterion:
            new_worthiness = self._step_function(neighborhood, solution, step_function_type)
            

            if new_worthiness.get_objective_value() < current_best_worthiness.get_objective_value():
                # If it is better, apply changes
                solution.change_from_delta(new_worthiness.get_delta())
                current_best_worthiness = new_worthiness
            
            trace.append(current_best_worthiness.get_objective_value())
            
            step = step + 1

        return Algorithm_Result(solution, trace)




    def _step_function(self, neighborhood, solution, step_function_type):

        neighborhood.set_solution(solution)
        neighborhood.reset_indexes()

        if step_function_type == Step_Function_Type.RANDOM:
            # Inefficient, but does the job
            k = random.randint(0, neighborhood.get_number_possible_solutions() - 1)
            for i in range(0, k):
                sol = neighborhood.next_solution()
            
            if k == 0 and neighborhood.get_number_possible_solutions() > 0:
                sol = neighborhood.next_solution()

            return sol
        else:
            current_solution = solution
            current_worthiness = Solution_Worthiness(solution.get_objective_value(), solution.get_max_trip_length(), solution.get_number_of_trips(), solution.get_prize(), Delta([]), Delta([]))

            k = 1
            number = neighborhood.get_number_possible_solutions()
            while k < number:
                new_worthiness = neighborhood.next_solution()

                if new_worthiness.get_objective_value() < current_worthiness.get_objective_value() and step_function_type == Step_Function_Type.FIRST:
                    return new_worthiness
                elif new_worthiness.get_objective_value() < current_worthiness.get_objective_value():
                    current_worthiness = new_worthiness

                k = k + 1

            return current_worthiness


            
class Step_Function_Type(Enum):
    FIRST = 1
    BEST = 2
    RANDOM = 3
       

        

