
import logging
import time
import random

from framework.constants import logger_name
from framework.result import Result

from construction_heuristics.combination_of_heuristics import Combination_Of_Heuristics
from search_algorithms.algorithm import Algorithm
from search_algorithms.ga.ga_solution import GA_Solution
from search_algorithms.ga.fitness_function import Fitness_Function

from search_algorithms.ga.tournament_selection import Tournament_Selection
from search_algorithms.ga.ox_crossover import OX_Crossover

from search_algorithms.ga.local_search_ga import Local_Search_GA, Step_Function_Type
from search_algorithms.ga.vnd_ga import Vnd_GA

from neighborhoods.neighborhood import Neighborhood
from neighborhoods.trip_2_opt import Trip_2_Opt
from neighborhoods.remove_customer import Remove_Customer
from neighborhoods.add_customer import Add_Customer
from neighborhoods.swap_served_unserved_customer import Swap_Served_Unserved_Customer
from neighborhoods.interchange_customers import Interchange_Customers
from neighborhoods.insert_customer import Insert_Customer
from neighborhoods.remove_hotel import Remove_Hotel
from neighborhoods.add_hotel import Add_Hotel
from neighborhoods.exchange_hotel import Exchange_Hotel
from neighborhoods.move_hotel import Move_Hotel


logger = logging.getLogger(logger_name)

class Genetic_Algorithm(Algorithm):

    def __init__(self, instance):
        self._instance = instance
        
        self._fitness_function = None

        self._random_k = 5


    def start_search(self, init_solution, step_function_type, neighborhoods, max_runtime, termination_criterion=3, starting_time = None, output = True):

        additional_params = {}

        max_runtime = 90
        population_size = 7
        new_pop_size = population_size
        k = 1
        termination_criterion = 10

        starting_time = time.time()

        cur_population = self.initialize_population(population_size)



        cur_population = sorted(cur_population, key=lambda individual : individual.get_fitness_value(), reverse = True)
        trace = [cur_population[0].get_objective_value()]

        counter = 0
        while counter < termination_criterion:
            """
            print("<<<<<<<<<<<<")
            print("COUNTER: " + str(counter))
            for individual in cur_population:
                print("-->INDIVIDUAL:")
                print(individual.to_string())
                print(individual.get_fitness_value())
                print("--<")
            print(">>>>>>>>>>>")
            """

            selected_population = self.selection(cur_population, new_pop_size, k)

            cx_population = self.crossover(selected_population)

            """
            print("<<<<<<<<<<<<")
            print("CX")
            for individual in cx_population:
                print("-->INDIVIDUAL:")
                print(individual.to_string())
                print(individual.get_fitness_value())
                print("--<")
            print(">>>>>>>>>>>")
            """

            mut_population = self.mutation(cx_population)

            mut_population = self.local_search_test(mut_population)

            cur_population = self.replacement(cur_population, mut_population, new_pop_size)

            trace.append(cur_population[0].get_objective_value())

            counter += 1

        print("<<<<<<<<<<<<")
        print("FIN")
        for individual in cur_population:
            print("-->INDIVIDUAL:")
            print(individual.to_string())
            print(individual.get_fitness_value())
            print("--<")
        print(">>>>>>>>>>>")

        solution = cur_population[0]


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

        self._fitness_function = initial_population[0]._fitness_function

        return initial_population


    def selection(self, population, new_pop_size, k):

        new = Tournament_Selection.perform_selection(population, n = len(population), k = k)
        return new

    def crossover(self, population):

        new_population = OX_Crossover.perform_crossover(population, self._fitness_function)

        return new_population

    def mutation(self, population):

        instance = population[0]._instance


        for solution in population:
            neighborhood = Trip_2_Opt(instance)
            neighborhood.set_solution(solution)

            # Inefficient, but does the job
            upper = neighborhood.get_number_possible_solutions() - 1

            sol = solution
            if upper > 0:
                k = random.randint(0, upper)
                for i in range(0, k):
                    new_worthiness = neighborhood.next_solution()

                if k == 0 and neighborhood.get_number_possible_solutions() > 0:
                    new_worthiness = neighborhood.next_solution()

                solution.change_from_delta(new_worthiness.get_delta())
                solution.compute_fitness_value()

        return population

    def replacement(self, cur_population, mut_population, new_length):

        cur_population = sorted(cur_population, key=lambda individual : individual.get_fitness_value(), reverse = True)
        mut_population = sorted(mut_population, key=lambda individual : individual.get_fitness_value(), reverse = True)

        new_population = []

        for i in range(new_length):
            index = int(i / 2)
            if i % 2 == 0:
                new_population.append(cur_population[index])
            else:
                new_population.append(mut_population[index])

        return new_population

    def local_search_test(self, population):

        new_pop = []

        for ga_solution in population:

            instance = ga_solution._instance

            """
            local_search = Local_Search_GA(instance, 0)
            neighborhoods = [Trip_2_Opt(instance)]
            local_search.start_search(ga_solution, Step_Function_Type.FIRST, neighborhoods, 90)
            """

            neighborhoods = [Interchange_Customers(instance),Insert_Customer(instance), Trip_2_Opt(instance), Swap_Served_Unserved_Customer(instance), Remove_Customer(instance), Add_Customer(instance), Exchange_Hotel(instance), Move_Hotel(instance), Remove_Hotel(instance), Add_Hotel(instance)]

            vnd = Vnd_GA(instance, 0)
            result = vnd.start_search(ga_solution, Step_Function_Type.FIRST, neighborhoods, 90, output = False)

            new_pop.append(result.get_best_solution())

        return new_pop
