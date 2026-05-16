"""Production Docker scaffolding for detected devctl projects."""

from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

from jinja2 import Environment, FileSystemLoader

SUPPORTED_DB_MODES = {"auto", "postgres", "mysql", "none"}

IGNORED_DIRECTORIES = {
    ".angular",
    ".git",
    ".mvn",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "venv",
}


class DockerScaffoldError(Exception):
    """Raised when Docker scaffolding cannot be completed."""


@dataclass(frozen=True)
class DockerProject:
    """A Dockerizable project discovered in a repository tree."""

    kind: str
    path: Path
    name: str
    service_name: str
    relative_context: str
    java_version: Optional[str] = None
    node_version: Optional[str] = None
    angular_output_name: Optional[str] = None
    inferred_db: Optional[str] = None


@dataclass(frozen=True)
class FileOperation:
    """A single file operation performed or planned by the scaffold command."""

    path: Path
    action: str


@dataclass(frozen=True)
class DockerScaffoldResult:
    """Summary returned after Docker scaffolding."""

    root_path: Path
    services: list[DockerProject]
    operations: list[FileOperation]
    warnings: list[str]
    compose_path: Optional[Path]
    db_type: Optional[str]

    @property
    def created_count(self) -> int:
        return sum(1 for operation in self.operations if operation.action == "created")

    @property
    def skipped_count(self) -> int:
        return sum(1 for operation in self.operations if operation.action == "skipped")

    @property
    def planned_count(self) -> int:
        return sum(1 for operation in self.operations if operation.action.startswith("would_"))


def sanitize_service_name(raw_name: str, fallback: str = "service") -> str:
    """Return a Docker Compose compatible, lowercase service name."""
    service_name = re.sub(r"[^a-z0-9-]+", "-", raw_name.lower()).strip("-")
    service_name = re.sub(r"-{2,}", "-", service_name)
    return service_name or fallback


def discover_docker_projects(root_path: Union[str, Path]) -> list[DockerProject]:
    """Discover all supported Dockerizable projects under ``root_path``."""
    root = Path(root_path).resolve()
    if not root.exists():
        raise DockerScaffoldError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise DockerScaffoldError(f"Path is not a directory: {root}")

    candidates: list[tuple[str, Path]] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORED_DIRECTORIES]

        project_path = Path(dirpath)
        filename_set = set(filenames)

        if "pom.xml" in filename_set:
            candidates.append(("spring", project_path))
        if "angular.json" in filename_set:
            candidates.append(("angular", project_path))
        has_vite_config = {"vite.config.ts", "vite.config.js"} & filename_set
        if has_vite_config and "angular.json" not in filename_set:
            candidates.append(("vue", project_path))

    used_names: set[str] = set()
    projects: list[DockerProject] = []

    for kind, project_path in sorted(candidates, key=lambda item: (str(item[1]), item[0])):
        name = _project_name(kind, project_path)
        service_name = _unique_service_name(name, used_names, fallback=kind)
        used_names.add(service_name)

        projects.append(
            DockerProject(
                kind=kind,
                path=project_path,
                name=name,
                service_name=service_name,
                relative_context=_relative_context(root, project_path),
                java_version=_spring_java_version(project_path) if kind == "spring" else None,
                node_version=(
                    _node_version(project_path, kind) if kind in {"angular", "vue"} else None
                ),
                angular_output_name=(
                    _angular_output_name(project_path) if kind == "angular" else None
                ),
                inferred_db=infer_database_type(project_path) if kind == "spring" else None,
            )
        )

    return projects


def infer_database_type(project_path: Union[str, Path]) -> Optional[str]:
    """Infer a Spring project's database type from common project files."""
    path = Path(project_path)
    searchable_files = [
        path / "pom.xml",
        path / "src" / "main" / "resources" / "application.properties",
        path / "docker-compose.yml",
        path / "docker-compose.yaml",
    ]
    content = "\n".join(
        file_path.read_text(encoding="utf-8", errors="ignore").lower()
        for file_path in searchable_files
        if file_path.exists()
    )

    has_postgres = any(
        token in content
        for token in ["postgresql", "postgres:", "image: postgres", "jdbc:postgresql"]
    )
    has_mysql = any(token in content for token in ["mysql", "jdbc:mysql", "mysql-connector"])

    if has_postgres and not has_mysql:
        return "postgres"
    if has_mysql and not has_postgres:
        return "mysql"
    return None


