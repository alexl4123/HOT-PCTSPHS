"""
The following is the file, where the instance is stored (and also the datastructure for the instnace).
The datastructure is a typical object-oriented one, although it consumes more space than an array one, it is easier to handle and therefore chosen.

"""
import logging

import networkx as nx
import matplotlib.pyplot as plt
import collections


from constants import logger_name

logger = logging.getLogger(logger_name)

class Vertex:

    def __init__(self, id):
        self._id = id

    def get_id(self):
        return self._id

class Hotel(Vertex):

    def __init__(self, id, fee):
        super().__init__(id)
        self._fee = fee

    def get_fee(self):
        return self._fee

class Customer(Vertex):
        
    def __init__(self, id, prize, penalty):
        super().__init__(id)
        self._prize = prize
        self._penalty = penalty

    def get_prize(self):
        return self._prize

    def get_penalty(self):
        return self._penalty

class Edge:

    def __init__(self, vertex_a, vertex_b, weight):
        self._vertex_a = vertex_a
        self._vertex_b = vertex_b
        self._weight = weight

    def get_vertex_a(self):
        return self._vertex_a

    def get_vertex_b(self):
        return self._vertex_b

    def get_weight(self):
        return self._weight

class Instance:

    def __init__(self, c1_L, c2_D, c3_P):
        self._hotels = {}
        self._hotels_list = []

        self._customers = {}
        self._customers_list = []

        self._edges = {}
        self._edges_list = []

        self._hotel_max_index = 0
        self._customer_max_index = 0
        self._edges_max_index = 0

        self._C1_L = c1_L
        self._C2_D = c2_D
        self._C3_P = c3_P

        self._graph = nx.Graph()

        self._edge_lookup = {}

        self._nearest_neighbors = {}
        self._nearest_hotels = {}
        self._nearest_customers = {}
        
    def add_hotel(self, fee):

        if self._customers or self._edges:
            logger.error("Hotel can only be added, when there are no customers and no edges, i.e. can only be called during setup!")
            quit()

        new_hotel_index = self._hotel_max_index
    
        hotel = Hotel(new_hotel_index, fee)

        self._edge_lookup[hotel.get_id()] = {}
        self._edge_lookup[hotel.get_id()][hotel.get_id()] = Edge(hotel, hotel, 0)

        self._hotels[new_hotel_index] = hotel
        self._hotels_list.append(hotel)
        self._graph.add_node(new_hotel_index)

        self._hotel_max_index = new_hotel_index + 1

    def add_customer(self, prize, penalty):
        if self._edges or not self._hotels:
            logger.error("Customer can only be added, when there are hotels and no edges, i.e. can only be called during setup!")
            quit()

        new_max_customer_index = self._customer_max_index

        new_customer_index = new_max_customer_index + self._hotel_max_index
        
        customer = Customer(new_customer_index, prize, penalty)

        self._edge_lookup[customer.get_id()] = {}

        self._customers[new_customer_index] = customer
        self._customers_list.append(customer)
        self._graph.add_node(new_customer_index)

        self._customer_max_index = new_max_customer_index + 1

    def add_edge(self, vertex_a_index, vertex_b_index, weight):

        if not self._hotels or not self._customers:
            logger.error("Edge can only be added, when there are hotels and customers already existent.")
            quit()

        if vertex_a_index < self._hotel_max_index:
            vertex_a_obj = self.get_hotel_per_index(vertex_a_index)
        else:
            vertex_a_obj = self.get_customer_per_index(vertex_a_index)

        if vertex_b_index < self._hotel_max_index:
            vertex_b_obj = self.get_hotel_per_index(vertex_b_index)
        else:
            vertex_b_obj = self.get_customer_per_index(vertex_b_index)

        edge = Edge(vertex_a_obj, vertex_b_obj, weight)

        new_max_edges_index = self._edges_max_index

        self._edge_lookup[vertex_a_obj.get_id()][vertex_b_obj.get_id()] = edge
        self._edge_lookup[vertex_b_obj.get_id()][vertex_a_obj.get_id()] = edge

        self._edges[new_max_edges_index] = edge
        self._edges_list.append(edge)
        self._graph.add_edge(vertex_a_obj.get_id(), vertex_b_obj.get_id(), weight = weight)

        self._edges_max_index = new_max_edges_index + 1


    def get_number_of_hotels(self):
        return self._hotel_max_index + 1

    def get_number_of_customers(self):
        return self._customer_max_index + 1

    def get_hotel_per_index(self, index):
        return self._hotels[index]

    def get_customer_per_index(self, index):
        return self._customers[index]

    def get_list_of_hotels(self):
        return self._hotels_list 

    def get_list_of_customers(self):
        return self._customers_list

    def get_list_of_edges(self):
        return self._edges_list
       
    def draw_show_graph(self):
        self._draw_graph()
        plt.show()

    def draw_save_graph(self, path='graph.jpg'):
        self._draw_graph()
        plt.savefig(path)


    def _draw_graph(self):
        pos = nx.spring_layout(self._graph)
        nx.draw(self._graph, pos, with_labels=True)   
        weights = nx.get_edge_attributes(self._graph, 'weight')
        nx.draw_networkx_edge_labels(self._graph, pos, edge_labels=weights)


    def precompute_all_nearest_neighbors(self, debug = False):

        nearest_neighbors = {}
        nearest_hotels = {}
        nearest_customers = {}

        for key in self._edge_lookup.keys():
            ds = self._edge_lookup[key]

            obj = self._get_object_from_index(key)
            
            sorted_by_value = sorted(ds.items(), key=lambda item: item[1].get_weight())

            nearest = []
            nc_c = []
            nc_h = []

            for (key_2,edge) in sorted_by_value:
                
                obj_2 = self._get_object_from_index(key_2)

                nearest.append(obj_2)

                if self._index_is_hotel(key_2):
                    nc_h.append(obj_2)
                else:
                    nc_c.append(obj_2)

        self._nearest_neighbors = nearest_neighbors
        self._nearest_hotels = nearest_hotels
        self._nearest_customers = nearest_customers

    def get_distance(self, vertex_a, vertex_b):
        """
        Precondition: precompute_all_pairs_shortest_paths must be called first.
        """

        return (self._edge_lookup[vertex_a.get_id()][vertex_b.get_id()]).get_weight()

        """
        if self._index_is_hotel(vertex_b.get_id()):
            return self._dist_hotels[vertex_a.get_id()][vertex_b.get_id()]
        else:
            return self._dist_customers[vertex_a.get_id()][vertex_b.get_id()]
        """

    def get_nearest_customer(self, vertex_a, position = 0):
        """
        Precondition: precompute_all_pairs_shortest_paths must be called first.
        """

        nearest_id = self._nearest_customers[vertex_a.get_id()][position]
        return self.get_customer_per_index(nearest_id)

    def get_nearest_hotel(self, vertex_a, position = 0):
        """
        Precondition: precompute_all_pairs_shortest_paths must be called first.
        """

        nearest_id = self._nearest_hotels[vertex_a.get_id()][position]
        return self.get_hotel_per_index(nearest_id)

    def obj_is_hotel(self, obj):
        index = obj.get_id()
        return self._index_is_hotel(index)

    def _index_is_hotel(self, index):
        if index < self._hotel_max_index:
            return True
        else:
            return False

    def _get_object_from_index(self, index):
        if self._index_is_hotel(index):
            return self.get_hotel_per_index(index)
        else:
            return self.get_customer_per_index(index)

