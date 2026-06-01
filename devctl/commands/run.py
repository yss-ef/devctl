"""
CLI command group for running the local development environment.
Automatically detects and launches backend, frontend, and database services.
"""

import typer
from pathlib import Path

from devctl.orchestrator.runner import launch_dev_environment
from devctl.generators.docker_scaffold import discover_docker_projects
from devctl.utils.dependencies import check_tool

app = typer.Typer(help="Local execution and development commands.")


@app.callback(invoke_without_command=True)
def run_env(ctx: typer.Context):
    """
    Scans the current tree and automatically launches Spring, Angular, Vue, and Databases.
    """
    if ctx.invoked_subcommand is not None:
        return

    typer.secho("Analyzing the current directory tree...", fg=typer.colors.CYAN)
    
    projects = discover_docker_projects(".")
    
    # Check for docker-compose.yml files
    docker_composes = []
    for p in Path(".").rglob("docker-compose.yml"):
        if "node_modules" not in str(p) and "target" not in str(p) and ".git" not in str(p):
            docker_composes.append(p.parent)

    has_spring = any(p.kind == "spring" for p in projects)
    has_angular = any(p.kind == "angular" for p in projects)
    has_vue = any(p.kind == "vue" for p in projects)
    has_docker = len(docker_composes) > 0

    # Check dependencies based on detection
    if has_docker:
        check_tool("docker", "running the database environment")

    if has_spring:
        check_tool("java", "running the Spring Boot backend")

    if has_angular or has_vue:
        check_tool("npm", "running the frontend project")

    # Visual summary of detection for the user
    def get_status(condition: bool):
        return typer.style("FOUND", fg=typer.colors.GREEN) if condition else typer.style("MISSING", fg=typer.colors.RED)

    typer.echo(f"  - Docker Compose ({len(docker_composes)}) : {get_status(has_docker)}")
    typer.echo(f"  - Spring Boot ({sum(1 for p in projects if p.kind == 'spring')})    : {get_status(has_spring)}")
    typer.echo(f"  - Angular Frontend ({sum(1 for p in projects if p.kind == 'angular')}) : {get_status(has_angular)}")
    typer.echo(f"  - Vue.js Frontend ({sum(1 for p in projects if p.kind == 'vue')})  : {get_status(has_vue)}")

    if not projects and not docker_composes:
        typer.secho("\nError: No valid development environment detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Transfer control to the system orchestration layer
    launch_dev_environment(projects, docker_composes)
