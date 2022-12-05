from main import experiments, Experiment, Step
import pandas
from nptdms import TdmsFile



tdms_file: TdmsFile = TdmsFile("A1417 Recipe Layer Number.tdms")


def get_experiment_object(code: str):
    
    for experiment in experiments.values():
        if experiment.code == code:
            return experiment
    raise ValueError(f'No experiment found for {code}')


code = 'A1417'  # TODO: ask for user input



df = tdms_file.as_dataframe()
df.to_csv(path_or_buf='result.csv', sep=';')

experiment: Experiment = get_experiment_object

with open('result.csv') as f:
    rel_time_map: dict[int, tuple[float, float]] = {}
    previous_time: float = 0.0

    for line in f.readlines()[1:]:
        tab = line.strip().split(';')
        layer_number = int(tab[1])
        layer_start_time = float(tab[2])

        if layer_number == experiment.n_layers:
            rel_time_map[layer_number] = (previous_time, float('inf'))
            
        elif layer_number != 1:
            rel_time_map[layer_number-1] = (previous_time, layer_start_time)

        previous_time = layer_start_time

for step in experiment.step_list:
    (step.rel_start, step.rel_end) = rel_time_map[step.step_number]
