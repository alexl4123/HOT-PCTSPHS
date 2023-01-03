

class Statistical_Test:

    def __init__(self, path_to_repository = "./", output_path = "stat_test.csv"):

        
        """
        self.test_instances_path = path_to_repository + "tsp_instances/00_batch_1_2/00_test.txt"
        path = Path(self.test_instances_path)
        parser = Input_File_Parser(path)
        instance = parser.load_and_parse_input_file()
        self.instances = [instance]
        """

        self.output_path = output_path
        self.alpha = 0.05
        self.iterations_per_alg = 10


        self.test_instances_path = path_to_repository + "tsp_instances/02_test_instances_after_"

        self.instances = []
        for f in os.listdir(self.test_instances_path):
            path = Path(join(self.test_instances_path, f))


            parser = Input_File_Parser(path)
            instance = parser.load_and_parse_input_file()
            self.instances.append(instance)

    def perform(self, algorithm, args):
        print("PERFORM")
        print(args)

        csv_file = open(self.output_path, "w")
        self.initialize_csv_file(csv_file, configurations)
        csv_file.close()


        for instance in self.instances:
            print(f">>>INSTANCE-NAME:{instance.get_instance_name()}")
            str_time = (datetime.now()).strftime("%Y%m%d:%H:%M:%S")
            print(f">>>CURRENT-TIME:{str_time}")
            results = []

            with Pool(self.iterations_per_alg + 1) as p:
                results = p.map(partial(self.pool_function, config = config, algorithm = algorithm, instance = instance), range(self.iterations_per_alg))

            csv_file = open(self.output_path, "a")
            str_time = (datetime.now()).strftime("%Y%m%d:%H:%M:%S")
            self.write_configuration_to_file(csv_file, config, iteration, instance, str_time,results)
            csv_file.close()




