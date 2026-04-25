import os

import typer
from jinja2 import Environment, FileSystemLoader

# Dictionnaire de traduction CLI -> Java
JAVA_TYPE_MAP = {
    "string": "String",
    "int": "Integer",
    "integer": "Integer",
    "double": "Double",
    "float": "Float",
    "boolean": "Boolean",
    "date": "LocalDate",
}


def parse_fields(fields_str: str):
    """
    Transforme la chaîne de caractères du terminal en données injectables.
    Exemple: "nom:string, age:int" -> [{"name": "nom", "java_type": "String"}, ...]
    """
    if not fields_str:
        return []

    parsed_fields = []
    raw_fields = [f.strip() for f in fields_str.split(",") if f.strip()]

    for raw in raw_fields:
        if ":" not in raw:
            continue
        name, field_type = raw.split(":", 1)
        java_type = JAVA_TYPE_MAP.get(field_type.lower().strip(), "String")
        parsed_fields.append({"name": name.strip(), "java_type": java_type})
    return parsed_fields


def find_spring_base_package_and_path():
    """
    Cherche le dossier contenant la classe @SpringBootApplication.
    C'est la méthode la plus fiable pour trouver le package de base sans parser le pom.xml.
    """
    java_src_dir = os.path.join(os.getcwd(), "src", "main", "java")

    if not os.path.exists(java_src_dir):
        return None, None

    for root, _dirs, files in os.walk(java_src_dir):
        for file in files:
            if file.endswith("Application.java"):
                rel_path = os.path.relpath(root, java_src_dir)
                base_package = rel_path.replace(os.sep, ".")
                return base_package, root

    return None, None


def generate_spring_resource(resource_name: str, fields_str: str):
    """
    Orchestre la création de l'architecture MVC + DTOs + Mapper.
    """
    base_package, base_path = find_spring_base_package_and_path()

    if not base_package:
        typer.secho(
            "❌ Erreur : Impossible de trouver un projet Spring Boot valide ici.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    entity_name = resource_name.capitalize()

    # Nouvelle configuration détaillée pour gérer les sous-dossiers (DTOs, Mapper)
    components = [
        {"dir": "entity", "suffix": "Entity", "template": "Entity.java.j2"},
        {"dir": "repository", "suffix": "Repository", "template": "Repository.java.j2"},
        {"dir": "service", "suffix": "Service", "template": "Service.java.j2"},
        {"dir": "controller", "suffix": "Controller", "template": "Controller.java.j2"},
        {"dir": "dto/request", "suffix": "Request", "template": "dto/Request.java.j2"},
        {"dir": "dto/response", "suffix": "Response", "template": "dto/Response.java.j2"},
        {"dir": "mapper", "suffix": "Mapper", "template": "mapper/Mapper.java.j2"},
    ]

    templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "spring")
    env = Environment(loader=FileSystemLoader(templates_dir))

    typer.echo(f"⚙️ Génération de la ressource Spring '{entity_name}' (avec MapStruct & DTOs)...")

    for comp in components:
        class_name = f"{entity_name}{comp['suffix']}"
        target_file_name = f"{class_name}.java"

        # Création du sous-dossier s'il n'existe pas (ex: src/.../dto/request)
        # os.path.normpath gère les slashes selon l'OS (Linux/Windows)
        target_dir = os.path.join(base_path, os.path.normpath(comp["dir"]))
        os.makedirs(target_dir, exist_ok=True)

        # Les données envoyées au template Jinja2
        context = {
            "base_package": base_package,
            "class_name": class_name,
            "entity_name": entity_name,
            "table_name": f"{resource_name.lower()}s",
            "fields": parse_fields(fields_str),
        }

        template = env.get_template(comp["template"])
        content = template.render(context)

        with open(os.path.join(target_dir, target_file_name), "w", encoding="utf-8") as f:
            f.write(content)

        typer.echo(f"  - Créé : {comp['dir']}/{target_file_name}")

    typer.secho(
        f"✅ Architecture {entity_name} complète générée avec succès !", fg=typer.colors.GREEN
    )


def generate_spring_security(_root_path: str = "."):
    """
    Génère la base de sécurité JWT de manière dynamique.
    """
    # Réutilisation de ta fonction de détection dynamique
    base_package, base_path = find_spring_base_package_and_path()

    if not base_package:
        typer.secho(
            "❌ Erreur : Impossible de localiser le package Java pour la sécurité.",
            fg=typer.colors.RED,
        )
        return

    # Création du dossier config au bon endroit
    target_dir = os.path.join(base_path, "config")
    os.makedirs(target_dir, exist_ok=True)

    # Setup Jinja2
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "spring", "config")
    env = Environment(loader=FileSystemLoader(templates_dir))

    security_files = [
        "JwtService.java",
        "JwtAuthenticationFilter.java",
        "SecurityConfig.java",
        "ApplicationConfig.java",
    ]

    typer.echo(f"🛡️  Injection de la sécurité JWT dans {base_package}.config...")

    for filename in security_files:
        template = env.get_template(f"{filename}.j2")
        content = template.render(base_package=base_package)

        with open(os.path.join(target_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        typer.echo(f"  - Créé : config/{filename}")

    typer.secho("✅ Sécurité initialisée avec succès !", fg=typer.colors.GREEN)
