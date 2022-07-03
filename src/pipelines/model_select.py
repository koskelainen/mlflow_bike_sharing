import argparse
import pathlib
import sys
from os import getenv
from typing import Text

import mlflow
from mlflow.pyfunc import load_model

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from src.utils.utils import load_yaml, path_resolve
from src.mlflow_client.client import set_mlflow_client


def model_select(config_path: Text, base_config_path: Text):
    """
    Split common config into configs for steps
    """
    config = load_yaml(config_path)  # type: dict
    base_config = load_yaml(base_config_path)  # type: dict
    models_dir = base_config["base"]["model"]["models_folder"]
    path_to_models = path_resolve(pathlib.Path().joinpath(*models_dir))

    set_mlflow_client(base_config)

    metric_sort = config.get("sort_of_metrics", getenv("METRIC_SORT", "metrics.RMSE_CV ASC"))
    experiment_name = base_config["base"]["mlflow"]["EXPERIMENT_NAME"]

    best_run_df = mlflow.search_runs(order_by=[metric_sort], max_results=1)
    if len(best_run_df.index) == 0:
        raise ValueError(f"Found no runs for experiment '{experiment_name}'")

    best_run = mlflow.get_run(best_run_df.at[0, "run_id"])
    best_model_uri = f"{best_run.info.artifact_uri}/model"

    model = load_model(best_model_uri)
    model._model_meta.save(path_resolve(path_to_models).joinpath("model.pkl"))


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--config", dest="config", required=True)
    args_parser.add_argument("--base_config", dest="base_config", required=True)
    args = args_parser.parse_args()

    model_select(config_path=args.config, base_config_path=args.base_config)
