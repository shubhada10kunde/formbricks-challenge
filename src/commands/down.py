import click
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
import sys

console = Console()

@click.command()
@click.option('--volumes', '-v', is_flag=True, help='Remove volumes as well')
@click.option('--force', '-f', is_flag=True, help='Force remove without confirmation')
def down_command(volumes, force):
    """Stop and clean up Formbricks instance"""
    
    console.print(Panel.fit(
        "[bold yellow]Stopping Formbricks[/bold yellow]",
        border_style="yellow"
    ))
    
    docker_compose_path = Path(__file__).parent.parent.parent / "docker-compose.yml"
    
    if not docker_compose_path.exists():
        console.print("[red]✗ docker-compose.yml not found[/red]")
        return
    
    if not force:
        console.print("[yellow]⚠ This will stop and remove Formbricks containers[/yellow]")
        confirm = click.confirm("Are you sure you want to continue?", default=False)
        if not confirm:
            console.print("[blue]Operation cancelled[/blue]")
            return
    
    try:
        # Stop containers
        console.print("[bold]Stopping containers...[/bold]")
        
        command = ["docker-compose", "down"]
        if volumes:
            command.append("-v")
        
        with console.status("[blue]Cleaning up...", spinner="dots"):
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=docker_compose_path.parent
            )
        
        if result.returncode == 0:
            console.print(Panel.fit(
                "[bold green]Formbricks stopped successfully![/bold green]",
                border_style="green"
            ))
            
            if volumes:
                console.print("[dim]All volumes have been removed[/dim]")
            else:
                console.print("[dim]Volumes preserved (use --volumes to remove)[/dim]")
        else:
            console.print(f"[red]✗ Error stopping containers:[/red]")
            console.print(result.stderr)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")