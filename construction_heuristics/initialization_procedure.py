import random
import numpy as np

from framework.solution import Solution

class Initialization_Procedure:

    def __init__(self, instance, alpha=1, beta=-0.5, gamma=-0.5, delta=0.5):
        self._instance = instance

        self._nearest_neighbors = {}
        self._nearest_hotels = {}
        self._nearest_customers = {}

        self._alpha = alpha
        self._beta = beta
        self._gamma = gamma
        self._delta_param = delta

        self.precompute_all_nearest_neighbors(alpha = alpha, beta = beta, gamma = gamma, delta = delta)

    def create_solution(self):
        return Solution(self._instance)


    def _ordering_function(self, edge, obj, alpha=1, beta=-0.5, gamma=-0.5, delta=0.5):
        """
        Used for ''ordering'', i.e. used to compute the ''nearest-neighbors''.
        alpha: Parameter for setting the influence of the ''distance''
        beta: Parameter for setting the influence of the prize of a customer
        gamma: Parameter for setting the influence of the penalty of a customer
        delta: Parameter for setting the influence of the fee of a hotel

        """
        term_1 = alpha * edge[1].get_weight()

        obj_1 = edge[1].get_vertex_a()
        obj_2 = edge[1].get_vertex_b()

        other_obj = None
        if obj == obj_1:
            other_obj = obj_2
        else:
            other_obj = obj_1

        if self._instance.obj_is_hotel(other_obj):
            term_2 = delta * other_obj.get_fee()
        else:
            term_2 = beta * other_obj.get_prize() + gamma * other_obj.get_penalty()


        return term_1 + term_2

    def precompute_all_nearest_neighbors(self, debug=False, alpha = 1, beta = -0.5, gamma = -0.5, delta = 0.5):

        nearest_neighbors = {}
        nearest_hotels = {}
        nearest_customers = {}


        for key in self._instance._edge_lookup.keys():

            ds = self._instance._edge_lookup[key]

            obj = self._instance._get_object_from_index(key)

            sorted_by_value = sorted(ds.items(), key=lambda item: self._ordering_function(item, obj, alpha, beta, gamma, delta))

            nearest = []
            nc_c = []
            nc_h = []

            for (key_2, edge) in sorted_by_value:

                obj_2 = self._instance._get_object_from_index(key_2)

                nearest.append(obj_2)

                if self._instance._index_is_hotel(key_2):
                    nc_h.append(obj_2)
                else:
                    nc_c.append(obj_2)

            nearest_neighbors[key] = nearest
            nearest_hotels[key] = nc_h
            nearest_customers[key] = nc_c


        self._nearest_neighbors = nearest_neighbors
        self._nearest_hotels = nearest_hotels
        self._nearest_customers = nearest_customers


    def get_all_nearest_customers(self, vertex_a, random_k=0):
        if random_k == 0:
            return self._nearest_customers[vertex_a.get_id()]
        else:
            if random_k > len(self._nearest_customers[vertex_a.get_id()]):
                random_k = len(self._nearest_customers[vertex_a.get_id()])

            l = range(0, random_k)
            permuted = np.random.permutation(l)
            shuffled = []
            for i in range(len(l)):
                shuffled.append(self._nearest_customers[vertex_a.get_id()][permuted[i]])

            shuffled = shuffled + self._nearest_customers[vertex_a.get_id()][random_k:]
            return shuffled

    def get_nearest_customer(self, vertex_a, position=0):
        """
        Precondition: precompute_all_pairs_shortest_paths must be called first.
        """

        return self._nearest_customers[vertex_a.get_id()][position]

    def get_all_nearest_hotels(self, vertex_a):
        return self._nearest_hotels[vertex_a.get_id()]

    def get_nearest_hotel(self, vertex_a, position=0):
        """
        Precondition: precompute_all_pairs_shortest_paths must be called first.
        """

        return self._nearest_hotels[vertex_a.get_id()][position]


    def get_nearest_unserved_customer(self, location, k, solution):

        remaining = k
        nearest_list = []

        for nearest in self.get_all_nearest_customers(location):
            if not solution.is_customer_served(nearest) and self._instance.get_distance(location, nearest) > 0 and k == 0:
                return nearest
            elif not solution.is_customer_served(nearest) and self._instance.get_distance(location, nearest) > 0 and k > 0:
                remaining = remaining - 1
                nearest_list.append(nearest)

                if remaining < 0:
                    break

        picked_index = random.randint(0, len(nearest_list) - 1)

        return nearest_list[picked_index]

        logger.critical("Ran out of nearest unserved customers! May never happen!")
        quit()







