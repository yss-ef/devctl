"""
Project scanner and environment detector.
Identifies Spring Boot, Angular, Vue.js, React, and Docker components in a directory tree.
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
        "has_react": False,
        "react_path": None,
        "project_root": os.path.abspath(root_path),
    }

    for dirpath, _dirnames, filenames in os.walk(root_path):
        # Optimization: ignore heavy folders for an instant scan
        if any(ignored in dirpath for ignored in ["node_modules", "target", ".git", ".angular", "dist"]):
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

    return env_state
