import typer
import os
from devctl.orchestrator.scanner import detect_environment
from devctl.generators.scaffold_spring import generate_spring_resource
from devctl.generators.scaffold_angular import generate_angular_resource

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

    original_dir = os.getcwd()
    project_detected = False # <-- On change le nom pour que ce soit plus logique

    if env_state["has_spring"]:
        project_detected = True
        typer.secho("🍃 Projet Spring Boot détecté. Lancement du générateur Java...", fg=typer.colors.GREEN)
        os.chdir(env_state["spring_path"])
        try:
            generate_spring_resource(name, fields)
        except Exception as e:
            typer.secho(f"❌ Erreur lors de la génération Spring : {e}", fg=typer.colors.RED)
        finally:
            os.chdir(original_dir)

    if env_state["has_angular"]:
        project_detected = True
        typer.secho("🅰️ Projet Angular détecté. Lancement du générateur TypeScript...", fg=typer.colors.CYAN)
        try:
            generate_angular_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"❌ Erreur lors de la génération Angular : {e}", fg=typer.colors.RED)

    # Le message d'erreur ne s'affiche que s'il n'y a VRAIMENT aucun projet
    if not project_detected:
        typer.secho(
            "❌ Impossible de déterminer le type de projet. Place-toi dans ou au-dessus d'un projet Spring ou Angular.",
            fg=typer.colors.RED
        )
        raise typer.Exit(code=1)