def scaffold_docker_assets(
    root_path: Union[str, Path] = ".",
    *,
    force: bool = False,
    dry_run: bool = False,
    include_compose: bool = True,
    db_mode: str = "auto",
) -> DockerScaffoldResult:
    """Generate production Docker assets for all supported projects in a tree."""
    if db_mode not in SUPPORTED_DB_MODES:
        supported = ", ".join(sorted(SUPPORTED_DB_MODES))
        raise DockerScaffoldError(
            f"Invalid database mode '{db_mode}'. Expected one of: {supported}"
        )

    root = Path(root_path).resolve()
    projects = discover_docker_projects(root)
    if not projects:
        raise DockerScaffoldError("No Spring Boot, Angular, or Vue/Vite project detected.")

    env = _template_environment()
    operations: list[FileOperation] = []
    warnings: list[str] = []

    spring_projects = [project for project in projects if project.kind == "spring"]
    frontend_projects = [project for project in projects if project.kind in {"angular", "vue"}]
    api_upstream = spring_projects[0].service_name if len(spring_projects) == 1 else None

    if len(spring_projects) > 1 and frontend_projects:
        warnings.append(
            "Multiple Spring services detected; frontend Nginx /api proxy was not generated."
        )

    for project in projects:
        operations.extend(
            _project_file_operations(
                env,
                project,
                api_upstream=api_upstream,
                force=force,
                dry_run=dry_run,
            )
        )

    selected_db = _selected_database_type(spring_projects, db_mode)
    if spring_projects and db_mode == "auto" and selected_db is None:
        warnings.append(
            "Database type could not be inferred confidently; "
            "compose will not include a DB service."
        )

    compose_path: Optional[Path] = None
    if include_compose:
        compose_path = _compose_output_path(root)
        compose_content = env.get_template("compose/docker-compose.yml.j2").render(
            db=_database_context(selected_db),
            services=_compose_services(projects, selected_db, api_upstream),
            has_spring=bool(spring_projects),
        )
        operations.append(_write_file(compose_path, compose_content, force=force, dry_run=dry_run))

        env_content = env.get_template("compose/env.example.j2").render(
            db_type=selected_db,
            has_spring=bool(spring_projects),
            services=_env_services(projects),
        )
        operations.append(
            _write_file(root / ".env.example", env_content, force=force, dry_run=dry_run)
        )

    return DockerScaffoldResult(
        root_path=root,
        services=projects,
        operations=operations,
        warnings=warnings,
        compose_path=compose_path,
        db_type=selected_db,
    )


def _project_file_operations(
    env: Environment,
    project: DockerProject,
    *,
    api_upstream: Optional[str],
    force: bool,
    dry_run: bool,
) -> list[FileOperation]:
    if project.kind == "spring":
        return [
            _write_file(
                project.path / "Dockerfile",
                env.get_template("spring/Dockerfile.j2").render(project=project),
                force=force,
                dry_run=dry_run,
            ),
            _write_file(
                project.path / ".dockerignore",
                env.get_template("spring/dockerignore.j2").render(),
                force=force,
                dry_run=dry_run,
            ),
        ]

    if project.kind == "angular":
        return [
            _write_frontend_dockerfile(env, project, force=force, dry_run=dry_run),
            _write_frontend_dockerignore(env, project, force=force, dry_run=dry_run),
            _write_nginx_config(env, project, api_upstream, force=force, dry_run=dry_run),
            _write_file(
                project.path / "src" / "environments" / "environment.docker.ts",
                env.get_template("frontend/angular.environment.docker.ts.j2").render(),
                force=force,
                dry_run=dry_run,
            ),
        ]

    return [
        _write_frontend_dockerfile(env, project, force=force, dry_run=dry_run),
        _write_frontend_dockerignore(env, project, force=force, dry_run=dry_run),
        _write_nginx_config(env, project, api_upstream, force=force, dry_run=dry_run),
        _write_file(
            project.path / ".env.docker",
            env.get_template("frontend/vue.env.docker.j2").render(),
            force=force,
            dry_run=dry_run,
        ),
    ]


def _write_frontend_dockerfile(
    env: Environment, project: DockerProject, *, force: bool, dry_run: bool
) -> FileOperation:
    return _write_file(
        project.path / "Dockerfile",
        env.get_template("frontend/Dockerfile.j2").render(project=project),
        force=force,
        dry_run=dry_run,
    )


def _write_frontend_dockerignore(
    env: Environment, project: DockerProject, *, force: bool, dry_run: bool
) -> FileOperation:
    return _write_file(
        project.path / ".dockerignore",
        env.get_template("frontend/dockerignore.j2").render(),
        force=force,
        dry_run=dry_run,
    )


