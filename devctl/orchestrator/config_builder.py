import os
from jinja2 import Environment, FileSystemLoader
import typer


def generate_config(project_name: str, db_type: str = "postgres", custom_port: int = None):
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))

    # Résolution intelligente du port par défaut
    if custom_port is None:
        db_port = 5432 if db_type == "postgres" else 3306
    else:
        db_port = custom_port

    context = {
        "project_name": project_name,
        "db_type": db_type,
        "db_service_name": f"{project_name}-db",
        "db_name": f"{project_name}_db".replace("-", "_"),
        "db_user": "admin",
        "db_password": "password",
        "db_port": db_port
    }

    project_path = os.path.join(os.getcwd(), project_name)

    try:
        docker_template = env.get_template('docker-compose.yml.j2')
        with open(os.path.join(project_path, 'docker-compose.yml'), 'w') as f:
            f.write(docker_template.render(context))

        props_path = os.path.join(project_path, 'src', 'main', 'resources', 'application.properties')
        if os.path.exists(props_path):
            props_template = env.get_template('application.properties.j2')
            with open(props_path, 'w') as f:
                f.write(props_template.render(context))

        typer.secho(f"⚙️ Configuration dynamique ({db_type} sur le port {db_port}) générée.", fg=typer.colors.GREEN)
        return True
    except Exception as e:
        typer.secho(f"❌ Erreur de configuration : {e}", fg=typer.colors.RED)
        return False