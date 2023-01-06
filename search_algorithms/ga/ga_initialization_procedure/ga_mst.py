import logging
import time
import random

import networkx as nx
#from networkx.algorithms.approximation import travelling_salesman_problem, christofides
#import networkx.approximation as naa

from framework.result import Result
from framework.instance import Edge
from framework.solution import Delta, Add, Remove, Reverse
from search_algorithms.ga.ga_initialization_procedure.initialization_procedure import GA_Initialization_Procedure
from search_algorithms.ga.ga_solution import GA_Solution
from framework.constants import logger_name

class GA_MST(GA_Initialization_Procedure):

    def __init__(self, instance, alpha=1, beta=-0.5, gamma=-0.5, delta=0.5, fitness_function = None):
        super().__init__(instance, alpha = alpha, beta = beta, gamma = gamma, delta = delta, fitness_function = fitness_function)


    def create_solution(self, random_k=0, show_output=True, max_runtime = 90):

        nodes_under_consideration = self.select_nodes_under_consideration()

        start_time = time.time()

        mst_edges = []

        edges = self._instance.get_list_of_edges()

        tmp_edges = []

        for edge in edges:

            if not self._instance.obj_is_hotel(edge.get_vertex_a()) and not self._instance.obj_is_hotel(edge.get_vertex_b()):
                tmp_edges.append(edge)
            elif edge.get_vertex_a().get_id() == 0 and not self._instance.obj_is_hotel(edge.get_vertex_b()):
                tmp_edges.append(edge)
            elif edge.get_vertex_b().get_id() == 0 and not self._instance.obj_is_hotel(edge.get_vertex_a()):
                tmp_edges.append(edge)


        edges = tmp_edges
        edges.sort(key=lambda e: e.get_weight())
        
        tmp_edges = []

        for edge in edges:
            factor = random.uniform(0.5,2)
            new_weight = int(factor * edge.get_weight()) + 1
            tmp_edges.append(Edge(edge.get_vertex_a(), edge.get_vertex_b(), new_weight))

        edges = tmp_edges

        G = nx.Graph()

        for edge in edges:  
            G.add_edge(edge.get_vertex_a().get_id(), edge.get_vertex_b().get_id(), weight=edge.get_weight())
            G.add_edge(edge.get_vertex_b().get_id(), edge.get_vertex_a().get_id(), weight=edge.get_weight())

        #sol = naa.traveling_salesman_problem(G,cycle = False, method=naa.christofides)
        sol = nx.approximation.traveling_salesman_problem(G,cycle = False, method=nx.approximation.christofides)

        trip = []
        already_used = {}

        index_of_hotel = 0

        for vertex_id in sol:
            if vertex_id == 0:
                break
            else:
                index_of_hotel += 1

        for index in range(index_of_hotel + 1, len(sol)):
            vertex_id = sol[index]

            if vertex_id in already_used or vertex_id == 0:
                continue
    
            already_used[vertex_id] = True

            obj = self._instance._get_object_from_index(vertex_id) 
            trip.append(obj)

        for index in range(0, index_of_hotel):
            vertex_id = sol[index]

            if vertex_id in already_used or vertex_id == 0:
                continue
    
            already_used[vertex_id] = True

            obj = self._instance._get_object_from_index(vertex_id) 
            trip.append(obj)

        solution = GA_Solution(self._instance, fitness_function = self._fitness_function)
        solution._trips.pop(0)
        solution._trips.append(trip)

        #print(sol)
        #print(solution.to_string())

        solution.update_values_from_slow_calculation()
        solution.compute_fitness_value()

        duration = time.time() - start_time

        return Result(solution, [solution.get_fitness_value()], duration)

    def select_nodes_under_consideration(self):

        return self._instance.get_list_of_customers()


