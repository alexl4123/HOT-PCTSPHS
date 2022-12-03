from pathlib import Path

class Algorithm:

    def __init__(self, instance):
        self._instance = instance

    def start_search(self, init_solution, step_function_type, neighborhoods, max_runtime, max_iteration_limit = 100):
        return Algorithm_Result(init_solution, [init_solution.get_objective_value()], 0)


