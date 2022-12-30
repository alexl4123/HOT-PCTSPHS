import os
import itertools
import random

from functools import partial
from multiprocessing import Pool

from scipy import stats
import scikit_posthocs as sp
import numpy as np

from os.path import isfile, join
from pathlib import Path


from framework.input_file_parser import Input_File_Parser

from search_algorithms.ga.ga_solution import GA_Solution

class Hyper_Parameter_Tuning:


    def __init__(self, path_to_repository = "./", output_path = "hpt.csv"):
        self.tuning_instances_path = path_to_repository + "tsp_instances/00_batch_1_2/00_test.txt"

        self.output_path = output_path

        path = Path(self.tuning_instances_path)
        parser = Input_File_Parser(path)
        instance = parser.load_and_parse_input_file()
        self.instances = [instance]

        self.alpha = 0.05
        self.iterations_per_alg = 5


        """
        self.tuning_instances_path = "tsp_instances/01_tuning_instances"

        self.instances = []
        
        for f in os.listdir(self.tuning_instances_path):
            path = Path(join(self.tuning_instances_path, f))


            parser = Input_File_Parser(path)
            instance = parser.load_and_parse_input_file()
            self.instances.append(instance)
            break

        """

    def perform(self, algorithm, args):

        # Generate configurations
        args_lists = {}
    
        for key in args.keys():
            vals = args[key]

            args_lists[key] = []
            for val in vals:    
                local = {key : val}
                args_lists[key].append(local)

        keys = list(args_lists.keys())
        product = args_lists[keys[0]]

        for index in range(1, len(keys)):

            second = args_lists[keys[index]]
            
            product = list(itertools.product(product, second))

            npi = []

            for item in product:
                i0 = item[0]
                i1 = item[1]
                n = i0.copy()

                i1_keys = list(i1.keys())
                if len(i1_keys) > 1:
                    print("MORe KEYS!!!")
                    print(i1)
                    quit()


                n[i1_keys[0]] = i1[i1_keys[0]]

                npi.append(n)

            product = npi


        # Perform Racing (F-RACE)

        configurations = product

        csv_file = open(self.output_path, "w")
        self.initialize_csv_file(csv_file, configurations)

        # F-Race: 
        max_iterations = 2
        iteration = 0
        while iteration < max_iterations:
            if len(configurations) < 3:
                # As otherwise Friedman test doesn't work anymore
                break
        
            print(f">>>RACE-ITERATION-{iteration}")
            print(f">>>CURRENT-CONFIGURATIONS:{len(configurations)}")
            print(configurations)

            self.write_configurations_to_file(csv_file, configurations, iteration)

            instance_index = random.randint(0, len(self.instances) - 1)
            instance = self.instances[instance_index]

            results = []

            for config_index in range(len(configurations)):
                config = configurations[config_index]
                config_results = []


                with Pool(self.iterations_per_alg + 1) as p:
                    config_results = p.map(partial(self.pool_function, config = config, algorithm = algorithm, instance = instance), range(self.iterations_per_alg))

                results.append(config_results)
 
            stats_result = stats.friedmanchisquare(*[r for r in results])

            print(stats_result)

            if stats_result.pvalue < self.alpha:
                data = np.array(results) 
                
                stats_result_2 = sp.posthoc_nemenyi_friedman(data.T)
            
                print(stats_result_2)

                highest_index_avg = -1
                highest_avg = None

                for index in range(len(results)):
                    s = results[index]
                    avg = sum(s)/len(s)

                    if not highest_avg:
                        highest_avg = avg
                        highest_index_avg = index
                    elif avg > highest_avg:
                        highest_avg = avg
                        highest_index_avg = index


                for index in range(len(results)):
                    if index == highest_index_avg:
                        continue
                    
                    val = stats_result_2[highest_index_avg][index]

                    if val < self.alpha:
                        configurations.pop(index)

            iteration += 1


        print(configurations)
        self.write_configurations_to_file(csv_file, configurations, iteration)
        csv_file.close()

    def initialize_csv_file(self, f, configurations):
        configuration = configurations[0]

        keys = list(configuration.keys())

        string = ""
        for index in range(len(keys)):
            key = keys[index]

            string += str(key) + ","

        string += "iteration\n"

        f.write(string)


    def write_configurations_to_file(self, f, configurations, iteration):

        for configuration in configurations:

            string = self.configuration_to_csv_row(configuration)

            f.write(string + ',' + str(iteration) + '\n')

        
    def configuration_to_csv_row(self, configuration):

        string = ""

        keys = list(configuration.keys())

        for index in range(len(keys)):
            key = keys[index]

            if key == "saw_policy":
                string += configuration[key].to_string() 
            elif key == "neighborhoods":
                string += "["
                for neighborhood in configuration[key]:
                    string += neighborhood.to_string() + ";"

                string += "]"
            else:
                string += str(configuration[key])

            if index < len(keys) - 1:
                string += ","

        return string

    def pool_function(self, j, config = None, algorithm = None, instance = None):
        
        config_results = None


        if config["type"] == "algorithm":
            alg = algorithm(instance, config["random_k"])

            kwargs = config.copy()
            del kwargs["random_k"]
            del kwargs["neighborhoods"]

            result = alg.start_search(None, None, config["neighborhoods"], 9000, output = False, **kwargs) 
            sol = result.get_best_solution()

            print(sol.get_objective_value())
            print(sol.slow_objective_values_calculation())
            print(sol.get_fitness_value())
            print(sol.to_string())

            config_results = (result.get_best_solution().get_fitness_value())
        elif config["type"] == "initialization":

            saw_policy = config["saw_policy"]
            termination_criterion = config["termination_criterion"]

            fitness_function = saw_policy.create_appropriate_fitness_function(instance, termination_criterion)


            population_size = config["population_size"]

            random_k = config["random_k"]

            cur_results = []

            randomized_procedure = algorithm(instance, fitness_function = fitness_function, alpha = config["alpha"], beta = config["beta"], gamma = config["gamma"], delta = config["delta"])

            iteration_2 = 0
            while len(cur_results) < population_size:
                result = randomized_procedure.create_solution(iteration_2, random_k = random_k, show_output = False, max_runtime = 600)
                if result.get_best_solution():
                    ga_solution = GA_Solution.from_solution(result.get_best_solution(), fitness_function = fitness_function)

                    cur_results.append(ga_solution.get_fitness_value())

                iteration_2 += 1

            average = sum(cur_results)/len(cur_results)

            config_results = (average)

        return config_results
    
    def configs_equal(self, prev_configs, configurations):

        equals = True

        for config_0 in configurations:

            found = False

            for config_1 in prev_configs:
                if config_0 == config_1: #As the objects should have the same reference, this should work
                    found = True
                    break

            equals = equals & found

        return equals

              



