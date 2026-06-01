import yaml
from typer.testing import CliRunner

from devctl.main import app

runner = CliRunner()


def test_deploy_mongodb(tmp_path):
    """Ensure deploy correctly detects and configures MongoDB."""
    # Setup project with MongoDB properties
    backend = tmp_path / "mongo-api"
    backend.mkdir()
    (backend / "pom.xml").write_text(
        "<project><artifactId>mongo-api</artifactId></project>", encoding="utf-8"
    )
    props = backend / "src" / "main" / "resources"
    props.mkdir(parents=True)
    (props / "application.properties").write_text(
        "spring.data.mongodb.uri=mongodb://admin:pass@localhost:27017/mydb?authSource=admin",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["deploy", str(tmp_path)])

    assert result.exit_code == 0
    compose_file = tmp_path / "docker-compose-prod.yml"
    assert compose_file.exists()

    with open(compose_file, "r") as f:
        config = yaml.safe_load(f)

    services = config["services"]
    assert "mydb-db" in services
    db_service = services["mydb-db"]
    assert db_service["image"] == "mongo:6.0"
    assert "MONGO_INITDB_ROOT_USERNAME" in db_service["environment"]
    assert db_service["environment"]["MONGO_INITDB_ROOT_USERNAME"] == "admin"
    assert "27017:27017" in db_service["ports"]
