import random

from solution import Delta, Solution_Worthiness
from algorithm import Algorithm, Algorithm_Result

from enum import Enum


class Local_Search(Algorithm):

    def __init__(self, instance):
        super().__init__(instance)

    def start_search(self, initialization_procedure, step_function_type, neighborhood, termination_criterion = 10):

        solution = initialization_procedure.create_solution()
        current_best_worthiness = Solution_Worthiness(solution.get_objective_value(), solution.get_max_trip_length(), solution.get_number_of_trips(), solution.get_prize(), Delta([],[]), Delta([],[]))

        trace = []
        trace.append(solution.get_objective_value())

        step = 0

        while step < termination_criterion:
            new_worthiness = self._step_function(neighborhood, solution, step_function_type)
            

            if not (new_worthiness.get_objective_value() > current_best_worthiness.get_objective_value()):
                # If it is not better, then go back
                solution.change_from_delta(new_worthiness.get_reverse_delta())
            else:
                current_best_worthiness = new_worthiness
            
            trace.append(current_best_worthiness.get_objective_value())
            
            step = step + 1

        return Algorithm_Result(solution, trace)




    def _step_function(self, neighborhood, solution, step_function_type):

        if step_function_type == Step_Function_Type.RANDOM:
            k = random.randint(0, neighborhood.get_number_possible_solutions() - 1)
            return neighborhood.calc_solution(solution, k)

        else:
            current_solution = solution
            current_worthiness = Solution_Worthiness(solution.get_objective_value(), solution.get_max_trip_length(), solution.get_number_of_trips(), solution.get_prize(), Delta([],[]), Delta([],[]))

            k = 0
            while k < neighborhood.get_number_possible_solutions():
                new_worthiness = neighborhood.calc_solution(solution, k)

                if new_worthiness.get_objective_value() < current_worthiness.get_objective_value() and step_function_type == Step_Function_Type.FIRST:
                    return new_worthiness
                elif new_worthiness.get_objective_value() < current_worthiness.get_objective_value():
                    current_worthiness = new_worthiness

                solution.change_from_delta(new_worthiness.get_reverse_delta())

                k = k + 1

            solution.change_from_delta(current_worthiness.get_delta())
            return current_worthiness


            
class Step_Function_Type(Enum):
    FIRST = 1
    BEST = 2
    RANDOM = 3
       

        

