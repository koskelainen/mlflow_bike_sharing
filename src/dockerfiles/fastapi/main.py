import os
from inspect import signature

import mlflow
from fastapi import FastAPI
from fastapi_mlflow.predictors import build_predictor
from mlflow.pyfunc import load_model

EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME", "rented_bikes")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_URL", "http://mlflow-server:5000")
METRIC_SORT = os.getenv("MODEL_ENDPOINT_FAST_API_METRIC_SORT", "metrics.RMSE_CV ASC")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

best_run_df = mlflow.search_runs(order_by=[METRIC_SORT], max_results=1)
if len(best_run_df.index) == 0:
    raise ValueError(f"Found no runs for experiment '{EXPERIMENT_NAME}'")

best_run = mlflow.get_run(best_run_df.at[0, 'run_id'])
best_model_uri = f"{best_run.info.artifact_uri}/model"

model = load_model(best_model_uri)
predictor = build_predictor(model)
app = FastAPI()

tmp = signature(predictor).return_annotation


app.add_api_route(
    "/prediction",
    predictor,
    response_model=signature(predictor).return_annotation,
    methods=["POST"],
)
