from devctl.orchestrator.scanner import detect_environment


def test_detect_empty_directory(tmp_path):
    """Ensure scanner returns empty state for an empty directory."""
    state = detect_environment(str(tmp_path))
    assert state["has_docker_compose"] is False
    assert state["has_spring"] is False
    assert state["has_angular"] is False
    assert state["has_vue"] is False


def test_detect_spring_project(tmp_path):
    """Ensure scanner detects a Spring project via pom.xml."""
    (tmp_path / "pom.xml").write_text("<project></project>")
    state = detect_environment(str(tmp_path))
    assert state["has_spring"] is True
    assert state["spring_path"] == str(tmp_path)


def test_detect_angular_project(tmp_path):
    """Ensure scanner detects an Angular project via angular.json."""
    (tmp_path / "angular.json").write_text("{}")
    state = detect_environment(str(tmp_path))
    assert state["has_angular"] is True
    assert state["angular_path"] == str(tmp_path)


def test_detect_vue_project(tmp_path):
    """Ensure scanner detects a Vue project via vite.config.ts."""
    (tmp_path / "vite.config.ts").write_text("export default {}")
    state = detect_environment(str(tmp_path))
    assert state["has_vue"] is True
    assert state["vue_path"] == str(tmp_path)


def test_detect_docker_compose(tmp_path):
    """Ensure scanner detects docker-compose.yml."""
    (tmp_path / "docker-compose.yml").write_text("version: '3'")
    state = detect_environment(str(tmp_path))
    assert state["has_docker_compose"] is True
    assert state["docker_path"] == str(tmp_path)


def test_detect_mixed_environment(tmp_path):
    """Ensure scanner detects multiple projects in subdirectories."""
    backend = tmp_path / "api"
    backend.mkdir()
    (backend / "pom.xml").write_text("")

    frontend = tmp_path / "web"
    frontend.mkdir()
    (frontend / "angular.json").write_text("")

    state = detect_environment(str(tmp_path))
    assert state["has_spring"] is True
    assert state["has_angular"] is True
    assert state["spring_path"] == str(backend)
    assert state["angular_path"] == str(frontend)
