
import logging

from constants import logger_name

logger = logging.getLogger(logger_name)

class Delta:

    def __init__(self, removes, adds):
        self._adds = adds
        self._removes = removes

    def get_adds(self):
        return self._adds

    def get_removes(self):
        return self._removes

    def add_add(self, add):
        self._adds.append(add)

    def add_remove(self, remove):
        self._removes.append(remove)

    def to_string(self):
        string = "("
        string = string + "["
        for rmv in self._removes:
            string = string + "(" + str(rmv[0].get_id()) + "," + str(rmv[1]) + "," + str(rmv[2]) + "),"

        string = string + "],["
        for add in self._adds:
            string = string +  "(" + str(add[0].get_id()) + "," + str(add[1]) + "," + str(add[2]) + "),"
        string = string + "])"

        return string

class Solution_Worthiness:
    def __init__(self, objective_value, max_trip_duration, performed_trips, collected_prizes, delta, reverse_delta):
        self._objective_value = objective_value
        self._max_trip_duration = max_trip_duration
        self._performed_trips = performed_trips
        self._collected_prizes = collected_prizes
        self._delta = delta
        self._reverse_delta = reverse_delta

    def get_objective_value(self):
        return self._objective_value

    def get_max_trip_duration(self):
        return self._max_trip_duration

    def get_performed_trips(self):
        return self._performed_trips

    def get_collected_prizes(self):
        return self._collected_prizes

    def get_delta(self):
        return self._delta

    def get_reverse_delta(self):
        return self._reverse_delta


