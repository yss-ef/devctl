import typer

# Import des modules de commandes
from devctl.commands import add, init, run

# Création de l'application Typer principale
app = typer.Typer(help="devctl: Local orchestrator for your Spring/Angular projects")

# Câblage des sous-menus
app.add_typer(init.app, name="init", help="Initialize a new project with its codebase.")
app.add_typer(
    run.app, name="run", help="Launch the local development environment in parallel."
)
app.add_typer(add.app, name="add", help="Generate code and business resources.")


@app.callback()
def callback():
    """
    devctl: Local orchestrator for your projects
    """
    # Ce callback vide permet à Typer de comprendre qu'il gère un menu multi-commandes
    pass


@app.command()
def ping():
    """
    Health check command to verify the CLI is responding.
    """
    typer.secho(
        "pong! The devctl CLI is perfectly operational.", fg=typer.colors.GREEN, bold=True
    )


def main():
    """
    Point d'entrée appelé par le système d'exploitation (via pyproject.toml)
    """
    app()


if __name__ == "__main__":
    main()
