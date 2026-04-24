import configparser
import os
from pathlib import Path

DEFAULTS = {
    "host": "camera2",
    "user": "root",
    "port": 22,
    "volume": 95,
    "gain": 20,
}

CONFIG_PATH = Path.home() / ".config" / "camera-speaker" / "config.ini"

ENV_MAP = {
    "host": "CAMERA_HOST",
    "user": "CAMERA_USER",
    "port": "CAMERA_PORT",
}


def load_config(cli_args: dict) -> dict:
    """Load config: CLI args > env vars > config file > defaults."""
    config = dict(DEFAULTS)

    # Config file
    if CONFIG_PATH.exists():
        cp = configparser.ConfigParser()
        cp.read(CONFIG_PATH)
        if "camera" in cp:
            for key in DEFAULTS:
                if key in cp["camera"]:
                    config[key] = cp["camera"][key]

    # Environment variables
    for key, env in ENV_MAP.items():
        val = os.environ.get(env)
        if val is not None:
            config[key] = val

    # CLI args (highest priority)
    for key, val in cli_args.items():
        if val is not None:
            config[key] = val

    config["port"] = int(config["port"])
    config["volume"] = int(config["volume"])
    config["gain"] = int(config["gain"])
    return config