def _write_nginx_config(
    env: Environment,
    project: DockerProject,
    api_upstream: Optional[str],
    *,
    force: bool,
    dry_run: bool,
) -> FileOperation:
    return _write_file(
        project.path / "nginx.conf",
        env.get_template("frontend/nginx.conf.j2").render(api_upstream=api_upstream),
        force=force,
        dry_run=dry_run,
    )


def _write_file(path: Path, content: str, *, force: bool, dry_run: bool) -> FileOperation:
    content = content.rstrip() + "\n"
    exists = path.exists()

    if exists and not force:
        return FileOperation(path=path, action="skipped")

    if dry_run:
        action = "would_overwrite" if exists else "would_create"
        return FileOperation(path=path, action=action)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return FileOperation(path=path, action="overwritten" if exists else "created")


def _template_environment() -> Environment:
    template_dir = Path(__file__).resolve().parent.parent / "templates" / "docker"
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def _project_name(kind: str, project_path: Path) -> str:
    if kind == "spring":
        return _spring_artifact_id(project_path) or project_path.name
    if kind == "angular":
        return (
            _angular_output_name(project_path) or _package_name(project_path) or project_path.name
        )
    return _package_name(project_path) or project_path.name


def _unique_service_name(raw_name: str, used_names: set[str], fallback: str) -> str:
    base_name = sanitize_service_name(raw_name, fallback=fallback)
    if base_name not in used_names:
        return base_name

    index = 2
    while f"{base_name}-{index}" in used_names:
        index += 1
    return f"{base_name}-{index}"


def _relative_context(root: Path, project_path: Path) -> str:
    try:
        relative = project_path.relative_to(root)
    except ValueError:
        relative = Path(os.path.relpath(project_path, root))

    if str(relative) == ".":
        return "."
    return f"./{relative.as_posix()}"


def _spring_artifact_id(project_path: Path) -> Optional[str]:
    pom_path = project_path / "pom.xml"
    if not pom_path.exists():
        return None

    try:
        root = ET.parse(pom_path).getroot()
    except ET.ParseError:
        return None

    for child in root:
        if _local_name(child.tag) == "artifactId" and child.text:
            return child.text.strip()
    return None


def _spring_java_version(project_path: Path) -> str:
    pom_path = project_path / "pom.xml"
    if not pom_path.exists():
        return "17"

    content = pom_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"<java\.version>\s*([^<\s]+)\s*</java\.version>", content)
    if match:
        version = match.group(1)
        major = re.match(r"\d+", version)
        if major:
            return major.group(0)
    return "17"


def _angular_output_name(project_path: Path) -> Optional[str]:
    angular_json = project_path / "angular.json"
    if not angular_json.exists():
        return None

    try:
        config = json.loads(angular_json.read_text(encoding="utf-8"))
        projects = config.get("projects", {})
    except (json.JSONDecodeError, OSError):
        return None

    if isinstance(projects, dict) and projects:
        return str(next(iter(projects.keys())))
    return None


def _package_name(project_path: Path) -> Optional[str]:
    package_json = _read_package_json(project_path)
    name = package_json.get("name")
    return str(name) if name else None


def _node_version(project_path: Path, kind: str) -> str:
    package_json = _read_package_json(project_path)
    engines = package_json.get("engines", {})
    node_range = str(engines.get("node", "")) if isinstance(engines, dict) else ""

    engine_major = _highest_supported_node_major(node_range)
    if engine_major:
        return engine_major

    if kind == "angular":
        angular_major = _angular_major(package_json)
        if angular_major >= 20:
            return "22"
        if angular_major >= 17:
            return "20"
        return "18"

    return "22"


