import subprocess
import time
import typer
import sys

# Détection de l'OS pour le routage des commandes
IS_WINDOWS = sys.platform == "win32"


def is_docker_running():
    """
    Vérifie si le daemon Docker est actif sur le système.
    """
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def launch_dev_environment(env_state: dict):
    """
    Lance les processus nécessaires en parallèle selon l'état détecté.
    """
    processes = []

    try:
        # 1. Lancement de la Base de données
        if env_state["has_docker_compose"]:
            if not is_docker_running():
                typer.secho("❌ Erreur : Le service Docker n'est pas démarré.", fg=typer.colors.RED)
                typer.echo("💡 Astuce : sudo systemctl start docker")
                sys.exit(1)

            typer.secho(f"🐳 Démarrage de Docker depuis {env_state['docker_path']}...", fg=typer.colors.BLUE)
            subprocess.run(["docker", "compose", "up", "-d"], cwd=env_state["docker_path"], check=True)
            time.sleep(5)  # Temporisation pour l'initialisation du moteur BDD

        # 2. Lancement du Backend Spring Boot
        if env_state["has_spring"]:
            typer.secho(f"🍃 Démarrage de Spring Boot depuis {env_state['spring_path']}...", fg=typer.colors.GREEN)

            # Routage dynamique de l'exécutable
            maven_cmd = "mvnw.cmd" if IS_WINDOWS else "./mvnw"

            p_spring = subprocess.Popen(
                [maven_cmd, "spring-boot:run"],
                cwd=env_state["spring_path"],
                shell=IS_WINDOWS
            )
            processes.append(("Spring Boot", p_spring))

        # 3. Lancement du Frontend Angular
        if env_state["has_angular"]:
            typer.secho(f"🅰️ Démarrage d'Angular depuis {env_state['angular_path']}...", fg=typer.colors.RED)

            p_angular = subprocess.Popen(
                ["npx", "ng", "serve"],
                cwd=env_state["angular_path"],
                shell=IS_WINDOWS
            )
            processes.append(("Angular", p_angular))

        if not processes and not env_state["has_docker_compose"]:
            typer.secho("⚠️ Aucun projet Spring, Angular ou DB détecté dans cette arborescence.",
                        fg=typer.colors.YELLOW)
            return

        typer.secho("\n✨ Environnement de développement actif ! Appuie sur Ctrl+C pour tout arrêter proprement.\n",
                    fg=typer.colors.CYAN, bold=True)

        # Maintien en vie du thread principal
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        typer.secho("\n🛑 Arrêt demandé. Nettoyage complet en cours (Merci de patienter, ne pas refaire Ctrl+C)...",
                    fg=typer.colors.YELLOW, bold=True)

        # 1. Arrêt des processus locaux enfants
        for name, p in processes:
            typer.echo(f"Fermeture de {name}...")
            p.terminate()
            p.wait()

        # 2. Destruction de l'infrastructure Docker (down -v pour purger les volumes)
        if env_state["has_docker_compose"]:
            typer.echo("Destruction de la base de données et des volumes Docker...")
            try:
                subprocess.run(
                    ["docker", "compose", "down", "-v"],
                    cwd=env_state["docker_path"],
                    check=True,
                    stdout=subprocess.DEVNULL  # Silence la sortie console de Docker
                )
            except subprocess.CalledProcessError:
                typer.secho("⚠️ Attention : Le nettoyage Docker ne s'est pas terminé correctement.",
                            fg=typer.colors.RED)

        typer.secho("✅ Nettoyage terminé. Environnement parfaitement propre.", fg=typer.colors.GREEN)
        sys.exit(0)

    except Exception as e:
        typer.secho(f"❌ Une erreur système est survenue : {e}", fg=typer.colors.RED)