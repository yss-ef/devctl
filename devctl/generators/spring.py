import os
import requests
import zipfile
import io
import typer


def download_spring_boilerplate(project_name: str, db_type: str = "postgres"):
    """
    Télécharge et extrait un projet Spring Boot via l'API start.spring.io
    """
    typer.echo(f"🔄 Génération du backend Spring Boot '{project_name}' (Driver: {db_type})...")

    safe_package_name = project_name.replace("-", "").replace("_", "").lower()

    # Mapping dynamique pour l'API Spring
    db_dependency = "postgresql" if db_type == "postgres" else "mysql"
    dependencies = f"web,data-jpa,{db_dependency}"

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
        "dependencies": dependencies
    }

    url = "https://start.spring.io/starter.zip"

    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            typer.secho(f"❌ Refus de l'API : {response.text}", fg=typer.colors.RED)
            return False

        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(os.getcwd())

        typer.secho(f"✅ Backend généré avec succès !", fg=typer.colors.GREEN)
        return True

    except requests.exceptions.RequestException as e:
        typer.secho(f"❌ Erreur réseau : {e}", fg=typer.colors.RED)
        return False