"""
CLI command group for adding new resources to existing projects.
Supports Spring Boot, Angular, and Vue.js scaffolding.
"""

import os

import typer

from devctl.generators.scaffold_angular import generate_angular_resource
from devctl.generators.scaffold_spring import generate_spring_resource
from devctl.generators.scaffold_vue import generate_vue_resource
from devctl.generators.scaffold_nestjs import generate_nest_resource
from devctl.orchestrator.scanner import detect_environment

app = typer.Typer(help="Adds resources to the current project (Scaffolding).")


@app.command()
def resource(
    name: str = typer.Argument(..., help="The name of the resource (e.g., Client, Product)"),
    fields: str = typer.Option(
        "", "--fields", "-f", help="Fields in the format 'name:type, age:int'"
    ),
):
    """
    Scans the current folder and generates a suitable business architecture.
    """
    typer.secho("Analyzing current context...", fg=typer.colors.CYAN)
    env_state = detect_environment(".")

    original_dir = os.getcwd()
    project_detected = False

    # Check for Spring Boot project
    if env_state["has_spring"]:
        project_detected = True
        typer.secho(
            "Spring Boot project detected. Launching Java generator...", fg=typer.colors.GREEN
        )
        os.chdir(env_state["spring_path"])
        try:
            generate_spring_resource(name, fields)
        except Exception as e:
            typer.secho(f"Error: Spring generation failed: {e}", fg=typer.colors.RED)
        finally:
            os.chdir(original_dir)

    # Check for Angular project
    if env_state["has_angular"]:
        project_detected = True
        typer.secho(
            "Angular project detected. Launching TypeScript generator...", fg=typer.colors.CYAN
        )
        try:
            generate_angular_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"Error: Angular generation failed: {e}", fg=typer.colors.RED)

    # Check for Vue.js project
    if env_state.get("has_vue"):
        project_detected = True
        typer.secho("Vue.js project detected. Launching Vue generator...", fg=typer.colors.GREEN)
        try:
            generate_vue_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"Error: Vue generation failed: {e}", fg=typer.colors.RED)

    # Check for NestJS project
    if env_state.get("has_nest"):
        project_detected = True
        typer.secho("NestJS project detected. Launching Nest generator...", fg=typer.colors.CYAN)
        try:
            generate_nest_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"Error: Nest generation failed: {e}", fg=typer.colors.RED)

    # Error message only if NO project detected
    if not project_detected:
        typer.secho(
            "Error: Unable to determine project type. "
            "Please run from within a Spring, Angular, or Vue.js project directory.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)
