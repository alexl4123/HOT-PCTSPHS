import os
import itertools
import random
import time

from datetime import datetime

from functools import partial
from multiprocessing import Pool

from scipy import stats
import scikit_posthocs as sp
import numpy as np

from os.path import isfile, join
from pathlib import Path


from framework.input_file_parser import Input_File_Parser

from search_algorithms.ga.ga_solution import GA_Solution



class Benchmark:

    def __init__(self, path_to_repository = "./", output_path = "benchmark.csv"):

        
        """
        self.test_instances_path = path_to_repository + "tsp_instances/00_batch_1_2/00_test.txt"
        path = Path(self.test_instances_path)
        parser = Input_File_Parser(path)
        instance = parser.load_and_parse_input_file()
        self.instances = [instance]
        """

        self.output_path = output_path
        self.alpha = 0.05
        self.iterations_per_alg = 20

        # Two batches of instances are added below!

        self.instances = []

        # Add default batch
        self.test_instances_path = path_to_repository + "tsp_instances/00_batch_1_2/"

        for f in os.listdir(self.test_instances_path):
            path = Path(join(self.test_instances_path, f))


            parser = Input_File_Parser(path)
            instance = parser.load_and_parse_input_file()
            self.instances.append(instance)

        self.test_instances_path = path_to_repository + "tsp_instances/03_competition_instance/"

        # Add competition batch
        for f in os.listdir(self.test_instances_path):
            path = Path(join(self.test_instances_path, f))


            parser = Input_File_Parser(path)
            instance = parser.load_and_parse_input_file()
            self.instances.append(instance)


    def perform(self, algorithm, config, solution_result_path = "."):
        print("PERFORM BENCHMARK")

        csv_file = open(self.output_path, "w")
        self.initialize_csv_file(csv_file, config)
        csv_file.close()


        iteration = 0
        for instance in self.instances:
            print(f">>>INSTANCE-NAME:{instance.get_instance_name()}")
            str_time = (datetime.now()).strftime("%Y%m%d:%H:%M:%S")
            print(f">>>CURRENT-TIME:{str_time}")
            results = []

            with Pool(self.iterations_per_alg + 1) as p:
                results = p.map(partial(self.pool_function, config = config, algorithm = algorithm, instance = instance), range(self.iterations_per_alg))

            writeable_results = []
            for result in results:
                writeable_results.append(result.get_fitness_value())

            csv_file = open(self.output_path, "a")
            str_time = (datetime.now()).strftime("%Y%m%d:%H:%M:%S")
            self.write_configuration_to_file(csv_file, config, iteration, instance, str_time,writeable_results)
            csv_file.close()


            best_sol = None
            for result in results:
                if not best_sol or result.get_fitness_value() > best_sol.get_fitness_value():
                    best_sol = result

            best_sol.write_solution_to_file(solution_result_path)

            iteration += 1

    def initialize_csv_file(self, f, configuration):

        keys = list(configuration.keys())

        string = ""
        for index in range(len(keys)):
            key = keys[index]

            string += str(key) + ","

        string += "iteration,instance,starting-time\n"

        f.write(string)


    def write_configuration_to_file(self, f, configuration, iteration, instance, time, results):

        string = self.configuration_to_csv_row(configuration)

        res_string = "["
        for res_index in range(len(results)):
            res_string += str(results[res_index])

            if res_index < len(results) - 1:
                res_string += ";"
        res_string += "]"

        f.write(string + ',' + str(iteration) + ',' + str(instance.get_instance_name()) + ',' + str(time) + ',' + res_string + '\n')

        
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

        alg = algorithm(instance, config["random_k"])

        neighborhoods = None

        kwargs = config.copy()
        if "random_k" in kwargs:
            del kwargs["random_k"]
        if "neighborhoods" in kwargs:
            neighborhoods = kwargs["neighborhoods"]
            del kwargs["neighborhoods"]
        if "type" in kwargs:
            del kwargs["type"]
        if "alpha" in kwargs:
            alpha = kwargs["alpha"]
            del kwargs["alpha"]
        if "beta" in kwargs:
            beta = kwargs["beta"]
            del kwargs["beta"]
        if "gamma" in kwargs:
            gamma = kwargs["gamma"]
            del kwargs["gamma"]
        if "delta" in kwargs:
            delta = kwargs["delta"]
            del kwargs["delta"]

        if hasattr(alg, "set_alpha_beta_gamma_delta"):
            alg.set_alpha_beta_gamma_delta(alpha, beta, gamma, delta)

        result = alg.start_search(None, None, neighborhoods, 9000, output = False, **kwargs) 
        sol = result.get_best_solution()

        return result.get_best_solution()
 



