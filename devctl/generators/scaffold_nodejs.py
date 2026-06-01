"""
NodeJS/Express resource scaffolding generator.
Handles the creation of routes and controllers.
"""

import os

import typer

from devctl.orchestrator.scanner import detect_environment


def generate_nodejs_resource(resource_name: str, _fields_str: str, root_path: str = "."):
    """
    Scaffolds a NodeJS/Express resource.
    """
    # Using basic manual file writing for simplicity and speed
    # In a more advanced version, we could use Jinja2 templates

    resource_lower = resource_name.lower()
    entity_name = resource_name.capitalize()

    src_dir = os.path.join(root_path, "src")
    if not os.path.exists(src_dir):
        # Try to find nodejs path from scanner
        detect_environment(root_path)
        # We need to add has_nodejs to scanner or just check if src exists in root
        src_dir = os.path.join(root_path, "src")

    routes_dir = os.path.join(src_dir, "routes")
    controllers_dir = os.path.join(src_dir, "controllers")

    os.makedirs(routes_dir, exist_ok=True)
    os.makedirs(controllers_dir, exist_ok=True)

    typer.secho(f"⚙️  Generating NodeJS/Express resource '{entity_name}'...", fg=typer.colors.CYAN)

    # 1. Generate Controller
    controller_content = f"""import {{ Request, Response }} from 'express';

export const get{entity_name}s = (req: Request, res: Response) => {{
  res.json({{ message: 'Get all {resource_lower}s' }});
}};

export const get{entity_name}ById = (req: Request, res: Response) => {{
  const {{ id }} = req.params;
  res.json({{ message: `Get {resource_lower} with id ${{id}}` }});
}};

export const create{entity_name} = (req: Request, res: Response) => {{
  const data = req.body;
  res.status(201).json({{
    message: '{entity_name} created',
    data
  }});
}};
"""
    controller_path = os.path.join(controllers_dir, f"{resource_lower}.controller.ts")
    with open(controller_path, "w") as f:
        f.write(controller_content)

    # 2. Generate Route
    route_content = f"""import {{ Router }} from 'express';
import * as {resource_lower}Controller from '../controllers/{resource_lower}.controller';

const router = Router();

router.get('/', {resource_lower}Controller.get{entity_name}s);
router.get('/:id', {resource_lower}Controller.get{entity_name}ById);
router.post('/', {resource_lower}Controller.create{entity_name});

export default router;
"""
    route_path = os.path.join(routes_dir, f"{resource_lower}.routes.ts")
    with open(route_path, "w") as f:
        f.write(route_content)

    typer.secho(f"✅ {entity_name} NodeJS resource successfully generated!", fg=typer.colors.GREEN)
    typer.echo(f"  - Created: controllers/{resource_lower}.controller.ts")
    typer.echo(f"  - Created: routes/{resource_lower}.routes.ts")
    typer.echo("💡 Don't forget to register the route in your main app file.")
