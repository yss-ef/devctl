# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-20

### Added
- **Vue.js Support**: Added Vue 3 TypeScript resource scaffolding including components, models, and services.
- **Security & CI**: Integrated CodeQL for security scanning, Semantic PR linter, and Release Drafter.
- **Documentation**: Added internal architecture documentation and standardized engine documentation headings.
- **License**: Added MIT License.

### Changed
- **Internationalization**: Completed full translation of CLI messages, comments, and docstrings from French to English.
- **Refactoring**: Standardized signatures across all README files and moved templates for better project organization.
- **Cleanup**: Removed emojis and refined the tone of all documentation for professional readiness.

### Fixed
- **Security**: Resolved CodeQL Jinja2 XSS warnings in Vue scaffolding.
- **Reliability**: Fixed accidental removal of `tmp_test` files and standardized code formatting using Ruff.

## [0.2.0] - 2026-04-15

### Added
- **Deployment**: Added `deploy` command to generate unified `docker-compose.yml` for orchestrated environments.
- **Dockerization**: Added `docker` command for scaffolding production-ready Dockerfiles for Spring Boot, Angular, and Vue projects.
- **Scaffolding Expansion**: Integrated Angular resource creation and enhanced Spring resource management (DTOs, Mappers).
- **Quality Tools**: Integrated Ruff, Dependabot, and CodeRabbit for automated code quality and dependency management.

### Fixed
- **Spring Integration**: Resolved Maven dependency issues and resource generation bugs.
- **Authentication**: Updated `AuthentificationProvider` for compatibility with newer Spring versions.
- **Networking**: Refactored Spring CORS configuration to better support Nginx reverse proxy architectures.

## [0.1.0] - 2026-03-01

### Added
- **Core Orchestrator**: Initial implementation of the `devctl` CLI with `init` and `run` commands.
- **Environment Detection**: Added automatic detection of Spring Boot, Angular, and Docker-based databases to the `run` command.
- **Spring Scaffolding**: Basic Spring Boot boilerplate generation with database configuration.
- **Local Release**: Stabilized core features for a "robust local release" including project initialization and automated local environment launch.
