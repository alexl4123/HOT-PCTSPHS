
from search_algorithms.ga.fitness_function import Fitness_Function
from search_algorithms.ga.saw_policy import SAW_Policy

class Constant_Weights(SAW_Policy):

    def __init__(self, gamma_1, gamma_2, gamma_3):
        self._gamma_1 = gamma_1
        self._gamma_2 = gamma_2
        self._gamma_3 = gamma_3


    def update_weights(self, iteration, population):    

        for individual in population:

            individual.stepwise_adaption_of_weights(self._gamma_1, self._gamma_2, self._gamma_3)   


    def create_appropriate_fitness_function(self, instance, max_iteration):

        ff = Fitness_Function(instance, self._gamma_1, self._gamma_2, self._gamma_3, self._gamma_1, self._gamma_2, self._gamma_3)
        ff._precompute_necessary_values()

        return ff

    def to_string(self):
        return f"Constant-Weights(Gamma-1:{self._gamma_1};Gamma-2:{self._gamma_2};Gamma-3:{self._gamma_3})"

