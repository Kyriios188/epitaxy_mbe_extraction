import datetime
import os
import re
import json
from typing import TextIO

labels_file = open('labels.json', 'r')
labels_json = json.load(labels_file)


class Experiment:
    # The names of the experiments, only present inside log files
    experiment_keywords = ['bragg']
    # The name of the csv and log files with the extension
    file_name: str

    # Start and end of the experiment
    init_time: datetime.datetime
    end_time: datetime.datetime

    rel_init_time: float
    rel_end_time: float
    
    # Total number of layers in the experiment.
    # Configuration steps not included as layers
    n_layers: int = 0

    # The keyword among the experiment keywords that fits the given file. Ex: A1417 is 'bragg'
    experiment_keyword: str
    # The code of the experiment (ex: A1717)
    code: str

    step_list: list = []
    label: float

    def __init__(self, log_file_name: str, experiment_keyword: str):
        self.file_name = log_file_name[:-4]
        self.experiment_keyword = experiment_keyword
        self.code = self.get_experiment_code()
        self.label = self.get_experiment_label()
        

    def get_experiment_keyword(self) -> str:
        """Returns the string like 'Bragg' to identify and group experiments"""

        for e in self.experiment_keywords:
            if e in self.file_name:
                return e
    
    def get_experiment_code(self) -> str:
        """Returns the string like 'A1417'"""
        str_match = re.search('[A-Z]\d{4}', self.file_name)
        if str_match:
            return str_match.group(0)
        
        else:
            return input(
                f"File <{self.file_name}> belongs to {self.experiment_keyword} "
                "yet has no experiment code with format like 'A1420'\nPlease enter the experiment code: "
            )
    
    def get_experiment_label(self) -> float:
        try:
            return labels_json[self.code]
        except KeyError:
            return float(input(f'Please enter the label for experiment {self.code}: '))

    @classmethod
    def is_relevant_experiment(cls, f: TextIO) -> bool:
        """
        Returns True if any experiment keyword is found.
        """

        result = re.search('Loop #\d\/\d', f.read())
        
        f.seek(0)  # Put the cursor back to the beginning so we can read again
        return result is not None

    @classmethod
    def find_relevant_experiment(cls, f: TextIO) -> str:
        """
        If the file is relevant, returns the name of the experiment it is part of.
        Else, returns "".
        """
        file_text = f.read().lower()
        for keyword in Experiment.experiment_keywords:
            if keyword in file_text:
                f.seek(0)
                return keyword


class Step:
    # The label is linked to the experiment
    experiment: Experiment
    # Ex: 0008| 2021/09/24 05:54:07,850| 76.47nm GaAs
    line: str
    line_index: int

    step_number: int

    start: datetime.datetime
    end: datetime.datetime

    rel_start: float
    rel_end: float

    def __init__(self, experiment: Experiment, line: str, line_index: int, initial=None):
        self.experiment = experiment
        self.line = line
        self.line_index = line_index

        self.start = Step.get_timestamp(self.line)
        if not initial:
            self.step_number = Step.get_step_number(self.line)
        else:
            self.step_number = 0
    
    @classmethod
    def get_step_number(cls, line: str) -> int:
        print(line)
        return int(re.search('\d{4}(?=\|)', line).group(0))

    @classmethod
    def is_layer(cls, line: str) -> bool:
        # If we can find '278.89nm' or '278.89 nm' inside the line then it is a layer line
        return re.search('[+-]?([0-9]*[.])?[0-9]+(?= ?nm)', line) is not None
    
    @classmethod
    def get_timestamp(self, line: str) -> datetime.datetime:
        # OwO wat are u doing step data?
        timestamp_str = re.search('\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}:\d{2},\d{3}', line).group(0)
        return datetime.datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S,%f')

    @classmethod
    def identify_line(cls, line: str) -> str:
        """
        Takes a line in lower case and finds what type of line was given.
        """
        # List of (possible_keywords, name)
        step_list: list[tuple[list[str], str]] = [
            (['starting recipe', 'with priority'], 'start'),
            (['mont', 'pour', 'ox'], 'montée déox'),
            (['descente tampon'], 'descente tampon'),
            (['fin tampon'], 'fin tampon'),
            (['tampon'], 'tampon'),  # Must be after the 'descente' and 'fin' or false positive
            (['loop #'], 'loop'),
            (['descente'], 'descente'),
            (['wait'], 'wait'),
            (['end'], 'end')
        ]

        if Step.is_layer(line):
            return 'layer'
        else:
            for step_kwrd in step_list:
                if all(e in line for e in step_kwrd[0]):
                    return step_kwrd[1]
        
        # Find second occurence of | and return what's next
        return line.strip().split('|')[2]


