import pathlib
import sys
import warnings
from os import environ, getenv

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))
warnings.filterwarnings('ignore')


def set_mlflow_client(base_config):
    """
    EXPERIMENT_NAME: console-exp-01
    AWS_REGION: eu-north-1
    AWS_DEFAULT_REGION: eu-north-1
    AWS_ACCESS_KEY_ID: admin
    AWS_SECRET_ACCESS_KEY: ********
    MLFLOW_S3_ENDPOINT_URL: http://localhost:9020
    MLFLOW_URL: http://localhost:5555
    """
    for variable_name, variable in base_config["base"]["mlflow"].items():
        environ[variable_name] = getenv(variable_name, default=base_config["base"]["mlflow"][variable_name])
    import mlflow
    mlflow.set_tracking_uri(getenv("MLFLOW_URL", default=base_config["base"]["mlflow"]["MLFLOW_URL"]))
    mlflow.set_experiment(getenv("EXPERIMENT_NAME", default=base_config["base"]["mlflow"]["EXPERIMENT_NAME"]))
