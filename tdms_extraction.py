from main import experiments, Experiment, Step, main

main()


def get_experiment_object(code: str):
    
    for experiment in experiments.values():
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
                rel_time_map[step_number-1] = (previous_time, layer_start_time)

                if step_number == len(exp.step_list) - 1:
                    # TODO: get the end of the experiment
                    rel_time_map[step_number] = (previous_time, float('inf'))

            previous_time = layer_start_time

    return rel_time_map
    

def link_step_to_rel_time(exp: Experiment, step_to_rel_map: dict[int, tuple[float, float]]):
    """
    Using a map between step number and relative time, sets the relative time
    start and end of every step in the given experiment's list.

    """
    
    for step in exp.step_list:
        # This step is not present in the log file
        if step.step_number == 0:
            (step.rel_start, step.rel_end) = 0, step_to_rel_map[1][1]
        else:
            (step.rel_start, step.rel_end) = step_to_rel_map[step.step_number]


def get_recipe_layer_number_list():
    pass


# TODO: loop through files like 'A1417 Recipe Layer Number.csv'

code = 'A1417'  # TODO: get it from file name
experiment: Experiment = get_experiment_object(code)
rel_time_map = map_step_to_rel_time(exp=experiment, file_path='result.csv')
link_step_to_rel_time(exp=experiment, step_to_rel_map=rel_time_map)

for exp in experiments.values():
   exp.print_experiment()