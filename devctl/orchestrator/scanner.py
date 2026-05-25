"""
Project scanner and environment detector.
Identifies Spring Boot, Angular, Vue.js, and Docker components in a directory tree.
"""

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
        "project_root": str(root),
    }

    for dirpath, dirnames, filenames in os.walk(root):
        # In-place modification of dirnames to prune the traversal
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRECTORIES]
        
        current_path = Path(dirpath)
        filename_set = set(filenames)

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

        # 4. Vue.js (Vite) detection
        vue_markers = {"vite.config.ts", "vite.config.js"}
        if (vue_markers & filename_set) and not env_state["has_vue"]:
            # Special case: don't shadow Angular if it also has a vite config (unlikely but safe)
            if not env_state["has_angular"]:
                env_state["has_vue"] = True
                env_state["vue_path"] = str(current_path)

    return env_state
