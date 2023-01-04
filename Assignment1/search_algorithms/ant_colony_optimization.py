
import logging
import time
import random

import numpy as np

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

class Ant_Colony_Optimization(Algorithm):

    def __init__(self, instance, random_k):
        self._instance = instance
        
        self._fitness_function = None

        self._random_k = random_k

    def start_search(self, init_solution, step_function_type, neighborhoods, max_runtime, termination_criterion=3, starting_time = None, output = True, population_size = 10, saw_policy = Constant_Weights(1,1,1), compute_distance_analysis = False, alpha = 1, beta = 1, rho = 0.02, p=0.5, min_max_ant_system = True, local_information = "objective_value"):

        mmas = min_max_ant_system

        #print("START ACO")
        additional_params = {}

        trace = []
        start_time = time.time()


        if local_information == "distance":

            hotels_list = self._instance.get_list_of_hotels()
            customers_list = self._instance.get_list_of_customers()

            hotels_list.sort(key = lambda h:h.get_id())
            customers_list.sort(key = lambda c:c.get_id())

            total_list = hotels_list + customers_list

            nested_distance_array = []
            
            for index_0 in range(len(total_list)):

                nested_distance_array.append([])
        
                for index_1 in range(len(total_list)):

                    obj_0 = total_list[index_0]
                    obj_1 = total_list[index_1]

                    dist = self._instance.get_distance(obj_0, obj_1)

                    nested_distance_array[index_0].append(dist)

            np_distance_array = np.array(nested_distance_array)
        elif local_information == "objective_value":

            hotels_list = self._instance.get_list_of_hotels()
            customers_list = self._instance.get_list_of_customers()

            hotels_list.sort(key = lambda h:h.get_id())
            customers_list.sort(key = lambda c:c.get_id())

            total_list = hotels_list + customers_list

            nested_distance_array = []
            
            for index_0 in range(len(total_list)):

                nested_distance_array.append([])
        
                for index_1 in range(len(total_list)):

                    obj_0 = total_list[index_0]
                    obj_1 = total_list[index_1]

                    dist = self._instance.get_distance(obj_0, obj_1)
                    if self._instance.obj_is_hotel(obj_1):
                        _p = obj_1.get_fee()
                    else:
                        _p = (-1) * obj_1.get_penalty()

                    nested_distance_array[index_0].append(dist + _p)

            np_distance_array = np.array(nested_distance_array)

            min_val = np.amin(np_distance_array)


            if min_val < 0:
                np_distance_array = np_distance_array - min_val + 1


            np.fill_diagonal(np_distance_array, 0)
            
        else:
            print("local_information " + str(local_information) + " not supported by ACO-algorithm!")
            quit()


        dimensions = len(total_list)
        max_tour_length = 4 * dimensions

        np_distance_array[np_distance_array == 0] = -1
        eta = (1 / np_distance_array)
        eta[eta == -1] = 0

        fitness_function = saw_policy.create_appropriate_fitness_function(self._instance, termination_criterion)

        # Min-Max-Ants

        t_max = 10 * (1 / (rho)) * (fitness_function.g_max)
        t_min = (t_max * (1 - (p ** (1/max_tour_length)))) / (((max_tour_length / 2) - 1) * (p ** (1/max_tour_length)))

        t_med = (t_max + t_min) / 2


        best_solution = None        
        best_feasible_solution = None

        
        #local_inf_mat_2 = np.sum(local_inf_mat)
        #print(local_inf_mat_2)

        tau = (np.ones(eta.shape)) + t_med

        new_time = time.time()

        counter = 0
        while counter < termination_criterion:
            #print(f">>>COUNTER:{counter}/{termination_criterion}")
            #old_time = new_time
            #new_time = time.time()
            #print(f">>>Last-Iter-Time:{new_time - old_time}")

            table = np.ones((population_size, max_tour_length)).astype(np.int)  
            table = (-1) * table


            prob_matrix = (tau ** alpha) * (eta ** beta)  # Calc general prob.-matrix
            # Evaluate each ant (O(pop * n))
            for j in range(population_size):  # For each ant
                table[j, 0] = 0  #
                allow_list = list(set(range(dimensions)))
                for k in range(max_tour_length - 3):  # Construct a path

                    g = table[j, k]

                    prob = prob_matrix[g, allow_list]
                    prob = prob / prob.sum()  
                    next_point = np.random.choice(allow_list, size=1, p=prob)[0]
                    table[j, k + 1] = next_point
          
                    if not self._instance._index_is_hotel(next_point):
                        allow_list = list(set(allow_list) - set([next_point]))

                    if next_point == 0:
                        break

                if (k == max_tour_length - 3 or k == max_tour_length - 4) and (table[j,k] != 0):
                    # Complete the tour, if the random procedure didn't find it
                    table[j,k+1] = 0

            list_representations = []
            for j in range(population_size):
                list_representations.append([])
                row = table[j,:]
                for k in range(len(row)):
                    if table[j,k] != -1:
                        val = int(table[j,k])
                        obj = self._instance._get_object_from_index(val)
                        list_representations[j].append(obj)
                    else:
                        break

            """
            print("-------------------")
            print(f"ITER:{counter}")
            print(table)
            """

            population = []
            for lst in list_representations:
                sol = GA_Solution(self._instance, fitness_function)
                sol.from_pure_list_representation_to_internal(lst)
                sol.update_values_from_slow_calculation()
                sol.compute_fitness_value()
                population.append(sol)
    
                """
                print(sol.to_string())
                print(sol.get_fitness_value())
                print(sol.get_objective_value())
                print(sol.is_c1_satisfied())
                print(sol.is_c2_satisfied())
                print(sol.is_c3_satisfied())
                """

            #print("-------------------")
            cur_best = None
            cur_best_j = 0


            counter_2 = 0
            for individual in population:
                if not best_solution:
                    best_solution = individual.clone()
                elif individual.get_fitness_value() > best_solution.get_fitness_value():
                    best_solution = individual.clone()

                if not cur_best:
                    cur_best = individual.clone()
                    cur_best_j = counter_2
                elif individual.get_fitness_value() > cur_best.get_fitness_value():
                    cur_best = individual.clone()
                    cur_best_j = counter_2

                counter_2 += 1
       
            if counter % 15 == 0:
                searched = self.subsequent_vnd([cur_best])
                if len(searched) > 0 and (not best_solution or searched[0].get_fitness_value() > best_solution.get_fitness_value()):
                    #print("SET VND BEST!")
                    best_solution = searched[0].clone()


                if len(searched) > 0 and (not best_feasible_solution or searched[0].get_fitness_value() < best_feasible_solution.get_objective_value()):
                    if searched[0].is_c1_satisfied() and  searched[0].is_c2_satisfied() and  searched[0].is_c3_satisfied():
                        best_feasible_solution = searched[0].clone()

            trace.append(cur_best.get_fitness_value())
            counter += 1

            if mmas:
                delta_tau = np.zeros((dimensions, dimensions))

                for j in range(population_size):  
                    individual_lst = list_representations[j]
                    individual = population[j]

                    for k in range(len(individual_lst)):  
                        if k >= max_tour_length - 1:
                            # Catch possible out of bounds
                            continue

                        n1, n2 = table[j, k], table[j, k + 1]  
                        delta_tau[n1, n2] += individual.get_fitness_value()
            
                        if j == cur_best_j:
                            delta_tau[n1, n2] += 2 * individual.get_fitness_value()
    

                tau = (1 - rho) * tau + delta_tau

                tau[tau < t_min] = t_min
                tau[tau > t_max] = t_max

            elif not mmas:
                delta_tau = np.zeros((dimensions, dimensions))
                for j in range(population_size):  
                    individual_lst = list_representations[j]
                    individual = population[j]

                    for k in range(len(individual_lst)):  
                        n1, n2 = table[j, k], table[j, k + 1]  
                        delta_tau[n1, n2] += individual.get_fitness_value()

                tau = (1 - rho) * tau + delta_tau

        """
        print("<<<<<<<<<<<<<<>>>>>>>>>>>>>>>")
        print("<<<<<<<<<<<<<<>>>>>>>>>>>>>>>")
        print("<<<<<<<<<<<<<<>>>>>>>>>>>>>>>")
        print(best_solution.to_string())
        print(best_solution.get_fitness_value())
        print(best_solution.get_objective_value())
        print(best_solution.is_c1_satisfied())
        print(best_solution.is_c2_satisfied())
        print(best_solution.is_c3_satisfied())
        """

        duration = time.time() - start_time

        print("<<>><<>>")
        print("<<>><<>>")
        print("<<>><<>>")
        print("BEST-FEASIBLE-SOLUTiON:")
        if best_feasible_solution:
            print(best_feasible_solution.get_objective_value())
            print(best_feasible_solution.get_fitness_value())
        else:
            print("NONE")
        print("<<>><<>>")
        print("<<>><<>>")
        print("<<>><<>>")


        return Result(best_solution, trace, duration, additional_params = additional_params)



    def subsequent_vnd(self, population):

        new_pop = []

        for aco_solution in population:

            instance = aco_solution._instance


            neighborhoods = [Interchange_Customers(instance),Insert_Customer(instance), Trip_2_Opt(instance), Swap_Served_Unserved_Customer(instance), Remove_Customer(instance), Add_Customer(instance), Exchange_Hotel(instance), Move_Hotel(instance), Add_Hotel(instance), Move_Hotel(instance), Remove_Hotel(instance)]

            vnd = Vnd_GA(instance, 0)
            result = vnd.start_search(aco_solution.clone(), Step_Function_Type.FIRST, neighborhoods, 90, output = False)

            new_pop.append(result.get_best_solution())

        return new_pop
        



     

