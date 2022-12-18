
from search_algorithms.ga.crossover import Crossover

class OX_Crossover(Crossover):

    @classmethod
    def perform_crossover(cls, population):



        first = population[0]

        list_rep = first.compute_pure_list_representation()
        print(first.to_string())
        string = ""
        for item in list_rep:
            string += str(item.get_id()) + " "
        print(string)

        first.from_pure_list_representation_to_internal(list_rep)
        print(first.to_string())






