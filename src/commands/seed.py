import click
import json
import time
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table
import asyncio

from src.api.formbricks_api import FormbricksAPI
from src.utils.config import Config

console = Console()

def load_data(data_dir: Path) -> tuple[Dict, Dict, Dict]:
    """Load generated data files"""
    # Try to load latest files
    surveys_file = data_dir / "surveys_latest.json"
    users_file = data_dir / "users_latest.json"
    responses_file = data_dir / "responses_latest.json"
    
    # Fallback to any JSON file
    if not surveys_file.exists():
        json_files = list(data_dir.glob("surveys_*.json"))
        if json_files:
            surveys_file = sorted(json_files)[-1]
    
    if not users_file.exists():
        json_files = list(data_dir.glob("users_*.json"))
        if json_files:
            users_file = sorted(json_files)[-1]
    
    if not responses_file.exists():
        json_files = list(data_dir.glob("responses_*.json"))
        if json_files:
            responses_file = sorted(json_files)[-1]
    
    if not all([surveys_file.exists(), users_file.exists(), responses_file.exists()]):
        raise FileNotFoundError("Generated data files not found. Run 'generate' first.")
    
    with open(surveys_file) as f:
        surveys = json.load(f)
    with open(users_file) as f:
        users = json.load(f)
    with open(responses_file) as f:
        responses = json.load(f)
    
    return surveys, users, responses

