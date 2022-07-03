import pathlib
from os import remove
from typing import Text, Union

import pandas
import yaml
from pandas import DataFrame


def get_root_dir() -> pathlib.Path:
    return pathlib.Path(__file__).parent.parent.parent


def path_resolve(file_path: Union[Text, pathlib.Path]) -> pathlib.Path:
    return get_root_dir().joinpath(file_path).resolve()


def load_yaml(file_path: Union[Text, pathlib.Path]) -> any:
    with open(path_resolve(file_path)) as fn:
        return yaml.load(fn, Loader=yaml.FullLoader)


def save_yaml(file_path: Union[Text, pathlib.Path], data) -> None:
    with open(path_resolve(file_path), "w") as fn:
        yaml.dump(
            data=data,
            stream=fn,
            default_flow_style=False,
        )


def load_dataset(file_path: Union[Text, pathlib.Path], *args, **kwargs) -> pandas.DataFrame:
    return pandas.read_csv(filepath_or_buffer=path_resolve(file_path), *args, **kwargs)


def to_csv(df: DataFrame, file_path: Union[Text, pathlib.Path], *args, **kwargs) -> None:
    return df.to_csv(path_or_buf=path_resolve(file_path), *args, **kwargs)


def remove_file(file_path: Union[Text, pathlib.Path]) -> None:
    file_path = path_resolve(file_path)
    if file_path.exists():
        remove(file_path)
    else:
        print(f"File: {file_path} not found!")
