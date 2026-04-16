import os
import json
import subprocess
import typer
from jinja2 import Environment, FileSystemLoader


def setup_angular_environments(project_path: str):
    """
    Génère les environnements et le proxy pour un projet Angular.
    """
    typer.echo("⚙️  Configuration du Proxy et des Environnements...")

    # 1. Chemins cibles
    src_dir = os.path.join(project_path, "src")
    env_dir = os.path.join(src_dir, "environments")
    os.makedirs(env_dir, exist_ok=True)

    # 2. Rendu des templates via Jinja2
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "angular", "config")
    env = Environment(loader=FileSystemLoader(templates_dir))

    files_to_generate = {
        "proxy.conf.json.j2": os.path.join(project_path, "src", "proxy.conf.json"),  # À la racine de src/
        "environment.ts.j2": os.path.join(env_dir, "environment.ts"),
        "environment.development.ts.j2": os.path.join(env_dir, "environment.development.ts")
    }

    for tpl_name, target_path in files_to_generate.items():
        try:
            template = env.get_template(tpl_name)
            content = template.render()
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            typer.secho(f"⚠️  Erreur lors de la génération de {tpl_name}: {e}", fg=typer.colors.YELLOW)

    # 3. Modification de angular.json pour activer le proxy
    angular_json_path = os.path.join(project_path, "angular.json")
    if os.path.exists(angular_json_path):
        with open(angular_json_path, "r", encoding="utf-8") as f:
            angular_config = json.load(f)

        try:
            # On trouve le nom du projet par défaut (souvent le même nom que le dossier)
            project_name = list(angular_config["projects"].keys())[0]

            # Injection du proxyConfig dans l'architecte "serve"
            serve_target = angular_config["projects"][project_name]["architect"]["serve"]

            # S'assure que "options" existe
            if "options" not in serve_target:
                serve_target["options"] = {}

            serve_target["options"]["proxyConfig"] = "src/proxy.conf.json"

            with open(angular_json_path, "w", encoding="utf-8") as f:
                json.dump(angular_config, f, indent=2)

            typer.echo("  - angular.json mis à jour avec le proxyConfig.")
        except Exception as e:
            typer.secho(f"⚠️  Impossible de modifier angular.json automatiquement : {e}", fg=typer.colors.YELLOW)


def generate_angular_boilerplate(project_name: str) -> bool:
    """
    Génère un projet Angular via le CLI natif (@angular/cli) et le configure.
    """
    typer.echo(f"🔄 Génération du frontend Angular '{project_name}'...")

    safe_name = project_name.lower().replace("_", "-")

    try:
        subprocess.run(["ng", "version"], capture_output=True, check=True)
    except FileNotFoundError:
        typer.secho("❌ Erreur : Le CLI Angular ('ng') est introuvable sur ton système.", fg=typer.colors.RED)
        return False
    except subprocess.CalledProcessError:
        typer.secho("❌ Erreur : Le CLI Angular est installé mais ne répond pas.", fg=typer.colors.RED)
        return False

    try:
        command = [
            "ng", "new", safe_name,
            "--routing=true",
            "--style=scss",
            "--skip-git=true"
        ]

        typer.echo("📦 Téléchargement des packages npm... (Cela peut prendre 1 à 2 minutes)")
        subprocess.run(command, check=True)

        # --- NOUVEAU : Appel de la configuration post-installation ---
        project_full_path = os.path.join(os.getcwd(), safe_name)
        setup_angular_environments(project_full_path)
        # -------------------------------------------------------------

        typer.secho(f"✅ Frontend '{safe_name}' généré et configuré avec succès !", fg=typer.colors.GREEN)
        return True

    except subprocess.CalledProcessError as e:
        typer.secho(f"❌ Le processus Angular a échoué avec le code : {e.returncode}", fg=typer.colors.RED)
        return False