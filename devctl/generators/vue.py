import os
import subprocess

import typer
from jinja2 import Environment, FileSystemLoader


def setup_vue_proxy(project_path: str):
    """
    Replaces the default vite.config.ts with our version including the proxy.
    """
    typer.secho("⚙️  Configuring Vite Proxy for Spring Boot...", fg=typer.colors.CYAN)

    templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "vue", "config")
    env = Environment(loader=FileSystemLoader(templates_dir))

    target_path = os.path.join(project_path, "vite.config.ts")

    try:
        template = env.get_template("vite.config.ts.j2")
        content = template.render()
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        typer.echo("  - vite.config.ts updated with /api proxy.")
    except Exception as e:
        typer.secho(f"⚠️  Error configuring proxy: {e}", fg=typer.colors.YELLOW)


def setup_vue_router(project_path: str):
    """
    Installs vue-router and configures the base architecture (main.ts, router, App.vue).
    """
    typer.secho("🛣️  Installing and configuring vue-router...", fg=typer.colors.CYAN)

    try:
        # 1. Installation du package npm
        subprocess.run(
            ["npm", "install", "vue-router@4"],
            cwd=project_path,
            check=True,
            stdout=subprocess.DEVNULL,
        )

        # 2. Création du dossier router
        src_dir = os.path.join(project_path, "src")
        router_dir = os.path.join(src_dir, "router")
        os.makedirs(router_dir, exist_ok=True)

        # 3. Rendu des templates Jinja2
        templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "vue", "config")
        env = Environment(loader=FileSystemLoader(templates_dir))

        files_to_generate = {
            "router.ts.j2": os.path.join(router_dir, "index.ts"),
            "main.ts.j2": os.path.join(src_dir, "main.ts"),
            "App.vue.j2": os.path.join(src_dir, "App.vue"),
        }

        for tpl_name, target_path in files_to_generate.items():
            template = env.get_template(tpl_name)
            content = template.render()
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)

        typer.echo("  - Navigation architecture ready.")
    except Exception as e:
        typer.secho(f"⚠️  Error configuring router: {e}", fg=typer.colors.YELLOW)


def generate_vue_boilerplate(project_name: str) -> bool:
    """
    Generates a Vue 3 + TypeScript project via Vite.
    """
    typer.secho(f"🔄 Generating Vue.js frontend '{project_name}' via Vite...", fg=typer.colors.CYAN)
    safe_name = project_name.lower().replace("_", "-")

    try:
        typer.secho("📦 Scaffolding Vite project...", fg=typer.colors.CYAN)
        subprocess.run(
            ["npm", "create", "vite@latest", safe_name, "--", "--template", "vue-ts"], check=True
        )

        project_full_path = os.path.join(os.getcwd(), safe_name)

        typer.secho("⏳ Installing npm dependencies...", fg=typer.colors.CYAN)
        subprocess.run(["npm", "install"], cwd=project_full_path, check=True)

        # --- APPEL DE NOS DEUX CONFIGURATEURS ---
        setup_vue_proxy(project_full_path)
        setup_vue_router(project_full_path)
        # ----------------------------------------

        typer.secho(
            f"✅ Vue.js frontend '{safe_name}' successfully generated!", fg=typer.colors.GREEN
        )
        return True

    except subprocess.CalledProcessError as e:
        typer.secho(f"❌ Vue/Vite process failed with code: {e.returncode}", fg=typer.colors.RED)
        return False
