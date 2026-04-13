# devctl — Local Development Orchestrator

`devctl` is a command-line interface (CLI) designed to automate and orchestrate the local development lifecycle, specifically for **Spring Boot** and **Angular** architectures.

It doesn't just generate code; it manages dynamic database configuration via Docker, injects ready-to-use security layers, and orchestrates the simultaneous execution of your technology stack.

## 🚀 Key Features

*   **Fullstack Generation**: Initializes Spring Boot projects (via Spring Initializr API) and Angular projects (via Angular CLI) with pre-established configurations.
*   **Automated Security**: Dynamically injects a complete **JWT** (JSON Web Token) security architecture into Spring projects (Filters, Services, SecurityConfig).
*   **Intelligent Scaffolding**: Generates business resources (Entity, Repository, Service, Controller) from simple CLI commands with automatic mapping of Java types.
*   **One-Click Orchestration**: Automatically detects components in your folder and simultaneously launches the database (Docker), backend (Maven), and frontend (Angular).
*   **Clean Shutdown**: Upon stopping (Ctrl+C), the tool handles stopping processes and removing Docker containers/volumes to leave the environment clean.

## 🛠️ Installation

The tool is optimized for a **Fedora** environment (managing `mvnw` permissions) and requires Python 3.9+.

```bash
# Installation in editable mode (recommended for development)
pip install -e .
```

## 📖 Command Guide

### 1. Initialization (`devctl init`)
Allows you to create the basic structure of your services.

*   **Spring Boot**: Downloads a boilerplate including JPA, Security, Lombok, and the chosen DB driver.
    ```bash
    devctl init spring "my-api" --db postgres --port 5432
    ```
*   **Angular**: Uses the `ng` CLI to generate a project with SCSS and routing enabled.
    ```bash
    devctl init angular "my-front"
    ```

### 2. Development & Scaffolding (`devctl add`)
Adds functionalities to an existing project by analyzing the context.

*   **Resource**: Generates the entire MVC stack for an entity.
    ```bash
    devctl add resource "Product" --fields "name:string,price:double,quantity:int"
    ```
    *Supported types: string, int, double, float, boolean, date.*

### 3. Orchestration (`devctl run`)
Scans the current directory to identify projects and launches the complete environment.

```bash
devctl run
```
**Orchestrated processes:**
1.  **Docker**: `docker compose up -d` (Database).
2.  **Backend**: `./mvnw spring-boot:run`.
3.  **Frontend**: `npx ng serve`.

### 4. Utility (`devctl ping`)
Simply verifies that the CLI is installed and responsive.

## 📂 Project Structure

*   `devctl/commands/`: Definition of Typer command groups (add, init, run).
*   `devctl/generators/`: Logic for file creation and calls to external APIs/CLIs.
*   `devctl/orchestrator/`: Tree scanning engine and system process management.
*   `devctl/templates/`: Jinja2 files for dynamic generation of Java code and Docker configurations.

## 📋 System Prerequisites

*   **Python** >= 3.9
*   **Docker** & **Docker Compose**

---

*Authored by Youssef Fellah.*