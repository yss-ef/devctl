import io
import os
import stat
import zipfile

import requests
import typer

from devctl.generators.scaffold_spring import generate_spring_security


def download_spring_boilerplate(project_name: str, db_type: str = "postgres"):
    """
    Downloads and extracts a Spring Boot project via the start.spring.io API.
    Automatically makes the Maven wrapper executable on Unix.
    """
    typer.secho(f"🔄 Generating Spring Boot backend '{project_name}' (Driver: {db_type})...", fg=typer.colors.CYAN)

    # Règle Java : un nom de package ne peut pas contenir de tirets
    safe_package_name = project_name.replace("-", "").replace("_", "").lower()

    # Mapping dynamique pour l'API Spring
    db_dependency = "postgresql" if db_type == "postgres" else "mysql"
    official_deps = [
        "web",
        "lombok",
        "data-jpa",
        "validation",
        "security",
        "devtools",
        "thymeleaf",
        db_dependency,  # postgresql ou mysql
    ]
    dependencies = ",".join(official_deps)

    # Paramètres de l'API Spring Initializr
    params = {
        "type": "maven-project",
        "language": "java",
        "baseDir": project_name,
        "groupId": "com.devctl",
        "artifactId": project_name,
        "name": project_name,
        "description": "Projet Spring Boot généré par devctl",
        "packageName": f"com.devctl.{safe_package_name}",
        "packaging": "jar",
        "javaVersion": "17",
        "dependencies": dependencies,
    }

    url = "https://start.spring.io/starter.zip"

    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            typer.secho(f"❌ API Rejected: {response.text}", fg=typer.colors.RED)
            return False

        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(os.getcwd())

        mvnw_path = os.path.join(os.getcwd(), project_name, "mvnw")
        if os.path.exists(mvnw_path):
            # Récupère les droits actuels du fichier
            st = os.stat(mvnw_path)
            # Ajoute le droit d'exécution (stat.S_IEXEC) pour l'utilisateur courant
            os.chmod(mvnw_path, st.st_mode | stat.S_IEXEC)

        os.chdir(project_name)
        generate_spring_security()
        os.chdir("..")

        typer.secho(
            f"✅ Backend successfully generated in folder ./{project_name}!",
            fg=typer.colors.GREEN,
        )
        return True

    except requests.exceptions.RequestException as e:
        typer.secho(f"❌ Network error contacting API: {e}", fg=typer.colors.RED)
        return False
