
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
        ├── constants <- constants from pipeline
        ├── dataset <- data prepare and/or preprocess
        ├── evaluate <- evaluating model stage code 
        ├── feauture <- impotant features visualization 
        ├── pipelines <- scripts of pipelines
        ├── test <- smoke test for mlfow, mlfow_api and fast_api
        ├── train <- train model stage code
        └── utils.py <- auxiliary functions and utils

- **Dateset:** Bike Sharing Dataset: http://archive.ics.uci.edu/ml/datasets/Bike+Sharing+Dataset
- **Goal:** predict `rented_bikes` (count per hour) based on weather and time information.


### 1. Get data

Download Bike Sharing Dataset

```bash
make dataset
```         

### Step 2: Automate pipelines (DAG) execution

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
