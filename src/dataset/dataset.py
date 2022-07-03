import pathlib
import sys

from pandas import DataFrame

sys.path.append(str(pathlib.Path().resolve().parent.parent))


def remove_unused_columns(dataset: DataFrame, columns: list) -> DataFrame:
    return dataset.drop(columns=columns)


def rename_columns(dataset: DataFrame, mapper: dict) -> DataFrame:
    return dataset.rename(columns=mapper, )


def data_preprocessing(dataset: DataFrame, drop_columns: list, dataset_rename_mapper: dict,) -> DataFrame:
    dataset = remove_unused_columns(dataset=dataset, columns=drop_columns)
    dataset = rename_columns(dataset=dataset, mapper=dataset_rename_mapper)
    return dataset

