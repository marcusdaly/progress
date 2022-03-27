"""
Functions to handle configuration.
"""
from configurator import Config
import os
import yaml

CONFIG_PATH = "./config.yml"

def _load_config() -> Config:
    """
    Loads in the current config from the default path
    """
    config = Config.from_path(CONFIG_PATH, optional=False)
    return config

def create_config(activity_directory: str) -> Config:
    """
    Creates and saves a new config.
    """
    config = {
        "activity_directory": os.path.abspath(activity_directory)
    }
    with open("./config.yml", "w") as file:
        yaml.dump(config, file)
    return config

def get_activity_directory() -> str:
    config = _load_config()
    return config["activity_directory"]