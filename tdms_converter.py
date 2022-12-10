import pandas  # Used
import os
from nptdms import TdmsFile

from dataset_env import dataset_env


def convert_tdms_files():

    folder_list = os.listdir(dataset_env.tdms_input_folder)

    for folder_name in folder_list:
        folder_path: str = os.path.join(dataset_env.tdms_input_folder, folder_name)

        if not os.path.isdir(folder_path):
            continue

        folder_files: list[str] = os.listdir(folder_path)
        
        for file in folder_files:
            file_path = os.path.join(folder_path, file)
            _, file_ext = os.path.splitext(file_path)

            if not file_ext == '.tdms':
                continue

            tdms_file: TdmsFile = TdmsFile(file_path)
            df = tdms_file.as_dataframe()
            file_name, _ = os.path.splitext(file)
            output_path: str = os.path.join(dataset_env.tdms_output_folder, file_name+'.csv')
            df.to_csv(path_or_buf=output_path, sep=';', encoding='utf-8')
