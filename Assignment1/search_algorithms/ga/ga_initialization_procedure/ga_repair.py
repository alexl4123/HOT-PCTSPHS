
import time

from framework.result import Result
from framework.solution import Delta, Add, Remove, Reverse


class GA_Repair:

    @classmethod
    def repair(cls, instance, solution):
        """
            Solution without hotels
            Over approximates hotels, i.e. inserts at each possible position a hotel
        """

        start_time = time.time()

        positions = len(solution._trips[0]) + 1

        for index in range(positions):
            
            trip_index = index

            if index == 0:
                trip_index_position = 0

                first_obj = solution._hotels[0]
                if len(solution._trips[0]) > 0:
                    second_obj = solution._trips[0][0]
                else:
                    # Special case for empty solution
                    second_obj = solution._hotels[1]
            elif index == positions - 1:
                trip_index_position = 1

                first_obj = solution._trips[trip_index][0]
                second_obj = solution._hotels[trip_index + 1]
            else:
                trip_index_position = 1
                
                first_obj = solution._trips[trip_index][0]
                second_obj = solution._trips[trip_index][1]

            hotel = GA_Repair.get_best_hotel_for_objs(first_obj, second_obj, instance)
            delta = Delta([Add(hotel, trip_index, trip_index_position)])

            solution.change_from_delta(delta)

                


        print(solution.to_string())
        print(hotel.get_id())

        end_time = time.time()

        solution.compute_fitness_value()
        return Result(solution, [solution.get_fitness_value()], end_time - start_time)


    @classmethod
    def get_best_hotel_for_objs(cls, first_obj, second_obj, instance):

        hotels = instance.get_list_of_hotels()

        best_hotel = None

        for hotel in hotels:

            hotel_dist = instance.get_distance(first_obj, hotel) + instance.get_distance(hotel, second_obj)
            
            if not best_hotel:
                best_hotel = hotel
            else:
                best_hotel_dist = instance.get_distance(first_obj, best_hotel) + instance.get_distance(best_hotel, second_obj)
                if hotel_dist < best_hotel_dist:
                    best_hotel = hotel

        return best_hotel






































































    
