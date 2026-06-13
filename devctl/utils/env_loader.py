"""
Utility for loading environment variables from .env files.
"""

import os
from pathlib import Path
from typing import Dict


def load_env_file(project_path: Path) -> Dict[str, str]:
    """
    Reads a .env file in the given path and returns a dictionary of variables.
    Does not override existing environment variables in os.environ by default
    when used for process injection, but provides the mapping for merge.
    """
    env_vars = {}
    env_path = project_path / ".env"

    if not env_path.exists():
        return env_vars

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue

                if "=" in line:
                    key, value = line.split("=", 1)
                    # Clean key and value
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or (
                        value.startswith("'") and value.endswith("'")
                    ):
                        value = value[1:-1]

                    env_vars[key] = value
    except Exception:
        # Fail silently to not break the runner if .env is malformed
        pass

    return env_vars


def get_project_env(project_path: Path) -> Dict[str, str]:
    """
    Returns a full environment dictionary merging system env and .env file.
    """
    env = os.environ.copy()
    dot_env = load_env_file(project_path)
    env.update(dot_env)
    return env
