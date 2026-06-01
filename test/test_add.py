from unittest.mock import patch
from typer.testing import CliRunner
from devctl.main import app
import os

runner = CliRunner()

def test_add_resource_spring(tmp_path):
    with patch("devctl.commands.add.detect_environment") as mock_detect:
        mock_detect.return_value = {
            "has_spring": True,
            "spring_path": str(tmp_path),
            "has_angular": False
        }
        with patch("devctl.commands.add.generate_spring_resource") as mock_gen:
            # Create a mock pom.xml so it looks like a spring project
            (tmp_path / "pom.xml").write_text("<project></project>")
            result = runner.invoke(app, ["add", "resource", "Product"])
            assert result.exit_code == 0
            mock_gen.assert_called_once()

def test_add_resource_angular(tmp_path):
    with patch("devctl.commands.add.detect_environment") as mock_detect:
        mock_detect.return_value = {
            "has_spring": False,
            "has_angular": True,
            "angular_path": str(tmp_path)
        }
        with patch("devctl.commands.add.generate_angular_resource") as mock_gen:
            result = runner.invoke(app, ["add", "resource", "User"])
            assert result.exit_code == 0
            mock_gen.assert_called_once()
