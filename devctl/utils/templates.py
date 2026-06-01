import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def get_jinja_env(template_subdir: str) -> Environment:
    """
    Returns a Jinja2 environment for a specific template subdirectory.
    """
    base_dir = Path(__file__).resolve().parent.parent / "templates"
    template_path = base_dir / template_subdir

    if not template_path.exists():
        raise FileNotFoundError(f"Template directory not found: {template_path}")

    return Environment(
        loader=FileSystemLoader(str(template_path)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
