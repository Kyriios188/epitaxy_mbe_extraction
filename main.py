import mbe_get_steps
import tdms_converter
import tdms_extraction
from dataset_env import dataset_env, DatasetEnv
from pickle_results import pickle_results_main


def main():
    mbe_get_steps.get_mbe_steps_main()

    # dataset_env.print_experiment_list()
    # DatasetEnv.clean_folder(dataset_env.tdms_output_folder)

    # # NE FONCTIONNE QUE SI ON MODIFIE LE CODE SOURCE venv/lib/python3.9/site-packages/nptdms/tdms_segment.py/
    # # if self.data_type is types.ExtendedFloat:
    # #     self.data_type.size = 8
    # #     self.data_type = types.DoubleFloat
    # tdms_converter.convert_tdms_files()

    tdms_extraction.tdms_extraction_main()

    # dataset_env.print_experiment_list()
    
    pickle_results_main(dataset_env.experiments)
    
    


if __name__ == '__main__':
    main()
