import networkx as nx
import random

# Gitlab-Test-Commit

def generate_graph(file):
    """
    Constructs from the given problem instance a graph object containing all
    necessary information

    :param file: Path to the file containing the instance
    :type file: str
    :return: The generated graph
    :rtype: networkx.Graph
    """
    graph: nx.Graph = nx.Graph()
    hotel_prices = []
    prizes = []
    penalties = []
    edges = []
    edge_costs = []

    with open(file, 'r') as f:
        first_line = f.readline()
        values = first_line.split()

        s = int(values[0])  # hotel number
        n = int(values[1])  # customer number
        m = int(values[2])  # edge number
        L = int(values[3])  # max allowed duration of the trip
        D = int(values[4])  # max performable trip number
        P = int(values[5])  # min prize count to collect

        for _ in range(s + 1):
            hotel_prices.append(int(f.readline()))

        for _ in range(n):
            prize, penalty = (f.readline().split())
            prizes.append(int(prize))
            penalties.append(int(penalty))

        for _ in range(m):
            edge_x, edge_y, edge_cost = (f.readline().split())
            edges.append((int(edge_x), int(edge_y)))
            edge_costs.append(int(edge_cost))
            graph.add_edge(int(edge_x), int(edge_y), weight=int(edge_cost))

    return graph


def get_edge_weight(n, m, graph: nx.Graph):
    sub = graph.get_edge_data(n, m)
    for key in sub:
        return int(sub[key])


def find_hamiltonian_cycle(graph: nx.Graph, node):
    node_cycle = []
    nodes = []
    for n in graph.nodes:
        nodes.append(n)
    while len(node_cycle) < node:
        chosen = random.choice(nodes)
        if chosen not in node_cycle:
            node_cycle.append(chosen)
    return nodeCycle


def calculate_route_cost(route, graph: nx.Graph):
    route_cost = 0
    for i in range(len(route)):
        route_cost += get_edge_weight(route[i], route[(i + 1) % len(route)], graph)
    return route_cost


g = generate_graph(r"pctsphs_instances_batch_1/test.txt")
