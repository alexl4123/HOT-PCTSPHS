
import random
from search_algorithms.ga.selection import Selection

class Tournament_Selection(Selection):

    @classmethod
    def perform_selection(cls, population, n = None, k = 1):

        new_population = []

        if n == None:
            n = len(population)

        for i in range(n):

            sample = random.sample(population, k = k)

            best = None
            for individual in sample:
                if not best or individual.get_fitness_value() > best.get_fitness_value():
                    best = individual.clone()

            new_population.append(best)

        return new_population




