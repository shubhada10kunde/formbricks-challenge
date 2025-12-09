import click
import json
import asyncio
import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.api.llm_generator import LLMGenerator
from src.utils.config import Config

console = Console()

@click.command()
@click.option('--provider', type=click.Choice(['ollama']),  # REMOVE 'openai'
              default='ollama', help='LLM provider')  # CHANGE default to ollama
@click.option('--model', help='Model to use (llama2, mistral, codellama, etc.)')
@click.option('--num-surveys', default=5, help='Number of surveys to generate')
@click.option('--num-users', default=10, help='Number of users to generate')
@click.option('--output-dir', default='./data', help='Output directory')
def generate_command(provider, model, num_surveys, num_users, output_dir):
    """Generate realistic survey data using Ollama (local LLM)"""
    
    console.print(Panel.fit(
        f"[bold blue]Generating Data with Ollama[/bold blue]",
        border_style="blue"
    ))

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    # Initialize generator
    try:
        generator = LLMGenerator(
            provider=provider,  #'ollama'
            api_key=None, 
            model=model or Config.OLLAMA_MODEL
        )
        
        # Generate data
        console.print("\n[bold]Generating data with Ollama...[/bold]")
        
        async def generate():
            return await generator.run(num_surveys, num_users)
        
        data = asyncio.run(generate())
        
        # Save data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        surveys_file = output_path / f"surveys_{timestamp}.json"
        users_file = output_path / f"users_{timestamp}.json"
        responses_file = output_path / f"responses_{timestamp}.json"
        
        # Also create latest symlinks
        latest_surveys = output_path / "surveys_latest.json"
        latest_users = output_path / "users_latest.json"
        latest_responses = output_path / "responses_latest.json"
        
        with open(surveys_file, 'w') as f:
            json.dump(data['surveys'], f, indent=2, default=str)
        if latest_surveys.exists() or latest_surveys.is_symlink():
            latest_surveys.unlink()
        latest_surveys.symlink_to(surveys_file.name)
        
        with open(users_file, 'w') as f:
            json.dump(data['users'], f, indent=2, default=str)
        if latest_users.exists() or latest_users.is_symlink():
            latest_users.unlink()
        latest_users.symlink_to(users_file.name)
        
        with open(responses_file, 'w') as f:
            json.dump(data['responses'], f, indent=2, default=str)
        if latest_responses.exists() or latest_responses.is_symlink():
            latest_responses.unlink()
        latest_responses.symlink_to(responses_file.name)
        
        # Show summary
        console.print(Panel.fit(
            "[bold green]Data Generation Complete![/bold green]",
            border_style="green"
        ))
        
        table = Table(title="Generated Data Summary")
        table.add_column("Type", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("File", style="yellow")
        
        table.add_row("Surveys", str(len(data['surveys'])), str(surveys_file))
        table.add_row("Users", str(len(data['users'])), str(users_file))
        table.add_row("Responses", str(len(data['responses'])), str(responses_file))
        
        console.print(table)
        
        # Show sample
        console.print("\n[bold]Sample Survey:[/bold]")
        if data['surveys']:
            survey = data['surveys'][0]
            console.print(f"  Name: {survey.get('name', 'N/A')}")
            console.print(f"  Questions: {len(survey.get('questions', []))}")
        
        console.print("\n[bold]User Roles:[/bold]")
        roles = {}
        for user in data['users']:
            role = user.get('role', 'unknown')
            roles[role] = roles.get(role, 0) + 1
        
        for role, count in roles.items():
            console.print(f"  {role}: {count}")
        
        console.print(f"\n[bold]Next:[/bold] Run [cyan]python main.py formbricks seed[/cyan] to populate Formbricks")
        
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        console.print("\n[bold]To setup Ollama:[/bold]")
        console.print("1. Install Ollama: https://ollama.com/")
        console.print("2. Run in terminal: ollama serve")
        console.print("3. Pull a model: ollama pull llama2")
        console.print("4. Make sure Ollama is running, then try again")