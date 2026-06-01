"""Dockerfile scaffolding for supported devctl projects."""

from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

from jinja2 import Environment, FileSystemLoader

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
    """Raised when Dockerfile scaffolding cannot be completed."""


@dataclass(frozen=True)
class DockerProject:
    """A project that can receive a generated Dockerfile."""

    kind: str
    path: Path
    name: str
    service_name: str
    relative_context: str
    java_version: Optional[str] = None
    node_version: Optional[str] = None
    angular_output_name: Optional[str] = None


@dataclass(frozen=True)
class FileOperation:
    """A single file operation performed or planned by the scaffold command."""

    path: Path
    action: str


@dataclass(frozen=True)
class DockerScaffoldResult:
    """Summary returned after Dockerfile scaffolding."""

    root_path: Path
    services: list[DockerProject]
    operations: list[FileOperation]

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
    """Return a lowercase Docker-friendly service name."""
    service_name = re.sub(r"[^a-z0-9-]+", "-", raw_name.lower()).strip("-")
    service_name = re.sub(r"-{2,}", "-", service_name)
    return service_name or fallback


def discover_docker_projects(root_path: Union[str, Path]) -> list[DockerProject]:
    """Discover all Spring Boot, Angular, and Vue/Vite projects under ``root_path``."""
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
        if "nest-cli.json" in filename_set:
            candidates.append(("nest", project_path))

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
            )
        )

    return projects


def scaffold_docker_assets(
    root_path: Union[str, Path] = ".",
    *,
    force: bool = False,
    dry_run: bool = False,
) -> DockerScaffoldResult:
    """Generate Dockerfiles for all supported projects in a tree."""
    root = Path(root_path).resolve()
    projects = discover_docker_projects(root)
    if not projects:
        raise DockerScaffoldError("No Spring Boot, Angular, or Vue/Vite project detected.")

    env = _template_environment()
    operations = [
        _write_file(
            project.path / "Dockerfile",
            _dockerfile_content(env, project),
            force=force,
            dry_run=dry_run,
        )
        for project in projects
    ]

    return DockerScaffoldResult(root_path=root, services=projects, operations=operations)


def _dockerfile_content(env: Environment, project: DockerProject) -> str:
    if project.kind == "spring":
        return env.get_template("spring/Dockerfile.j2").render(project=project)
    if project.kind == "nest":
        return env.get_template("nestjs/Dockerfile.j2").render(project=project)
    return env.get_template("frontend/Dockerfile.j2").render(project=project)


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

    if kind == "nest":
        return "20"

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


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]
