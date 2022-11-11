
from solution import Solution

class Initialization_Procedure:

    def __init__(self, instance):
        self._instance = instance

    def create_solution(self):
        return Solution(self._instance)
