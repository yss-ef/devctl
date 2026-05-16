from pathlib import Path

import pytest

from devctl.generators.docker_scaffold import (
    DockerScaffoldError,
    discover_docker_projects,
    infer_database_type,
    sanitize_service_name,
    scaffold_docker_assets,
)


def write_spring_project(path: Path, name: str = "sample-api", db: str = "postgres") -> None:
    path.mkdir(parents=True, exist_ok=True)
    dependency = {
        "postgres": "<groupId>org.postgresql</groupId><artifactId>postgresql</artifactId>",
        "mysql": "<groupId>com.mysql</groupId><artifactId>mysql-connector-j</artifactId>",
        "none": "",
    }[db]
    (path / "pom.xml").write_text(
        f"""<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>{name}</artifactId>
  <version>0.0.1</version>
  <properties>
    <java.version>21</java.version>
  </properties>
  <dependencies>
    <dependency>{dependency}</dependency>
  </dependencies>
</project>
""",
        encoding="utf-8",
    )
    source_dir = path / "src" / "main" / "java" / "com" / "example"
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "Application.java").write_text("class Application {}", encoding="utf-8")


def write_angular_project(path: Path, name: str = "sample-front") -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "angular.json").write_text(
        f'{{"projects": {{"{name}": {{"architect": {{"build": {{}}}}}}}}}}',
        encoding="utf-8",
    )
    (path / "package.json").write_text(
        """{
  "name": "sample-front",
  "scripts": {"build": "ng build"},
  "dependencies": {"@angular/core": "^21.0.0"}
}
""",
        encoding="utf-8",
    )
    (path / "src" / "environments").mkdir(parents=True, exist_ok=True)


def write_vue_project(path: Path, name: str = "sample-vue") -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "vite.config.ts").write_text("export default {}", encoding="utf-8")
    (path / "package.json").write_text(
        f'{{"name": "{name}", "scripts": {{"build": "vite build"}}}}',
        encoding="utf-8",
    )


def test_sanitize_service_name():
    assert sanitize_service_name("My API_Service") == "my-api-service"
    assert sanitize_service_name("!!!", fallback="spring") == "spring"


def test_discover_docker_projects_detects_multiple_services(tmp_path):
    write_spring_project(tmp_path / "api")
    write_angular_project(tmp_path / "web")
    write_vue_project(tmp_path / "admin")

    projects = discover_docker_projects(tmp_path)

    assert [project.kind for project in projects] == ["vue", "spring", "angular"]
    assert {project.service_name for project in projects} == {
        "sample-api",
        "sample-front",
        "sample-vue",
    }
    assert next(project for project in projects if project.kind == "spring").java_version == "21"
    assert next(project for project in projects if project.kind == "angular").node_version == "22"


def test_infer_database_type_from_spring_project(tmp_path):
    write_spring_project(tmp_path / "postgres-api", db="postgres")
    write_spring_project(tmp_path / "mysql-api", db="mysql")
    write_spring_project(tmp_path / "plain-api", db="none")

    assert infer_database_type(tmp_path / "postgres-api") == "postgres"
    assert infer_database_type(tmp_path / "mysql-api") == "mysql"
    assert infer_database_type(tmp_path / "plain-api") is None


def test_scaffold_docker_assets_dry_run_does_not_write_files(tmp_path):
    write_spring_project(tmp_path / "api")

    result = scaffold_docker_assets(tmp_path, dry_run=True)

    assert result.planned_count > 0
    assert not (tmp_path / "api" / "Dockerfile").exists()
    assert not (tmp_path / "docker-compose.yml").exists()


def test_scaffold_docker_assets_generates_production_files(tmp_path):
    write_spring_project(tmp_path / "api")
    write_angular_project(tmp_path / "web")

    result = scaffold_docker_assets(tmp_path)

    assert result.db_type == "postgres"
    assert (tmp_path / "api" / "Dockerfile").exists()
    assert (tmp_path / "api" / ".dockerignore").exists()
    assert (tmp_path / "web" / "Dockerfile").exists()
    assert (tmp_path / "web" / "nginx.conf").exists()
    assert (tmp_path / "web" / "src" / "environments" / "environment.docker.ts").exists()
    assert (tmp_path / ".env.example").exists()

    spring_dockerfile = (tmp_path / "api" / "Dockerfile").read_text(encoding="utf-8")
    compose = (tmp_path / "docker-compose.yml").read_text(encoding="utf-8")
    env_example = (tmp_path / ".env.example").read_text(encoding="utf-8")
    nginx = (tmp_path / "web" / "nginx.conf").read_text(encoding="utf-8")

    assert "FROM maven:3.9-eclipse-temurin-21 AS build" in spring_dockerfile
    assert "USER app" in spring_dockerfile
    assert "${DB_PASSWORD:?Set DB_PASSWORD in .env}" in compose
    assert "condition: service_healthy" in compose
    assert "DB_PASSWORD=" in env_example
    assert "DB_PASSWORD=password" not in env_example
    assert "proxy_pass http://sample-api:8080/api/;" in nginx


def test_scaffold_docker_assets_skips_existing_files_unless_forced(tmp_path):
    write_spring_project(tmp_path / "api")
    dockerfile = tmp_path / "api" / "Dockerfile"
    dockerfile.write_text("custom", encoding="utf-8")

    result = scaffold_docker_assets(tmp_path)

    assert any(
        operation.path == dockerfile and operation.action == "skipped"
        for operation in result.operations
    )
    assert dockerfile.read_text(encoding="utf-8") == "custom"

    scaffold_docker_assets(tmp_path, force=True)

    assert "Generated by devctl dockerize" in dockerfile.read_text(encoding="utf-8")


def test_scaffold_docker_assets_uses_devctl_compose_when_compose_exists(tmp_path):
    write_spring_project(tmp_path / "api")
    (tmp_path / "docker-compose.yml").write_text("services: {}", encoding="utf-8")

    result = scaffold_docker_assets(tmp_path)

    assert result.compose_path == tmp_path / "docker-compose.devctl.yml"
    assert (tmp_path / "docker-compose.yml").read_text(encoding="utf-8") == "services: {}"
    assert (tmp_path / "docker-compose.devctl.yml").exists()


def test_scaffold_docker_assets_no_compose(tmp_path):
    write_vue_project(tmp_path / "web")

    result = scaffold_docker_assets(tmp_path, include_compose=False)

    assert result.compose_path is None
    assert not (tmp_path / "docker-compose.yml").exists()
    assert (tmp_path / "web" / "Dockerfile").exists()


def test_scaffold_docker_assets_fails_without_supported_projects(tmp_path):
    with pytest.raises(DockerScaffoldError):
        scaffold_docker_assets(tmp_path)
