
class Fitness_Function:

    g_max = 0
    g_min = 0


    def __init__(self, instance, max_gamma_1, max_gamma_2, max_gamma_3, gamma_1 = 1, gamma_2 = 1, gamma_3 = 1):
        self._instance = instance

        self._max_gamma_1 = max_gamma_1
        self._max_gamma_2 = max_gamma_2
        self._max_gamma_3 = max_gamma_3

        self._gamma_1 = gamma_1
        self._gamma_2 = gamma_2
        self._gamma_3 = gamma_3

        # These values are set by ''precompute_necessary_values'' 
        self._max_dist = 0
        self._sum_penalties = 0
        self._sum_prizes = 0
        self._max_penalty = 0
        self._min_prize = 0
        self._max_fee = 0

        self._precompute_necessary_values()

        Fitness_Function.g_min = self.compute_g_min()
        Fitness_Function.g_max = self.compute_g_max()

    def set_gamma_1(self, gamma_1):
        self._gamma_1 = gamma_1
    
    def set_gamma_2(self, gamma_2):
        self._gamma_2 = gamma_2

    def set_gamma_3(self, gamma_3):
        self._gamma_3 = gamma_3

    def _precompute_necessary_values(self):

        max_dist = 0

        customer_list = self._instance.get_list_of_customers()
        hotel_list = self._instance.get_list_of_hotels()

        # Compute max distance between two vertices:
        for customer_0_index in range(len(customer_list)):

            customer_0 = customer_list[customer_0_index]

            for customer_1_index in range(customer_0_index + 1, len(customer_list)):
                customer_1 = customer_list[customer_1_index]

                c_0_1_dist = self._instance.get_distance(customer_0, customer_1)

                if c_0_1_dist > max_dist:
                    max_dist = c_0_1_dist

            for hotel in hotel_list:
                dist_0_h = self._instance.get_distance(customer_0, hotel)

                if dist_0_h > max_dist:
                    max_dist = dist_0_h

        for hotel_0_index in range(len(hotel_list)):
            hotel_0 = hotel_list[hotel_0_index]

            for hotel_1_index in range(hotel_0_index + 1, len(hotel_list)):
                hotel_1 = hotel_list[hotel_1_index]

                h_0_1_dist = self._instance.get_distance(hotel_0, hotel_1)

                if h_0_1_dist > max_dist:
                    max_dist = h_0_1_dist

        self._max_dist = max_dist

        # Compute sum of penalties, max penalty and min prize:
        sum_penalties = 0
        max_penalty = 0

        sum_prizes = 0
        min_prize = -1

        for customer in customer_list:

            p = customer.get_penalty()

            if p > max_penalty:
                max_penalty = p
        
            sum_penalties += p

            prz = customer.get_prize()

            if min_prize == -1 or min_prize > prz:
                min_prize = prz

            sum_prizes += prz

        self._sum_penalties = sum_penalties
        self._max_penalty = max_penalty
        self._min_prize = min_prize
        self._sum_prizes = sum_prizes

        # Compute max hotel fee:
        max_fee = 0

        for hotel in self._instance.get_list_of_hotels():
            if hotel.get_fee() > max_fee:
                max_fee = hotel.get_fee()

        self._max_fee = max_fee

    def compute_g_max(self):
        """
            In detail pretty complicated, but in general it computes four things and then adds them up:
            0.) A value, s.t. this value is to a very high likelihood bigger than the maximum value of a correct solution
            1.) A value s.t. this value is greater than the max constraint 1 violation value
            2.) A value s.t. this value is greater than the max constraint 2 violation value
            3.) A value s.t. this value is greater than the max constraint 3 violation value

        """


        # Assuming lockstep between hotels and customers -> this is an upper bound for distance
        t0 = len(self._instance.get_list_of_customers()) + 1
        t0 = t0 * (self._max_dist * 2 + self._max_fee)
        t0 = t0 + self._sum_penalties

        t1 = self.compute_psi_1(self._max_dist *  len(self._instance.get_list_of_customers()) + 1) * self._max_gamma_1

        t2 = self.compute_psi_2(2 * self._instance.get_C2(), t0) * self._max_gamma_2

        t3 = self.compute_psi_3(0) * self._max_gamma_3

        return t0 + t1 + t2 + t3

    def compute_g_min(self):
        """
            As trips >= 0, penalties >= 0 and fees >= 0; it must be 0
        """
        return 0


    def compute_psi_1(self, maximum_trip_length):

        if maximum_trip_length <= self._instance.get_C1():
            return 0

        t0 = (self._max_fee + self._max_dist) * (maximum_trip_length / self._instance.get_C1())

        return t0

    def compute_psi_2(self, number_of_trips, solution_obj_value):

        if number_of_trips <= self._instance.get_C2():
            return 0

        t0 = (self._max_fee + self._max_dist + solution_obj_value) * (number_of_trips - self._instance.get_C2())

        return t0

    def compute_psi_3(self, collected_prize):
        
        if collected_prize >= self._instance.get_C3():
            return 0
        
        t0 = ((self._instance.get_C3() - collected_prize) / self._min_prize) * (self._max_dist * self._max_fee)

        return t0


    def compute_fitness(self, solution):
        """
            Given a solution it computes the fitness value, basically according to the following function:
            f(i) = g_{max} - [(g(i) + g_{min}) + \gamma_1 \Psi_1(i) + \gamma_2 \Psi_2(i) + \gamma_3 \Psi_3(i)]

            Where
        """

        

        if solution.get_objective_value() < 0:
            print("<<<<<!!!!!SET-NEW-MIN-VALUE-FOR-FITNESS-FUNCTION!!!!!!>>>>>>>>")
            Fitness_Function.g_min = solution.get_objective_value()

        if solution.get_objective_value() > Fitness_Function.g_max:
            print("<<<<<!!!!!SET-NEW-MAX-VALUE-FOR-FITNESS-FUNCTION!!!!!!>>>>>>>>")
            Fitness_Function.g_max = solution.get_objective_value()

        t0 = solution.get_objective_value() + Fitness_Function.g_min
        t1 = self._gamma_1 * self.compute_psi_1(solution._max_trip_length)
        t2 = self._gamma_2 * self.compute_psi_2(solution._trips_size, solution.get_objective_value())
        t3 = self._gamma_3 * self.compute_psi_3(solution._prize)

        if (t0 + t1 + t2 + t3) > Fitness_Function.g_max:
            Fitness_Function.g_max = (t0 + t1 + t2 + t3)

        t4 = Fitness_Function.g_max - (t0 + t1 + t2 + t3)

        """
        print("T0::" + str(t0))
        print("T1::" + str(t1))
        print("T2::" + str(t2))
        print("T3::" + str(t3))
        print("T4::" + str(t4))
        """


        return t4




