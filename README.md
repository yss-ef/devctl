# devctl

## Local Development Environment Orchestrator

`devctl` is a powerful Command Line Interface (CLI) tool designed to streamline the orchestration of local development environments, particularly for Spring and Angular projects. It simplifies the setup and management of your development stack, allowing you to quickly initialize new projects and run your environment in parallel.

## Features

*   **Project Initialization (`init`)**: Quickly set up new projects with a predefined codebase structure.
*   **Environment Orchestration (`run`)**: Launch and manage your local development environment components in parallel.
*   **Health Check (`ping`)**: A simple command to verify that the `devctl` CLI is operational.

## Installation

`devctl` requires Python 3.9 or higher.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/devctl.git
    cd devctl
    ```

2.  **Install using pip**:
    It's recommended to install `devctl` in a virtual environment.

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    pip install .
    ```

    This will install `devctl` and its dependencies, making the `devctl` command available in your terminal.

## Usage

### General Help

To see the main help message:

```bash
devctl --help
```

### Ping Command

Verify the CLI is working:

```bash
devctl ping
```

Expected output:
```
pong ! Le CLI devctl est parfaitement opérationnel.
```

### Initialize a New Project

To initialize a new project (e.g., a Spring or Angular project):

```bash
devctl init --help
# Follow the instructions for the 'init' command
```

### Run the Development Environment

To launch your local development environment:

```bash
devctl run --help
# Follow the instructions for the 'run' command
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details (if applicable).
