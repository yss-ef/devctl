import typer
from devctl.orchestrator.runner import launch_dev_environment
from devctl.orchestrator.scanner import detect_environment

app = typer.Typer(help="Commandes d'exécution et de développement local.")


@app.callback(invoke_without_command=True)
def run_env(ctx: typer.Context):
    """
    Scanne l'arborescence courante et lance automatiquement Spring, Angular et la Base de données.
    """
    if ctx.invoked_subcommand is not None:
        return

    typer.echo("🔍 Analyse de l'arborescence courante...")
    env_state = detect_environment(".")

    # Résumé visuel de la détection pour l'utilisateur
    typer.echo(f"  - Base de données Docker : {'✅' if env_state['has_docker_compose'] else '❌'}")
    typer.echo(f"  - Backend Spring Boot  : {'✅' if env_state['has_spring'] else '❌'}")
    typer.echo(f"  - Frontend Angular     : {'✅' if env_state['has_angular'] else '❌'}")
    typer.echo(f"  - Frontend Vue.js      : {'✅' if env_state['has_vue'] else '❌'}")

    has_env = any([
        env_state['has_docker_compose'],
        env_state['has_spring'],
        env_state['has_angular'],
        env_state.get('has_vue')
    ])

    if not has_env:
        typer.secho(
            "\n❌ Aucun environnement de développement valide détecté ici.",
            fg=typer.colors.RED
        )
        raise typer.Exit(code=1)

    # Transfert à la couche d'orchestration système
    launch_dev_environment(env_state)
