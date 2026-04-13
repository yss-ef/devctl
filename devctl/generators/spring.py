import os
import stat
import requests
import zipfile
import io
import typer


def download_spring_boilerplate(project_name: str, db_type: str = "postgres"):
    """
    Télécharge et extrait un projet Spring Boot via l'API start.spring.io.
    Rend automatiquement le wrapper Maven exécutable sous Unix.
    """
    typer.echo(f"🔄 Génération du backend Spring Boot '{project_name}' (Driver: {db_type})...")

    # Règle Java : un nom de package ne peut pas contenir de tirets
    safe_package_name = project_name.replace("-", "").replace("_", "").lower()

    # Mapping dynamique pour l'API Spring
    db_dependency = "postgresql" if db_type == "postgres" else "mysql"
    dependencies = f"web,data-jpa,{db_dependency}"

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

        # --- RÉPARATION DES PERMISSIONS UNIX (Le fix pour Fedora) ---
        mvnw_path = os.path.join(os.getcwd(), project_name, "mvnw")
        if os.path.exists(mvnw_path):
            # Récupère les droits actuels du fichier
            st = os.stat(mvnw_path)
            # Ajoute le droit d'exécution (stat.S_IEXEC) pour l'utilisateur courant
            os.chmod(mvnw_path, st.st_mode | stat.S_IEXEC)
        # -------------------------------------------------------------

        typer.secho(f"✅ Backend généré avec succès dans le dossier ./{project_name} !", fg=typer.colors.GREEN)
        return True

    except requests.exceptions.RequestException as e:
        typer.secho(f"❌ Erreur réseau lors du contact de l'API : {e}", fg=typer.colors.RED)
        return False