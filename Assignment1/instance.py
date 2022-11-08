"""
The following is the file, where the instance is stored (and also the datastructure for the instnace).
The datastructure is a typical object-oriented one, although it consumes more space than an array one, it is easier to handle and therefore chosen.

"""
import logging

import networkx as nx
import matplotlib.pyplot as plt


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

        self._nearest_hotels = None
        self._nearest_customers = None
    
        self._dist_hotels = None
        self._dist_customers = None

        self._paths_hotels = None
        self._paths_customers = None


    def add_hotel(self, fee):

        if self._customers or self._edges:
            logger.error("Hotel can only be added, when there are no customers and no edges, i.e. can only be called during setup!")
            quit()

        new_hotel_index = self._hotel_max_index
    
        hotel = Hotel(new_hotel_index, fee)
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

    def precompute_all_pairs_shortest_paths(self, debug = False):
        """
        Computes all pairs shortest paths and further arranges the result in datastructures, such that there is a differentiation between hotels and customers.
        Further it precomputes all nearests neighbors.

        The runtime complexity should mainly be determined by the all_paris_dijkstra function, the rest runs in about O(n^2), where n is |V|, i.e. the amount of vertices.
        """

        # This line computes all pairs shortest paths
        shortest_path_dict = dict(nx.all_pairs_dijkstra(self._graph))

        nearest_hotels = {}
        nearest_customers = {}
        
        dist_hotels = {}
        dist_customers = {}

        paths_hotels = {}
        paths_customers = {}

        for index in shortest_path_dict.keys():
            (distances, paths) = shortest_path_dict[index]

            nearest_hotels[index] = []
            nearest_customers[index] = []

            dist_hotels[index] = {}
            dist_customers[index] = {}

            paths_hotels[index] = {}
            paths_customers[index] = {}

            for index_b in distances.keys():
                if index == index_b:
                    continue
                elif self._index_is_hotel(index_b):
                    nearest_hotels[index].append(index_b)
                    dist_hotels[index][index_b] = distances[index_b]
                    paths_hotels[index][index_b] = paths[index_b]

                else:
                    nearest_customers[index].append(index_b)
                    dist_customers[index][index_b] = distances[index_b]
                    paths_customers[index][index_b] = paths[index_b]

        
            if debug:
                if self._index_is_hotel(index):
                    print("We created DS for Hotel with index: " + str(index))
                else:
                    print("We created DS for Customer with index: " + str(index))
                     
                print(nearest_hotels[index])
                print(nearest_customers[index])

                print(dist_hotels[index])
                print(dist_customers[index])

                print(paths_hotels[index])
                print(paths_customers[index])

            
            # TODO sanity check -> can be removed if it works:
            for nearest_index in range(1, len(nearest_hotels[index]) - 1):
                nearest_index_1 = nearest_hotels[index][nearest_index]
                nearest_index_2 = nearest_hotels[index][nearest_index -1]

                if dist_hotels[index][nearest_index_2] > dist_hotels[index][nearest_index_1]:
                    print("ERROR - for index " + str(index) + " it holds that the nearest neighbors (HOTELS) are not sorted!")
                    quit()
            for nearest_index in range(1, len(nearest_customers[index]) - 1):
                nearest_index_1 = nearest_customers[index][nearest_index]
                nearest_index_2 = nearest_customers[index][nearest_index -1]

                if dist_customers[index][nearest_index_2] > dist_customers[index][nearest_index_1]:
                    print("ERROR - for index " + str(index) + " it holds that the nearest neighbors (CUSTOMERS) are not sorted!")
                    quit()   

            self._nearest_hotels = nearest_hotels
            self._nearest_customers = nearest_customers
        
            self._dist_hotels = dist_hotels
            self._dist_customers = dist_customers

            self._paths_hotels = paths_hotels
            self._paths_customers = paths_customers

    def get_distance(self, vertex_a, vertex_b):
        """
        Precondition: precompute_all_pairs_shortest_paths must be called first.
        """

        if self._index_is_hotel(vertex_b.get_id()):
            return self._dist_hotels[vertex_a.get_id()][vertex_b.get_id()]
        else:
            return self._dist_customers[vertex_a.get_id()][vertex_b.get_id()]

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
            return self.get_hotel_per_index(vertex_b_index)
        else:
            return self.get_customer_per_index(vertex_b_index)


