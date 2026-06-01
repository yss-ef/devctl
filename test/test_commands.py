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
    with patch("devctl.commands.run.discover_docker_projects") as mock_discover:
        mock_discover.return_value = []
        # Also need to mock Path.rglob or something to avoid finding docker-compose.yml
        with patch("devctl.commands.run.Path.rglob") as mock_rglob:
            mock_rglob.return_value = []
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


def test_dockerize_no_project(tmp_path):
    """Ensure dockerize fails when no supported project is detected."""
    result = runner.invoke(app, ["dockerize", str(tmp_path)])
    assert result.exit_code == 1
    assert "Error: No supported project detected." in result.stdout


def test_dockerize_dry_run(tmp_path):
    """Ensure dockerize dry-run reports planned files without writing them."""
    (tmp_path / "pom.xml").write_text(
        """<project xmlns="http://maven.apache.org/POM/4.0.0">
  <artifactId>demo-api</artifactId>
  <properties><java.version>17</java.version></properties>
  <dependencies>
    <dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId></dependency>
  </dependencies>
</project>
""",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["dockerize", str(tmp_path), "--dry-run"])

    assert result.exit_code == 0
    assert "would_create" in result.stdout
    assert not (tmp_path / "Dockerfile").exists()


def test_dockerize_generates_dockerfile_only(tmp_path):
    """Ensure dockerize generates only a Dockerfile for a frontend project."""
    (tmp_path / "vite.config.ts").write_text("export default {}", encoding="utf-8")
    (tmp_path / "package.json").write_text(
        '{"name": "web", "scripts": {"build": "vite build"}}',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["dockerize", str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / "Dockerfile").exists()
    assert not (tmp_path / "docker-compose.yml").exists()
    assert not (tmp_path / ".dockerignore").exists()
