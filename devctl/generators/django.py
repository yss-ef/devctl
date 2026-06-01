"""
Generators for Django projects.
Includes boilerplate generation with Django and DRF.
"""

import os
import subprocess

import typer


def generate_django_boilerplate(project_name: str) -> bool:
    """
    Generates a new Django project.
    """
    typer.secho(f"Generating Django project '{project_name}'...", fg=typer.colors.CYAN)
    safe_name = project_name.lower().replace("-", "_")  # Django prefers underscores
    project_path = os.path.join(os.getcwd(), project_name)

    try:
        os.makedirs(project_path, exist_ok=True)

        # 1. Create requirements.txt
        requirements = """django
djangorestframework
django-cors-headers
"""
        with open(os.path.join(project_path, "requirements.txt"), "w") as f:
            f.write(requirements)

        # 2. Create virtual environment
        typer.secho("Creating virtual environment...", fg=typer.colors.CYAN)
        subprocess.run(["python3", "-m", "venv", ".venv"], cwd=project_path, check=True)

        # 3. Install Django
        typer.secho("Installing Django and DRF...", fg=typer.colors.CYAN)
        pip_path = os.path.join(".venv", "bin", "pip")
        subprocess.run(
            [pip_path, "install", "django", "djangorestframework"],
            cwd=project_path,
            check=True,
            stdout=subprocess.DEVNULL,
        )

        # 4. Start Project
        typer.secho("Scaffolding Django project structure...", fg=typer.colors.CYAN)
        django_admin = os.path.join(".venv", "bin", "django-admin")
        subprocess.run([django_admin, "startproject", safe_name, "."], cwd=project_path, check=True)

        # 5. Create core app
        python_path = os.path.join(".venv", "bin", "python")
        subprocess.run([python_path, "manage.py", "startapp", "core"], cwd=project_path, check=True)

        typer.secho(
            f"Django project '{project_name}' successfully generated!", fg=typer.colors.GREEN
        )
        return True

    except Exception as e:
        typer.secho(f"Error: Django initialization failed: {e}", fg=typer.colors.RED)
        return False
