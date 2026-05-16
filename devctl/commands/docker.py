from pathlib import Path

import typer

from devctl.generators.docker_scaffold import (
    SUPPORTED_DB_MODES,
    DockerScaffoldError,
    scaffold_docker_assets,
)

PATH_ARGUMENT = typer.Argument(
    Path("."),
    help="Repository or project directory to scan for Dockerizable services.",
)
FORCE_OPTION = typer.Option(
    False,
    "--force",
    help="Overwrite generated Docker files that already exist.",
)
DRY_RUN_OPTION = typer.Option(
    False,
    "--dry-run",
    help="Show what would be generated without writing files.",
)
NO_COMPOSE_OPTION = typer.Option(
    False,
    "--no-compose",
    help="Generate per-project Docker assets without a Compose stack.",
)
DB_OPTION = typer.Option(
    "auto",
    "--db",
    help="Database service mode: auto, postgres, mysql, or none.",
)


def dockerize(
    path: Path = PATH_ARGUMENT,
    force: bool = FORCE_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    no_compose: bool = NO_COMPOSE_OPTION,
    db: str = DB_OPTION,
):
    """
    Scaffold production Docker assets for Spring Boot, Angular, and Vue/Vite projects.
    """
    db_mode = db.lower()
    if db_mode not in SUPPORTED_DB_MODES:
        supported = ", ".join(sorted(SUPPORTED_DB_MODES))
        typer.secho(
            f"❌ Invalid --db value '{db}'. Expected one of: {supported}.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    try:
        result = scaffold_docker_assets(
            path,
            force=force,
            dry_run=dry_run,
            include_compose=not no_compose,
            db_mode=db_mode,
        )
    except DockerScaffoldError as exc:
        typer.secho(f"❌ {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    mode = "Dry run" if dry_run else "Docker scaffolding"
    typer.secho(f"🐳 {mode} complete for {result.root_path}", fg=typer.colors.CYAN, bold=True)

    typer.echo("\nDetected services:")
    for service in result.services:
        typer.echo(f"  - {service.kind}: {service.service_name} ({service.relative_context})")

    typer.echo("\nFiles:")
    for operation in result.operations:
        relative_path = operation.path.relative_to(result.root_path)
        typer.echo(f"  - {operation.action}: {relative_path}")

    if result.compose_path is not None:
        typer.echo(f"\nCompose file: {result.compose_path.relative_to(result.root_path)}")
    if result.db_type is not None:
        typer.echo(f"Database service: {result.db_type}")

    for warning in result.warnings:
        typer.secho(f"⚠️  {warning}", fg=typer.colors.YELLOW)

    typer.secho(
        f"\nSummary: {result.created_count} created, "
        f"{result.skipped_count} skipped, {result.planned_count} planned.",
        fg=typer.colors.GREEN,
    )
