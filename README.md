# Étapes pour configurer le script

## Construction du venv

Sur Linux : `python -m venv venv & source venv/bin/activate & python -m pip install -r requirements.txt`

Sur Windows : `python -m venv venv & source venv/Scripts/activate & python -m pip install -r requirements.txt`

## Modification code source npTDMS

`cp tdms_segment.py venv/Lib/site-packages/nptdms/tdms_segment.py`

## Création des dossiers manquants

Il faut les dossiers suivants : 
* csv_sensor_data (vide)
* mbe_data (contient tous les ficheirs MBE en vrac)
* sensor_data (contient les dossiers A1417 - A1425)

## Vérification du dataset_env.py et du main.py

* Si csv_sensor_data est vide, décommenter `tdms_converter.convert_tdms_files()` et `DatasetEnv.clean_folder(dataset_env.tdms_output_folder)` dans le `main.py`.
* Vérifier que `mbe_folder_path` vaut 'mbe_data/' et non 'test_mbe_data/'.
* Une fois avoir lancé le script une première fois, si ya eu une erreur dans la génération des csv (OSError de mémoire), débugger et relancer le main.
* Si tout c'est bien passé, recommenter `tdms_converter.convert_tdms_files()` et `DatasetEnv.clean_folder(dataset_env.tdms_output_folder)` dans le `main.py` pour ne pas avoir à générer les csv à chaque fois.

## Lancement du script et obtention des résultats

Juste besoin de vérifier que `dataset_env.print_experiment_list()` n'est pas commenté dans `main.py` puis lancer `python main.py > output.txt`.