"""
ReactJS resource scaffolding generator.
Handles the creation of components, hooks, and services.
"""

import os

import typer

from devctl.orchestrator.scanner import detect_environment


def generate_react_resource(resource_name: str, fields_str: str, root_path: str = "."):
    """
    Scaffolds a React resource (Component, Service).
    """
    env_state = detect_environment(root_path)

    if not env_state["has_react"]:
        typer.secho("❌ Error: No ReactJS project detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    react_root = env_state["react_path"]
    resource_lower = resource_name.lower()
    entity_name = resource_name.capitalize()

    # Structure: src/components/ResourceName/...
    components_dir = os.path.join(react_root, "src", "components", entity_name)
    services_dir = os.path.join(react_root, "src", "services")

    os.makedirs(components_dir, exist_ok=True)
    os.makedirs(services_dir, exist_ok=True)

    typer.secho(f"⚙️  Generating ReactJS resource '{entity_name}'...", fg=typer.colors.CYAN)

    # 1. Generate Component (tsx)
    component_content = f"""import React from 'react';

export const {entity_name}List: React.FC = () => {{
  return (
    <div>
      <h1>{entity_name} List</h1>
      <p>Manage your {resource_lower}s here.</p>
    </div>
  );
}};

export const {entity_name}Form: React.FC = () => {{
  return (
    <form>
      <h1>Create {entity_name}</h1>
      {fields_str}
    </form>
  );
}};
"""
    with open(os.path.join(components_dir, f"{entity_name}.tsx"), "w") as f:
        f.write(component_content)

    # 2. Generate Service
    service_content = f"""export const fetch{entity_name}s = async () => {{
  const response = await fetch('/api/{resource_lower}s');
  return response.json();
}};

export const create{entity_name} = async (data: any) => {{
  const response = await fetch('/api/{resource_lower}s', {{
    method: 'POST',
    body: JSON.stringify(data),
    headers: {{ 'Content-Type': 'application/json' }}
  }});
  return response.json();
}};
"""
    with open(os.path.join(services_dir, f"{resource_lower}.service.ts"), "w") as f:
        f.write(service_content)

    typer.secho(f"✅ {entity_name} React feature successfully generated!", fg=typer.colors.GREEN)
    typer.echo(f"  - Created: src/components/{entity_name}/{entity_name}.tsx")
    typer.echo(f"  - Created: src/services/{resource_lower}.service.ts")
