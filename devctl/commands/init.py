import typer
# Générateur Spring
from devctl.generators.spring import download_spring_boilerplate


# L'application Typer locale pour le groupe de commandes "init"
app = typer.Typer(help="Initialise un nouveau projet selon le framework choisi.")


@app.command("spring")
def init_spring(name: str):
    """
    Initialise un nouveau projet backend Spring Boot.
    """
    typer.echo(f"🚀 Initialisation d'un projet Spring Boot : '{name}'...")

    success = download_spring_boilerplate(name)

    if success:
        typer.secho("\n✨ Projet Spring prêt ! Prochaine étape : on configurera la DB.", fg=typer.colors.CYAN)


@app.command("angular")
def init_angular(name: str):
    """
    (Bientôt) Initialise un nouveau projet frontend Angular.
    """
    # Pour l'instant, c'est juste un espace réservé (placeholder)
    typer.echo(f"🚀 Initialisation d'un projet Angular : '{name}'...")
    typer.secho("⚠️ Le générateur Angular n'est pas encore implémenté.", fg=typer.colors.YELLOW)


@app.command("express")
def init_express(name: str):
    """
    (Bientôt) Initialise un nouveau projet Node.js / Express.
    """
    typer.echo(f"🚀 Initialisation d'un projet Express : '{name}'...")
    typer.secho("⚠️ Le générateur Express n'est pas encore implémenté.", fg=typer.colors.YELLOW)