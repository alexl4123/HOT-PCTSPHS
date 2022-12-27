
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



