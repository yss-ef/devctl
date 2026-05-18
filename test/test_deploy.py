from typer.testing import CliRunner

from devctl.main import app

runner = CliRunner()

def test_deploy_no_project(tmp_path):
    """Ensure deploy fails when no supported project is detected."""
    result = runner.invoke(app, ["deploy", str(tmp_path)])
    assert result.exit_code == 1
    assert "No supported projects" in result.stdout

def test_deploy_full_stack(tmp_path):
    """Ensure deploy generates a combined docker-compose for back and front."""
    # Setup Spring project
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "pom.xml").write_text(
        "<project><artifactId>api</artifactId></project>", encoding="utf-8"
    )
    props = backend / "src" / "main" / "resources"
    props.mkdir(parents=True)
    (props / "application.properties").write_text(
        "spring.datasource.url=jdbc:postgresql://localhost:5432/mydb\n"
        "spring.datasource.username=user\n"
        "spring.datasource.password=pass",
        encoding="utf-8"
    )

    # Setup Angular project
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "angular.json").write_text('{"projects": {"web": {}}}', encoding="utf-8")

    result = runner.invoke(app, ["deploy", str(tmp_path)])

    assert result.exit_code == 0
    compose_file = tmp_path / "docker-compose.yml"
    assert compose_file.exists()

    content = compose_file.read_text()
    assert "api:" in content
    assert "web:" in content
    assert "mydb-db:" in content
    assert "POSTGRES_DB: mydb" in content
    assert "SPRING_DATASOURCE_URL=jdbc:postgresql://mydb-db:5432/mydb" in content

def test_deploy_with_existing_db_name(tmp_path):
    """Ensure deploy respects service name from existing docker-compose.yml."""
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "pom.xml").write_text(
        "<project><artifactId>api</artifactId></project>", encoding="utf-8"
    )
    (backend / "docker-compose.yml").write_text(
        "services:\n"
        "  custom-db:\n"
        "    image: postgres:15-alpine\n"
        "    environment:\n"
        "      POSTGRES_DB: mydb\n",
        encoding="utf-8"
    )

    result = runner.invoke(app, ["deploy", str(tmp_path)])

    assert result.exit_code == 0
    content = (tmp_path / "docker-compose.yml").read_text()
    assert "custom-db:" in content
    assert "depends_on:\n      - custom-db" in content
