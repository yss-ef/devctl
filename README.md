# devctl — Local Development Orchestrator

`devctl` is a powerful command-line interface (CLI) designed to automate and orchestrate the local development lifecycle, specifically tailored for **Spring Boot**, **Angular**, and **Vue.js** architectures.

## 🌟 Why devctl?

Setting up a modern full-stack environment often involves repetitive and error-prone tasks:
*   Configuring Docker databases and connection strings.
*   Setting up boilerplate security (JWT, Filters, Config).
*   Manually creating CRUD layers (Entity, Repository, Service, Controller).
*   Managing multiple terminal windows to run the database, backend, and frontend simultaneously.
*   Ensuring the environment is cleaned up after development.

**devctl** solves these problems by providing a single point of control. It automates the "boring parts" so you can focus on writing business logic.

## 🏗️ How it works

`devctl` is built with a modular architecture using **Python 3**:

*   **CLI Engine**: Uses [Typer](https://typer.tiangolo.com/) for a modern, type-hinted command-line experience.
*   **Templating**: Leverages [Jinja2](https://palletsprojects.com/p/jinja/) to dynamically generate Java code, TypeScript, and configuration files.
*   **Spring Integration**: Communicates with the [Spring Initializr API](https://start.spring.io/) to download tailored project structures.
*   **Frontend Generation**: Orchestrates `@angular/cli` and `Vite` to bootstrap modern frontend projects.
*   **Smart Orchestration**: Uses a recursive scanning engine to detect projects in your directory and manages them as parallel system processes.
*   **Docker Management**: Automatically handles `docker-compose` lifecycles, including volume cleanup.

## 📋 System Prerequisites

Before installing, ensure you have the following tools available:

*   **Python** >= 3.9
*   **Docker** & **Docker Compose**
*   **Java 17+** (for Spring Boot)
*   **Node.js** & **npm** (for Angular/Vue.js)
*   **Angular CLI** (`npm install -g @angular/cli`) - *Required for Angular projects*

## 🛠️ Installation Guide

Follow these steps to set up `devctl` locally:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/devctl.git
    cd devctl
    ```

2.  **Create a virtual environment (Recommended)**:
    ```bash
    python -m venv .venv
    source .venv/bin/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate      # On Windows
    ```

3.  **Install in editable mode**:
    This allows you to use the `devctl` command globally while reflecting any code changes immediately.
    ```bash
    pip install -e .
    ```

4.  **Verify installation**:
    ```bash
    devctl ping
    ```

## 📖 Command Reference

### 1. Project Initialization (`devctl init`)

Initialize a new project from scratch with pre-configured defaults.

*   **Spring Boot**: Downloads a project with Security (JWT), JPA, and chosen DB.
    ```bash
    devctl init spring "my-api" --db [postgres|mysql] --port 5432
    ```
*   **Angular**: Bootstraps an Angular project with Routing, SCSS, and Proxy configuration.
    ```bash
    devctl init angular "my-front"
    ```
*   **Vue.js**: Bootstraps a Vue 3 + TypeScript project via Vite with `vue-router` and proxy.
    ```bash
    devctl init vue "my-vue-front"
    ```

### 2. Scaffolding (`devctl add`)

Add business resources to your existing projects. This command scans the current directory and injects code into both detected Backend and Frontend projects.

*   **Resource Generation**: Generates Entity, Repository, Service, Controller (Spring) and Models, Services, Components (Angular).
    ```bash
    devctl add resource "Product" --fields "name:string,price:double,quantity:int"
    ```
    *Supported types: string, int, double, float, boolean, date.*

### 3. One-Click Run (`devctl run`)

The heart of `devctl`. It scans your current folder tree, identifies all components, and launches them.

```bash
devctl run
```

**What happens behind the scenes:**
1.  **Docker**: Runs `docker compose up -d` for the database.
2.  **Backend**: Runs `./mvnw spring-boot:run` for Spring projects.
3.  **Frontend**: Runs `npx ng serve` (Angular) or `npm run dev` (Vue.js).
4.  **Cleanup**: When you press **Ctrl+C**, `devctl` stops all processes and runs `docker compose down -v` to leave your system clean.

### 4. Utility (`devctl ping`)

A simple health check to ensure the CLI is properly installed and responsive.
```bash
devctl ping
```

---
*Authored by Youssef Fellah.*
