"""
Project scanner and environment detector.
Identifies Spring Boot, Angular, Vue.js, React, NextJS, NestJS, NodeJS, FastAPI,
Django, Svelte, Go, and Docker components in a directory tree.
"""

import json
import os
from pathlib import Path

# Directories to ignore during scanning
IGNORED_DIRECTORIES = {
    "node_modules",
    "target",
    ".git",
    ".angular",
    "dist",
    "build",
    "venv",
    ".venv",
    "__pycache__",
}


def detect_environment(root_path: str = "."):
    """
    Scans the directory tree and its subfolders to identify components.
    Returns the state and absolute paths of each component.
    """
    root = Path(root_path).resolve()
    env_state = {
        "has_docker_compose": False,
        "docker_path": None,
        "has_spring": False,
        "spring_path": None,
        "has_angular": False,
        "angular_path": None,
        "has_vue": False,
        "vue_path": None,
        "has_react": False,
        "react_path": None,
        "has_nextjs": False,
        "nextjs_path": None,
        "has_nest": False,
        "nest_path": None,
        "has_nodejs": False,
        "nodejs_path": None,
        "has_fastapi": False,
        "fastapi_path": None,
        "has_django": False,
        "django_path": None,
        "has_svelte": False,
        "svelte_path": None,
        "has_go": False,
        "go_path": None,
        "project_root": os.path.abspath(root_path),
    }

    for dirpath, _dirnames, filenames in os.walk(root_path):
        # Optimization: ignore heavy folders for an instant scan
        if any(
            ignored in dirpath
            for ignored in [
                "node_modules",
                "target",
                ".git",
                ".angular",
                "dist",
                ".next",
                ".venv",
                ".svelte-kit",
            ]
        ):
            continue

        # 1. Docker Compose detection
        if "docker-compose.yml" in filename_set and not env_state["has_docker_compose"]:
            env_state["has_docker_compose"] = True
            env_state["docker_path"] = str(current_path)

        # 2. Spring Boot detection
        if ("pom.xml" in filename_set or "mvnw" in filename_set) and not env_state["has_spring"]:
            env_state["has_spring"] = True
            env_state["spring_path"] = str(current_path)

        # 3. Angular detection
        if "angular.json" in filename_set and not env_state["has_angular"]:
            env_state["has_angular"] = True
            env_state["angular_path"] = str(current_path)

        vue_files = ["vite.config.ts", "vite.config.js"]
        if any(f in filenames for f in vue_files) and not any(
            [env_state["has_vue"], env_state["has_react"]]
        ):
            # Distinguish by package.json
            pkg_path = os.path.join(dirpath, "package.json")
            if os.path.exists(pkg_path):
                try:
                    with open(pkg_path, "r") as f:
                        pkg = json.load(f)
                        all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                        if "react" in all_deps:
                            env_state["has_react"] = True
                            env_state["react_path"] = dirpath
                        else:
                            env_state["has_vue"] = True
                            env_state["vue_path"] = dirpath
                except Exception:
                    env_state["has_vue"] = True
                    env_state["vue_path"] = dirpath
            else:
                env_state["has_vue"] = True
                env_state["vue_path"] = dirpath

        if "nest-cli.json" in filenames and not env_state["has_nest"]:
            env_state["has_nest"] = True
            env_state["nest_path"] = dirpath

        if any(f.startswith("next.config.") for f in filenames) and not env_state["has_nextjs"]:
            env_state["has_nextjs"] = True
            env_state["nextjs_path"] = dirpath

        if "package.json" in filenames and not any(
            [
                env_state["has_angular"],
                env_state["has_vue"],
                env_state["has_react"],
                env_state["has_nest"],
                env_state["has_nextjs"],
            ]
        ):
            env_state["has_nodejs"] = True
            env_state["nodejs_path"] = dirpath

        if "requirements.txt" in filenames:
            req_path = os.path.join(dirpath, "requirements.txt")
            try:
                with open(req_path, "r") as f:
                    req_content = f.read().lower()
                    if "fastapi" in req_content and not env_state["has_fastapi"]:
                        env_state["has_fastapi"] = True
                        env_state["fastapi_path"] = dirpath
                    if "django" in req_content and not env_state["has_django"]:
                        env_state["has_django"] = True
                        env_state["django_path"] = dirpath
            except Exception:
                pass

        if "svelte.config.js" in filenames and not env_state["has_svelte"]:
            env_state["has_svelte"] = True
            env_state["svelte_path"] = dirpath

        if "go.mod" in filenames and not env_state["has_go"]:
            env_state["has_go"] = True
            env_state["go_path"] = dirpath

    return env_state
