from unittest.mock import patch

from typer.testing import CliRunner

from devctl.main import app

runner = CliRunner()


def test_init_spring_unsupported_db():
    """Ensure init spring fails with unsupported database."""
    # We mock check_tool to avoid needing java installed for this test
    with patch("devctl.commands.init.check_tool"):
        result = runner.invoke(app, ["init", "spring", "my-api", "--db", "sqlite"])
        assert result.exit_code == 1
        assert "is not supported" in result.stdout


def test_run_no_environment():
    """Ensure run command fails when no project is detected."""
    with patch("devctl.commands.run.detect_environment") as mock_detect:
        mock_detect.return_value = {
            "has_docker_compose": False,
            "has_spring": False,
            "has_angular": False,
            "has_vue": False,
        }
        result = runner.invoke(app, ["run"])
        assert result.exit_code == 1
        assert "No valid development environment detected" in result.stdout


def test_add_resource_no_project():
    """Ensure add resource fails when not in a project."""
    with patch("devctl.commands.add.detect_environment") as mock_detect:
        mock_detect.return_value = {"has_spring": False, "has_angular": False}
        result = runner.invoke(app, ["add", "resource", "User"])
        assert result.exit_code == 1
        assert "Unable to determine project type" in result.stdout
