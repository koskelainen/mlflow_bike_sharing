import argparse
import pathlib
import sys
from typing import Text

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from src.utils.utils import load_yaml, save_yaml


def prepare_configs(config_path: Text):
    """
    Split common config into configs for steps
    """
    config = load_yaml(config_path)
    exp_dir = config['base']['experiments']['experiments_folder']
    exp_dir = pathlib.Path().joinpath(*exp_dir) if isinstance(exp_dir, list) else exp_dir

    for config_name, config_params in config.items():
        if not config_name.startswith("template"):
            filepath = f'{exp_dir}/{config_name}_config.yml'
            save_yaml(file_path=filepath, data=config_params)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config', dest='config', required=True)
    args = args_parser.parse_args()

    prepare_configs(config_path=args.config)
