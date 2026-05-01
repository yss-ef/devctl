import subprocess
import sys
import time

import typer


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
        # 4. Lancement du Frontend Vue.js
        if env_state.get("has_vue"):
            typer.secho(
                f"🟢 Starting Vue.js from {env_state['vue_path']}...", fg=typer.colors.GREEN
            )

            p_vue = subprocess.Popen(
                ["npm", "run", "dev"],  # Commande standard de Vite
                cwd=env_state["vue_path"],
            )
            processes.append(("Vue.js", p_vue))

        # 1. Lancement de la Base de données
        if env_state["has_docker_compose"]:
            if not is_docker_running():
                typer.secho("❌ Error: Docker service is not running.", fg=typer.colors.RED)
                typer.echo("💡 Hint: sudo systemctl start docker")
                sys.exit(1)

            typer.secho(
                f"🐳 Starting Docker from {env_state['docker_path']}...", fg=typer.colors.CYAN
            )
            subprocess.run(
                ["docker", "compose", "up", "-d"], cwd=env_state["docker_path"], check=True
            )
            time.sleep(5)

            # 2. Lancement du Backend Spring Boot
        if env_state["has_spring"]:
            typer.secho(
                f"🍃 Starting Spring Boot from {env_state['spring_path']}...",
                fg=typer.colors.GREEN,
            )

            # Exécution native Linux
            p_spring = subprocess.Popen(["./mvnw", "spring-boot:run"], cwd=env_state["spring_path"])
            processes.append(("Spring Boot", p_spring))

        # 3. Lancement du Frontend Angular
        if env_state["has_angular"]:
            typer.secho(
                f"🅰️ Starting Angular from {env_state['angular_path']}...", fg=typer.colors.CYAN
            )

            # Exécution native Linux
            p_angular = subprocess.Popen(["npx", "ng", "serve"], cwd=env_state["angular_path"])
            processes.append(("Angular", p_angular))

        if not processes and not env_state["has_docker_compose"]:
            typer.secho(
                "⚠️ No Spring, Angular, Vue.js or DB project detected in this tree.",
                fg=typer.colors.YELLOW,
            )
            return

        typer.secho(
            "\n✨ Development environment active! Press Ctrl+C "
            "to stop everything gracefully.\n",
            fg=typer.colors.GREEN,
            bold=True,
        )

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        typer.secho(
            "\n🛑 Shutdown requested. Performing full cleanup (Please wait, "
            "do not press Ctrl+C again)...",
            fg=typer.colors.YELLOW,
            bold=True,
        )

        for name, p in processes:
            typer.echo(f"Closing {name}...")
            p.terminate()
            p.wait()

        if env_state["has_docker_compose"]:
            typer.echo("Destroying database and Docker volumes...")
            try:
                subprocess.run(
                    ["docker", "compose", "down", "-v"],
                    cwd=env_state["docker_path"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                )
            except subprocess.CalledProcessError:
                typer.secho(
                    "⚠️ Warning: Docker cleanup did not complete correctly.",
                    fg=typer.colors.RED,
                )

        typer.secho(
            "✅ Cleanup finished. Environment is perfectly clean.", fg=typer.colors.GREEN
        )
        sys.exit(0)

    except Exception as e:
        typer.secho(f"❌ A system error occurred: {e}", fg=typer.colors.RED)
