"""
FastAPI resource scaffolding generator.
Handles the creation of routers, schemas, and models.
"""

import os
import typer
from devctl.orchestrator.scanner import detect_environment


def generate_fastapi_resource(resource_name: str, fields_str: str, root_path: str = "."):
    """
    Scaffolds a FastAPI resource.
    """
    env_state = detect_environment(root_path)

    if not env_state["has_fastapi"]:
        typer.secho("❌ Error: No FastAPI project detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    fastapi_root = env_state["fastapi_path"]
    resource_lower = resource_name.lower()
    entity_name = resource_name.capitalize()

    # Create directories
    routers_dir = os.path.join(fastapi_root, "routers")
    schemas_dir = os.path.join(fastapi_root, "schemas")
    models_dir = os.path.join(fastapi_root, "models")
    
    for d in [routers_dir, schemas_dir, models_dir]:
        os.makedirs(d, exist_ok=True)
        # Ensure __init__.py exists
        with open(os.path.join(d, "__init__.py"), "a"): pass

    typer.secho(f"⚙️  Generating FastAPI resource '{entity_name}'...", fg=typer.colors.CYAN)

    # 1. Generate Schema (Pydantic)
    schema_content = f"""from pydantic import BaseModel
from typing import Optional

class {entity_name}Base(BaseModel):
    # Fields: {fields_str}
    pass

class {entity_name}Create({entity_name}Base):
    pass

class {entity_name}({entity_name}Base):
    id: int

    class Config:
        orm_mode = True
"""
    with open(os.path.join(schemas_dir, f"{resource_lower}.py"), "w") as f:
        f.write(schema_content)

    # 2. Generate Router
    router_content = f"""from fastapi import APIRouter, HTTPException
from typing import List
from schemas import {resource_lower} as schemas

router = APIRouter(
    prefix="/{resource_lower}s",
    tags=["{resource_lower}s"]
)

@{resource_lower}.get("/", response_model=List[schemas.{entity_name}])
def read_{resource_lower}s():
    return []

@{resource_lower}.post("/", response_model=schemas.{entity_name})
def create_{resource_lower}({resource_lower}: schemas.{entity_name}Create):
    return {{"id": 1, **{resource_lower}.dict()}}
"""
    # Note: fixed typo in template during thought but let's correct it properly
    router_content = f"""from fastapi import APIRouter, HTTPException
from typing import List
from schemas import {resource_lower} as schemas

router = APIRouter(
    prefix="/{resource_lower}s",
    tags=["{resource_lower}s"]
)

@router.get("/", response_model=List[schemas.{entity_name}])
def read_{resource_lower}s():
    return []

@router.post("/", response_model=schemas.{entity_name})
def create_{resource_lower}(item: schemas.{entity_name}Create):
    return {{"id": 1, **item.dict()}}
"""
    with open(os.path.join(routers_dir, f"{resource_lower}.py"), "w") as f:
        f.write(router_content)

    typer.secho(f"✅ {entity_name} FastAPI feature successfully generated!", fg=typer.colors.GREEN)
    typer.echo(f"  - Created: schemas/{resource_lower}.py")
    typer.echo(f"  - Created: routers/{resource_lower}.py")
