import re
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from jinja2 import Environment, FileSystemLoader

from devctl.generators.docker_scaffold import (
    discover_docker_projects,
)

app = typer.Typer(help="Deployment and orchestration commands.")

PATH_ARGUMENT = typer.Argument(
    Path("."),
    help="Repository or project directory to scan for services.",
)


def extract_db_info(project_path: Path) -> Optional[Dict[str, Any]]:
    """
    Extract database information from a Spring Boot project's application.properties.
    """
    props_path = project_path / "src" / "main" / "resources" / "application.properties"
    if not props_path.exists():
        # Fallback to checking for docker-compose.yml in the same dir
        return extract_db_from_compose(project_path / "docker-compose.yml")

    content = props_path.read_text(encoding="utf-8", errors="ignore")

    # spring.datasource.url=jdbc:postgresql://localhost:5432/sample_api_db
    url_match = re.search(r"spring\.datasource\.url=jdbc:([^:]+)://[^:]+:(\d+)/([\w-]+)", content)
    user_match = re.search(r"spring\.datasource\.username=([\w-]+)", content)
    pass_match = re.search(r"spring\.datasource\.password=([\w-]+)", content)

    if not url_match:
        return extract_db_from_compose(project_path / "docker-compose.yml")

    db_type_raw = url_match.group(1)
    db_type = "postgresql" if "postgres" in db_type_raw else "mysql"
    db_port = url_match.group(2)
    db_name = url_match.group(3)
    db_user = user_match.group(1) if user_match else "admin"
    db_pass = pass_match.group(1) if pass_match else "password"

    db_dict = _build_db_dict(db_type, db_port, db_name, db_user, db_pass)

    # Try to refine service name from existing docker-compose if possible
    compose_path = project_path / "docker-compose.yml"
    if compose_path.exists():
        compose_content = compose_path.read_text(encoding="utf-8", errors="ignore")
        service_match = re.search(r"services:\s*\n\s+([\w-]+):", compose_content)
        if service_match:
            db_dict["service_name"] = service_match.group(1)

    return db_dict


def extract_db_from_compose(compose_path: Path) -> Optional[Dict[str, Any]]:
    """
    Extract database information from a docker-compose.yml file using regex.
    """
    if not compose_path.exists():
        return None

    content = compose_path.read_text(encoding="utf-8", errors="ignore")

    # This is a bit hacky without PyYAML but follows devctl's generated structure
    # Try to find the first service name under 'services:'
    service_match = re.search(r"services:\s*\n\s+([\w-]+):", content)
    original_service_name = service_match.group(1) if service_match else None

    image_match = re.search(r"image:\s+(postgres|mysql)(:[\w.-]+)?", content)
    if not image_match:
        return None

    db_type = "postgresql" if image_match.group(1) == "postgres" else "mysql"

    # Try to find env vars
    if db_type == "postgresql":
        user = re.search(r"POSTGRES_USER:\s+([\w-]+)", content)
        password = re.search(r"POSTGRES_PASSWORD:\s+([\w-]+)", content)
        db_name = re.search(r"POSTGRES_DB:\s+([\w-]+)", content)
    else:
        user = re.search(r"MYSQL_USER:\s+([\w-]+)", content)
        password = re.search(r"MYSQL_PASSWORD:\s+([\w-]+)", content)
        db_name = re.search(r"MYSQL_DATABASE:\s+([\w-]+)", content)

    port_match = re.search(r"\"(\d+):(\d+)\"", content)

    db_dict = _build_db_dict(
        db_type,
        port_match.group(1) if port_match else ("5432" if db_type == "postgresql" else "3306"),
        db_name.group(1) if db_name else "db",
        user.group(1) if user else "admin",
        password.group(1) if password else "password",
    )

    if original_service_name:
        db_dict["service_name"] = original_service_name

    return db_dict


def _build_db_dict(db_type: str, port: str, name: str, user: str, password: str) -> Dict[str, Any]:
    is_postgres = db_type == "postgresql"
    internal_port = "5432" if is_postgres else "3306"

    env = {}
    if is_postgres:
        env = {
            "POSTGRES_USER": user,
            "POSTGRES_PASSWORD": password,
            "POSTGRES_DB": name,
        }
    else:
        env = {
            "MYSQL_ROOT_PASSWORD": password,
            "MYSQL_DATABASE": name,
            "MYSQL_USER": user,
            "MYSQL_PASSWORD": password,
        }

    return {
        "type": db_type,
        "port": port,
        "internal_port": internal_port,
        "name": name,
        "user": user,
        "password": password,
        "service_name": f"{name}-db",
        "image": "postgres:15-alpine" if is_postgres else "mysql:8.0",
        "volume_name": f"{name}_data",
        "volume_path": "/var/lib/postgresql/data" if is_postgres else "/var/lib/mysql/data",
        "env": env,
    }


@app.command()
def deploy(path: Path = PATH_ARGUMENT):
    """
    Generate a global docker-compose.yml by scanning subdirectories.
    """
    typer.secho(f"🚀 Preparing deployment for {path.resolve()}...", fg=typer.colors.CYAN, bold=True)

    try:
        projects = discover_docker_projects(path)
    except Exception as e:
        typer.secho(f"❌ Error scanning projects: {e}", fg=typer.colors.RED)
        raise typer.Exit(1) from e

    if not projects:
        typer.secho("❌ No supported projects (Spring, Angular, Vue) found.", fg=typer.colors.RED)
        raise typer.Exit(1)

    services_data = []
    databases = []
    seen_db_names = set()

    for project in projects:
        dockerfile_path = project.path / "Dockerfile"
        if not dockerfile_path.exists():
            typer.secho(
                f"⚠️ Warning: No Dockerfile found in {project.path}. "
                "You may need to run 'devctl dockerize' first.",
                fg=typer.colors.YELLOW,
            )

        service_dict = {
            "service_name": project.service_name,
            "kind": project.kind,
            "relative_context": project.relative_context,
            "db": None,
        }

        if project.kind == "spring":
            db_info = extract_db_info(project.path)
            if db_info:
                service_dict["db"] = db_info
                if db_info["service_name"] not in seen_db_names:
                    databases.append(db_info)
                    seen_db_names.add(db_info["service_name"])

        services_data.append(service_dict)

    # Setup Jinja2
    template_dir = Path(__file__).resolve().parent.parent / "templates" / "docker"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("deploy.yml.j2")

    # Render template
    output = template.render(services=services_data, databases=databases)

    # Write to root docker-compose.yml
    output_path = path / "docker-compose.yml"
    output_path.write_text(output, encoding="utf-8")

    typer.secho(f"✅ Generated {output_path}", fg=typer.colors.GREEN, bold=True)
    typer.echo(f"Summary: {len(services_data)} services, {len(databases)} databases.")
