"""Utilities for reading project configuration from config.ini."""

from configparser import ConfigParser
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.ini"


def load_config(config_path: Optional[Path] = None) -> ConfigParser:
    """Load application configuration from an INI file.

    Args:
        config_path: Optional custom path to the config file.

    Returns:
        Parsed ConfigParser instance.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    resolved_path = config_path or CONFIG_PATH

    if not resolved_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {resolved_path}")

    parser = ConfigParser()
    parser.read(resolved_path, encoding="utf-8")
    return parser