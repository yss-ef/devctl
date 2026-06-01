# Devctl core engine documentation

This documentation describes the internal architecture of the `devctl` core
engine, including the implementation of the CLI, orchestrator, and
generators.

## System architecture

`devctl` is a modular CLI application. The CLI layer delegates tasks to
specialized orchestrators and generators.

```mermaid
graph TD
    CLI[CLI Layer - Typer] --> Commands[Commands - init, run, add, deploy, docker]
    Commands --> Scanner[Scanner - Env Detection]
    Commands --> Runner[Runner - Process Management]
    Commands --> ConfigBuilder[Config Builder - Jinja2 Templates]
    Commands --> Generators[Generators - Spring, Angular, Vue]
    
    Generators --> SpringGen[Spring Generator - API + POM Patching]
    Generators --> AngularGen[Angular Generator - CLI + Config]
    Generators --> ScaffoldGen[Scaffolding - Resource CRUD]
    
    Runner --> Subprocess[Subprocess Management]
    Runner --> Docker[Docker Compose]
```

## Class and module diagram

The tool organizes logic into modules that function as services.

```mermaid
classDiagram
    class CLI {
        +app Typer
        +main()
    }
    class Scanner {
        +detect_environment(root_path)
    }
    class Runner {
        +launch_dev_environment(env_state)
        +is_docker_running()
    }
    class ConfigBuilder {
        +generate_config(project_name, db_type, custom_port)
    }
    class SpringGenerator {
        +download_spring_boilerplate()
        +patch_pom_xml()
        +generate_spring_resource()
        +generate_spring_security()
    }
    class AngularGenerator {
        +generate_angular_boilerplate()
        +setup_angular_environments()
        +generate_angular_resource()
    }

    CLI --> Scanner : uses
    CLI --> Runner : uses
    CLI --> ConfigBuilder : uses
    CLI --> SpringGenerator : delegates
    CLI --> AngularGenerator : delegates
```

## Sequence diagram: `devctl run`

The following diagram illustrates the lifecycle of the `run` command for local
orchestration.

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Scanner
    participant Runner
    participant Docker
    participant Subprocesses

    User->>CLI: devctl run
    CLI->>Scanner: detect_environment(".")
    Scanner-->>CLI: env_state
    CLI->>Runner: launch_dev_environment(env_state)
    
    alt Docker Compose found
        Runner->>Docker: docker compose up -d
        Docker-->>Runner: status ok
    end
    
    par Launch Backend
        Runner->>Subprocesses: ./mvnw spring-boot:run
    and Launch Frontend
        Runner->>Subprocesses: npx ng serve / npm run dev
    end
    
    User->>Runner: Ctrl+C (Interrupt)
    Runner->>Subprocesses: Terminate all
    alt Docker Compose found
        Runner->>Docker: docker compose down -v
    end
    Runner-->>User: Cleanup finished
```

## Sequence diagram: `devctl add resource`

The scaffolding command handles cross-stack code generation.

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Scanner
    participant SpringGenerator
    participant AngularGenerator
    participant FileSystem

    User->>CLI: devctl add resource Product --fields "name:string,price:double"
    CLI->>Scanner: detect_environment(".")
    Scanner-->>CLI: env_state
    
    alt is Spring Boot project
        CLI->>SpringGenerator: generate_spring_resource("Product", fields)
        SpringGenerator->>FileSystem: Create Entity, DTOs, Mapper, Service, Controller
    end
    
    alt is Angular project
        CLI->>AngularGenerator: generate_angular_resource("Product", fields)
        AngularGenerator->>FileSystem: Create Models, Service, Routes, List/Form Components
    end
```

## Key concepts

### 1. Intelligent environment scanning

The `Scanner` searches for signature files such as `pom.xml`, `angular.json`,
or `docker-compose-db.yml`. This allows the CLI to be context-aware and run
commands relative to project roots without complex configuration.

### 2. Parallel process management

The `Runner` uses `subprocess.Popen` to launch backend and frontend services
concurrently. It manages a graceful shutdown sequence upon receiving a
termination signal, ensuring no zombie processes remain.

### 3. Surgical POM patching

The `SpringGenerator` uses Python's `xml.etree.ElementTree` to inject
dependencies and annotation processors into the `pom.xml` file. This preserves
user changes while ensuring required libraries are present.

### 4. Jinja2 templating

Code generation relies on Jinja2 templates. This separates generation logic
from boilerplate code, facilitating updates to the generated structure.

### 5. Multi-tier scaffolding mapping

The generators translate simple field definitions into language-specific types.
The tool then generates a full vertical slice, including backend entities,
services, and controllers, along with frontend components and models.
