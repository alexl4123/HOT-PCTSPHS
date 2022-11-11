
import logging

from constants import logger_name

logger = logging.getLogger(logger_name)

class Delta:

    def __init__(self, removes, adds):
        self._adds = adds
        self._removes = removes
        self._objective_value = -1

    def get_adds(self):
        return self._adds

    def get_removes(self):
        return self._removes

    def set_objective_value(self, value):
        self._objective_value = value


class Solution:


    def __init__(self, instance):

        self._instance = instance

        self._trips = []
        self._trips.insert(0, [])
        self._hotels = [instance.get_hotel_per_index(0), instance.get_hotel_per_index(0)]

        self._prize = 0
        self._trip_lengths = [0]
        self._max_trip_length = 0    

        self._trips_size = 1


        self._hotel_fees = 0

        self._penalties = 0
        for customer in instance.get_list_of_customers():
            self._penalties = self._penalties + customer.get_penalty()

        self._objective_value = self._penalties

        # TODO -> Compute the evaluation function!
        
    def change_from_delta(self, delta):
        """
        Given a delta, change the solution.
        Delta is object with removes and adds, where each is a list of three tuples,
        specifying the object and the position.
        """

        removes = delta.get_removes()
        for remove in removes: # rmv:(customer/hotel, trip_index, trip_position_index)

            (obj, trip_index, trip_position_index) = remove

            if self._instance.obj_is_hotel(obj):
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

                # ----- Remove hotel and combine lists ----- 
                self._hotels.pop(trip_index)
                
                new_trip = old_left_trip + old_right_trip # Concatenate lists

                self._trips_size = self._trips_size - 1
           
                self._hotel_fees = self._hotel_fees - obj.get_fee() 
                self._objective_value = self._objective_value - rm_d1 - rm_d2 + rm_a1 - obj.get_fee()

                self._trip_lengths[trip_index - 1] = old_trip_val - rm_d1 - rm_d2 + rm_a1
                self._trips[trip_index - 1] = new_trip

                self._trip_lengths.pop(trip_index)
                self._trips.pop(trip_index)
            
                if (old_trip_val - rm_d1 - rm_d2 + rm_a1) > self._max_trip_length:
                    self._max_trip_length = old_trip_val - rm_d1 - rm_d2 + rm_a1
                elif (old_trip_val - rm_d1 - rm_d2 + rm_a1) < self._max_trip_length and old_trip_val >= self._max_trip_length:
                    new_max = 0
                    for trip_length in self._trip_lengths:
                        if trip_length > new_max:
                            new_max = trip_length

                    self._max_trip_length = new_max

                
            else:
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
                        

                    self._prize = self._prize - item.get_prize()
                    self._penalties = self._penalties + obj.get_penalty()

                    self._objective_value = self._objective_value - rm_d1 - rm_d2 + rm_a1 + obj.get_penalty()
                    self._trip_lengths[trip_index] = old_trip_value - rm_d1 - rm_d2 + rm_a1

                    if (old_trip_value - rm_d1 - rm_d2 + rm_a1) > self._max_trip_length:
                        self._max_trip_length = old_trip_value - rm_d1 - rm_d2 + rm_a1
                    elif (old_trip_value - rm_d1 - rm_d2 + rm_a1) < self._max_trip_length and old_trip_value >= self._max_trip_length:
                        new_max = 0
                        for trip_length in self._trip_lengths:
                            if trip_length > new_max:
                                new_max = trip_length

                        self._max_trip_length = new_max
    
            
                    trip.pop(trip_position_index)

                else:
                    print("Cannot remove, due to index out of bounds for obj: " + str(obj.get_id()))


        # ------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------
        # ----------------------------- ADDS -------------------------------------------------
        # ------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------

        adds = delta.get_adds()
        for add in adds: # add:(obj=customer/hotel, trip_index, trip_position_index)
            (obj, trip_index, trip_position_index) = add

            if self._instance.obj_is_hotel(obj):
                # ------- ADD SINGLE HOTEL ------------
                old_trip = self._trips[trip_index]

                new_left = old_trip[:trip_position_index]
                new_right = old_trip[trip_position_index:]
            
                # One additional trip


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

                    new_right_val = self._instance.get_distance(new_right_val[len(new_right) - 1], self._hotels[trip_index + 1])

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

                # ----------------------------------- RECALC - TRIP - VALUES - END --------------------

                # Ctd. adding hotel

                self._trips_size = self._trips_size + 1

                self._trips[trip_index] = new_left
                self._trips.insert(trip_index + 1, new_right)
                self._trip_lengths[trip_index] = new_left_val
                self._trip_lengths.insert(trip_index + 1, new_right_val)
                self._hotel_fees = self._hotel_fees + obj.get_fee() 

                self._objective_value = self._objective_value - old_trip_value + new_left_val + new_right_val + obj.get_fee()

                if new_left_val >= new_right_val and new_left_val > self._max_trip_length:
                        self._max_trip_length = new_left_val
                elif new_right_val > new_left_val and new_right_val > self._max_trip_length:
                        self._max_trip_length = new_right_val
                elif new_right_val < self._max_trip_length and new_left_val < self._max_trip_length and old_trip_value >= self._max_trip_length:
                    new_max = 0
                    for trip_length in self._trip_lengths:
                        if trip_length > new_max:
                            new_max = trip_length

                    self._max_trip_length = new_max


                # Prize (i.e. customers) doesn't change 

                self._hotels.insert(trip_index + 1, obj)
            else:
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


                    self._penalties = self._penalties - obj.get_penalty()
                    self._objective_value = self._objective_value + cur_trip_value - old_trip_value - obj.get_penalty()
                    self._trip_lengths[trip_index] = cur_trip_value

   

                    if cur_trip_value > self._max_trip_length:
                        self._max_trip_length = cur_trip_value
                    elif cur_trip_value < self._max_trip_length and old_trip_value >= self._max_trip_length:
                        new_max = 0
                        for trip_length in self._trip_lengths:
                            if trip_length > new_max:
                                new_max = trip_length

                        self._max_trip_length = new_max
 

                    self._prize = self._prize + obj.get_prize()

                    trip.insert(trip_position_index, obj)
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

   

    
















