import typer

# Import command modules
from devctl.commands import add, docker, init, run

# Create the main Typer application
app = typer.Typer(help="devctl: Local orchestrator for your Spring/Angular projects")

# Register sub-menus
app.add_typer(init.app, name="init", help="Initialize a new project with its codebase.")
app.add_typer(run.app, name="run", help="Launch the local development environment in parallel.")
app.add_typer(add.app, name="add", help="Generate code and business resources.")
app.command("dockerize", help="Scaffold Dockerfiles for supported projects.")(docker.dockerize)


@app.callback()
def callback():
    """
    devctl: Local orchestrator for your projects
    """
    # This empty callback allows Typer to understand it's managing a multi-command menu
    pass


@app.command()
def ping():
    """
    Health check command to verify the CLI is responding.
    """
    typer.secho("pong! The devctl CLI is perfectly operational.", fg=typer.colors.GREEN, bold=True)


def main():
    """
    Application entry point called by the OS (via pyproject.toml)
    """
    app()


if __name__ == "__main__":
    main()