@click.command()
@click.option('--api-key', help='Formbricks Management API key (or set FORMBRICKS_API_KEY in .env)')
@click.option('--data-dir', default='./data', help='Directory with generated data')
@click.option('--base-url', default=None, help='Formbricks base URL (default: from .env or http://localhost:3000)')
@click.option('--skip-users', is_flag=True, help='Skip creating users')
@click.option('--skip-responses', is_flag=True, help='Skip submitting responses')
def seed_command(api_key, data_dir, base_url, skip_users, skip_responses):
    """Seed Formbricks with generated data using APIs"""
    
    console.print(Panel.fit(
        "[bold blue]Seeding Formbricks via APIs[/bold blue]",
        border_style="blue"
    ))
    
    # Get API key
    if not api_key:
        api_key = Config.FORMBRICKS_API_KEY
    
    if not api_key:
        console.print("[red]✗ Formbricks API key required![/red]")
        console.print("Set --api-key or FORMBRICKS_API_KEY in .env file")
        console.print("\n[bold]How to get API key:[/bold]")
        console.print("1. Start Formbricks: python main.py formbricks up")
        console.print("2. Open http://localhost:3000")
        console.print("3. Setup your admin account (first visit)")
        console.print("4. Go to Settings → API Keys")
        console.print("5. Create a Management API key")
        console.print("\n[bold]Your .env should look like:[/bold]")
        console.print("  FORMBRICKS_API_KEY=fbrcks_your_key_here")
        return
    
    # Get base URL
    if not base_url:
        base_url = Config.FORMBRICKS_URL
    
    # Check if Formbricks is running
    # if not api.health_check():
    #     console.print("[red]✗ Formbricks is not running[/red]")
    #     console.print("Start it with: python main.py formbricks up")
    #     return
    
    api = FormbricksAPI(base_url=base_url)
    
    # Load data
    try:
        console.print("[bold]Loading generated data...[/bold]")
        surveys, users, responses = load_data(Path(data_dir))
        
        console.print(f"[green]✓[/green] Loaded {len(surveys)} surveys, {len(users)} users, {len(responses)} responses")
        
    except Exception as e:
        console.print(f"[red]✗ Failed to load data: {e}[/red]")
        return
    
    # Setup API
    api.setup_api_key(api_key)
    
    # Track results
    results = {
        'surveys': {'created': 0, 'failed': 0, 'ids': {}},
        'users': {'created': 0, 'failed': 0, 'ids': {}},
        'responses': {'submitted': 0, 'failed': 0}
    }
    
    # Create surveys
    console.print("\n[bold]📋 Creating Surveys via Management API...[/bold]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Creating surveys...", total=len(surveys))
        
        for survey in surveys:
            survey_name = survey.get('name', 'Unnamed Survey')
            
            try:
                # Format survey for Formbricks API
                formbricks_survey = {
                    'name': survey_name,
                    'type': 'link',
                    'questions': survey.get('questions', []),
                    'welcomeCard': survey.get('welcomeCard', {}),
                    'thankYouCard': survey.get('thankYouCard', {}),
                    'status': 'inProgress',
                    'language': 'en'
                }
                
                result = api.create_survey(formbricks_survey)
                
                if result and 'id' in result:
                    results['surveys']['created'] += 1
                    results['surveys']['ids'][survey_name] = result['id']
                    progress.console.print(f"[dim]  ✓ Created: {survey_name}[/dim]")
                else:
                    results['surveys']['failed'] += 1
                    progress.console.print(f"[yellow]  ⚠ Failed: {survey_name}[/yellow]")
                
            except Exception as e:
                results['surveys']['failed'] += 1
                progress.console.print(f"[red]  ✗ Error: {e}[/red]")
            
            progress.advance(task)
            time.sleep(1)  # Rate limiting
    
    # Create users (if not skipped)
    if not skip_users:
        console.print("\n[bold]👥 Creating Users via Management API...[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Creating users...", total=len(users))
            
            for user in users:
                user_email = user.get('email', 'unknown@example.com')
                
                try:
                    # Formbricks user creation
                    user_data = {
                        'email': user_email,
                        'name': user.get('name', 'User'),
                        'role': user.get('role', 'viewer')
                    }
                    
                    result = api.create_user(user_data)
                    
                    if result:
                        results['users']['created'] += 1
                        results['users']['ids'][user_email] = result.get('id', 'unknown')
                        progress.console.print(f"[dim]  ✓ User: {user_email} ({user.get('role')})[/dim]")
                    else:
                        results['users']['failed'] += 1
                        progress.console.print(f"[yellow]  ⚠ User might need manual invitation: {user_email}[/yellow]")
                
                except Exception as e:
                    results['users']['failed'] += 1
                    progress.console.print(f"[red]  ✗ Error with {user_email}: {e}[/red]")
                
                progress.advance(task)
                time.sleep(0.5)
    
    # Submit responses (if not skipped)
    if not skip_responses and results['surveys']['ids']:
        console.print("\n[bold]📝 Submitting Responses via Client API...[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Submitting responses...", total=len(responses))
            
            for response in responses:
                survey_name = response.get('survey_name')
                survey_id = results['surveys']['ids'].get(survey_name)
                
                if survey_id:
                    try:
                        response_data = {
                            'surveyId': survey_id,
                            'responses': response.get('answers', {}),
                            'finished': response.get('completed', True),
                            'userId': response.get('user_id', 'anonymous'),
                            'meta': response.get('meta', {})
                        }
                        
                        result = api.submit_response(survey_id, response_data)
                        
                        if result:
                            results['responses']['submitted'] += 1
                            progress.console.print(f"[dim]  ✓ Response for {survey_name}[/dim]")
                        else:
                            results['responses']['failed'] += 1
                            progress.console.print(f"[yellow]  ⚠ Failed to submit response for {survey_name}[/yellow]")
                    
                    except Exception as e:
                        results['responses']['failed'] += 1
                        progress.console.print(f"[red]  ✗ Error: {e}[/red]")
                else:
                    results['responses']['failed'] += 1
                    progress.console.print(f"[yellow]  ⚠ No survey ID for {survey_name}[/yellow]")
                
                progress.advance(task)
                time.sleep(0.3)
    
    # Display results
    console.print(Panel.fit(
        "[bold green]Seeding Complete![/bold green]",
        border_style="green"
    ))
    
    table = Table(title="Seeding Results")
    table.add_column("Resource", style="cyan")
    table.add_column("Created/Submitted", style="green")
    table.add_column("Failed", style="red")
    table.add_column("Success Rate", style="yellow")
    
    for resource in ['surveys', 'users', 'responses']:
        created = results[resource].get('created', results[resource].get('submitted', 0))
        failed = results[resource]['failed']
        total = created + failed
        
        if total > 0:
            success_rate = (created / total) * 100
            table.add_row(
                resource.title(),
                str(created),
                str(failed),
                f"{success_rate:.1f}%"
            )
    
    console.print(table)
    
    # Save mapping file
    if results['surveys']['ids']:
        mapping_file = Path(data_dir) / "survey_mapping.json"
        with open(mapping_file, 'w') as f:
            json.dump(results['surveys']['ids'], f, indent=2)
        console.print(f"\n[dim]Survey mapping saved to: {mapping_file}[/dim]")
    
    console.print(f"\n[bold]Access Formbricks:[/bold] {base_url}")
    
    if results['responses']['submitted'] > 0:
        console.print("\n[green]✅ Data successfully seeded via Formbricks APIs![/green]")
        console.print("\n[bold]Check your Formbricks dashboard to see the seeded data.[/bold]")