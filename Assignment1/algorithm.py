
class Algorithm:

    def __init__(self, instance):
        self._instance = instance

class Algorithm_Result:
    def __init__(self, best_solution, trace):
        self._best_solution = best_solution
        self._trace = trace


    def get_best_solution(self):
        return self._best_solution

    def get_trace(self):
        return self._trace


