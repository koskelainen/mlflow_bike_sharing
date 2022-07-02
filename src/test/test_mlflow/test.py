import os
from random import random, randint

import mlflow as ml
from mlflow import log_metric, log_param, log_artifacts

os.environ["AWS_DEFAULT_REGION"] = "eu-north-1"
os.environ["AWS_REGION"] = "eu-north-1"
os.environ["AWS_ACCESS_KEY_ID"] = "admin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "R9mTkRt4z"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9020"

ml.set_tracking_uri("http://localhost:5555")
ml.set_experiment("test-01-experiment")

if __name__ == "__main__":
    # Log a parameter (key-value pair)
    log_param("param1", randint(0, 100))

    # Log a metric; metrics can be updated throughout the run
    log_metric("foo", random())
    log_metric("foo", random() + 1)
    log_metric("foo", random() + 2)

    # Log an artifact (output file)
    if not os.path.exists("../outputs"):
        os.makedirs("../outputs")
    with open("../outputs/test.txt", "w") as f:
        f.write("log_artifacts")
    log_artifacts("../outputs")
