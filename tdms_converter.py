import pandas  # Used
import os
from nptdms import TdmsFile

tdms_input_folder: str = 'sensor_data/'
tdms_output_folder: str = 'csv_sensor_data/'


def convert_tdms_files():
    tdms_files = os.listdir(tdms_input_folder)
    for file in tdms_files:
        file_name, file_ext = os.path.splitext(file)
        if file_ext == '.tdms':

            tdms_file: TdmsFile = TdmsFile(tdms_input_folder+file)

            df = tdms_file.as_dataframe()
            output_path: str = os.path.join(tdms_output_folder, file_name+'.csv')
            df.to_csv(path_or_buf=output_path, sep=';')

convert_tdms_files()
