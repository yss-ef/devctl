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
    ".next",
    ".svelte-kit",
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
        "project_root": str(root),
    }

    for dirpath, dirnames, filenames in os.walk(root):
        # In-place modification of dirnames to prune the traversal
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRECTORIES]

        current_path = Path(dirpath)
        filename_set = set(filenames)

        # 1. Docker Compose detection
        if "docker-compose-db.yml" in filename_set and not env_state["has_docker_compose"]:
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

        # 4. Vite-based detection (Vue/React)
        vue_markers = {"vite.config.ts", "vite.config.js"}
        if (vue_markers & filename_set) and not any([env_state["has_vue"], env_state["has_react"]]):
            # Distinguish by package.json
            pkg_path = current_path / "package.json"
            if pkg_path.exists():
                try:
                    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
                    deps = pkg.get("dependencies", {})
                    dev_deps = pkg.get("devDependencies", {})
                    all_deps = {**deps, **dev_deps}
                    if "react" in all_deps:
                        env_state["has_react"] = True
                        env_state["react_path"] = str(current_path)
                    else:
                        env_state["has_vue"] = True
                        env_state["vue_path"] = str(current_path)
                except Exception:
                    env_state["has_vue"] = True
                    env_state["vue_path"] = str(current_path)
            else:
                env_state["has_vue"] = True
                env_state["vue_path"] = str(current_path)

        # 5. NestJS detection
        if "nest-cli.json" in filename_set and not env_state["has_nest"]:
            env_state["has_nest"] = True
            env_state["nest_path"] = str(current_path)

        # 6. NextJS detection
        if any(f.startswith("next.config.") for f in filename_set) and not env_state["has_nextjs"]:
            env_state["has_nextjs"] = True
            env_state["nextjs_path"] = str(current_path)

        # 7. Generic NodeJS detection (if not already caught)
        if "package.json" in filename_set and not any(
            [
                env_state["has_angular"],
                env_state["has_vue"],
                env_state["has_react"],
                env_state["has_nest"],
                env_state["has_nextjs"],
            ]
        ):
            env_state["has_nodejs"] = True
            env_state["nodejs_path"] = str(current_path)

        # 8. Python detection (FastAPI/Django)
        if "requirements.txt" in filename_set:
            req_path = current_path / "requirements.txt"
            try:
                req_content = req_path.read_text(encoding="utf-8").lower()
                if "fastapi" in req_content and not env_state["has_fastapi"]:
                    env_state["has_fastapi"] = True
                    env_state["fastapi_path"] = str(current_path)
                if "django" in req_content and not env_state["has_django"]:
                    env_state["has_django"] = True
                    env_state["django_path"] = str(current_path)
            except (OSError, UnicodeDecodeError):
                # Ignore unreadable requirements files during environment scanning
                pass

        # 9. Svelte detection
        if "svelte.config.js" in filename_set and not env_state["has_svelte"]:
            env_state["has_svelte"] = True
            env_state["svelte_path"] = str(current_path)

        # 10. Go detection
        if "go.mod" in filename_set and not env_state["has_go"]:
            env_state["has_go"] = True
            env_state["go_path"] = str(current_path)

    return env_state
