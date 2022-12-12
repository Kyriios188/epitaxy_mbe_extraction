import os

from database import Experiment, Step
from dataset_env import dataset_env


def get_experiment_object(code: str):
    for experiment in dataset_env.experiments.values():
        if experiment.code == code:
            return experiment
    raise ValueError(f'No experiment found for {code}')


def map_step_to_rel_time(exp: Experiment, file_path: str) -> dict[int, tuple[float, float]]:
    """
    Using the path to a 'AXXX Recipe Number Layer.csv', build a map to link the step number to 
    the relative time start and end.
    
    Step number goes from 0 ('Starting recipe ... with priority x') to n+1 (a step with identical 
    relative start and end to signify the end)
    """

    with open(file_path) as f:
        rel_time_map: dict[int, tuple[float, float]] = {}
        previous_time: float = 0.0

        for line in f.readlines()[1:]:
            tab = line.strip().split(';')
            step_number = int(tab[1])
            layer_start_time = float(tab[2])

            if step_number != 1:
                try:
                    rel_time_map[step_number - 1] = (previous_time, layer_start_time)
                except KeyError:
                    print(f"{exp} : Recipe Layer Number does not have a n°{step_number - 1}")

            previous_time = layer_start_time
    # Can't detect the end since the end is not consistent with the mbe absolute time step number :)
    rel_time_map[step_number] = (layer_start_time, float('inf'))

    return rel_time_map


def link_step_to_rel_time(exp: Experiment, step_to_rel_map: dict[int, tuple[float, float]]):
    """
    Using a map between step number and relative time, sets the relative time
    start and end of every step in the given experiment's list.

    """

    for step in exp.step_list:

        # This step is not present in the log file
        if step.step_number == 0:
            (step.rel_start, step.rel_end) = 0, step_to_rel_map[1][0]
        else:
            try:
                (step.rel_start, step.rel_end) = step_to_rel_map[step.step_number]
            except KeyError:
                pass


def get_csv_list(title: str) -> list[str]:
    """
    Returns the list of filenames with the step and rel times.
    These files are found when they have 'Recipe Layer Number' 
    in their name and are .csv files.

    """

    file_list = os.listdir(dataset_env.tdms_output_folder)
    recipe_file_list: list[str] = []
    for file in file_list:
        file_name, file_ext = os.path.splitext(file)
        if title in file_name and file_ext == '.csv':
            recipe_file_list.append(file)
    return recipe_file_list


def extract_data(file_path: str, icol: int, experiment: Experiment, data_type: str):
    
    attr_dict: dict[str, str] = {
        'Wafer Temperature': 'wafer_temperature',
        'Curvature': 'curvature',
        'Roughness': 'roughness'
    }
        
    previous_step_index = 0
    with open(file_path, 'r') as f:
        all_lines: list[str] = f.readlines()
        for line in all_lines[1:]:
            tab: list[str] = line.strip().split(';')
            
            # Wafer Temperature files have measures after the end of time itself
            if tab[1] is None or tab[1] == '' \
                or tab[icol] is None or tab[icol] == '':              
                    continue
            
            rel_time: float = float(tab[1])
            data: float = float(tab[icol])
            
            # To go fast, we search the right step near where the previous rel_time was

            previous_step_index = experiment.get_step_index_for_rel_time(
                rel_time=rel_time,
                previous_index=previous_step_index
            )
            if previous_step_index is None:
                return
            corresponding_step: Step = experiment.step_list[previous_step_index]
            # Get the right list of the step
            data_list_attr: list[tuple[float, float]] = getattr(
                corresponding_step,
                attr_dict[data_type]
            )
            data_list_attr.append(
                (rel_time, data)
            )


def tdms_extraction_main():
    
    csv_recipe_list: list[str] = get_csv_list('Recipe Layer Number')
    for csv_recipe_file in csv_recipe_list:
        code = csv_recipe_file[:5]
        experiment: Experiment = get_experiment_object(code)
        rel_time_map = map_step_to_rel_time(
            exp=experiment,
            file_path=dataset_env.tdms_output_folder+csv_recipe_file
        )
        link_step_to_rel_time(exp=experiment, step_to_rel_map=rel_time_map)
    
    
    data_file_name: dict[str, int] = {
        'Wafer Temperature': 2,
        'Curvature': 3,
        'Roughness': 2
    }
    for data_name in data_file_name.keys():
        csv_list: list[str] = get_csv_list(data_name)
        for csv_file in csv_list:
            code = csv_file[:5]
            experiment: Experiment = get_experiment_object(code)
            extract_data(
                file_path=dataset_env.tdms_output_folder+csv_file,
                icol=data_file_name[data_name],
                data_type=data_name,
                experiment=experiment
            )
        
    
