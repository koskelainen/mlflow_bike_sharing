import os

import mlflow
from mlflow.models import cli

EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME", "rented_bikes")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_URL", "http://mlflow-server:5000")
METRIC_SORT = os.getenv("MODEL_ENDPOINT_MLFLOW_API_METRIC_SORT", "metrics.RMSE_CV ASC")
API_PORT = int(os.getenv("MODEL_ENDPOINT_MLFLOW_API_PORT", 5005))
API_WORKERS = int(os.getenv("MODEL_ENDPOINT_MLFLOW_API_WORKERS", 1))

if __name__ == '__main__':
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    best_run_df = mlflow.search_runs(order_by=[METRIC_SORT], max_results=1)
    if len(best_run_df.index) == 0:
        raise ValueError(f"Found no runs for experiment '{EXPERIMENT_NAME}'")

    best_run = mlflow.get_run(best_run_df.at[0, 'run_id'])
    best_model_uri = f"{best_run.info.artifact_uri}/model"

    cli.serve([
        "--model-uri", best_model_uri,
        "--no-conda",
        "--host", "0.0.0.0",
        "--port", API_PORT,
        "--workers", API_WORKERS,
    ])
