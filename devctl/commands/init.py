import typer

# Génerateur Angular
from devctl.generators.angular import generate_angular_boilerplate

# Générateur Spring
from devctl.generators.spring import download_spring_boilerplate
from devctl.generators.vue import generate_vue_boilerplate
from devctl.orchestrator.config_builder import generate_config

# L'application Typer locale pour le groupe de commandes "init"
app = typer.Typer(help="Initialise un nouveau projet selon le framework choisi.")


@app.command("spring")
def init_spring(
        name: str,
        db: str = typer.Option("postgres", help="Type de base de données (postgres ou mysql)"),
        port: int = typer.Option(None, help="Port local (optionnel)")
):
    """
    Initialise un nouveau projet backend Spring Boot avec sa base de données.
    """
    # Validation stricte des entrées
    if db not in ["postgres", "mysql"]:
        typer.secho(
            f"❌ Erreur : La base de données '{db}' n'est pas supportée.",
            fg=typer.colors.RED
        )
        raise typer.Exit(code=1)

    typer.echo(f"🚀 Initialisation d'un projet Spring Boot : '{name}'...")

    success_download = download_spring_boilerplate(name, db_type=db)

    if success_download:
        generate_config(name, db_type=db, custom_port=port)
        typer.secho("\n✨ Projet Spring prêt !", fg=typer.colors.CYAN)

@app.command("angular")
def init_angular(name: str):
    """
    (Bientôt) Initialise un nouveau projet frontend Angular.
    """
    # Pour l'instant, c'est juste un espace réservé (placeholder)
    typer.echo(f"🚀 Initialisation d'un projet Angular : '{name}'...")
    success = generate_angular_boilerplate(name)

    if success:
        typer.secho("\n✨ Projet Angular prêt !", fg=typer.colors.CYAN)




@app.command("vue")
def init_vue(name: str):
    """
    Initialise un nouveau projet frontend Vue.js (Vite + TS).
    """
    typer.echo(f"🚀 Initialisation d'un projet Vue.js : '{name}'...")
    success = generate_vue_boilerplate(name)

    if success:
        typer.secho("\n✨ Projet Vue.js prêt !", fg=typer.colors.CYAN)
