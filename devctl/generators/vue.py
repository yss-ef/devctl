import os
import subprocess

import typer
from jinja2 import Environment, FileSystemLoader


def setup_vue_proxy(project_path: str):
    """
    Remplace le fichier vite.config.ts généré par défaut par notre version incluant le proxy.
    """
    typer.echo("⚙️  Configuration du Proxy Vite pour Spring Boot...")

    templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "vue", "config")
    env = Environment(loader=FileSystemLoader(templates_dir))

    target_path = os.path.join(project_path, "vite.config.ts")

    try:
        template = env.get_template("vite.config.ts.j2")
        content = template.render()
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        typer.echo("  - vite.config.ts mis à jour avec le proxy /api.")
    except Exception as e:
        typer.secho(f"⚠️  Erreur lors de la configuration du proxy : {e}", fg=typer.colors.YELLOW)


def setup_vue_router(project_path: str):
    """
    Installe vue-router et configure l'architecture de base (main.ts, router, App.vue).
    """
    typer.echo("🛣️  Installation et configuration de vue-router...")

    try:
        # 1. Installation du package npm
        subprocess.run(
            ["npm", "install", "vue-router@4"],
            cwd=project_path,
            check=True,
            stdout=subprocess.DEVNULL
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
            "App.vue.j2": os.path.join(src_dir, "App.vue")
        }

        for tpl_name, target_path in files_to_generate.items():
            template = env.get_template(tpl_name)
            content = template.render()
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)

        typer.echo("  - Architecture de navigation prête.")
    except Exception as e:
        typer.secho(f"⚠️  Erreur lors de la configuration du routeur : {e}", fg=typer.colors.YELLOW)


def generate_vue_boilerplate(project_name: str) -> bool:
    """
    Génère un projet Vue 3 + TypeScript via Vite.
    """
    typer.echo(f"🔄 Génération du frontend Vue.js '{project_name}' via Vite...")
    safe_name = project_name.lower().replace("_", "-")

    try:
        typer.echo("📦 Scaffolding du projet Vite...")
        subprocess.run(
            ["npm", "create", "vite@latest", safe_name, "--", "--template", "vue-ts"],
            check=True
        )

        project_full_path = os.path.join(os.getcwd(), safe_name)

        typer.echo("⏳ Installation des dépendances npm...")
        subprocess.run(["npm", "install"], cwd=project_full_path, check=True)

        # --- APPEL DE NOS DEUX CONFIGURATEURS ---
        setup_vue_proxy(project_full_path)
        setup_vue_router(project_full_path)  # NOUVEAU
        # ----------------------------------------

        typer.secho(f"✅ Frontend Vue.js '{safe_name}' généré avec succès !", fg=typer.colors.GREEN)
        return True

    except subprocess.CalledProcessError as e:
        typer.secho(
            f"❌ Le processus Vue/Vite a échoué avec le code : {e.returncode}",
            fg=typer.colors.RED
        )
        return False
