"""
Local development environment runner.
Handles parallel process management for multi-tier applications with log prefixing.
"""

import subprocess
import sys
import time
import threading
import signal
from pathlib import Path
from typing import List

import typer
from rich.console import Console

from devctl.generators.docker_scaffold import DockerProject

console = Console()

# Global list to track processes for cleanup
active_processes = []
active_threads = []


def is_docker_running():
    """Checks if the Docker daemon is active on the system."""
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def stream_logs(name: str, process: subprocess.Popen, color: str):
    """Streams logs from a process with a colored prefix."""
    try:
        # Use line-buffered reading
        for line in iter(process.stdout.readline, b""):
            if line:
                decoded_line = line.decode("utf-8", errors="ignore").rstrip()
                console.print(f"[{color}]{name:>15} |[/{color}] {decoded_line}")
    except Exception as e:
        console.print(f"[red]Error streaming logs for {name}: {e}[/red]")


def launch_dev_environment(projects: List[DockerProject], docker_composes: List[Path]):
    """
    Launches the necessary processes in parallel with structured startup and log streaming.
    """
    global active_processes

    def signal_handler(sig, frame):
        typer.echo("\n🛑 Shutdown requested. Cleaning up...")
        cleanup_and_exit(docker_composes)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # 1. Start Databases
        if docker_composes:
            if not is_docker_running():
                typer.secho("❌ Error: Docker service is not running.", fg=typer.colors.RED)
                sys.exit(1)

            for compose_path in docker_composes:
                typer.secho(f"🐳 Starting Docker Compose in {compose_path}...", fg=typer.colors.CYAN)
                subprocess.run(
                    ["docker", "compose", "up", "-d"], cwd=str(compose_path), check=True
                )
            
            typer.echo("⏳ Waiting 5s for databases to initialize...")
            time.sleep(5)

        # 2. Start Backends (Spring Boot)
        backends = [p for p in projects if p.kind == "spring"]
        for p in backends:
            typer.secho(f"🍃 Starting Spring Boot: {p.name}...", fg=typer.colors.GREEN)
            
            proc = subprocess.Popen(
                ["./mvnw", "spring-boot:run"],
                cwd=str(p.path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
            )
            active_processes.append((p.name, proc))
            
            t = threading.Thread(target=stream_logs, args=(p.name, proc, "green"), daemon=True)
            t.start()
            active_threads.append(t)

        # 3. Start Frontends (Angular / Vue / Svelte)
        frontends = [p for p in projects if p.kind in ["angular", "vue", "svelte"]]
        for p in frontends:
            color = "cyan" if p.kind == "angular" else ("magenta" if p.kind == "vue" else "red")
            icon = "🅰️" if p.kind == "angular" else ("🟢" if p.kind == "vue" else "🧡")
            cmd = ["npx", "ng", "serve"] if p.kind == "angular" else ["npm", "run", "dev"]
            
            typer.secho(f"{icon} Starting {p.kind.capitalize()}: {p.name}...", fg=typer.colors.CYAN if p.kind == "angular" else (typer.colors.MAGENTA if p.kind == "vue" else typer.colors.RED))
            
            proc = subprocess.Popen(
                cmd,
                cwd=str(p.path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
            )
            active_processes.append((p.name, proc))
            
            t = threading.Thread(target=stream_logs, args=(p.name, proc, color), daemon=True)
            t.start()
            active_threads.append(t)

        if not active_processes and not docker_composes:
            typer.secho("⚠️ No projects or databases detected to run.", fg=typer.colors.YELLOW)
            return

        typer.secho(
            "\n✨ Development environment active! Press Ctrl+C to stop everything gracefully.\n",
            fg=typer.colors.GREEN,
            bold=True,
        )

        # Keep the main thread alive
        while True:
            time.sleep(1)
            # Check if any process has died unexpectedly
            for name, proc in active_processes:
                if proc.poll() is not None:
                    typer.secho(f"⚠️ Process {name} exited with code {proc.returncode}", fg=typer.colors.RED)
                    active_processes.remove((name, proc))

    except Exception as e:
        typer.secho(f"❌ A system error occurred: {e}", fg=typer.colors.RED)
        cleanup_and_exit(docker_composes)


def cleanup_and_exit(docker_composes: List[Path]):
    """Stops all active processes and docker containers."""
    for name, proc in active_processes:
        typer.echo(f"Closing {name}...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            typer.echo(f"Force killing {name}...")
            proc.kill()

    for compose_path in docker_composes:
        typer.echo(f"Stopping Docker Compose in {compose_path}...")
        try:
            subprocess.run(
                ["docker", "compose", "down", "-v"],
                cwd=str(compose_path),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            typer.secho(f"⚠️ Warning: Docker cleanup failed for {compose_path}", fg=typer.colors.RED)

    typer.secho("✅ Cleanup finished. Environment is clean.", fg=typer.colors.GREEN)
    sys.exit(0)
