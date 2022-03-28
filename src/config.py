"""
Functions to handle configuration.
"""
import os

import yaml
from configurator import Config

CONFIG_PATH = "./config.yml"


def _load_config() -> Config:
    """
    Loads in the current config from the default path
    """
    config = Config.from_path(CONFIG_PATH, optional=False)
    return config


def create_config(activity_vault: str) -> Config:
    """
    Creates and saves a new config.
    """
    config = {"activity_vault": os.path.abspath(activity_vault)}
    with open("./config.yml", "w") as file:
        yaml.dump(config, file)
    return config


def get_activity_vault() -> str:
    config = _load_config()
    return config["activity_vault"]
