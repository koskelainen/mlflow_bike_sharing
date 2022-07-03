import argparse
import itertools
import pathlib
import sys
import warnings
from typing import Text

import mlflow
import numpy as np
from mlflow.models.signature import infer_signature
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold, cross_val_score

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))
warnings.filterwarnings('ignore')

from src.config.config import RANDOM_STATE
from src.utils.utils import load_yaml, load_dataset, path_resolve, remove_file
from src.config.config import ESTIMATORS_MAPPER
from src.features.features import model_feature_importance, model_permutation_importance
from src.mlflow_client.client import set_mlflow_client


def rmse(y, y_pred):
    return np.sqrt(mean_squared_error(y, y_pred))


def rmsle_cv(model, X_train, y_train, random_state):
    """calculate a score by cross-validation"""
    kf = KFold(n_splits=3, shuffle=True, random_state=random_state).get_n_splits(X_train.values)
    return np.sqrt(-cross_val_score(model, X_train.values, y_train, scoring="neg_mean_squared_error", cv=kf))


def training_grid_search(config_path: Text, base_config_path: Text):
    config = load_yaml(config_path)  # type: dict
    base_config = load_yaml(base_config_path)  # type: dict
    models_dir = base_config["base"]["model"]["models_folder"]
    path_to_models = path_resolve(pathlib.Path().joinpath(*models_dir))
    path_feature_importance = path_to_models.joinpath("feature_importance.png")
    path_permutation_importance = path_to_models.joinpath("permutation_importance.png")
    random_state = int(config.get("random_state", RANDOM_STATE))

    X_train = load_dataset(file_path=base_config["split_train_test"]['x_train_csv'])
    X_test = load_dataset(file_path=base_config["split_train_test"]['x_test_csv'])
    y_train = load_dataset(file_path=base_config["split_train_test"]['y_train_csv'])
    y_test = load_dataset(file_path=base_config["split_train_test"]['y_test_csv'])

    remove_file(path_to_models.joinpath("model.pkl"))

    set_mlflow_client(base_config)

    for estimator_name, estimator_settings in config['estimators'].items():
        if estimator_name not in ESTIMATORS_MAPPER:
            raise ValueError(f"That {estimator_name} doesn't support.")

        model_estimator = ESTIMATORS_MAPPER[estimator_name]
        parameters = estimator_settings['param_grid']
        # generate parameters combinations
        params_keys = parameters.keys()
        params_values = [
            parameters[key] if isinstance(parameters[key], list) else [parameters[key]]
            for key in params_keys
        ]
        runs_parameters = [
            dict(zip(params_keys, combination)) for combination in itertools.product(*params_values)
        ]

        for i, run_parameters in enumerate(runs_parameters):
            if mlflow.active_run():
                mlflow.end_run()
            # mlflow:track run
            mlflow.start_run(run_name=f"Run {i}")
            model = model_estimator(**run_parameters)
            model.fit(X_train, y_train)

            # get evaluations scores
            score = rmse(y_test, model.predict(X_test))
            score_cv = rmsle_cv(model, X_train, y_train, random_state)

            # generate charts
            model_feature_importance(model, X_train, path_to_models)
            model_permutation_importance(model, X_train, X_test, y_test, path_to_models)

            # get model signature
            signature = infer_signature(model_input=X_train, model_output=model.predict(X_train))

            mlflow.set_tag("estimator_name", model.__class__.__name__)
            # log input features
            mlflow.set_tag("features", str(X_train.columns.values.tolist()))
            # Log tracked parameters only | run_parameters
            mlflow.log_params({key: model.get_params()[key] for key in parameters})
            mlflow.log_metrics({
                "RMSE_CV": score_cv.mean(),
                "RMSE": score,
            })
            # log training loss
            for s in model.train_score_:
                mlflow.log_metric("Train Loss", s)
            # Save model to artifacts
            mlflow.sklearn.log_model(model, "model", signature=signature)
            # log charts
            mlflow.log_artifacts(str(path_to_models))
            mlflow.end_run()
    # clear model directory
    remove_file(path_feature_importance)
    remove_file(path_permutation_importance)


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--config", dest="config", required=True)
    args_parser.add_argument("--base_config", dest="base_config", required=True)
    args = args_parser.parse_args()

    training_grid_search(config_path=args.config, base_config_path=args.base_config)
