import typer
import os
from devctl.orchestrator.scanner import detect_environment
from devctl.generators.scaffold_spring import generate_spring_resource

app = typer.Typer(help="Ajoute des ressources au projet courant (Scaffolding).")


@app.command()
def resource(
        name: str = typer.Argument(..., help="Le nom de la ressource (ex: Client, Produit)"),
        fields: str = typer.Option("", "--fields", "-f", help="Les champs au format 'nom:type, age:int'")
):
    """
    Scanne le dossier courant et génère une architecture métier adaptée.
    """
    typer.echo("🔍 Analyse du contexte courant...")
    env_state = detect_environment(".")

    if env_state["has_spring"]:
        typer.secho("🍃 Projet Spring Boot détecté. Lancement du générateur Java...", fg=typer.colors.GREEN)

        # On se déplace virtuellement dans le dossier Spring au cas où on lance la commande depuis la racine d'un monorepo
        original_dir = os.getcwd()
        os.chdir(env_state["spring_path"])

        generate_spring_resource(name, fields)

        os.chdir(original_dir)

    elif env_state["has_angular"]:
        typer.secho("🚧 Projet Angular détecté. La génération frontend arrive dans la prochaine version !",
                    fg=typer.colors.YELLOW)

    else:
        typer.secho(
            "❌ Impossible de déterminer le type de projet. Place-toi dans un dossier contenant un projet Spring ou Angular.",
            fg=typer.colors.RED)
        raise typer.Exit(code=1)