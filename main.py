#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import click
from rich.console import Console
from rich.panel import Panel

from src.commands.up import up_command
from src.commands.down import down_command
from src.commands.generate import generate_command
from src.commands.seed import seed_command
from src.utils.config import Config

console = Console()

@click.group()
def cli():
    """Formbricks Challenge CLI - Real API Implementation"""
    pass

@cli.group()
def formbricks():
    """Formbricks instance management"""
    pass

@cli.command()
def config():
    """Show current configuration"""
    Config.print_config()
    
    errors = Config.validate()
    if errors:
        console.print("\n[bold red]Configuration Issues:[/bold red]")
        for error in errors:
            console.print(f"  • {error}")

@cli.command()
def setup():
    """Setup Formbricks challenge environment"""
    console.print(Panel.fit(
        "[bold blue]Formbricks Challenge Setup[/bold blue]",
        border_style="blue"
    ))
    
    # Check Docker
    console.print("[bold]Checking Docker...[/bold]")
    try:
        import subprocess
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[green]✓ Docker installed: {result.stdout.split(',')[0]}[/green]")
        else:
            console.print("[red]✗ Docker not found[/red]")
            console.print("Install Docker Desktop from: https://www.docker.com/products/docker-desktop/")
            return
    except:
        console.print("[red]✗ Docker not found[/red]")
        return
    
    # Check Python packages
    console.print("\n[bold]Checking Python packages...[/bold]")
    try:
        import pkg_resources
        with open("requirements.txt") as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        for req in requirements:
            try:
                pkg_resources.require(req)
                console.print(f"[green]✓ {req}[/green]")
            except:
                console.print(f"[yellow]⚠ {req} not installed[/yellow]")
    except Exception as e:
        console.print(f"[yellow]⚠ Could not check packages: {e}[/yellow]")
    
    console.print("\n[bold]Setup complete![/bold]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Copy .env.example to .env (already done)")
    console.print("2. Install Ollama: https://ollama.com/")
    console.print("3. Run: ollama serve (in another terminal)")
    console.print("4. Run: ollama pull llama2")
    console.print("5. Run: python main.py formbricks up")
    console.print("6. Setup Formbricks admin account at http://localhost:3000")
    console.print("7. Get Formbricks API key from Settings → API Keys")
    console.print("8. Run: python main.py formbricks generate")
    console.print("9. Run: python main.py formbricks seed")

# Add formbricks subcommands
formbricks.add_command(up_command, name="up")
formbricks.add_command(down_command, name="down")
formbricks.add_command(generate_command, name="generate")
formbricks.add_command(seed_command, name="seed")

if __name__ == "__main__":
    cli()