import logging
import random

from framework.constants import logger_name

logger = logging.getLogger(logger_name)


class Operation:

    def to_string(self):
        return ""


class Add(Operation):

    def __init__(self, obj, trip_index, trip_index_position):
        self._obj = obj
        self._trip_index = trip_index
        self._trip_index_position = trip_index_position

    def get_operation(self):
        return self._obj, self._trip_index, self._trip_index_position

    def to_string(self):
        return "(ADD:" + str(self._obj.get_id()) + "," + str(self._trip_index) + "," + str(
            self._trip_index_position) + ")"


class Remove(Operation):

    def __init__(self, obj, trip_index, trip_index_position):
        self._obj = obj
        self._trip_index = trip_index
        self._trip_index_position = trip_index_position

    def get_operation(self):
        return self._obj, self._trip_index, self._trip_index_position

    def to_string(self):
        return "(REMOVE:" + str(self._obj.get_id()) + "," + str(self._trip_index) + "," + str(
            self._trip_index_position) + ")"


class Reverse(Operation):

    def __init__(self, obj_1, start_trip_index, start_trip_index_position, obj_2, end_trip_index,
                 end_trip_index_position):
        self._obj_1 = obj_1
        self._start_trip_index = start_trip_index
        self._start_trip_index_position = start_trip_index_position
        self._obj_2 = obj_2
        self._end_trip_index = end_trip_index
        self._end_trip_index_position = end_trip_index_position

    def get_operation(self):
        return (self._obj_1, self._start_trip_index, self._start_trip_index_position, self._obj_2, self._end_trip_index,
                self._end_trip_index_position)

    def to_string(self):
        return "(REVERSE:" + str(self._obj_1.get_id()) + "," + str(self._start_trip_index) + "," + str(
            self._start_trip_index_position) + "," + str(self._obj_2.get_id()) + "," + str(
            self._end_trip_index) + "," + str(self._end_trip_index_position) + ")"


class Swap(Operation):
    def __init__(self, old_obj, old_trip_index, old_trip_index_position, new_obj, new_trip_index,
                 new_trip_index_position):
        self._old_obj = old_obj
        self._old_trip_index = old_trip_index
        self._old_trip_index_position = old_trip_index_position

        self._new_obj = new_obj
        self._new_trip_index = new_trip_index
        self._new_trip_index_position = new_trip_index_position

    def get_operation(self):
        return (self._old_obj, self._old_trip_index, self._old_trip_index_position, self._new_obj, self._new_trip_index,
                self._new_trip_index_position)

    def to_string(self):
        string = "(SWAP:" + str(self._old_obj.get_id()) + "," + str(self._old_obj_trip_index) + "," + str(
            self._old_obj_trip_index_position) + "," + str(self._new_obj.get_id()) + "," + str(
            self._new_trip_index) + "," + str(self._new_trip_index_position) + ")"


