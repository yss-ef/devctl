from typer.testing import CliRunner

from devctl.main import app

runner = CliRunner()


def test_ping_command():
    """Test the 'devctl ping' command."""
    result = runner.invoke(app, ["ping"])
    assert result.exit_code == 0
    assert "pong" in result.stdout.lower()


def test_version_command():
    """Test the '--version' flag if it exists, or a basic help check."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "devctl" in result.stdout
