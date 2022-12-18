
import random

from search_algorithms.ga.ga_solution import GA_Solution
from search_algorithms.ga.crossover import Crossover

class OX_Crossover(Crossover):

    @classmethod
    def perform_crossover(cls, population, fitness_function):

        pop_list_rep = []
        for individual in population:
            pop_list_rep.append(individual.compute_pure_list_representation())

        new_pop = []

        for i in range(0,len(pop_list_rep) - 1,2):
            p1 = pop_list_rep[i]
            p2 = pop_list_rep[i+1]

            (c1, c2) = OX_Crossover.perform_ox_crossover_algorithm(p1, p2)

            c1_o = GA_Solution(population[0]._instance, fitness_function)
            c1_o.from_pure_list_representation_to_internal(c1)

            c1_o.update_values_from_slow_calculation()
            c1_o.compute_fitness_value()

            c2_o = GA_Solution(population[0]._instance, fitness_function)
            c2_o.from_pure_list_representation_to_internal(c2)

            c2_o.update_values_from_slow_calculation()
            c2_o.compute_fitness_value()

            new_pop.append(c1_o)
            new_pop.append(c2_o)

        if len(pop_list_rep) % 2 ==  1:
            new_pop.append(population[len(pop_list_rep) - 1])

        return new_pop


    @classmethod
    def perform_ox_crossover_algorithm(cls, p1, p2):

        initial_hotel = p1[0]

        # Preprocess (set first element to -1 and remove last):
        p1[0] = "-1"
        p1.pop(len(p1)-1)

        p2[0] = "-1"
        p2.pop(len(p2)-1)

        (lower_p1, upper_p1, lower_p2, upper_p2) = OX_Crossover.compute_cx_ranges(p1, p2)


        c1 = OX_Crossover.create_child(p1, p2, lower_p1, upper_p1, lower_p2, upper_p2, initial_hotel)
        c2 = OX_Crossover.create_child(p2, p1, lower_p2, upper_p2, lower_p1, upper_p1, initial_hotel)

        return (c1, c2)

    @classmethod
    def compute_cx_ranges(cls, p1, p2):

        # Get CX-Ranges 
        # Lower ones cannot be the last one (-2)
        lower_p1 = random.randint(0, len(p1) - 2)
        lower_p2 = random.randint(0, len(p2) - 2)

        # Determine the length
        v_p1_val = len(p1) - lower_p1 - 1
        v_p2_val = len(p2) - lower_p2 - 1

        if v_p1_val < v_p2_val:
            max_length = v_p1_val
        else:
            max_length = v_p2_val

        length = random.randint(0, max_length)

        upper_p1 = lower_p1 + length
        upper_p2 = lower_p2 + length
        # Range is between lower_pi and upper_pi

        return (lower_p1, upper_p1, lower_p2, upper_p2)


    @classmethod
    def create_child(cls, p1, p2, lower_p1, upper_p1, lower_p2, upper_p2, initial_hotel):
        """
            Given parent_1, parent_2 and the crossover ranges, this method computes the child which has the parent_1 as the ''primary parent''
            Note that the ''initial'' hotel is the hotel 0
        """

        # Create C1:
        # Step 1: Mark all that shall be removed
        p1_cpy = p1.copy()

        for index in range(lower_p2, upper_p2 + 1):
            obj = p2[index]

            # Mark all those objects in p1 as ''-2'' that occur in the cx-range of p1
            for index_2 in range(0, len(p1_cpy)):
                obj_2 = p1_cpy[index_2]

                if obj_2 == "-2":
                    continue
                elif obj == "-1" and obj_2 == "-1":
                    p1_cpy[index_2] = "-2"
                    break
                elif obj_2 != "-1" and obj != "-1":
                    # Assume obj and obj_2 are objects (either hotel or customer)
                    if obj_2.get_id() == obj.get_id():
                        p1_cpy[index_2] = "-2"
                        break

        c1_first_hotel_index = None

        c1 = []

        # First items are the items from the CX range of p1
        for index in range(lower_p1, upper_p1 + 1):
            obj = p1_cpy[index]

            if obj == "-2":
                continue
            elif obj == "-1":
                c1_first_hotel_index = len(c1)
                c1.append("-1")
            else:
                c1.append(obj)

        # Second items are the items from the CX range of p2
        for index in range(lower_p2, upper_p2 + 1):
            obj = p2[index]

            if obj == "-1":
                c1_first_hotel_index = len(c1)

            c1.append(obj)

        # Third items are the remaining items, in the order starting from the end of the p1-cx-range to the beginning of the p1-cx-range

        for index in range(upper_p1 + 1, len(p1_cpy)):
            obj = p1_cpy[index]

            if obj == "-2":
                continue
            elif obj == "-1":
                c1_first_hotel_index = len(c1)
                c1.append("-1")
            else:
                c1.append(obj)

        for index in range(0, lower_p1):
            obj = p1_cpy[index]

            if obj == "-2":
                continue
            elif obj == "-1":
                c1_first_hotel_index = len(c1)
                c1.append("-1")
            else:
                c1.append(obj)

        # Fix list, by bringing it in the order, where the hotel 0 is at the beginning and at the end
        c1_new = []
        c1_new.append(initial_hotel)
        for index in range(c1_first_hotel_index + 1, len(c1)):
            c1_new.append(c1[index])
        for index in range(0, c1_first_hotel_index):
            c1_new.append(c1[index])
        c1_new.append(initial_hotel)

        return c1_new



    @classmethod
    def list_printer(cls, lst):
        string = ""
        for s in lst:
            if s == "-1":
                string += "-1 "
            elif s == "-2":
                string += "-2 "
            else:
                string += str(s.get_id()) + " "

        print(string)






