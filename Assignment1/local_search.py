import random

from algorithm import Algorithm, Algorithm_Result

from enum import Enum


class Local_Search(Algorithm):

    def __init__(self, instance):
        super().__init__(instance)

    def start_search(self, initialization_procedure, step_function_type, neighborhood, termination_criterion = 10):

        current_solution = initialization_procedure.create_solution()
        trace = []
        trace.append(current_solution.get_objective_value())

        step = 0

        while step < termination_criterion:
            new_solution = self._step_function(neighborhood, current_solution, step_function_type)

            if new_solution.get_objective_value() < current_solution.get_objective_value():
                current_solution = new_solution

            
            trace.append(current_solution.get_objective_value())
            step = step + 1

        return Algorithm_Result(new_solution, trace)




    def _step_function(self, neighborhood, solution, step_function_type):
        if step_function_type == Step_Function_Type.RANDOM:
            k = random.randint(0, neighborhood.get_number_possible_solutions() - 1)
            return neighborhood.calc_solution(solution, k)
        else:
            current_solution = solution
            k = 0
            while k < neighborhood.get_number_possible_solutions():
                new_solution = neighborhood.calc_solution(solution, k)

                if new_solution.get_objective_value() < current_solution.get_objective_value():
                    current_solution = new_solution

                    if step_function_type == Step_Function_Type.FIRST:
                        return current_solution

                k = k + 1

            return current_solution


            
class Step_Function_Type(Enum):
    FIRST = 1
    BEST = 2
    RANDOM = 3
       

        

