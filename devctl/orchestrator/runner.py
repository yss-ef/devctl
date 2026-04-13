import subprocess
import time
import typer
import sys


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
    Lance les processus nécessaires en parallèle (Optimisé pour Linux/Fedora).
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
            time.sleep(5)

            # 2. Lancement du Backend Spring Boot
        if env_state["has_spring"]:
            typer.secho(f"🍃 Démarrage de Spring Boot depuis {env_state['spring_path']}...", fg=typer.colors.GREEN)

            # Exécution native Linux
            p_spring = subprocess.Popen(
                ["./mvnw", "spring-boot:run"],
                cwd=env_state["spring_path"]
            )
            processes.append(("Spring Boot", p_spring))

        # 3. Lancement du Frontend Angular
        if env_state["has_angular"]:
            typer.secho(f"🅰️ Démarrage d'Angular depuis {env_state['angular_path']}...", fg=typer.colors.RED)

            # Exécution native Linux
            p_angular = subprocess.Popen(
                ["npx", "ng", "serve"],
                cwd=env_state["angular_path"]
            )
            processes.append(("Angular", p_angular))

        if not processes and not env_state["has_docker_compose"]:
            typer.secho("⚠️ Aucun projet Spring, Angular ou DB détecté dans cette arborescence.",
                        fg=typer.colors.YELLOW)
            return

        typer.secho("\n✨ Environnement de développement actif ! Appuie sur Ctrl+C pour tout arrêter proprement.\n",
                    fg=typer.colors.CYAN, bold=True)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        typer.secho("\n🛑 Arrêt demandé. Nettoyage complet en cours (Merci de patienter, ne pas refaire Ctrl+C)...",
                    fg=typer.colors.YELLOW, bold=True)

        for name, p in processes:
            typer.echo(f"Fermeture de {name}...")
            p.terminate()
            p.wait()

        if env_state["has_docker_compose"]:
            typer.echo("Destruction de la base de données et des volumes Docker...")
            try:
                subprocess.run(
                    ["docker", "compose", "down", "-v"],
                    cwd=env_state["docker_path"],
                    check=True,
                    stdout=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError:
                typer.secho("⚠️ Attention : Le nettoyage Docker ne s'est pas terminé correctement.",
                            fg=typer.colors.RED)

        typer.secho("✅ Nettoyage terminé. Environnement parfaitement propre.", fg=typer.colors.GREEN)
        sys.exit(0)

    except Exception as e:
        typer.secho(f"❌ Une erreur système est survenue : {e}", fg=typer.colors.RED)