class Solution:


    def __init__(self, instance):

        self._instance = instance

        self._trips = []
        self._trips.insert(0, [])
        self._hotels = [self._instance.get_hotel_per_index(0),self._instance.get_hotel_per_index(0)]

        self._prize = 0
        self._trip_lengths = [0]
        self._max_trip_length = 0    

        self._trips_size = 1

        # Initialize objective value:
        self._sum_of_trips = 0
        self._hotel_fees = 0

        self._penalties = 0
        for customer in instance.get_list_of_customers():
            self._penalties = self._penalties + customer.get_penalty()

        self._objective_value = self._sum_of_trips + self._hotel_fees + self._penalties

        self._is_customer_served = {}

    def change_from_delta(self, delta):
        """
        Given a delta, change the solution.
        Delta is object with removes and adds, where each is a list of three tuples,
        specifying the object and the position.
        """

        reverse_delta = Delta([],[])

        removes = delta.get_removes()
        for remove in removes: # rmv:(customer/hotel, trip_index, trip_position_index)

            (obj, trip_index, trip_position_index) = remove

            if self._instance.obj_is_hotel(obj):
                self._remove_hotel(obj, trip_index, trip_position_index, reverse_delta)

            else:
                self._remove_customer(obj, trip_index, trip_position_index, reverse_delta)

        adds = delta.get_adds()
        for add in adds: # add:(obj=customer/hotel, trip_index, trip_position_index)
            (obj, trip_index, trip_position_index) = add

            if self._instance.obj_is_hotel(obj):
                self._add_hotel(obj, trip_index, trip_position_index, reverse_delta)
            else:
                self._add_customer(obj, trip_index, trip_position_index, reverse_delta)

        return Solution_Worthiness(self._objective_value, self._max_trip_length, self._trips_size, self._prize, delta, reverse_delta)
 
    def calculate_max_trip_length(self, new_value, old_trip_value, skipped_indexes):
        max_trip_length = self._max_trip_length
        if new_value > self._max_trip_length:
            max_trip_length = new_value
        elif new_value < self._max_trip_length and old_trip_value >= self._max_trip_length:
            new_max = 0
            for index in range(0, len(self._trip_lengths)):
                if index in skipped_indexes:
                    if new_value > new_max:
                        new_max = new_value
                elif self._trip_lengths[index] > new_max:
                    new_max = self._trip_lengths[index]

            max_trip_length = new_max

        return max_trip_length

  

    def _remove_hotel(self, obj, trip_index, trip_position_index, reverse_delta):
        # ----- REMOVE SINGLE HOTEL --------
       
        # ----- Define old lists ----- 
        old_left_trip = self._trips[trip_index - 1]
        old_left_trip_val = self._trip_lengths[trip_index - 1]

        old_right_trip = self._trips[trip_index]
        old_right_trip_val = self._trip_lengths[trip_index]

        old_trip_val = old_left_trip_val + old_right_trip_val

        # ----- Recompute delta values (and constaint values) ----- 

        if len(old_left_trip) == 0 and len(old_right_trip) == 0:
            rm_d1 = self._instance.get_distance(self._hotels[trip_index - 1], obj)
            rm_d2 = self._instance.get_distance(obj, self._hotels[trip_index + 1])

            rm_a1 = self._instance.get_distance(self._hotels[trip_index - 1], self._hotels[trip_index + 1])
        elif len(old_left_trip) > 0 and len(old_right_trip) == 0:
            rm_d1 = self._instance.get_distance(old_left_trip[len(old_left_trip) - 1], obj)
            rm_d2 = self._instance.get_distance(obj, self._hotels[trip_index + 1])

            rm_a1 = self._instance.get_distance(old_left_trip[len(old_left_trip) - 1],  self._hotels[trip_index + 1])
        elif len(old_left_trip) == 0 and len(old_right_trip) > 0:   
            rm_d1 = self._instance.get_distance(self._hotels[trip_index - 1], obj)
            rm_d2 = self._instance.get_distance(obj, old_right_trip[0])

            rm_a1 = self._instance.get_distance(self._hotels[trip_index - 1], old_right_trip[0])
        elif len(old_left_trip) > 0 and len(old_right_trip) > 0:
            rm_d1 = self._instance.get_distance(old_left_trip[len(old_left_trip) - 1], obj)
            rm_d2 = self._instance.get_distance(obj, old_right_trip[0])

            rm_a1 = self._instance.get_distance(old_left_trip[len(old_left_trip) - 1], old_right_trip[0])

        # ------ CALCULATIONS --------

        trips_size = self._trips_size - 1

        hotel_fees = self._hotel_fees - obj.get_fee() 
        sum_of_trips = self._sum_of_trips - rm_d1 - rm_d2 + rm_a1

        objective_value = sum_of_trips + hotel_fees + self._penalties

        max_trip_length = self.calculate_max_trip_length((old_trip_val - rm_d1 - rm_d2 + rm_a1), old_trip_val, [trip_index - 1, trip_index])


        # ----- SOLUTION CHANGES ----

    
        reverse_delta.add_add((obj, trip_index - 1, len(old_left_trip)))

        self._hotels.pop(trip_index)

        new_trip = old_left_trip + old_right_trip # Concatenate lists

        self._trips_size = trips_size

        self._hotel_fees = hotel_fees
        self._sum_of_trips = sum_of_trips

        self._trip_lengths[trip_index - 1] = old_trip_val - rm_d1 - rm_d2 + rm_a1
        self._trip_lengths.pop(trip_index)

        self._trips[trip_index - 1] = new_trip
        self._trips.pop(trip_index)

        self._max_trip_length = max_trip_length

        self._objective_value = objective_value

    def _remove_customer(self, obj, trip_index, trip_position_index, reverse_delta):
        # --------- REMOVE SINGLE CUSTOMER --------------
        trip = self._trips[trip_index]

        if trip_position_index < len(trip):
            item = trip[trip_position_index]

            old_trip_value = self._trip_lengths[trip_index]


            if len(trip) == 1 and trip_position_index == 0:
                rm_a1 = self._instance.get_distance(self._hotels[trip_index], self._hotels[trip_index + 1])
                rm_d1 = self._instance.get_distance(self._hotels[trip_index], obj)
                rm_d2 = self._instance.get_distance(obj, self._hotels[trip_index + 1])
            elif trip_position_index == 0:
                rm_a1 = self._instance.get_distance(self._hotels[trip_index], trip[1])
                rm_d1 = self._instance.get_distance(self._hotels[trip_index], obj)
                rm_d2 = self._instance.get_distance(obj, trip[trip_position_index + 1])
            elif trip_position_index == (len(trip) - 1):
                rm_a1 = self._instance.get_distance(trip[trip_position_index - 1], self._hotels[trip_index + 1])
                rm_d1 = self._instance.get_distance(trip[trip_position_index - 1], obj)
                rm_d2 = self._instance.get_distance(obj, self._hotels[trip_index + 1])
            else: # trip_position_index > 0 and trip_position_index < len(trip) - 1
                rm_a1 = self._instance.get_distance(trip[trip_position_index - 1], trip[trip_position_index + 1])
                rm_d1 = self._instance.get_distance(trip[trip_position_index - 1], obj)
                rm_d2 = self._instance.get_distance(obj, trip[trip_position_index + 1])

            # ---- ONLY CALCULATIONS -----

            prize = self._prize - item.get_prize()
            penalties = self._penalties + obj.get_penalty()

            sum_of_trips = self._sum_of_trips - rm_d1 - rm_d2 + rm_a1 

            max_trip_length = self.calculate_max_trip_length((old_trip_value - rm_d1 - rm_d2 + rm_a1), old_trip_value, [trip_index])
    
            objective_value = sum_of_trips + penalties + self._hotel_fees

            # ----- SOLUTION CHANGES ----

            reverse_delta.add_add((obj, trip_index, trip_position_index))

            self._prize = prize
            self._penalties = penalties

            self._sum_of_trips = sum_of_trips

            self._trip_lengths[trip_index] = old_trip_value - rm_d1 - rm_d2 + rm_a1

            self._max_trip_length = max_trip_length
    
            trip.pop(trip_position_index)

            self._objective_value = objective_value

            del self._is_customer_served[obj]


        else:
            print("Cannot remove, due to index out of bounds for obj: " + str(obj.get_id()))


    def _add_hotel(self, obj, trip_index, trip_position_index, reverse_delta):
        # ------- ADD SINGLE HOTEL ------------
        old_trip = self._trips[trip_index]

        new_left = old_trip[:trip_position_index]
        new_right = old_trip[trip_position_index:]
    
        # ----------------------------------- RECALC - TRIP - VALUES - BEGIN --------------------
        old_trip_value = self._trip_lengths[trip_index]
        # TODO: This part of delta-eval is in O(n)!!!
        if len(new_left) <= len(new_right) and len(new_left) > 0 and len(new_right) > 0:
    
            new_left_val = self._instance.get_distance(self._hotels[trip_index], new_left[0])

            for customer_index in range(1,len(new_left) - 1):
                customer_prev = new_left[customer_index - 1]
                customer = new_left[customer_index]
            
                new_left_val = new_left_val + self._instance.get_distance(customer_prev, customer)

            # Order of the following three lines is important
            new_right_val = old_trip_value - new_left_val - self._instance.get_distance(new_left[len(new_left) - 1], new_right[0])

            new_left_val = new_left_val + self._instance.get_distance(new_left[len(new_left) - 1], obj)
            new_right_val = new_right_val + self._instance.get_distance(obj, new_right[0])

        # Special Case
        elif len(new_left) == 0:
            new_left_val = self._instance.get_distance(self._hotels[trip_index], obj)
            if len(new_right) == 0:
                # Further Special Case
                new_right_val = self._instance.get_distance(obj, self._hotels[trip_index + 1])
            else:
                new_right_val = old_trip_value - self._instance.get_distance(self._hotels[trip_index], new_right[0]) + self._instance.get_distance(obj, new_right[0])

        # TODO: In O(n)!!!
        elif len(new_right) > 0 and len(new_right) < len(new_left) and len(new_left) > 0:

            new_right_val = self._instance.get_distance(new_right[len(new_right) - 1], self._hotels[trip_index + 1])

            for customer_index in range(1, len(new_right) - 1):
                customer_prev = new_left[customer_index - 1]
                customer = new_left[customer_index]
            
                new_right_val = new_right_val + self._instance.get_distance(customer_prev, customer)

            new_left_val = old_trip_value - new_right_val - self._instance.get_distance(new_left[len(new_left) - 1], new_right[0])

            new_right_val = new_right_val + self._instance.get_distance(obj, new_right[0])

            new_left_val = new_left_val + self._instance.get_distance(new_left[len(new_left) - 1], obj)
        else: # len(right) == 0
            new_right_val = self._instance.get_distance(obj, self._hotels[trip_index + 1])
            if len(new_left) == 0:
                # Further Special Case
                new_left_val = self._instance.get_distance(self._hotels[trip_index], obj)
            else:
                new_left_val = old_trip_value - self._instance.get_distance(new_left[len(new_left) - 1], self._hotels[trip_index + 1]) + self._instance.get_distance(new_left[len(new_left) - 1], obj)


        # ----------- CALCULATION --------

        trips_size = self._trips_size + 1

        hotel_fees = self._hotel_fees + obj.get_fee() 

        sum_of_trips = self._sum_of_trips - old_trip_value + new_left_val + new_right_val

        left_max = self.calculate_max_trip_length(new_left_val, old_trip_value, [trip_index])
        right_max = self.calculate_max_trip_length(new_right_val, old_trip_value, [trip_index])

        if left_max > right_max:
            max_trip_length = left_max
        else:
            max_trip_length = right_max

        objective_value = sum_of_trips + hotel_fees + self._penalties

        # ----- SOLUTION CHANGES ----

        reverse_delta.add_remove((obj, trip_index + 1, 0))

        self._trips_size = trips_size

        self._trips[trip_index] = new_left
        self._trips.insert(trip_index + 1, new_right)
        self._trip_lengths[trip_index] = new_left_val
        self._trip_lengths.insert(trip_index + 1, new_right_val)

        self._hotel_fees = hotel_fees 

        self._sum_of_trips = sum_of_trips

        self._max_trip_length = max_trip_length
            
        self._hotels.insert(trip_index + 1, obj)

        self._objective_value = objective_value

    def _add_customer(self, obj, trip_index, trip_position_index, reverse_delta):
        # -------- ADD SINGLE CUSTOMER ---------------
        trip = self._trips[trip_index]

        if trip_position_index <= len(trip):

            cur_trip_value = self._trip_lengths[trip_index]
            old_trip_value = cur_trip_value

            # Recalc trip value
            if len(trip) == 0:
                cur_trip_value = self._instance.get_distance(self._hotels[trip_index], obj) + self._instance.get_distance(obj, self._hotels[trip_index + 1])

            elif trip_position_index == 0:
                cur_trip_value = cur_trip_value - self._instance.get_distance(self._hotels[trip_index], trip[0]) + self._instance.get_distance(self._hotels[trip_index + 1], obj) + self._instance.get_distance(obj, trip[0])


            elif trip_position_index >= (len(trip) - 1):
                cur_trip_value = cur_trip_value - self._instance.get_distance(trip[len(trip) - 1], self._hotels[trip_index + 1]) + self._instance.get_distance(trip[len(trip) - 1], obj) + self._instance.get_distance(obj, self._hotels[trip_index + 1])

            elif trip_position_index > 0 and trip_position_index < (len(trip) - 1):
                cur_trip_value = cur_trip_value - self._instance.get_distance(trip[trip_position_index - 1], trip[trip_position_index]) + self._instance.get_distance(trip[trip_position_index - 1], obj) + self._instance.get_distance(obj, trip[trip_position_index])

            # ----- CALCULATIONS -------

            penalties = self._penalties - obj.get_penalty()
            sum_of_trips = self._sum_of_trips + cur_trip_value - old_trip_value

            max_trip_length = self.calculate_max_trip_length(cur_trip_value, old_trip_value, [trip_index])
           
            prize = self._prize + obj.get_prize()

            objective_value = sum_of_trips + penalties + self._hotel_fees

            # ----- SOLUTION CHANGES ----

            reverse_delta.add_remove((obj, trip_index, trip_position_index))

            self._penalties = penalties
            self._sum_of_trips = sum_of_trips

            self._trip_lengths[trip_index] = cur_trip_value

            self._max_trip_length = max_trip_length
           
            self._prize = prize

            trip.insert(trip_position_index, obj)

            self._objective_value = objective_value

            self._is_customer_served[obj] = True

        else:
            logger.error("Cannot insert, due to index out of bounds for obj: " + str(obj.get_id()) + " and trip index: " + str(trip_index) + " and trip index position " + str(trip_position_index))


                
                
    def get_objective_value(self):
        return self._objective_value

    def get_max_trip_length(self):
        return self._max_trip_length

    def get_number_of_trips(self):
        return self._trips_size

    def get_prize(self):
        return self._prize

    def is_customer_served(self, customer):
        if customer in self._is_customer_served and self._is_customer_served[customer]:
            return True
        else:
            return False

    def is_c3_satisfied(self):
        if self._prize >= self._instance.get_C3():
            return True
        else:
            return False

    def is_c2_satisfied(self):
        if self._trips_size <= self._instance.get_C2():
            return True
        else:
            return False

    def is_c1_satisfied(self):
        if self._max_trip_length <= self._instance.get_C1():
            return True
        else:
            return False

    def get_nearest_unserved_customer(self, location):
        for nearest in self._instance.get_all_nearest_customers(location):
            if not self.is_customer_served(nearest) and self._instance.get_distance(location, nearest) > 0:
                return nearest

        logger.critical("Ran out of nearest unserved customers! May never happen!")
        quit()

 
    def to_string(self):
        string = "[0,"

        for index in range(0, self._trips_size):
            trip = self._trips[index]

            string = string + "["
            for index_2 in range(0, len(trip)):
                obj = trip[index_2]
                if index_2 < (len(trip) - 1):
                    string = string + str(obj.get_id()) + "-"
                else:
                    string = string + str(obj.get_id())

            string = string + "],"

            if index < (self._trips_size - 1):
                string = string + str(self._hotels[index + 1].get_id()) + ","
            else:
                string = string + str(self._hotels[index + 1].get_id()) + "]"

        return string

   
    def clone(self):
        solution = Solution(self._instance)

        solution._trips = self._trips
        solution._hotels = self._hotels

        solution._prize = self._prize
        solution._trip_lengths = self._trip_lengths.copy()
        solution._max_trip_length = self._max_trip_length
        solution._trips_size = self._trips_size

        solution._sum_of_trips = self._sum_of_trips 
        solution._hotel_fees = self._hotel_fees
        solution._penalties = self._penalties
        solution._objective_value = self._objective_value
        solution._is_customer_served = self._is_customer_served.copy()

        return solution