def _read_package_json(project_path: Path) -> dict[str, Any]:
    package_path = project_path / "package.json"
    if not package_path.exists():
        return {}

    try:
        content = json.loads(package_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    return content if isinstance(content, dict) else {}


def _highest_supported_node_major(node_range: str) -> Optional[str]:
    supported = {18, 20, 22, 24}
    majors = {int(value) for value in re.findall(r"(?<!\.)\b(18|20|22|24)\b", node_range)}
    usable = sorted(majors & supported)
    return str(usable[-1]) if usable else None


def _angular_major(package_json: dict[str, Any]) -> int:
    sections = ["dependencies", "devDependencies"]
    for section in sections:
        dependencies = package_json.get(section, {})
        if not isinstance(dependencies, dict):
            continue
        version = dependencies.get("@angular/core") or dependencies.get("@angular/cli")
        if version:
            match = re.search(r"(\d+)", str(version))
            if match:
                return int(match.group(1))
    return 20


def _selected_database_type(projects: list[DockerProject], db_mode: str) -> Optional[str]:
    if db_mode == "none" or not projects:
        return None
    if db_mode in {"postgres", "mysql"}:
        return db_mode

    inferred = {project.inferred_db for project in projects if project.inferred_db}
    if len(inferred) == 1:
        return inferred.pop()
    return None


def _compose_output_path(root: Path) -> Path:
    default_path = root / "docker-compose.yml"
    if default_path.exists():
        return root / "docker-compose.devctl.yml"
    return default_path


def _database_context(db_type: Optional[str]) -> Optional[dict[str, str]]:
    if db_type is None:
        return None

    if db_type == "postgres":
        return {
            "type": "postgres",
            "image": "postgres:16-alpine",
            "container_port": "5432",
            "volume_path": "/var/lib/postgresql/data",
            "healthcheck": "pg_isready -U $${DB_USER:-app} -d $${DB_NAME:-app}",
        }

    return {
        "type": "mysql",
        "image": "mysql:8.4",
        "container_port": "3306",
        "volume_path": "/var/lib/mysql",
        "healthcheck": "mysqladmin ping -h localhost --silent",
    }


def _compose_services(
    projects: list[DockerProject], db_type: Optional[str], api_upstream: Optional[str]
) -> list[dict[str, Any]]:
    services = []
    spring_index = 0
    frontend_index = 0

    for project in projects:
        env_prefix = _environment_prefix(project.service_name)

        if project.kind == "spring":
            spring_index += 1
            internal_port = 8080
            host_port = 8080 + spring_index - 1
            service = {
                "kind": project.kind,
                "name": project.service_name,
                "context": project.relative_context,
                "internal_port": internal_port,
                "port_mapping": f"${{{env_prefix}_PORT:-{host_port}}}:{internal_port}",
                "java_opts_env": f"${{{env_prefix}_JAVA_OPTS:-}}",
                "depends_on_database": db_type is not None,
                "environment": _spring_environment(db_type),
            }
        else:
            frontend_index += 1
            internal_port = 80
            spring_count = len([item for item in projects if item.kind == "spring"])
            host_port = 8080 + spring_count + frontend_index - 1
            service = {
                "kind": project.kind,
                "name": project.service_name,
                "context": project.relative_context,
                "internal_port": internal_port,
                "port_mapping": f"${{{env_prefix}_PORT:-{host_port}}}:{internal_port}",
                "depends_on_api": api_upstream,
            }

        services.append(service)

    return services


def _spring_environment(db_type: Optional[str]) -> dict[str, str]:
    environment = {
        "SERVER_PORT": "8080",
        "APPLICATION_SECURITY_JWT_SECRET_KEY": "${JWT_SECRET:?Set JWT_SECRET in .env}",
    }

    if db_type == "postgres":
        environment.update(
            {
                "SPRING_DATASOURCE_URL": "jdbc:postgresql://database:5432/${DB_NAME:-app}",
                "SPRING_DATASOURCE_USERNAME": "${DB_USER:-app}",
                "SPRING_DATASOURCE_PASSWORD": "${DB_PASSWORD:?Set DB_PASSWORD in .env}",
            }
        )
    elif db_type == "mysql":
        environment.update(
            {
                "SPRING_DATASOURCE_URL": "jdbc:mysql://database:3306/${DB_NAME:-app}",
                "SPRING_DATASOURCE_USERNAME": "${DB_USER:-app}",
                "SPRING_DATASOURCE_PASSWORD": "${DB_PASSWORD:?Set DB_PASSWORD in .env}",
            }
        )

    return environment


def _env_services(projects: list[DockerProject]) -> list[dict[str, str]]:
    services = []
    spring_index = 0
    frontend_index = 0
    spring_count = len([project for project in projects if project.kind == "spring"])

    for project in projects:
        env_prefix = _environment_prefix(project.service_name)
        if project.kind == "spring":
            spring_index += 1
            default_port = str(8080 + spring_index - 1)
            services.append(
                {
                    "name": project.service_name,
                    "port_env": f"{env_prefix}_PORT",
                    "default_port": default_port,
                    "java_opts_env": f"{env_prefix}_JAVA_OPTS",
                    "kind": project.kind,
                }
            )
        else:
            frontend_index += 1
            services.append(
                {
                    "name": project.service_name,
                    "port_env": f"{env_prefix}_PORT",
                    "default_port": str(8080 + spring_count + frontend_index - 1),
                    "java_opts_env": "",
                    "kind": project.kind,
                }
            )

    return services


def _environment_prefix(service_name: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", service_name.upper()).strip("_") or "SERVICE"


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]
