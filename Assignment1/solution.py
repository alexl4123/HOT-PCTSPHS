
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
        self._trips_size = 1
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

                # ----- Recompute delta values (and constaint values) ----- 
                self._trips_size = self._trips_size - 1

                rm_d1 = self._instance.get_distance(old_left_trip[len(old_left_trip) - 1], obj)
                rm_d2 = self._instance.get_distance(obj, old_right_trip[1])

                rm_a1 = self._instance.get_distance(old_left_trip[len(old_left_trip) - 1], old_right_trip[1])

                # ----- Remove hotel and combine lists ----- 
                self._hotels.pop(trip_index)
                
                new_trip = old_left_trip + old_right_trip # Concatenate lists

                new_trip_val = old_left_trip_val + old_right_trip_val
                self._trip_lengths[trip_index - 1] = new_trip_val - rm_d1 - rm_d2 + rm_a1
                self._trips[trip_index - 1] = new_trip

                self._trip_lengths.pop(trip_index)
                self._trips.pop(trip_index)


            else:
                # --------- REMOVE SINGLE CUSTOMER --------------
                trip = self._trips[trip_index]

                if trip_position_index < len(trip):
                    item = trip[trip_position_index]
                    self._prize = self._prize - item.get_prize()

                    if trip_position_index > 0:
                        rm_d1 = self._instance.get_distance(trip[trip_position_index - 1], obj)
                    else:
                        rm_d1 = self._instance.get_distance(self._hotels[trip_index - 1], obj)

                    if trip_position_index < (len(trip) - 1):
                        rm_d2 = self._instance.get_distance(obj, trip[trip_position_index + 1])
                    else:
                        rm_d2 = self._instance.get_distance(obj, self._hotels[trip_index])

            
                    if trip_position_index > 0 and trip_position_index < (len(trip) - 1):
                        rm_a1 = self._instance.get_distance(trip[trip_position_index - 1], trip[trip_position_index + 1])
                    elif trip_position_index == 0 and len(trip) == 1:
                        rm_a1 = self._instance.get_distance(self._hotels[trip_index - 1], self._hotels[trip_index])
                    elif trip_position_index == 0 and len(trip) > 1:
                        rm_a1 = self._instance.get_distance(self._hotels[trip_index - 1], trip[trip_position_index + 1])
                    else: # trip_position_index > 0 and trip_position_index >= (len(trip) - 1)
                        rm_a1 = self._instance.get_distance(trip[trip_position_index - 1], self._hotels[trip_index])


                    self._trip_lengths[trip_index] = self._trip_lengths[trip_index] - rm_d1 - rm_d2 + rm_a1
            
                    trip.pop(trip_position_index)

                else:
                    print("Cannot remove, due to index out of bounds for obj: " + str(obj.get_id()))

        adds = delta.get_adds()
        for add in adds: # add:(obj=customer/hotel, trip_index, trip_position_index)
            (obj, trip_index, trip_position_index) = add

            if self._instance.obj_is_hotel(obj):
                # ------- ADD SINGLE HOTEL ------------
                old_trip = self._trips[trip_index]

                new_left = old_trip[:trip_position_index]
                new_right = old_trip[trip_position_index:]
            
                # One additional trip
                self._trips_size = self._trips_size + 1


                # ----------------------------------- RECALC - TRIP - VALUES - BEGIN --------------------
                old_trip_value = self._trip_lengths[trip_index]
                # TODO: This part of delta-eval is in O(n)!!!
                if len(new_left) <= len(new_right) and len(new_left) > 0:
            
                    new_left_val = 0
                    new_left_val = new_left_val + self._instance.get_distance(self._hotels[trip_index - 1], new_left[0])

                    for customer_index in range(1,len(new_left) - 1):
                        customer_prev = new_left[customer_index - 1]
                        customer = new_left[customer_index]
                    
                        new_left_val = new_left_val + self._instance.get_distance(customer_prev, customer)

                    new_right_val = old_trip_value - new_left_val

                    new_left_val = new_left_val + self._instance.get_distance(new_left[len(new_left) - 1], obj)
                    if len(new_right) > 0:
                        new_right_val = new_right_val + self._instance.get_distance(obj, new_right[0])
                    else:
                        new_right_val = self._instance.get_distance(obj, self._hotels[trip_index])
        
                # Special Case
                elif len(new_left) == 0:
                    new_left_val = self._instance.get_distance(self._hotels[trip_index - 1], obj)
                    if len(new_right) == 0:
                        # Further Special Case
                        new_right_val = self._instance.get_distance(obj, self._hotels[trip_index])
                    else:
                        new_right_val = old_trip_value - self._instance.get_distance(self._hotels[trip_index - 1], new_right[0]) + self._instance.get_distance(obj, new_right[0])



                # TODO: In O(n)!!!
                elif len(new_right) > 0:
                    new_right_val = 0
                    new_right_val = new_right_val + self._instance.get_distance(obj, new_right_val[0])

                    for customer_index in range(1,len(new_right) - 1):
                        customer_prev = new_left[customer_index - 1]
                        customer = new_left[customer_index]
                    
                        new_right_val = new_right_val + self._instance.get_distance(customer_prev, customer)

                    new_left_val = old_trip_value - new_right_val

                    new_right_val = new_right_val + self._instance.get_distance(new_right[len(new_right) - 1], self._hotels[trip_index])

                    if len(new_left) > 0:
                        new_left_val = new_left_val + self._instance.get_distance(new_left[len(new_left) - 1], obj)
                    else:
                        new_left_val = self._instance.get_distance(self._hotels[trip_index - 1], obj)
                else:
                    # Right list is empty, e.g. [hi,[ck],obj,[],hj]
                    new_right_val = self._instance.get_distance(obj, self._hotels[trip_index])
                    if len(new_left) == 0:
                        # Further Special Case
                        new_left_val = self._instance.get_distance(self._hotels[trip_index - 1], obj)
                    else:
                        new_left_val = old_trip_value - self._instance.get_distance(new_left[len(new_left) - 1], self._hotels[trip_index]) + self._instance.get_distance(new_left[len(new_left) - 1], obj)

                # ----------------------------------- RECALC - TRIP - VALUES - END --------------------

                # Ctd. adding hotel

                self._trips[trip_index] = new_left
                self._trips.insert(trip_index + 1, new_right)
                self._trip_lengths[trip_index] = new_left_val
                self._trip_lengths.insert(trip_index + 1, new_right_val)

                # Prize doesn't change 

                self._hotels.insert(trip_index + 1, obj)
            else:
                # -------- ADD SINGLE CUSTOMER ---------------
                trip = self._trips[trip_index]

                if trip_position_index <= len(trip):
                    self._prize = self._prize + obj.get_prize()

                    # Recalc trip value
                    if len(trip) == 0:
                        cur_trip_value = self._instance.get_distance(self._hotels[trip_index - 1], obj) + self._instance.get_distance(obj, self._hotels[trip_index])
                    elif trip_position_index == 0:
                        cur_trip_value = self._trip_lengths[trip_index]

                        cur_trip_value = cur_trip_value - self._instance.get_distance(self._hotels[trip_index - 1], trip[0]) + self._instance.get_distance(self._hotels[trip_index - 1], obj) + self._instance.get_distance(obj, trip[0])
    
                    elif trip_position_index >= (len(trip) - 1):
                        cur_trip_value = self._trip_lengths[trip_index]

                        cur_trip_value = cur_trip_value - self._instance.get_distance(trip[len(trip) - 1], self._hotels[trip_index]) + self._instance.get_distance(trip[len(trip) - 1], obj) + self._instance.get_distance(obj, self._hotels[trip_index])

                    elif trip_position_index > 0 and trip_position_index < (len(trip) - 1):
                        cur_trip_value = self._trip_lengths[trip_index]
                        cur_trip_value = cur_trip_value - self._instance.get_distance(trip[trip_position_index - 1], trip[trip_position_index]) + self._instance.get_distance(trip[trip_position_index - 1], obj) + self._instance.get_distance(obj, trip[trip_position_index])


                    self._trip_lengths[trip_index] = cur_trip_value

                    trip.insert(trip_position_index, obj)
                else:
                    logger.error("Cannot insert, due to index out of bounds for obj: " + str(obj.get_id()) + " and trip index: " + str(trip_index) + " and trip index position " + str(trip_position_index))
        
                
                
            
    

    

















