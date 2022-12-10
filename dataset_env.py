import glob
import os

from database import Experiment


class DatasetEnv:
    mbe_folder_path: str = 'mbe_data/'
    experiments: 'dict[str, Experiment]' = {}

    tdms_input_folder: str = 'sensor_data/'
    tdms_output_folder: str = 'csv_sensor_data/'

    def print_experiment_list(self):
        for exp in self.experiments.values():
            exp.print_experiment()

    @classmethod
    def clean_folder(cls, folder: str):
        """
        Empties the output of the given folder.

        """

        if folder[-1] != '/':
            folder += '/'

        old_output_files = glob.glob(folder + '*')
        for file in old_output_files:
            os.remove(file)


dataset_env = DatasetEnv()
