from unittest.mock import patch

import pytest
import typer

from devctl.utils.dependencies import check_tool


def test_check_tool_success():
    """Ensure check_tool does nothing if the tool exists."""
    with patch("shutil.which", return_value="/usr/bin/docker"):
        # Should not raise any exception
        check_tool("docker")


def test_check_tool_failure():
    """Ensure check_tool raises Exit(1) if the tool is missing."""
    with patch("shutil.which", return_value=None):
        with pytest.raises(typer.Exit) as excinfo:
            check_tool("nonexistent-tool")
        assert excinfo.value.exit_code == 1
