import subprocess
import typer


def generate_angular_boilerplate(project_name: str) -> bool:
    """
    Génère un projet Angular via le CLI natif (@angular/cli)
    """
    typer.echo(f"🔄 Génération du frontend Angular '{project_name}'...")

    # Règle Angular : les noms préfèrent les tirets et les minuscules
    safe_name = project_name.lower().replace("_", "-")

    # 1. Vérification des prérequis de l'OS
    try:
        # On teste si 'ng' répond. S'il n'existe pas, ça lève une FileNotFoundError
        subprocess.run(["ng", "version"], capture_output=True, check=True)
    except FileNotFoundError:
        typer.secho("❌ Erreur : Le CLI Angular ('ng') est introuvable sur ton système.", fg=typer.colors.RED)
        typer.echo("💡 Astuce : Installe-le d'abord avec la commande : npm install -g @angular/cli")
        return False
    except subprocess.CalledProcessError:
        typer.secho("❌ Erreur : Le CLI Angular est installé mais ne répond pas correctement.", fg=typer.colors.RED)
        return False

    # 2. Exécution de la création du projet
    try:
        # On configure les flags pour éviter que 'ng new' ne pose des questions interactives
        command = [
            "ng", "new", safe_name,
            "--routing=true",
            "--style=scss",
            "--skip-git=true"  # On gérera Git globalement plus tard, pas juste pour le front
        ]

        typer.echo("📦 Téléchargement des packages npm... (Cela peut prendre 1 à 2 minutes)")

        # On lance la commande. On ne capture pas la sortie pour que tu puisses voir
        # la barre de progression npm d'Angular directement dans ton terminal.
        subprocess.run(command, check=True)

        typer.secho(f"✅ Frontend '{safe_name}' généré avec succès dans le dossier ./{safe_name} !",
                    fg=typer.colors.GREEN)
        return True

    except subprocess.CalledProcessError as e:
        typer.secho(f"❌ Le processus Angular a échoué avec le code : {e.returncode}", fg=typer.colors.RED)
        return False