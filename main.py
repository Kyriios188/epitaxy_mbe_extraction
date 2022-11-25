import datetime
import os
import re
import json
from typing import TextIO

labels_file = open('labels.json', 'r')
labels_json = json.dumps(labels_file.read())


# TODO: implement
def get_datetime_from_str(line: str) -> datetime.datetime:
    return datetime.datetime.now()


class Experiment:
    # The names of the experiments, only present inside log files
    expirement_keywords = ['bragg']
    # The name of the csv and log files with the extension
    file_name: str

    # Start and end of the experiment
    init_time: datetime.datetime
    end_time: datetime.datetime
    
    # Total number of layers in the experiment.
    # Configuration steps not included as layers
    n_layers: int
    # The keyword among the experiment keywords that fits the given file. Ex: A1417 is 'bragg'
    expirement_keyword: str
    # The code of the experiment (ex: A1717)
    code: str

    # TODO: add list of other steps (wait, init, tampon)
    layers_list: list
    label: float

    def __init__(self, log_file_name: str):
        self.file_name = log_file_name[:-3]
        self.n_layers = 1
        self.code = self.get_experiment_code()
        self.label = self.get_experiment_label()
    
    def get_experiment_code(self) -> str:
        str_match = re.search('[A-Z]\d{4}', self.file_name)
        if str_match:
            return str_match
        
        else:
            return input(
                f"File <{self.file_name}> belongs to {self.expirement_keyword} "
                "yet has no experiment code with format like 'A1420'\nPlease enter the experiment code: "
            )
    
    def get_experiment_label(self) -> float:
        try:
            code: str = labels_json[self.code]
        except KeyError:
            self.label = input(f'Please enter the label for experiment {code}: ')

    @classmethod
    def is_relevant_experiment(cls, f: TextIO) -> str:
        """
        Returns True if any experiment keyword is found.
        """
        
        return any(keyword in f.read().lower() for keyword in Experiment.expirement_keywords)

    @classmethod
    def find_relevant_experiment(cls, f: TextIO) -> str:
        """
        If the file is relevant, returns the name of the experiment it is part of.
        Else, returns "".
        """
        file_text = f.read().lower()
        for keyword in Experiment.expirement_keywords:
            if keyword in file_text:
                return keyword


class Layer:

    # The label is linked to the experiment
    experiment: Experiment
    # Ex: 0008| 2021/09/24 05:54:07,850| 76.47nm GaAs
    line: str
    line_index: int


    # Ex: GaAs
    element: str

    # Percentage of the element (100% if only element)
    percentage: str

    # Size of the layer in nanometers (ex: 76.47)
    size: float

    start: datetime.datetime
    end: datetime.datetime

    def __init__(self, experiment: Experiment, line: str, line_index: int):
        self.experiment = experiment
        self.line = line
        self.line_index = line_index

        self.extract_layer_data()
    
    def extract_layer_data(self):

        # Find a word preceded by 'nm '
        self.element = re.search('(?<=nm )\w*', self.line)

        # Get a float followed by 'nm' or ' nm'
        self.size = float(re.search('[+-]?([0-9]*[.])?[0-9]+(?= ?nm)', self.line).group(0))

        # Get a float followed by '%'. If no percentage is found, returns 100
        percentage_match = re.search('[+-]?([0-9]*[.])?[0-9]+(?=%)', self.line)
        if percentage_match is None:
            self.percentage = 100
        else:
            self.percentage = float(percentage_match.group(0))

        timestamp_str = re.search('\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}:\d{2},\d{3}', self.line).group(0)
        self.start = datetime.datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S,%f')
    
    @classmethod
    def is_layer(cls, line: str) -> bool:
        # If we can find '278.89nm' or '278.89 nm' inside the line then it is a layer line
        return re.search('[+-]?([0-9]*[.])?[0-9]+(?= ?nm)', line) is not None



mbe_folder_path: str = 'mbe_data\\'
experiments: dict[str, Experiment] = {}


def main():

    filenames: list[str] = os.listdir(mbe_folder_path)

    for filename in filenames:
        # Useful files with timestamps are .log, can find the csv based on these files
        if filename.endswith('.log'):

            with open(file=mbe_folder_path+filename, mode='r') as f:

                if Experiment.is_relevant_experiment(f):

                    # The log files are small (<100 lines) and their size is proportional to the number of Layers,
                    # so we can afford to open them multiple times.
                    current_experiment: Experiment = Experiment(log_file_name=filename)
                    current_layer: Layer = Layer(experiment=current_experiment)

                    all_lines = f.readlines()
                    for i, line in enumerate(all_lines):

                        # If we find the experiment start
                        # TODO: use a regexp for this
                        if '#1/' in line.lower():
                            current_experiment.init_time = get_datetime_from_str(all_lines[i+1])
                            # The start of the first Layer is the init of the experiment
                            # TODO: verify that the start of the first Layer is the i+1 of the Loop #1
                            current_layer.start = current_experiment.init_time

                        # If we find the end of the experiment
                        elif 'descente' in line.lower():
                            # TODO: verify that keyword 'Descente' is one line after the end of the Layer
                            #  use the length of the Layer to predict the end of the final Layer?
                            current_layer.end = get_datetime_from_str(all_lines[i-1])
                            current_experiment.layers_list.append(current_layer)

                        # If we find a new Layer, and it does not contain '#1/', then it is the end of the previous
                        # Layer and the start of the next Layer
                        elif 'loop' in line.lower():
                            # TODO: verify that the i+1 timestamp is indeed the end of the i Layer
                            current_layer.end = get_datetime_from_str(all_lines[i+1])
                            current_experiment.layers_list.append(current_layer)
                            # Create next Layer
                            current_layer = Layer(experiment=current_experiment)
                            current_layer.start = get_datetime_from_str(all_lines[i+1])
