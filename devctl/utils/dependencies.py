import shutil

import typer


def check_tool(tool_name: str, required_for: str = "this operation"):
    """
    Check if a tool is available in the system PATH.
    If not, print a friendly error message and exit.
    """
    if shutil.which(tool_name) is None:
        typer.secho(
            f"\n❌ Error: '{tool_name}' is not installed or not in your PATH.",
            fg=typer.colors.RED,
            bold=True,
        )
        typer.echo(f"It is required for {required_for}.")

        # Provide helpful hints for common tools
        hints = {
            "docker": "Visit https://docs.docker.com/get-docker/",
            "npm": "Install Node.js from https://nodejs.org/",
            "java": "Install OpenJDK (e.g., version 17) from your package manager.",
            "mvnw": "Ensure you are in a Spring Boot project root with the 'mvnw' wrapper.",
            "ng": "Install Angular CLI using 'npm install -g @angular/cli'.",
        }

        if tool_name in hints:
            typer.echo(f"💡 Hint: {hints[tool_name]}")

        raise typer.Exit(code=1)
