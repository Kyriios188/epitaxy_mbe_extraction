import datetime
import os
from typing import TextIO


# TODO: implement
def get_datetime_from_str(line: str) -> datetime.datetime:
    return datetime.datetime.now()


class Experiment:
    log_file_name: str
    csv_file_name: str

    init_time: datetime.datetime
    n_cycles: int

    cycles: list

    def __init__(self, log_file_name: str):
        self.experiment = log_file_name
        # TODO: verify that
        self.csv_file_name = log_file_name[:-3] + 'csv'
        self.n_cycles = 1

    @classmethod
    def is_relevant_experiment(cls, f: TextIO):
        return 'loop' in f.read().lower()


class Cycle:
    experiment: Experiment
    start: datetime.datetime
    end: datetime.datetime
    label: float

    def __init__(self, experiment: Experiment):
        self.experiment = experiment


mbe_folder_path: str = 'mbe_data\\'
experiments: dict[str, Experiment] = {}


def main():

    filenames: list[str] = os.listdir(mbe_folder_path)

    for filename in filenames:
        # Useful files with timestamps are .log, can find the csv based on these files
        if filename.endswith('.log'):

            with open(file=mbe_folder_path+filename, mode='r') as f:

                if Experiment.is_relevant_experiment(f):

                    # The log files are small (<100 lines) and their size is proportional to the number of cycles,
                    # so we can afford to open them multiple times.
                    current_experiment: Experiment = Experiment(log_file_name=filename)
                    current_cycle: Cycle = Cycle(experiment=current_experiment)

                    all_lines = f.readlines()
                    for i, line in enumerate(all_lines):

                        # If we find the experiment start
                        # TODO: use a regexp for this
                        if '#1/' in line.lower():
                            current_experiment.init_time = get_datetime_from_str(all_lines[i+1])
                            # The start of the first cycle is the init of the experiment
                            # TODO: verify that the start of the first cycle is the i+1 of the Loop #1
                            current_cycle.start = current_experiment.init_time

                        # If we find the end of the experiment
                        elif 'descente' in line.lower():
                            # TODO: verify that keyword 'Descente' is one line after the end of the cycle
                            #  use the length of the cycle to predict the end of the final cycle?
                            current_cycle.end = get_datetime_from_str(all_lines[i-1])
                            current_experiment.cycles.append(current_cycle)

                        # If we find a new Cycle, and it does not contain '#1/', then it is the end of the previous
                        # cycle and the start of the next cycle
                        elif 'loop' in line.lower():
                            # TODO: verify that the i+1 timestamp is indeed the end of the i cycle
                            current_cycle.end = get_datetime_from_str(all_lines[i+1])
                            current_experiment.cycles.append(current_cycle)
                            # Create next cycle
                            current_cycle = Cycle(experiment=current_experiment)
                            current_cycle.start = get_datetime_from_str(all_lines[i+1])
