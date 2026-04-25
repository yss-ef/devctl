import typer

# Import des modules de commandes
from devctl.commands import add, init, run

# Création de l'application Typer principale
app = typer.Typer(help="devctl : L'orchestrateur local pour tes projets Spring/Angular")

# Câblage des sous-menus
app.add_typer(init.app, name="init", help="Initialise un nouveau projet avec sa base de code.")
app.add_typer(
    run.app, name="run", help="Lance l'environnement de développement local en parallèle."
)
app.add_typer(add.app, name="add", help="Génère du code et des ressources métier.")


@app.callback()
def callback():
    """
    devctl : L'orchestrateur local pour tes projets
    """
    # Ce callback vide permet à Typer de comprendre qu'il gère un menu multi-commandes
    pass


@app.command()
def ping():
    """
    Commande de test pour vérifier que le CLI répond.
    """
    typer.secho(
        "pong ! Le CLI devctl est parfaitement opérationnel.", fg=typer.colors.GREEN, bold=True
    )


def main():
    """
    Point d'entrée appelé par le système d'exploitation (via pyproject.toml)
    """
    app()


if __name__ == "__main__":
    main()