class OtherStep(Step):
    step_type: str

    def __init__(self, experiment: Experiment, line: str, line_index: int, line_type: str, initial=None):
        super(OtherStep, self).__init__(experiment, line, line_index, initial)

        self.step_type = line_type


class Layer(Step):


    # Ex: GaAs
    element: str

    # Percentage of the element (100% if only element)
    percentage: str

    # Size of the layer in nanometers (ex: 76.47)
    size: float

    def __init__(self, experiment: Experiment, line: str, line_index: int):
        super(Layer, self).__init__(experiment, line, line_index)

        self.extract_layer_data()
    
    def extract_layer_data(self):

        # Find a word preceded by 'nm '
        self.element = re.search('(?<=nm )\w*', self.line).group(0)

        # Get a float followed by 'nm' or ' nm'
        self.size = float(re.search('[+-]?([0-9]*[.])?[0-9]+(?= ?nm)', self.line).group(0))

        # Get a float followed by '%'. If no percentage is found, returns 100
        percentage_match = re.search('[+-]?([0-9]*[.])?[0-9]+(?=%)', self.line)
        if percentage_match is None:
            self.percentage = 100
        else:
            self.percentage = float(percentage_match.group(0))
    


mbe_folder_path: str = 'test_mbe_data/'
experiments: 'dict[str, Experiment]' = {}


def main():

    filenames: list[str] = os.listdir(mbe_folder_path)

    for filename in filenames:
        # Useful files with timestamps are .log, can find the csv based on these files
        if filename.endswith('.log'):

            with open(file=mbe_folder_path+filename, mode='r', encoding='utf-8', errors='replace') as f:
                

                if Experiment.is_relevant_experiment(f):
                    
                    # Example: 'Bragg'
                    relevant_experiment: str = Experiment.find_relevant_experiment(f)

                    # The log files are small (<100 lines) and their size is proportional to the number of Layers,
                    # so we can afford to open them multiple times.
                    current_experiment: Experiment = Experiment(
                        log_file_name=filename,
                        experiment_keyword=relevant_experiment
                    )
                    previous_step: Step

                    all_lines = f.readlines()
                    found_start = False
                    found_end = False

                    for i, line in enumerate(all_lines):

                        lower_line: str = line.lower()
                        line_type: str = Step.identify_line(lower_line)

                        if (not found_start and line_type != 'start') or found_end or line_type == 'loop':
                            continue
                            
                        line_timestamp: datetime.datetime = Step.get_timestamp(line)

                        # If there is no previous_step
                        if line_type == 'start':
                            current_experiment.init_time = line_timestamp
                            found_start = True
                            previous_step = OtherStep(
                                experiment=current_experiment,
                                line=line,
                                line_index=i,
                                line_type=line_type,
                                initial=True
                            )

                        # If this is the last step i.e. the step before the ------> Stopped/Completed
                        elif i == len(all_lines) - 2:
                            # Finish the last step
                            found_end = True
                            previous_step.end = line_timestamp
                            current_experiment.step_list.append(previous_step)

                            last_step = OtherStep(
                                experiment=current_experiment,
                                line=line,
                                line_index=i,
                                line_type=line_type
                            )
                            last_step.end = line_timestamp  # This step starts and finishes instantly
                            current_experiment.step_list.append(last_step)

                        # If there is a previous_step from past loop and if it is ot the final line in the file
                        elif i != len(all_lines):
                            # Finish previous step
                            previous_step.end = line_timestamp
                            current_experiment.step_list.append(previous_step)

                            # initialize next step
                            if line_type == 'layer':
                                previous_step = Layer(
                                    experiment=current_experiment,
                                    line=line,
                                    line_index=i
                                )
                                current_experiment.n_layers += 1
                            else:
                                previous_step = OtherStep(
                                    experiment=current_experiment,
                                    line=line,
                                    line_index=i,
                                    line_type=line_type
                                )

                    experiments[filename] = current_experiment

# main()
# for exp in experiments.values():
#    print(vars(exp))
#    for step in exp.step_list:
#        print(vars(step))
