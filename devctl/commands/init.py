import typer

# Génerateur Angular
from devctl.generators.angular import generate_angular_boilerplate

# Générateur Spring
from devctl.generators.spring import download_spring_boilerplate
from devctl.generators.vue import generate_vue_boilerplate
from devctl.orchestrator.config_builder import generate_config
from devctl.utils.dependencies import check_tool

# L'application Typer locale pour le groupe de commandes "init"
app = typer.Typer(help="Initializes a new project based on the chosen framework.")


@app.command("spring")
def init_spring(
    name: str,
    db: str = typer.Option("postgres", help="Database type (postgres or mysql)"),
    port: int = typer.Option(None, help="Local port (optional)"),
):
    """
    Initializes a new Spring Boot backend project with its database.
    """
    check_tool("java", "initializing a Spring Boot project")

    # Validation stricte des entrées
    if db not in ["postgres", "mysql"]:
        typer.secho(f"❌ Error: Database '{db}' is not supported.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"🚀 Initializing Spring Boot project: '{name}'...", fg=typer.colors.CYAN)

    success_download = download_spring_boilerplate(name, db_type=db)

    if success_download:
        generate_config(name, db_type=db, custom_port=port)
        typer.secho("\n✨ Spring project ready!", fg=typer.colors.GREEN)


@app.command("angular")
def init_angular(name: str):
    """
    Initializes a new Angular frontend project.
    """
    check_tool("npm", "initializing an Angular project")
    check_tool("ng", "initializing an Angular project")

    typer.secho(f"🚀 Initializing Angular project: '{name}'...", fg=typer.colors.CYAN)
    success = generate_angular_boilerplate(name)

    if success:
        typer.secho("\n✨ Angular project ready!", fg=typer.colors.GREEN)


@app.command("vue")
def init_vue(name: str):
    """
    Initializes a new Vue.js frontend project (Vite + TS).
    """
    check_tool("npm", "initializing a Vue.js project")

    typer.secho(f"🚀 Initializing Vue.js project: '{name}'...", fg=typer.colors.CYAN)
    success = generate_vue_boilerplate(name)

    if success:
        typer.secho("\n✨ Vue.js project ready!", fg=typer.colors.GREEN)
