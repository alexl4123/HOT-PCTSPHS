
from search_algorithms.ga.fitness_function import Fitness_Function
from framework.solution import Solution

class GA_Solution(Solution):

    def __init__(self, instance, fitness_function = None):
        super().__init__(instance)

        if not fitness_function:
            self._fitness_function = Fitness_Function(instance, 1, 1, 1)
        else:
            self._fitness_function = fitness_function
        

        self._fitness_value = self._fitness_function.compute_fitness(self)

    @classmethod
    def from_solution(cls, solution, fitness_function = None):
        ga_solution = GA_Solution(solution._instance, fitness_function)

        ga_solution._trips = []
        for trip in solution._trips:
            ga_solution._trips.append(trip.copy())

        ga_solution._hotels = solution._hotels.copy()
        ga_solution._is_customer_served = solution._is_customer_served.copy()

        ga_solution._trip_lengths = solution._trip_lengths.copy()

        ga_solution._prize = solution._prize
        ga_solution._max_trip_length = solution._max_trip_length
        ga_solution._trips_size = solution._trips_size

        ga_solution._sum_of_trips = solution._sum_of_trips
        ga_solution._hotel_fees = solution._hotel_fees
        ga_solution._penalties = solution._penalties
        ga_solution._objective_value = solution._objective_value

        ga_solution._fitness_value = ga_solution.compute_fitness_value()
    
        return ga_solution


    def compute_fitness_value(self):
        self._fitness_value = self._fitness_function.compute_fitness(self)
        return self._fitness_value
        

    def get_fitness_value(self):
        return self._fitness_value

    def clone(self):
        solution = GA_Solution(self._instance, self._fitness_function)

        solution._trips = []
        for trip in self._trips:
            solution._trips.append(trip.copy())

        solution._hotels = self._hotels.copy()
        solution._is_customer_served = self._is_customer_served.copy()

        solution._trip_lengths = self._trip_lengths.copy()

        solution._prize = self._prize
        solution._max_trip_length = self._max_trip_length
        solution._trips_size = self._trips_size

        solution._sum_of_trips = self._sum_of_trips
        solution._hotel_fees = self._hotel_fees
        solution._penalties = self._penalties
        solution._objective_value = self._objective_value

        solution._fitness_value = self._fitness_value

        return solution


    

