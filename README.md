# devctl — Local Development Orchestrator

`devctl` is a command-line interface (CLI) designed to automate and orchestrate the local development lifecycle, specifically tailored for Spring Boot, Angular, and Vue.js architectures.

## Purpose

Modern full-stack development involves repetitive configuration and environment management tasks that are prone to human error. `devctl` provides a unified point of control to automate these processes, allowing developers to focus on implementation rather than infrastructure.

Key challenges addressed:
*   Standardized database configuration via Docker.
*   Automated security boilerplate generation (JWT, Filters, Configuration).
*   Surgical CRUD layer generation (Entity, Repository, Service, Controller).
*   Concurrent process management for multi-tier applications.
*   Automated environment cleanup.

## Architecture and Integration

The tool is built on a modular Python 3 architecture leveraging industry-standard libraries:

*   **CLI Engine**: Typer-based interface for type-safe command execution.
*   **Templating**: Jinja2 for dynamic generation of Java, TypeScript, and configuration assets.
*   **Spring Integration**: Integration with the Spring Initializr API for tailored project bootstrapping.
*   **Frontend Orchestration**: Native support for @angular/cli and Vite.
*   **Orchestration Engine**: Recursive scanning for project detection and parallel process management.
*   **Container Management**: Lifecycle management for Docker Compose, including volume persistence control.

## System Requirements

The following dependencies must be available in the system path:

*   **Python**: >= 3.9
*   **Docker & Docker Compose**
*   **Java**: 17+ (for Spring Boot modules)
*   **Node.js & npm**: (for Angular/Vue.js modules)
*   **Angular CLI**: Required for Angular project initialization.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/devctl.git
    cd devctl
    ```

2.  **Configure a virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate   # Windows
    ```

3.  **Install the package**:
    ```bash
    pip install -e .
    ```

4.  **Verify installation**:
    ```bash
    devctl ping
    ```

## Command Reference

### Project Initialization

Bootstrap new projects with pre-configured defaults and security standards.

*   **Spring Boot**:
    ```bash
    devctl init spring "api-service" --db [postgres|mysql] --port 5432
    ```
*   **Angular**:
    ```bash
    devctl init angular "web-client"
    ```
*   **Vue.js**:
    ```bash
    devctl init vue "vue-client"
    ```

### Resource Scaffolding

Inject business resources into existing project structures. The command automatically detects active modules and updates both backend and frontend layers.

```bash
devctl add resource "Product" --fields "name:string,price:double,quantity:int"
```
*Supported types: string, int, double, float, boolean, date.*

### Orchestration

Scan the current directory tree and launch all detected components (Database, Backend, Frontend) in parallel.

```bash
devctl run
```

Upon termination (Ctrl+C), `devctl` gracefully stops all processes and performs a clean teardown of Docker resources.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Authored by Youssef Fellah.*
*Personal Project.*
