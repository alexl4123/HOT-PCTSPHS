
import logging
import time
import random

from framework.constants import logger_name
from framework.result import Result
from framework.distance_measure import Distance_Measure

from construction_heuristics.combination_of_heuristics import Combination_Of_Heuristics
from search_algorithms.algorithm import Algorithm
from search_algorithms.ga.ga_solution import GA_Solution
from search_algorithms.ga.fitness_function import Fitness_Function

from search_algorithms.ga.tournament_selection import Tournament_Selection
from search_algorithms.ga.ox_crossover import OX_Crossover

from search_algorithms.ga.local_search_ga import Local_Search_GA, Step_Function_Type
from search_algorithms.ga.vnd_ga import Vnd_GA

from search_algorithms.ga.saw_policy import SAW_Policy
from search_algorithms.ga.constant_weights import Constant_Weights

from search_algorithms.ga.ga_initialization_procedure.construction_builder import Construction_Builder

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

    def __init__(self, instance, random_k):
        self._instance = instance
        
        self._fitness_function = None

        self._random_k = random_k

        self._alpha = 1
        self._beta = -0.5
        self._gamma = -0.5
        self._delta = 0.5

        self.globally_best = None

    def set_alpha_beta_gamma_delta(self, alpha, beta, gamma, delta):
        self._alpha = alpha
        self._beta = beta
        self._gamma = gamma
        self._delta = delta


    def start_search(self, init_solution, step_function_type, neighborhoods, max_runtime, termination_criterion=3, starting_time = None, output = True, population_size = 10, tournament_k = 3, percentage_replaced = 0.5, saw_policy = Constant_Weights(1,1,1), compute_distance_analysis = False):

        additional_params = {}

        # Population Size
        # Which mutation parameters
        # k for 

        max_runtime = 90
        new_pop_size = population_size

        starting_time = time.time()

        fitness_function = saw_policy.create_appropriate_fitness_function(self._instance, termination_criterion)
        self._fitness_function = fitness_function

        cur_population = self.initialize_population(population_size, fitness_function)

        if compute_distance_analysis:
            dist_average_trace = [Distance_Measure.average_distance_of_population(cur_population)]
            dist_median_trace = [Distance_Measure.median_distance_of_population(cur_population)]
      
        for individual in cur_population:
            individual._fitness_function._precompute_necessary_values()
            val = individual.compute_fitness_value()

        for individual in cur_population:
            individual._fitness_function._precompute_necessary_values()
            val = individual.compute_fitness_value()
 
        cur_population = sorted(cur_population, key=lambda individual : individual.get_fitness_value(), reverse = True)
        trace = [cur_population[0].get_objective_value()]
        fitness_trace = [cur_population[0].get_fitness_value()]



        self.neighborhood_position = 0

        counter = 0
        while counter < termination_criterion:
            if output:
                print(f"--> Iter:{counter}/{termination_criterion}")

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

            st_sel = time.time()
            selected_population = self.selection(cur_population, new_pop_size, tournament_k)
            et_sel = time.time()

            st_cx = time.time()
            cx_population = self.crossover(selected_population)
            et_cx = time.time()

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

            st_mut = time.time()
            mut_population = self.mutation(cx_population, neighborhoods)
            mut_population_2 = self.mutation(selected_population, neighborhoods)

            self.neighborhood_position += 1
            if self.neighborhood_position >= len(neighborhoods):
                self.neighborhood_position = 0
            et_mut = time.time()


            st_repl = time.time()
            cur_population = self.replacement(cur_population, mut_population, mut_population_2, new_pop_size, percentage_replaced, counter)
            et_repl = time.time()

            if output:
                print(f"Timing-analysis:<selection:{et_sel - st_sel}s>;<cx:{et_cx - st_cx}s>;<mut:{et_mut - st_mut}s -- Mut-Name:{neighborhoods[self.neighborhood_position]}>;<repl:{st_repl - et_repl}s>")

            saw_policy.update_weights(counter, cur_population)

            trace.append(cur_population[0].get_objective_value())
            fitness_trace.append(cur_population[0].get_fitness_value())

        
            if compute_distance_analysis:
                dist_average_trace.append(Distance_Measure.average_distance_of_population(cur_population))
                dist_median_trace.append(Distance_Measure.median_distance_of_population(cur_population))


            counter += 1

        """
        print("<<<<<<<<<<<<")
        print("FIN")
        for individual in cur_population:
            print("-->INDIVIDUAL:")
            print(individual.to_string())
            print(individual.get_fitness_value())
            print("--<")
        print(">>>>>>>>>>>")
        """




        duration = time.time() - starting_time
        """
        if duration > max_runtime:
            logger.info("Runtime limit reached, actual runtime: " + str(max_runtime))

            duration = max_runtime
        """

        found_solution = None
        if self.globally_best:
            found_solution = self.globally_best
        else:
            found_solution = population[0]

        if compute_distance_analysis:
            print(dist_average_trace)
            print(dist_median_trace)

        return Result(found_solution, fitness_trace, duration, additional_params = additional_params)

    def initialize_population(self, population_size, fitness_function):
        initial_population = []
            

        #randomized_procedure = Greedy_Nearest_Neighbor_Initialization(self._instance, fitness_function = fitness_function)
        #randomized_procedure = Combination_Of_Heuristics(self._instance)

        randomized_procedure = Construction_Builder(self._instance, fitness_function = fitness_function, alpha = self._alpha, beta = self._beta, gamma = self._gamma, delta = self._delta)

        iteration = 0
        while len(initial_population) < population_size:
            result = randomized_procedure.create_solution(iteration, random_k = self._random_k, show_output = False, max_runtime = 600)
            if result.get_best_solution():
                ga_solution = GA_Solution.from_solution(result.get_best_solution(), fitness_function = fitness_function)

                initial_population.append(ga_solution)

            iteration += 1

        return initial_population


    def selection(self, population, new_pop_size, k):

        new = Tournament_Selection.perform_selection(population, n = len(population), k = k)
        return new

    def crossover(self, population):

        new_population = OX_Crossover.perform_crossover(population, self._fitness_function)

        return new_population

    def mutation(self, population, neighborhoods):

        neighborhood_structure = neighborhoods[self.neighborhood_position]

        instance = population[0]._instance

        neighborhood = neighborhood_structure(instance)
        neighborhood.set_solution(population[0])
        #print(f"<<Neighborhood-possible-pos:{neighborhood.get_number_possible_solutions()}>>")

        for solution in population:
            neighborhood = neighborhood_structure(instance)
            neighborhood.set_solution(solution)

            # Inefficient, but does the job
            upper = neighborhood.get_number_possible_solutions() - 1

            sol = solution
            if upper > 0:
                k = random.randint(0, upper)
               
                new_worthiness = neighborhood.get_specific_solution(k)

                solution.change_from_delta(new_worthiness.get_delta())
                solution.compute_fitness_value()
        return population

    def replacement(self, cur_population, mut_population, mut_population_2, new_length, percentage_replaced, counter):
        """
            percentage_replaced in [0,1]
        """

        for individual in cur_population:
            individual.update_values_from_slow_calculation()
            individual.compute_fitness_value()
        for individual in mut_population:
            individual.update_values_from_slow_calculation()
            individual.compute_fitness_value()
        for individual in mut_population_2:
            individual.update_values_from_slow_calculation()
            individual.compute_fitness_value()

        cur_population = sorted(cur_population, key=lambda individual : individual.get_fitness_value(), reverse = True)
        mut_population = sorted(mut_population, key=lambda individual : individual.get_fitness_value(), reverse = True)
        mut_population_2 = sorted(mut_population_2, key=lambda individual : individual.get_fitness_value(), reverse = True)

        locally_searched = None

        if counter % 45 == 0:
            locally_searched = self.subsequent_vnd([cur_population[0]])[0]
        elif counter % 45 == 15:
            locally_searched = self.subsequent_vnd([mut_population[0]])[0]
        elif counter % 45 == 30:
            locally_searched = self.subsequent_vnd([mut_population_2[0]])[0]

        if locally_searched:
            locally_searched.update_values_from_slow_calculation()
            locally_searched.compute_fitness_value(output=False)
            if not self.globally_best or locally_searched.get_fitness_value() > self.globally_best.get_fitness_value():
                self.globally_best = locally_searched.clone()

        old_pop_size = int((1 - percentage_replaced) * new_length)
        new_pop_size = int(percentage_replaced * new_length / 2)
        new_pop_size_2 = int(percentage_replaced * new_length / 2)

        if old_pop_size + new_pop_size + new_pop_size_2 < new_length:
            new_pop_size_2 = new_length - old_pop_size - new_pop_size

        new_population = []

        for i in range(old_pop_size):
            new_population.append(cur_population[i])

        for i in range(new_pop_size):
            new_population.append(mut_population[i])

        for i in range(new_pop_size_2):
            new_population.append(mut_population_2[i])
        
        return new_population

    def subsequent_vnd(self, population):

        new_pop = []

        for ga_solution in population:

            instance = ga_solution._instance

            neighborhoods = [Interchange_Customers(instance),Insert_Customer(instance), Trip_2_Opt(instance), Swap_Served_Unserved_Customer(instance), Remove_Customer(instance), Add_Customer(instance), Exchange_Hotel(instance), Move_Hotel(instance), Add_Hotel(instance), Move_Hotel(instance), Remove_Hotel(instance)]

            vnd = Vnd_GA(instance, 0)
            result = vnd.start_search(ga_solution, Step_Function_Type.FIRST, neighborhoods, 90, output = False)

            new_pop.append(result.get_best_solution())

        return new_pop
