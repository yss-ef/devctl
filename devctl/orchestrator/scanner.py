import os

def detect_environment(root_path: str = "."):
    """
    Scanne le répertoire et ses sous-dossiers pour identifier les composants.
    Retourne l'état et les chemins absolus de chaque composant.
    """
    env_state = {
        "has_docker_compose": False,
        "docker_path": None,
        "has_spring": False,
        "spring_path": None,
        "has_angular": False,
        "angular_path": None,
        "project_root": os.path.abspath(root_path)
    }

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Optimisation : on ignore les dossiers lourds pour un scan instantané
        if any(ignored in dirpath for ignored in ["node_modules", "target", ".git", ".angular"]):
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

    return env_state