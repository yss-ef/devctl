import os
import requests
import zipfile
import io
import typer


def download_spring_boilerplate(project_name: str):
    """
    Télécharge et extrait un projet Spring Boot via l'API start.spring.io
    """
    typer.echo(f"🔄 Génération du backend Spring Boot '{project_name}'...")

    # Règle Java : un nom de package ne peut pas contenir de tirets
    safe_package_name = project_name.replace("-", "").replace("_", "").lower()

    # Paramètres de l'API Spring Initializr (sans bootVersion pour avoir toujours la dernière stable)
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
        "dependencies": "web,data-jpa,postgresql"
    }

    url = "https://start.spring.io/starter.zip"

    try:
        response = requests.get(url, params=params)

        # Affiche l'erreur exacte renvoyée par l'API si elle échoue encore
        if response.status_code != 200:
            typer.secho(f"❌ Refus de l'API : {response.text}", fg=typer.colors.RED)
            return False

        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(os.getcwd())

        typer.secho(f"✅ Backend '{project_name}' généré avec succès dans le dossier ./{project_name} !",
                    fg=typer.colors.GREEN)
        return True

    except requests.exceptions.RequestException as e:
        typer.secho(f"❌ Erreur réseau : {e}", fg=typer.colors.RED)
        return False