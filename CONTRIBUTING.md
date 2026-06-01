# Contributing to devctl

Thank you for your interest in contributing to `devctl`! We welcome contributions from the community to make this tool even better.

## How to Contribute

1.  **Report Bugs**: If you find a bug, please open an issue on GitHub with a detailed description and steps to reproduce it.
2.  **Suggest Features**: Have an idea for a new feature? Open an issue to discuss it.
3.  **Submit Pull Requests**:
    *   Fork the repository.
    *   Create a new branch for your feature or bugfix.
    *   Ensure your code follows the project's style (we use [Ruff](https://github.com/astral-sh/ruff)).
    *   Add tests for any new functionality.
    *   Submit a PR with a clear description of your changes.

## Development Setup

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/devctl.git
    cd devctl
    ```
2.  Create a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
3.  Install dependencies in editable mode:
    ```bash
    pip install -e .
    ```
4.  Run tests:
    ```bash
    pytest
    ```

## Code Quality

We use `ruff` for linting and formatting. You can run it with:
```bash
ruff check .
ruff format .
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
