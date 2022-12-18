
import time


from framework.result import Result
from construction_heuristics.combination_of_heuristics import Combination_Of_Heuristics
from search_algorithms.algorithm import Algorithm
from search_algorithms.ga.ga_solution import GA_Solution
from search_algorithms.ga.fitness_function import Fitness_Function

from search_algorithms.ga.tournament_selection import Tournament_Selection
from search_algorithms.ga.ox_crossover import OX_Crossover

class Genetic_Algorithm(Algorithm):

    def __init__(self, instance):
        self._instance = instance

        self._random_k = 5


    def start_search(self, init_solution, step_function_type, neighborhoods, max_runtime, termination_criterion=3, starting_time = None, output = True):

        additional_params = {}

        population_size = 5
        new_pop_size = population_size
        k = 1
        termination_criterion = 1

        starting_time = time.time()

        cur_population = self.initialize_population(population_size)

        counter = 0
        while counter < termination_criterion:
            print("COUNTER: " + str(counter))

            selected_population = self.selection(cur_population, new_pop_size, k)

            cx_population = self.crossover(selected_population)

            mut_population = self.mutation(cx_population)

            self.replacement(cur_population, mut_population)



            counter += 1

        solution = cur_population[0]
        trace = [solution.get_objective_value()]


        duration = time.time() - starting_time
        if duration > max_runtime:
            logger.info("Runtime limit reached, actual runtime: " + max_runtime)

            duration = max_runtime


        return Result(solution, trace, duration, additional_params = additional_params)

    def initialize_population(self, population_size):
        initial_population = []

        randomized_procedure = Combination_Of_Heuristics(self._instance)
        while len(initial_population) < population_size:
            result = randomized_procedure.create_solution(random_k = self._random_k, show_output = False, max_runtime = 4)
            if result.get_best_solution():
                ga_solution = GA_Solution.from_solution(result.get_best_solution())

                initial_population.append(ga_solution)

        return initial_population


    def selection(self, population, new_pop_size, k):

        new = Tournament_Selection.perform_selection(population, n = len(population), k = k)
        return new

    def crossover(self, population):

        OX_Crossover.perform_crossover(population)

        # TODO -> Mockup
        return population

    def mutation(self, population):

        # TODO -> Mockup
        return population

    def replacement(self, cur_population, mut_population):

        # TODO -> Mockup
        pass










