import os
import typer
from jinja2 import Environment, FileSystemLoader
from devctl.orchestrator.scanner import detect_environment

# Mapping CLI -> TypeScript
TS_TYPE_MAP = {
    "string": "string", "int": "number", "integer": "number",
    "double": "number", "float": "number", "boolean": "boolean", "date": "string"
}


def parse_ts_fields(fields_str: str):
    if not fields_str: return []
    parsed = []
    for raw in [f.strip() for f in fields_str.split(",") if f.strip()]:
        if ":" not in raw: continue
        name, field_type = raw.split(":", 1)
        ts_type = TS_TYPE_MAP.get(field_type.lower().strip(), "string")
        parsed.append({"name": name.strip(), "ts_type": ts_type})
    return parsed


def inject_vue_route(vue_root: str, resource_lower: str, uppercase_name: str):
    """Injecte la route dynamiquement dans le routeur Vue."""
    router_path = os.path.join(vue_root, "src", "router", "index.ts")

    if not os.path.exists(router_path):
        typer.secho("⚠️ src/router/index.ts introuvable. Route non injectée.", fg=typer.colors.YELLOW)
        return

    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()

    import_statement = f"import {{ {uppercase_name}_ROUTES }} from '../features/{resource_lower}/{resource_lower}.routes'\n"
    route_definition = f"\n    {{ path: '/{resource_lower}s', children: {uppercase_name}_ROUTES }},"

    if f"../features/{resource_lower}/" in content:
        typer.echo("  - 🛣️  La route existe déjà (Ignoré).")
        return

    # 1. Ajout de l'import
    if "// --- DEBUT DES ROUTES DEVCTL ---" in content:
        content = content.replace("// --- DEBUT DES ROUTES DEVCTL ---",
                                  f"// --- DEBUT DES ROUTES DEVCTL ---\n{import_statement}")
    else:
        content = import_statement + content

    # 2. Ajout de la définition de route
    if "routes: [" in content:
        content = content.replace("routes: [", f"routes: [{route_definition}")

    with open(router_path, "w", encoding="utf-8") as f:
        f.write(content)

    typer.echo(f"  - 🛣️  Route '/{resource_lower}s' injectée avec succès !")


def generate_vue_resource(resource_name: str, fields_str: str, root_path: str = "."):
    env_state = detect_environment(root_path)

    if not env_state.get("has_vue"):
        typer.secho("❌ Erreur : Aucun projet Vue.js détecté.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    vue_root = env_state["vue_path"]
    resource_lower = resource_name.lower()
    entity_name = resource_name.capitalize()

    # Dossier de destination : src/features/{resource}/
    feature_dir = os.path.join(vue_root, "src", "features", resource_lower)

    components = [
        {"dir": "models", "name": f"{resource_lower}-request.model.ts", "template": "models/request.model.ts.j2"},
        {"dir": "models", "name": f"{resource_lower}-response.model.ts", "template": "models/response.model.ts.j2"},
        {"dir": "services", "name": f"{resource_lower}.service.ts", "template": "services/service.ts.j2"},
        {"dir": "", "name": f"{resource_lower}.routes.ts", "template": "routes.ts.j2"},
        {"dir": "pages", "name": f"{entity_name}List.vue", "template": "pages/List.vue.j2"},
        {"dir": "pages", "name": f"{entity_name}Form.vue", "template": "pages/Form.vue.j2"}
    ]

    templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "vue", "feature")
    env = Environment(loader=FileSystemLoader(templates_dir))

    typer.echo(f"⚙️ Génération de la feature Vue.js '{entity_name}'...")

    context = {
        "entity_name": entity_name,
        "resource_name_lower": resource_lower,
        "table_name": f"{resource_lower}s",
        "uppercase_name": resource_name.upper(),
        "fields": parse_ts_fields(fields_str)
    }

    for comp in components:
        target_dir = os.path.join(feature_dir, os.path.normpath(comp["dir"]))
        os.makedirs(target_dir, exist_ok=True)

        try:
            template = env.get_template(comp["template"])
            content = template.render(context)
            with open(os.path.join(target_dir, comp["name"]), "w", encoding="utf-8") as f:
                f.write(content)

            display_dir = comp['dir'] if comp['dir'] else "racine"
            typer.echo(f"  - Créé : {display_dir}/{comp['name']}")
        except Exception as e:
            typer.secho(f"⚠️ Erreur sur {comp['template']} : {e}", fg=typer.colors.YELLOW)

    inject_vue_route(vue_root, resource_lower, resource_name.upper())
    typer.secho(f"✅ Feature {entity_name} générée avec succès côté Vue.js !", fg=typer.colors.GREEN)