class Delta:

    def __init__(self, operations):
        self._operations = operations

    def add_operation(self, operation):
        self._operations.append(operation)

    def push_operation(self, operation):
        self._operations.insert(0, operation)

    def get_operations(self):
        return self._operations

    def to_string(self):
        string = "("
        for op in self._operations:
            string = string + op.to_string() + ","

        string = string + ")"

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
        self._hotels = [self._instance.get_hotel_per_index(0), self._instance.get_hotel_per_index(0)]

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

        reverse_delta = Delta([])

        operations = delta.get_operations()

        for operation in operations:
            if isinstance(operation, Remove):
                (obj, trip_index, trip_position_index) = operation.get_operation()

                if self._instance.obj_is_hotel(obj):
                    self._remove_hotel(obj, trip_index, trip_position_index, reverse_delta)

                else:
                    self._remove_customer(obj, trip_index, trip_position_index, reverse_delta)
            elif isinstance(operation, Add):
                (obj, trip_index, trip_position_index) = operation.get_operation()

                if self._instance.obj_is_hotel(obj):
                    self._add_hotel(obj, trip_index, trip_position_index, reverse_delta)
                else:
                    self._add_customer(obj, trip_index, trip_position_index, reverse_delta)
            elif isinstance(operation, Reverse):
                (obj_1, start_trip_index, start_trip_index_position, obj_2, end_trip_index,
                 end_trip_index_position) = operation.get_operation()

                if start_trip_index == end_trip_index and not self._instance.obj_is_hotel(
                        obj_1) and not self._instance.obj_is_hotel(obj_2):
                    self._reverse_customers_from_same_trip(start_trip_index, start_trip_index_position,
                                                           end_trip_index_position)
                else:
                    logger.error("Not supported REVERSE operation:")
                    print(operation)
                    quit()
            elif isinstance(operation, Swap):
                logger.info("Is SWAP")

            else:
                logger.error("Not supported operation")
                print(operation)
                quit()

        return Solution_Worthiness(self._objective_value, self._max_trip_length, self._trips_size, self._prize, delta,
                                   reverse_delta)

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

    def left_neighbor_customer(self, trip_index, trip_index_position):
        trip = self._trips[trip_index]

        if trip_index_position == 0:
            return self._hotels[trip_index]
        else:
            return trip[trip_index_position - 1]

    def right_neighbor_customer(self, trip_index, trip_index_position):
        trip = self._trips[trip_index]

        if trip_index_position == len(trip) - 1:
            return self._hotels[trip_index + 1]
        else:
            return trip[trip_index_position + 1]

    def _reverse_customers_from_same_trip(self, trip_index, start_trip_index_position, end_trip_index_position):

        trip = self._trips[trip_index]
        inst = self._instance

        old_trip_val = self._trip_lengths[trip_index]

        obj_1 = trip[start_trip_index_position]
        obj_2 = trip[end_trip_index_position]

        prev_obj_1 = self.left_neighbor_customer(trip_index, start_trip_index_position)
        post_obj_2 = self.right_neighbor_customer(trip_index, end_trip_index_position)

        delta_minus = - inst.get_distance(prev_obj_1, obj_1) - inst.get_distance(obj_2, post_obj_2)
        delta_plus = inst.get_distance(prev_obj_1, obj_2) + inst.get_distance(obj_1, post_obj_2)

        lower_index = start_trip_index_position
        upper_index = end_trip_index_position

        while lower_index < upper_index:
            tmp = trip[lower_index]
            trip[lower_index] = trip[upper_index]
            trip[upper_index] = tmp

            lower_index = lower_index + 1
            upper_index = upper_index - 1

        sum_of_trips = self._sum_of_trips + delta_minus + delta_plus

        objective_value = sum_of_trips + self._hotel_fees + self._penalties

        max_trip_length = self.calculate_max_trip_length((old_trip_val + delta_minus + delta_plus), old_trip_val,
                                                         [trip_index])

        # ------------- Write to solution ---------
        self._sum_of_trips = sum_of_trips

        self._trip_lengths[trip_index] = old_trip_val + delta_minus + delta_plus

        self._max_trip_length = max_trip_length

        self._objective_value = objective_value

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

            rm_a1 = self._instance.get_distance(old_left_trip[len(old_left_trip) - 1], self._hotels[trip_index + 1])
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

        max_trip_length = self.calculate_max_trip_length((old_trip_val - rm_d1 - rm_d2 + rm_a1), old_trip_val,
                                                         [trip_index - 1, trip_index])

        # ----- SOLUTION CHANGES ----

        reverse_delta.push_operation(Add(obj, trip_index - 1, len(old_left_trip)))

        self._hotels.pop(trip_index)

        new_trip = old_left_trip + old_right_trip  # Concatenate lists

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
            else:  # trip_position_index > 0 and trip_position_index < len(trip) - 1
                rm_a1 = self._instance.get_distance(trip[trip_position_index - 1], trip[trip_position_index + 1])
                rm_d1 = self._instance.get_distance(trip[trip_position_index - 1], obj)
                rm_d2 = self._instance.get_distance(obj, trip[trip_position_index + 1])

            # ---- ONLY CALCULATIONS -----

            prize = self._prize - item.get_prize()
            penalties = self._penalties + obj.get_penalty()

            sum_of_trips = self._sum_of_trips - rm_d1 - rm_d2 + rm_a1

            max_trip_length = self.calculate_max_trip_length((old_trip_value - rm_d1 - rm_d2 + rm_a1), old_trip_value,
                                                             [trip_index])

            objective_value = sum_of_trips + penalties + self._hotel_fees

            # ----- SOLUTION CHANGES ----

            reverse_delta.push_operation(Add(obj, trip_index, trip_position_index))

            self._prize = prize
            self._penalties = penalties

            self._sum_of_trips = sum_of_trips

            self._trip_lengths[trip_index] = old_trip_value - rm_d1 - rm_d2 + rm_a1

            self._max_trip_length = max_trip_length

            trip.pop(trip_position_index)

            self._objective_value = objective_value

            del self._is_customer_served[obj]


        else:
            print(self.to_string())
            print(trip_index)
            print(trip_position_index)
            logger.error("Cannot remove, due to index out of bounds for obj: " + str(obj.get_id()))

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

            for customer_index in range(1, len(new_left)):
                customer_prev = new_left[customer_index - 1]
                customer = new_left[customer_index]

                new_left_val = new_left_val + self._instance.get_distance(customer_prev, customer)

            # Order of the following three lines is important
            new_right_val = old_trip_value - new_left_val - self._instance.get_distance(new_left[len(new_left) - 1],
                                                                                        new_right[0])

            new_left_val = new_left_val + self._instance.get_distance(new_left[len(new_left) - 1], obj)
            new_right_val = new_right_val + self._instance.get_distance(obj, new_right[0])

        # Special Case
        elif len(new_left) == 0:
            new_left_val = self._instance.get_distance(self._hotels[trip_index], obj)
            if len(new_right) == 0:
                # Further Special Case
                new_right_val = self._instance.get_distance(obj, self._hotels[trip_index + 1])
            else:
                new_right_val = old_trip_value - self._instance.get_distance(self._hotels[trip_index], new_right[
                    0]) + self._instance.get_distance(obj, new_right[0])

        # TODO: In O(n)!!!
        elif len(new_right) > 0 and len(new_right) < len(new_left) and len(new_left) > 0:

            new_right_val = self._instance.get_distance(new_right[len(new_right) - 1], self._hotels[trip_index + 1])

            for customer_index in range(1, len(new_right)):
                customer_prev = new_right[customer_index - 1]
                customer = new_right[customer_index]

                new_right_val = new_right_val + self._instance.get_distance(customer_prev, customer)

            new_left_val = old_trip_value - new_right_val - self._instance.get_distance(new_left[len(new_left) - 1],
                                                                                        new_right[0])

            new_right_val = new_right_val + self._instance.get_distance(obj, new_right[0])

            new_left_val = new_left_val + self._instance.get_distance(new_left[len(new_left) - 1], obj)

        else:  # len(right) == 0
            new_right_val = self._instance.get_distance(obj, self._hotels[trip_index + 1])
            if len(new_left) == 0:
                # Further Special Case
                new_left_val = self._instance.get_distance(self._hotels[trip_index], obj)
            else:
                new_left_val = old_trip_value - self._instance.get_distance(new_left[len(new_left) - 1], self._hotels[
                    trip_index + 1]) + self._instance.get_distance(new_left[len(new_left) - 1], obj)

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

        reverse_delta.push_operation(Remove(obj, trip_index + 1, 0))

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
                cur_trip_value = self._instance.get_distance(self._hotels[trip_index],
                                                             obj) + self._instance.get_distance(obj, self._hotels[
                    trip_index + 1])

            elif trip_position_index == 0:
                cur_trip_value = cur_trip_value - self._instance.get_distance(self._hotels[trip_index],
                                                                              trip[0]) + self._instance.get_distance(
                    self._hotels[trip_index], obj) + self._instance.get_distance(obj, trip[0])


            elif trip_position_index > (len(trip) - 1):
                cur_trip_value = cur_trip_value - self._instance.get_distance(trip[len(trip) - 1], self._hotels[
                    trip_index + 1]) + self._instance.get_distance(trip[len(trip) - 1],
                                                                   obj) + self._instance.get_distance(obj, self._hotels[
                    trip_index + 1])

            elif trip_position_index > 0 and trip_position_index <= (len(trip) - 1):
                cur_trip_value = cur_trip_value - self._instance.get_distance(trip[trip_position_index - 1], trip[
                    trip_position_index]) + self._instance.get_distance(trip[trip_position_index - 1],
                                                                        obj) + self._instance.get_distance(obj, trip[
                    trip_position_index])

            # ----- CALCULATIONS -------

            penalties = self._penalties - obj.get_penalty()
            sum_of_trips = self._sum_of_trips + cur_trip_value - old_trip_value

            max_trip_length = self.calculate_max_trip_length(cur_trip_value, old_trip_value, [trip_index])

            prize = self._prize + obj.get_prize()

            objective_value = sum_of_trips + penalties + self._hotel_fees

            # ----- SOLUTION CHANGES ----

            reverse_delta.push_operation(Remove(obj, trip_index, trip_position_index))

            self._penalties = penalties
            self._sum_of_trips = sum_of_trips

            self._trip_lengths[trip_index] = cur_trip_value

            self._max_trip_length = max_trip_length

            self._prize = prize

            trip.insert(trip_position_index, obj)

            self._objective_value = objective_value

            self._is_customer_served[obj] = True

        else:
            logger.error(
                "Cannot insert, due to index out of bounds for obj: " + str(obj.get_id()) + " and trip index: " + str(
                    trip_index) + " and trip index position " + str(trip_position_index))

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

    def get_nearest_unserved_customer(self, location, k):

        remaining = k
        nearest_list = []

        for nearest in self._instance.get_all_nearest_customers(location):
            if not self.is_customer_served(nearest) and self._instance.get_distance(location, nearest) > 0 and k == 0:
                return nearest
            elif not self.is_customer_served(nearest) and self._instance.get_distance(location, nearest) > 0 and k > 0:
                remaining = remaining - 1
                nearest_list.append(nearest)

                if remaining < 0:
                    break

        picked_index = random.randint(0, len(nearest_list) - 1)

        return nearest_list[picked_index]

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

    def slow_objective_values_calculation(self):

        sum_trips = 0
        max_trip_length = 0
        collected_prize = 0
        trips_size = len(self._trips)
        trip_lengths = []

        used = {}

        hotel_fees = 0
        penalties = 0

        for customer in self._instance._customers_list:
            penalties = penalties + customer.get_penalty()

        for trip_index in range(0, len(self._trips)):
            trip = self._trips[trip_index]

            if len(trip) > 0:
                trip_dist = self._instance.get_distance(self._hotels[trip_index], trip[0])

                collected_prize = collected_prize + trip[0].get_prize()
                penalties = penalties - trip[0].get_penalty()

                if trip[0] in used:
                    logger.error("Customer " + str(trip[0].get_id()) + " is used more often than ONCE!")
                else:
                    used[trip[0]] = True

                for trip_index_position in range(1, len(trip)):
                    trip_dist = trip_dist + self._instance.get_distance(trip[trip_index_position - 1],
                                                                        trip[trip_index_position])
                    collected_prize = collected_prize + trip[trip_index_position].get_prize()
                    penalties = penalties - trip[trip_index_position].get_penalty()

                    if trip[trip_index_position] in used:
                        logger.error(
                            "Customer " + str(trip[trip_index_position].get_id()) + " is used more often than ONCE!")
                    else:
                        used[trip[trip_index_position]] = True

                trip_dist = trip_dist + self._instance.get_distance(trip[len(trip) - 1], self._hotels[trip_index + 1])
            else:
                trip_dist = self._instance.get_distance(self._hotels[trip_index], self._hotels[trip_index + 1])

            if trip_dist > max_trip_length:
                max_trip_length = trip_dist

            trip_lengths.append(trip_dist)

            if trip_index > 0 and trip_index < trips_size:
                hotel_fees = hotel_fees + self._hotels[trip_index].get_fee()

            sum_trips = sum_trips + trip_dist

        objective_value = sum_trips + penalties + hotel_fees

        avg_trip_length = 0
        for trip_index in range(len(trip_lengths)):
            avg_trip_length = avg_trip_length + trip_lengths[trip_index]
        avg_trip_length = avg_trip_length / len(trip_lengths)

        return (
            objective_value, sum_trips, penalties, hotel_fees, hotel_fees, max_trip_length, trips_size, collected_prize,
            trip_lengths, avg_trip_length)

    def write_solution_to_file(self, file_path):

        basename = self._instance.get_basename()

        solution_string = ""

        for index in range(len(self._trips)):
            solution_string = solution_string + str(self._hotels[index].get_id()) + " "

            for index_2 in range(len(self._trips[index])):
                solution_string = solution_string + str(self._trips[index][index_2].get_id()) + " "

        solution_string = solution_string + str(self._hotels[len(self._trips)].get_id())

        print(basename)
        print(solution_string)

        output_file = open(file_path + "/solutions/" + basename + ".txt", "w")
        output_file.write(basename + "\n")
        output_file.write(solution_string)

        output_file.close()

        output_file = open(file_path + "/evaluations_of_solutions/" + basename + "_eval.txt", "w")

        output_file.write("Objective_Value: " + str(self._objective_value) + "\n")
        output_file.write("Sum_Trips_Value: " + str(self._sum_of_trips) + "\n")
        output_file.write("Penalties_Value: " + str(self._penalties) + "\n")
        output_file.write("Hotel_Fees_Value:" + str(self._hotel_fees) + "\n")
        output_file.write("-----------------\n")
        output_file.write("C1_Value (Max trip duration):" + str(self._max_trip_length) + "\n")
        output_file.write("C2_Value (Number of trips):" + str(len(self._trips)) + "\n")
        output_file.write("C3_Value (Collected Prize):" + str(self._prize) + "\n")

        output_file.close()
