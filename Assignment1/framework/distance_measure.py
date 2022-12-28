
import statistics

class Distance_Measure:


    @classmethod
    def distance_two_solutions(cls, x1, x2):

        instance = x1._instance

        hotel_count_x1 = {}
        hotel_count_x2 = {}
        customer_count_x1 = {}
        customer_count_x2 = {}

        for hotel in instance.get_list_of_hotels():
            hotel_count_x1[hotel.get_id()] = 0
            hotel_count_x2[hotel.get_id()] = 0

        for customer in instance.get_list_of_customers():
            customer_count_x1[customer.get_id()] = 0
            customer_count_x2[customer.get_id()] = 0

        
        hotels_x1 = x1._hotels

        for hotel in hotels_x1:
            hotel_count_x1[hotel.get_id()] = hotel_count_x1[hotel.get_id()] + 1
    
        hotels_x2 = x2._hotels

        for hotel in hotels_x2:
            hotel_count_x2[hotel.get_id()] = hotel_count_x2[hotel.get_id()] + 1
    
        trips_x1 = x1._trips 
    
        for trip in trips_x1:
            for customer in trip:
                customer_count_x1[customer.get_id()] = customer_count_x1[customer.get_id()] + 1
    
 
        trips_x2 = x2._trips 
    
        for trip in trips_x2:
            for customer in trip:
                customer_count_x2[customer.get_id()] = customer_count_x2[customer.get_id()] + 1

        diff_hotels = 0        

        for hotel in instance.get_list_of_hotels():
            diff_hotels += abs(hotel_count_x1[hotel.get_id()] - hotel_count_x2[hotel.get_id()])

        diff_customers = 0        

        for customer in instance.get_list_of_customers():
            diff_customers += abs(customer_count_x1[customer.get_id()] - customer_count_x2[customer.get_id()])

   
        list_x1 = x1.compute_pure_list_representation()

        list_x2 = x2.compute_pure_list_representation()

        diff = 0
    
        for index_x1 in range(len(list_x1) - 1):
            v0_x1 = list_x1[index_x1]
            v1_x1 = list_x1[index_x1 + 1] 


            found = False

            for index_x2 in range(len(list_x2) - 1):
                v0_x2 = list_x2[index_x2]
                v1_x2 = list_x2[index_x2 + 1] 
            
                if v0_x1.get_id() == v0_x2.get_id() and v1_x1.get_id() == v1_x2.get_id():
                    found = True

            if not found:
                diff += 1

     
        for index_x2 in range(len(list_x2) - 1):
            v0_x2 = list_x2[index_x2]
            v1_x2 = list_x2[index_x2 + 1] 


            found = False

            for index_x1 in range(len(list_x1) - 1):
                v0_x1 = list_x1[index_x1]
                v1_x1 = list_x1[index_x1 + 1] 
            
                if v0_x1.get_id() == v0_x2.get_id() and v1_x1.get_id() == v1_x2.get_id():
                    found = True

            if not found:
                diff += 1

        distance = diff_hotels + diff_customers + diff
 
        """
        print("<<<<<<<<<<<<<<<ANALYSIS-OF-TWO-SOLUTIONS>>>>>>>>>>>>>")
        print(x1.to_string())
        print(x2.to_string())
        print(f"Total-Dist:{distance},Diff_Hotels={diff_hotels},Diff_Customers={diff_customers},Diff={diff}")
        print("<<<<<<<<<<<<<<<START>>>>>>>>>>>>>")
        """

        return distance

    @classmethod
    def distances_of_population(cls, population):
       

        dists = []
 
        for index_x1 in range(len(population) - 1):
            x1 = population[index_x1]
        
            for index_x2 in range(index_x1 + 1, len(population)):
                x2 = population[index_x2]

                dist = Distance_Measure.distance_two_solutions(x1, x2)

                dists.append(dist)

        return dists

    @classmethod
    def average_distance_of_population(cls, population):

        dists = Distance_Measure.distances_of_population(population)

        average = sum(dists) / len(dists)

        #print(f"Average Distance of Population:{average}")

        return average 

    @classmethod
    def median_distance_of_population(cls, population):

        dists = Distance_Measure.distances_of_population(population)

        median = statistics.median(dists)

        #print(f"Median Distance of Population:{median}")

        return median


        

                       

            






