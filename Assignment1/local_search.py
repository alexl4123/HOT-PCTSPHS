import random

from solution import Delta
from algorithm import Algorithm, Algorithm_Result

from enum import Enum


class Local_Search(Algorithm):

    def __init__(self, instance):
        super().__init__(instance)

    def start_search(self, initialization_procedure, step_function_type, neighborhood, termination_criterion = 10):

        current_solution = initialization_procedure.create_solution()
        current_objective_value = current_solution.get_objective_value()

        trace = []
        trace.append(current_solution.get_objective_value())

        step = 0

        while step < termination_criterion:
            (new_solution, reverse_delta) = self._step_function(neighborhood, current_solution, step_function_type)

            if not (new_solution.get_objective_value() < current_objective_value):
                # If it is not better, then go back
                new_solution.change_from_delta(reverse_delta)

            
            trace.append(current_solution.get_objective_value())
            step = step + 1

        return Algorithm_Result(new_solution, trace)




    def _step_function(self, neighborhood, solution, step_function_type):
        if step_function_type == Step_Function_Type.RANDOM:
            k = random.randint(0, neighborhood.get_number_possible_solutions() - 1)
            (new_solution, delta, reverse_delta) = neighborhood.calc_solution(solution, k)

            return (new_solution, reverse_delta)
        else:
            current_solution = solution
            current_value = solution.get_objective_value()
            best_delta = Delta([],[])
            best_reverse_delta = Delta([],[])

            k = 0
            while k < neighborhood.get_number_possible_solutions():
                (new_solution, delta, reverse_delta) = neighborhood.calc_solution(solution, k)

                """
                if new_solution.get_objective_value() < current_value and step_function_type == Step_Function_Type.FIRST:
                    return (new_solution, reverse_delta)
                elif 


                if                     current_solution = new_solution

                    if 
                """

                k = k + 1



            return (current_solution, best_reverse_delta)


            
class Step_Function_Type(Enum):
    FIRST = 1
    BEST = 2
    RANDOM = 3
       

        

