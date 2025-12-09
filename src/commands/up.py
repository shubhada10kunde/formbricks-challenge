import click
import subprocess
import time
import os
from pathlib import Path
from rich.console import Console
from rich.status import Status
from rich.panel import Panel
import requests
import sys

console = Console()

def check_docker_installed() -> bool:
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[green]✓ Docker: {result.stdout.strip()}[/green]")
            return True
    except FileNotFoundError:
        console.print("[red]✗ Docker not found. Please install Docker Desktop.[/red]")
    return False

def check_docker_compose_installed() -> bool:
    """Check if Docker Compose is installed"""
    try:
        result = subprocess.run(["docker-compose", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[green]✓ Docker Compose: {result.stdout.strip()}[/green]")
            return True
    except FileNotFoundError:
        # Try with docker compose (v2)
        try:
            result = subprocess.run(["docker", "compose", "version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                console.print(f"[green]✓ Docker Compose V2 available[/green]")
                return True
        except:
            pass
    console.print("[red]✗ Docker Compose not found.[/red]")
    return False

def wait_for_formbricks(timeout: int = 180) -> bool:
    """Wait for Formbricks to be ready"""
    console.print("[yellow]⏳ Waiting for Formbricks to start...[/yellow]")
    
    start_time = time.time()
    url = "http://localhost:3000"
    
    with Status("[bold blue]Waiting for Formbricks...", console=console):
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{url}/api/health", timeout=5)
                if response.status_code == 200:
                    console.print(f"\n[green]✓ Formbricks is ready![/green]")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            # Check if containers are still running
            try:
                result = subprocess.run(
                    ["docker-compose", "ps", "--services", "--filter", "status=running"],
                    capture_output=True, text=True
                )
                if "formbricks" in result.stdout:
                    console.print(f"[dim]Formbricks container is running...[/dim]")
            except:
                pass
            
            time.sleep(5)
    
    console.print("[red]✗ Formbricks failed to start within timeout[/red]")
    return False

@click.command()
@click.option('--build', is_flag=True, help='Rebuild Docker images')
@click.option('--timeout', default=180, help='Timeout in seconds for startup')
def up_command(build, timeout):
    """Start Formbricks locally using Docker Compose"""
    
    console.print(Panel.fit(
        "[bold blue]Starting Formbricks Locally[/bold blue]",
        border_style="blue"
    ))
    
    # Check prerequisites
    console.print("[bold]Checking prerequisites...[/bold]")
    if not check_docker_installed():
        return
    if not check_docker_compose_installed():
        return
    
    # Check if already running
    try:
        response = requests.get("http://localhost:3000/api/health", timeout=2)
        if response.status_code == 200:
            console.print("[yellow]⚠ Formbricks is already running[/yellow]")
            console.print("\n[bold]Access:[/bold] http://localhost:3000")
            return
    except:
        pass
    
    # Start Formbricks
    docker_compose_path = Path(__file__).parent.parent.parent / "docker-compose.yml"
    
    if not docker_compose_path.exists():
        console.print("[red]✗ docker-compose.yml not found[/red]")
        console.print("Please create docker-compose.yml first")
        return
    
    console.print("\n[bold]Starting Formbricks...[/bold]")
    
    try:
        command = ["docker-compose", "up", "-d"]
        if build:
            command.append("--build")
        
        with Status("[bold blue]Starting containers...", console=console):
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=docker_compose_path.parent
            )
        
        if result.returncode != 0:
            console.print(f"[red]✗ Failed to start containers:[/red]")
            console.print(result.stderr)
            
            # Show logs for debugging
            console.print("\n[bold]Checking container logs...[/bold]")
            subprocess.run(["docker-compose", "logs", "--tail=20"], 
                         cwd=docker_compose_path.parent)
            return
        
        # Wait for Formbricks to be ready
        if wait_for_formbricks(timeout):
            console.print(Panel.fit(
                "[bold green]Formbricks is now running![/bold green]\n\n"
                "[bold]Access Formbricks:[/bold] http://localhost:3000\n"
                "[bold]Setup Instructions:[/bold]\n"
                "  1. Open http://localhost:3000\n"
                "  2. Create your admin account on first visit\n\n"
                "[bold]Next Steps:[/bold]\n"
                "1. Setup your admin account in Formbricks\n"
                "2. Go to Settings → API Keys\n"
                "3. Create a Management API key\n"
                "4. Use it with: python main.py formbricks seed --api-key YOUR_KEY",
                border_style="green"
            ))
        else:
            console.print("[red]Failed to start Formbricks. Check logs with:[/red]")
            console.print("  docker-compose logs")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")