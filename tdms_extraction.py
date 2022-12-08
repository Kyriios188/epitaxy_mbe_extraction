from main import experiments, Experiment, Step, main
import pandas
from nptdms import TdmsFile

main()

tdms_file: TdmsFile = TdmsFile("A1417 Recipe Layer Number.tdms")


def get_experiment_object(code: str):
    
    for experiment in experiments.values():
        if experiment.code == code:
            return experiment
    raise ValueError(f'No experiment found for {code}')


code = 'A1417'  # TODO: ask for user input

# TODO: convert every tdms to csv and adapt the code to a loop

df = tdms_file.as_dataframe()
df.to_csv(path_or_buf='result.csv', sep=';')

experiment: Experiment = get_experiment_object(code)

with open('result.csv') as f:
    rel_time_map: dict[int, tuple[float, float]] = {}
    previous_time: float = 0.0

    for line in f.readlines()[1:]:
        tab = line.strip().split(';')
        step_number = int(tab[1])
        layer_start_time = float(tab[2])     
            
        if step_number != 1:
            rel_time_map[step_number-1] = (previous_time, layer_start_time)

            if step_number == len(experiment.step_list) - 1:
                # TODO: get the end of the experiment
                rel_time_map[step_number] = (previous_time, float('inf'))

        previous_time = layer_start_time


for step in experiment.step_list:
    # This step is not present in the log file
    if step.step_number == 0:
        (step.rel_start, step.rel_end) = 0, rel_time_map[1][1]
    else:
        (step.rel_start, step.rel_end) = rel_time_map[step.step_number]



for exp in experiments.values():
   print(vars(exp))
   for step in exp.step_list:
       print(vars(step))