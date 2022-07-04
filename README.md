
Directory Structure
--------------------

    .
    ├── README.md
    ├── config  <- any configuration files
    ├── data
    │   ├── dc_volumes <- docker compose valumes
    │   ├── experiments <- experiments config yaml files
    │   ├── processed <- data after all preprocessing has been done
    │   └── raw <- original unmodified data acting as source of truth and provenance
    ├── docker <- docker image(s) for running project inside container(s)
    ├── models  <- compiled model .pkl and other model's files
    └── src
        ├── config <- configure from pipline
        ├── dataset <- data prepare and/or preprocess
        ├── feauture <- impotant features visualization 
        ├── mlflow_client <- set/run mlflow clint 
        ├── pipelines <- scripts of pipelines
        ├── test <- smoke test for mlfow, mlfow_api and fast_api
        ├── train <- train model stage code
        └── utils <- auxiliary functions and utils

- **Dateset:** Bike Sharing Dataset: http://archive.ics.uci.edu/ml/datasets/Bike+Sharing+Dataset
- **Goal:** predict `rented_bikes` (count per hour) based on weather and time information.


### 1. Run demo

Just run all steps prepare, get model and run api endpoints 

```bash
make venv
source ./venv/bin/activate
make demo
```

### 1. Get data

Download Bike Sharing Dataset

```bash
make dataset
```

### 2. Build and run docker containers 

Build and run containers from docker-compose.yml

```bash
make start
```

### 3. Run dvc pipline

Run dvc pipeline with all stepc to dvc.yaml

```bash
make dvcrun
```     

### Step 4: Automate pipelines (DAG) execution

__1) Prepare configs__

Run stage:
```bash
dvc stage add -n prepare_configs \
        -d src/pipelines/prepare_configs.py \
        -d config/config.yml \
        -o data/experiments/base_config.yml \
        -o data/experiments/model_select_config.yml \
        -o data/experiments/prepare_dataset_config.yml \
        -o data/experiments/split_train_test_config.yml \
        -o data/experiments/train_config.yml \
        python src/pipelines/prepare_configs.py --config=config/config.yml
```

Reproduce stage: `dvc repro prepare_configs`



__2) Prepare dataset__

Run stage:
```bash
dvc stage add -n prepare_dataset \
        -d src/pipelines/prepare_dataset.py \
        -d data/experiments/prepare_dataset_config.yml \
        -d data/raw/hour.csv \
        -o data/processed/hour.csv \
        python src/pipelines/prepare_dataset.py --config=data/experiments/prepare_dataset_config.yml
```

Reproduce stage: `dvc repro prepare_dataset`


__2) Split train/test datasets__

Run stage:

```bash
dvc stage add -n split_dataset \
    -d src/pipelines/split_train_test.py \
    -d data/experiments/split_train_test_config.yml \
    -d data/processed/hour.csv \
    -o data/processed/x_train_bike.csv \
    -o data/processed/x_test_bike.csv \
    -o data/processed/y_train_bike.csv \
    -o data/processed/y_test_bike.csv \
    python src/pipelines/split_train_test.py \
    --config=data/experiments/split_train_test_config.yml
```

this stage:

1) creates csv files `x_train_bike.csv`,`x_test_bike.csv`,`y_train_bike.csv` and `y_test_bike.csv`
in folder `data/processed` 

Reproduce stage: `dvc repro split_dataset`

__3) Train model__ 

Run stage:
```bash
dvc stage add -n train \
    -d src/pipelines/train.py \
    -d data/experiments/train_config.yml \
    -d data/processed/x_train_bike.csv \
    -d data/processed/x_test_bike.csv \
    -d data/processed/y_train_bike.csv \
    -d data/processed/y_test_bike.csv \
    python src/pipelines/train.py --config=data/experiments/train_config.yml --base_config=config/config.yml
```

this stage:

1) trains and save model 

Reproduce stage: `dvc repro train`

__3) Get best model__ 

Run stage:
```bash
dvc stage add -n model_select \
    -d src/pipelines/model_select.py \
    -d data/experiments/model_select_config.yml \
    -d config/config.yml \
    -o models/model.pkl \
    python src/pipelines/model_select.py --config=data/experiments/model_select_config.yml --base_config=config/config.yml
```

this stage:

1) trains and save model 

Reproduce stage: `dvc repro model_select`


### REST API check

1) Check fast api

```shell
curl --silent --show-error 'http://0.0.0.0:5005/invocations' -H 'Content-Type: application/json' -d '{
    "columns": ["season", "year", "month", "hour_of_day", "is_holiday", "weekday", "is_workingday", "weather_situation", "temperature", "feels_like_temperature", "humidity", "windspeed"],
    "data": [[1, 0, 1, 0, 1, 6, 0, 1, 0.24, 0.2671, 0.81, 0.0000]]
}'
```

2) Check mlflow api 

```shell
curl --silent --show-error 'http://localhost:5001/prediction' -H 'Content-Type: application/json' -d '[{
  "season": 1, "year": 0, "month": 1, "hour_of_day": 0, "is_holiday": 1, "weekday": 0,
  "is_workingday": 0, "weather_situation": 1, "temperature": 0.24,
  "feels_like_temperature": 0.2671, "humidity": 0.81, "windspeed": 0.0000
}]'
```
