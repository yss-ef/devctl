"""
Project scanner and environment detector.
<<<<<<< HEAD
<<<<<<< HEAD
Identifies Spring Boot, Angular, Vue.js, React, NextJS, NestJS, NodeJS, FastAPI, and Docker components in a directory tree.
=======
Identifies Spring Boot, Angular, Vue.js, Django, and Docker components in a directory tree.
>>>>>>> feat/django
=======
Identifies Spring Boot, Angular, Vue.js, Svelte, and Docker components in a directory tree.
>>>>>>> feat/svelte
"""

import os
import json


def detect_environment(root_path: str = "."):
    """
    Scans the directory and its subfolders to identify components.
    Returns the state and absolute paths of each component.
    """
    env_state = {
        "has_docker_compose": False,
        "docker_path": None,
        "has_spring": False,
        "spring_path": None,
        "has_angular": False,
        "angular_path": None,
        "has_vue": False,
        "vue_path": None,
<<<<<<< HEAD
<<<<<<< HEAD
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
=======
        "has_django": False,
        "django_path": None,
>>>>>>> feat/django
=======
        "has_svelte": False,
        "svelte_path": None,
>>>>>>> feat/svelte
        "project_root": os.path.abspath(root_path),
    }

    for dirpath, _dirnames, filenames in os.walk(root_path):
        # Optimization: ignore heavy folders for an instant scan
<<<<<<< HEAD
<<<<<<< HEAD
        if any(ignored in dirpath for ignored in ["node_modules", "target", ".git", ".angular", "dist", ".next", ".venv"]):
=======
        if any(ignored in dirpath for ignored in ["node_modules", "target", ".git", ".angular", ".venv"]):
>>>>>>> feat/django
=======
        if any(ignored in dirpath for ignored in ["node_modules", "target", ".git", ".angular", ".svelte-kit"]):
>>>>>>> feat/svelte
            continue

        if "docker-compose.yml" in filenames and not env_state["has_docker_compose"]:
            env_state["has_docker_compose"] = True
            env_state["docker_path"] = dirpath

        if ("pom.xml" in filenames or "mvnw" in filenames) and not env_state["has_spring"]:
            env_state["has_spring"] = True
            env_state["spring_path"] = dirpath

        if "angular.json" in filenames and not env_state["has_angular"]:
            env_state["has_angular"] = True
            env_state["angular_path"] = dirpath

        vue_files = ["vite.config.ts", "vite.config.js"]
        if any(f in filenames for f in vue_files) and not any([env_state["has_vue"], env_state["has_react"]]):
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

        if "package.json" in filenames and not any([env_state["has_angular"], env_state["has_vue"], env_state["has_react"], env_state["has_nest"], env_state["has_nextjs"]]):
            env_state["has_nodejs"] = True
            env_state["nodejs_path"] = dirpath

        if "main.py" in filenames and "requirements.txt" in filenames:
            req_path = os.path.join(dirpath, "requirements.txt")
            try:
                with open(req_path, "r") as f:
                    if "fastapi" in f.read().lower():
                        env_state["has_fastapi"] = True
                        env_state["fastapi_path"] = dirpath
            except Exception:
                pass

        if "manage.py" in filenames and "requirements.txt" in filenames:
            req_path = os.path.join(dirpath, "requirements.txt")
            try:
                with open(req_path, "r") as f:
                    if "django" in f.read().lower():
                        env_state["has_django"] = True
                        env_state["django_path"] = dirpath
            except Exception:
                pass

        if "svelte.config.js" in filenames and not env_state["has_svelte"]:
            env_state["has_svelte"] = True
            env_state["svelte_path"] = dirpath

    return env_state
