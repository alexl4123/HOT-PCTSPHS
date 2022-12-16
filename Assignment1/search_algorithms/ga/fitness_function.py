
class Fitness_Function:

    def __init__(self, instance, max_gamma_1, max_gamma_2, max_gamma_3, gamma_1 = 1, gamma_2 = 1, gamma_3 = 1):
        self._instance = instance

        self._max_gamma_1 = max_gamma_1
        self._max_gamma_2 = max_gamma_2
        self._max_gamma_3 = max_gamma_3

        self._gamma_1 = gamma_1
        self._gamma_2 = gamma_2
        self._gamma_3 = gamma_3

        self._precompute_necessary_values()

    def _precompute_necessary_values(self):
        pass

    def compute_g_max(self):
        """
            In detail pretty complicated, but in general it computes four things and then adds them up:
            0.) A value, s.t. this value is to a very high likelihood bigger than the maximum value of a correct solution
            1.) A value s.t. this value is greater than the max constraint 1 violation value
            2.) A value s.t. this value is greater than the max constraint 2 violation value
            3.) A value s.t. this value is greater than the max constraint 3 violation value

        """
        return 0

    def compute_g_min(self):
        """
            As trips >= 0, penalties >= 0 and fees >= 0; it must be 0
        """
        return 0


    def compute_psi_1(self, maximum_trip_length):
        return 0

    def compute_psi_2(self, number_of_trips):
        return 0

    def compute_psi_3(self, collected_prize):
        return 0


    def compute_fitness(self, solution):
        """
            Given a solution it computes the fitness value, basically according to the following function:
            f(i) = g_{max} - [(g(i) + g_{min}) + \gamma_1 \Psi_1(i) + \gamma_2 \Psi_2(i) + \gamma_3 \Psi_3(i)]

            Where
        """
        return 0




