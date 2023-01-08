import pickle
import database as db


def pickle_results_main(experiments: dict[str, db.Experiment]):
    
    experiment_list: list[db.Experiment] = []
    for exp in experiments.values():
        experiment_list.append(exp)
    
    with open("database.pkl", "wb") as f:
        pickle.dump(experiment_list, f)
