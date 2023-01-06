
from search_algorithms.ga.fitness_function import Fitness_Function
from search_algorithms.ga.saw_policy import SAW_Policy

class Linear_Weights(SAW_Policy):

    def __init__(self, gamma_1, gamma_2, gamma_3, alpha_gamma_1, alpha_gamma_2, alpha_gamma_3):
        self._gamma_1 = gamma_1
        self._gamma_2 = gamma_2
        self._gamma_3 = gamma_3

        self._alpha_gamma_1 = alpha_gamma_1
        self._alpha_gamma_2 = alpha_gamma_2
        self._alpha_gamma_3 = alpha_gamma_3

    def update_weights(self, iteration, population):    

        gamma_1 = self._gamma_1 + iteration * self._alpha_gamma_1
        gamma_2 = self._gamma_2 + iteration * self._alpha_gamma_2
        gamma_3 = self._gamma_3 + iteration * self._alpha_gamma_3

        for individual in population:

            individual.stepwise_adaption_of_weights(gamma_1, gamma_2, gamma_3)   

    def create_appropriate_fitness_function(self, instance, max_iteration):
        max_gamma_1 = self._gamma_1 + max_iteration * self._alpha_gamma_1
        max_gamma_2 = self._gamma_2 + max_iteration * self._alpha_gamma_2
        max_gamma_3 = self._gamma_3 + max_iteration * self._alpha_gamma_3

        ff = Fitness_Function(instance, max_gamma_1, max_gamma_2, max_gamma_3, self._gamma_1, self._gamma_2, self._gamma_3)
        ff._precompute_necessary_values()

        return ff

    def to_string(self):
        return f"Linear-Sequence-Weights(Gamma-1:{self._gamma_1};Gamma-2:{self._gamma_2};Gamma-3:{self._gamma_3};Alpha-Gamma-1:{self._alpha_gamma_1};Alpha-Gamma-2:{self._alpha_gamma_2};Alpha-Gamma-3:{self._alpha_gamma_3})"


