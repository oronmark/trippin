import os
from pathlib import Path

RESOURCES_FOLDER = 'resources'


def get_root_path() -> Path:
    return Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


def get_resources_path() -> Path:
    return Path(os.path.join(get_root_path(), RESOURCES_FOLDER))

