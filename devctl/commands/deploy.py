import re
from pathlib import Path
from typing import Any, Dict, Optional

import typer
import yaml
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
        try:
            with open(compose_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if config and "services" in config:
                    # Find the first service that looks like a database
                    for s_name, s_cfg in config["services"].items():
                        image = str(s_cfg.get("image", ""))
                        if db_type == "postgresql" and "postgres" in image:
                            db_dict["service_name"] = s_name
                            break
                        if db_type == "mysql" and "mysql" in image:
                            db_dict["service_name"] = s_name
                            break
        except Exception:
            pass

    return db_dict


def extract_db_from_compose(compose_path: Path) -> Optional[Dict[str, Any]]:
    """
    Extract database information from a docker-compose.yml file using PyYAML.
    """
    if not compose_path.exists():
        return None

    try:
        with open(compose_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception:
        return None

    if not config or "services" not in config:
        return None

    for service_name, service_cfg in config["services"].items():
        image = str(service_cfg.get("image", ""))
        if "postgres" in image or "mysql" in image:
            db_type = "postgresql" if "postgres" in image else "mysql"

            # Extract environment variables
            env = service_cfg.get("environment", {})
            env_dict = {}
            if isinstance(env, list):
                for item in env:
                    if "=" in item:
                        k, v = item.split("=", 1)
                        env_dict[k] = v
                    elif ":" in item:
                        k, v = item.split(":", 1)
                        env_dict[k] = v.strip()
            elif isinstance(env, dict):
                env_dict = env

            # Extract info based on db_type
            if db_type == "postgresql":
                user = env_dict.get("POSTGRES_USER", "admin")
                password = env_dict.get("POSTGRES_PASSWORD", "password")
                db_name = env_dict.get("POSTGRES_DB", "db")
            else:
                user = env_dict.get("MYSQL_USER", env_dict.get("MYSQL_ROOT_PASSWORD", "admin"))
                password = env_dict.get("MYSQL_PASSWORD", env_dict.get("MYSQL_ROOT_PASSWORD", "password"))
                db_name = env_dict.get("MYSQL_DATABASE", "db")

            # Extract port
            ports = service_cfg.get("ports", [])
            host_port = None
            if ports and isinstance(ports, list):
                first_port = str(ports[0])
                if ":" in first_port:
                    host_port = first_port.split(":")[0].strip("'").strip('"')

            db_dict = _build_db_dict(
                db_type,
                host_port or ("5432" if db_type == "postgresql" else "3306"),
                db_name,
                user,
                password,
            )
            db_dict["service_name"] = service_name
            return db_dict

    return None


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
