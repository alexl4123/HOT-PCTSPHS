from pathlib import Path

class Result:

    def __init__(self, best_solution, trace, needed_time):
        self._best_solution = best_solution
        self._trace = trace
        self._needed_time = needed_time

    def get_best_solution(self):
        return self._best_solution

    def get_trace(self):
        return self._trace

    def get_time(self):
        return self._needed_time

    def write_result_metadata_to_file(self, file_path, header_line, content_line, instance = None):

        if self._best_solution:
            basename = self._best_solution._instance.get_basename()
            instance_name = self._best_solution._instance.get_instance_name()
        elif instance:
            basename = instance.get_basename()
            instance_name = instance.get_instance_name()
        else:
            print("NOT ALLOWED WHILE WRITE METADATA")

        # Just for abbrevation purposes
        solution = self._best_solution

        path_str = file_path + "/evaluations_of_solutions/analysis.csv"
        path = Path(path_str)

        add_first_line = False
        if not path.is_file():
            add_first_line = True


        output_file = open(path_str, "a")

        if add_first_line:
            header_line_str = ""
            for index in range(len(header_line) - 1):
                header_line_str += header_line[index] + ","

            header_line_str += header_line[len(header_line) - 1] + "\n"

            output_file.write(header_line_str)

        
        content_line_str = ""
        for index in range(len(content_line) - 1):
            content_line_str += content_line[index] + ","

        content_line_str += content_line[len(content_line) - 1] + "\n"

        output_file.write(content_line_str)

        output_file.close()


