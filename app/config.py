import os
import rtoml


CONFIG_PATH = os.environ.get("CONFIG_PATH", "config/config.toml")
with open(CONFIG_PATH) as f:
    CONFIG = rtoml.load(f)
