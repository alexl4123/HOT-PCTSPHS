import os
import itertools
import random

from scipy import stats
import scikit_posthocs as sp
import numpy as np

from os.path import isfile, join
from pathlib import Path


from framework.input_file_parser import Input_File_Parser

class Hyper_Parameter_Tuning:


    def __init__(self):
        self.tuning_instances_path = "tsp_instances/00_batch_1_2/00_test.txt"


        path = Path(self.tuning_instances_path)
        parser = Input_File_Parser(path)
        instance = parser.load_and_parse_input_file()
        self.instances = [instance]


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

        args_lists = {}
    
        for key in args.keys():
            vals = args[key]

            args_lists[key] = []
            for val in vals:    
                local = {key : val}
                args_lists[key].append(local)
        print(args_lists)

        keys = list(args_lists.keys())
        product = args_lists[keys[0]]

        for index in range(1, len(keys)):

            second = args_lists[keys[index]]
            
            product = list(itertools.product(product, second))

            npi = []

            for item in product:
                i0 = item[0]
                i1 = item[1]
                n = i0

                i1_keys = list(i1.keys())
                if len(i1_keys) > 1:
                    print("MORe KEYS!!!")
                    print(i1)
                    quit()


                n[i1_keys[0]] = i1[i1_keys[0]]

                npi.append(n)

            product = npi


        configurations = product
           
        # F-Race: 
        for i in range(1):
            instance_index = random.randint(0, len(self.instances) - 1)
            instance = self.instances[instance_index]

            results = []

            for config_index in range(len(configurations)):
                config = configurations[config_index]

                config_results = []
    
                for j in range(2):
                    alg = algorithm(instance, config["random_k"])

                    kwargs = config.copy()
                    del kwargs["random_k"]
                    del kwargs["neighborhoods"]

                    result = alg.start_search(None, None, config["neighborhoods"], 9000,**kwargs) 

                    config_results.append(result.get_best_solution().get_fitness_value())

                results.append(config_results)

                       
 
            stats_result = stats.friedmanchisquare(*[r for r in results])

            data = np.array(results)
            
            stats_result_2 = sp.posthoc_nemenyi_friedman(data.T)


            print(results)
            print(stats_result)
            print(stats_result.pvalue)

            print(stats_result_2)


            

              



