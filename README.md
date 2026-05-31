# Devctl

`devctl` is a command-line interface (CLI) that automates and orchestrates the
local development lifecycle for Spring Boot, Angular, and Vue.js
architectures.

## Purpose

Full-stack development involves repetitive configuration and environment
management tasks. `devctl` provides a unified control point to automate these
processes, allowing you to focus on implementation rather than infrastructure.

The tool addresses the following challenges:
- Standardized database configuration using Docker.
- Automated security boilerplate generation (JWT, filters, and configuration).
- Surgical CRUD layer generation (entities, repositories, services, and
  controllers).
- Concurrent process management for multi-tier applications.
- Automated environment cleanup.

## Architecture and integration

The tool uses a modular Python 3 architecture and industry-standard libraries:

- CLI engine: Typer-based interface for type-safe command execution.
- Templating: Jinja2 for dynamic generation of Java, TypeScript, and
  configuration assets.
- Spring integration: Connects with the Spring Initializr API for project
  bootstrapping.
- Frontend orchestration: Native support for @angular/cli and Vite.
- Orchestration engine: Recursive scanning for project detection and parallel
  process management.
- Container management: Lifecycle management for Docker Compose, including
  volume persistence control.

## System requirements

The following dependencies must be in the system path:

- Python: version 3.9 or later.
- Docker and Docker Compose.
- Java: version 17 or later for Spring Boot modules.
- Node.js and npm for Angular and Vue.js modules.
- Angular CLI for Angular project initialization.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/devctl.git
   cd devctl
   ```
2. Configure a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   ```
3. Install the package:
   ```bash
   pip install -e .
   ```
4. Verify the installation:
   ```bash
   devctl ping
   ```

## Command reference

### Project initialization

Bootstrap new projects with pre-configured defaults and security standards.

- Spring Boot:
  ```bash
  devctl init spring "api-service" --db [postgres|mysql] --port 5432
  ```
- Angular:
  ```bash
  devctl init angular "web-client"
  ```
- Vue.js:
  ```bash
  devctl init vue "vue-client"
  ```

### Resource scaffolding

Inject business resources into existing project structures. The command detects
active modules and updates both backend and frontend layers.

```bash
devctl add resource "Product" --fields "name:string,price:double,quantity:int"
```

### Orchestration

Scan the current directory tree and launch all detected components (database,
backend, and frontend) in parallel.

```bash
devctl run
```

Upon termination (Ctrl+C), `devctl` stops all processes and performs a clean
teardown of Docker resources.

### Dockerfile scaffolding

Generate Dockerfiles for detected Spring Boot, Angular, and Vue/Vite services.

```bash
devctl dockerize
devctl dockerize ./my-workspace --dry-run
devctl dockerize --force
```

Generated assets are limited to service-local `Dockerfile` files. Existing
files are skipped unless you use the `--force` flag.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for details.

Authored by Youssef Fellah.
Personal project.
