import argparse
import pathlib
import sys
from typing import Text

from sklearn.model_selection import train_test_split

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from src.utils.utils import load_yaml, load_dataset, to_csv
from src.config.config import RANDOM_STATE, TEST_SIZE


def split_dataset(config_path: Text):
    config = load_yaml(config_path)
    dataset = load_dataset(config['dataset_csv'])
    target_column = config['target_column']

    random_state = int(config.get("random_state", RANDOM_STATE))
    test_size = float(config.get("test_size", TEST_SIZE))
    train_size = 1 - test_size

    X_train_csv_path = config['x_train_csv']
    X_test_csv_path = config['x_test_csv']
    y_train_csv_path = config['y_train_csv']
    y_test_csv_path = config['y_test_csv']

    X = dataset.drop(columns=target_column, axis=1)
    y = dataset[target_column]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=train_size, test_size=test_size, random_state=random_state
    )

    to_csv(X_train, X_train_csv_path, index=False)
    to_csv(X_test, X_test_csv_path, index=False)
    to_csv(y_train, y_train_csv_path, index=False)
    to_csv(y_test, y_test_csv_path, index=False)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config', dest='config', required=True)
    args = args_parser.parse_args()

    split_dataset(config_path=args.config)
