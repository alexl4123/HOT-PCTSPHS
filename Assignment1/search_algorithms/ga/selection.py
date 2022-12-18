

class Selection:

    @classmethod
    def perform_selection(cls, population):
        """
            population must be an iterable data structure with solution (or subtypes of it) elements
        """
        new_population = []

        for pop in population:
            new_population.append(pop.clone())

        return new_population


