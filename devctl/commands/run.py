import typer

from devctl.orchestrator.runner import launch_dev_environment
from devctl.orchestrator.scanner import detect_environment
from devctl.utils.dependencies import check_tool

app = typer.Typer(help="Local execution and development commands.")


@app.callback(invoke_without_command=True)
def run_env(ctx: typer.Context):
    """
    Scans the current tree and automatically launches Spring, Angular, and the Database.
    """
    if ctx.invoked_subcommand is not None:
        return

    typer.secho("🔍 Analyzing the current directory tree...", fg=typer.colors.CYAN)
    env_state = detect_environment(".")

    # Check dependencies based on detection
    if env_state["has_docker_compose"]:
        check_tool("docker", "running the database environment")

    if env_state["has_spring"]:
        check_tool("java", "running the Spring Boot backend")

    if env_state["has_angular"] or env_state.get("has_vue"):
        check_tool("npm", "running the frontend project")

    # Résumé visuel de la détection pour l'utilisateur
    typer.echo(f"  - Docker Database  : {'✅' if env_state['has_docker_compose'] else '❌'}")
    typer.echo(f"  - Spring Boot Backend : {'✅' if env_state['has_spring'] else '❌'}")
    typer.echo(f"  - Angular Frontend    : {'✅' if env_state['has_angular'] else '❌'}")
    typer.echo(f"  - Vue.js Frontend     : {'✅' if env_state['has_vue'] else '❌'}")

    has_env = any(
        [
            env_state["has_docker_compose"],
            env_state["has_spring"],
            env_state["has_angular"],
            env_state.get("has_vue"),
        ]
    )

    if not has_env:
        typer.secho("\n❌ No valid development environment detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Transfert à la couche d'orchestration système
    launch_dev_environment(env_state)
