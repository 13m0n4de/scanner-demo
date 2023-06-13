import os
import rtoml

from functools import lru_cache


@lru_cache
def get_app_config():
    config_path = os.environ.get('CONFIG_PATH', 'config/config.toml')
    with open(config_path) as f:
        config = rtoml.load(f)
    return config
