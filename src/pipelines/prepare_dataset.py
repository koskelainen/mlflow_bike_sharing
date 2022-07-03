import argparse
import pathlib
import sys
from typing import Text

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from src.dataset.dataset import data_preprocessing
from src.utils.utils import load_yaml, to_csv, load_dataset


def prepare_dataset(config_path: Text):
    config = load_yaml(config_path)

    origin_dataset_csv = config["origin_dataset_csv"]
    dataset_csv = config["dataset_csv"]
    drop_columns = config["drop_columns"]
    dataset_rename_mapper = config["dataset_rename_mapper"]

    df = load_dataset(file_path=origin_dataset_csv)
    df = data_preprocessing(dataset=df, drop_columns=drop_columns, dataset_rename_mapper=dataset_rename_mapper)
    to_csv(df, dataset_csv, index=False)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config', dest='config', required=True)
    args = args_parser.parse_args()

    prepare_dataset(config_path=args.config)
