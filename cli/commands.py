
"""
CLI command definitions and handlers
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional

console = Console()

# Sub-application for command management
app = typer.Typer(help="Command management utilities")


@app.command("config")
def show_config():
    """Show current configuration."""
    from config.settings import Settings
    
    settings = Settings()
    config = settings.get_config_summary()
    
    table = Table(title="Current Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in config.items():
        table.add_row(key, str(value))
    
    console.print(table)


@app.command("stats")
def show_stats():
    """Show usage statistics."""
    from storage.command_store import CommandStore
    
    store = CommandStore()
    stats = store.get_statistics()
    
    console.print(Panel(
        f"Total Commands: {stats['total_commands']}\n"
        f"Executed: {stats['executed_commands']}\n"
        f"Successful: {stats['successful_commands']}\n"
        f"Execution Rate: {stats['execution_rate']:.1%}\n"
        f"Success Rate: {stats['success_rate']:.1%}\n"
        f"Active Days: {stats['active_days']}",
        title="Usage Statistics"
    ))
    
    if stats['risk_distribution']:
        table = Table(title="Risk Level Distribution")
        table.add_column("Risk Level", style="yellow")
        table.add_column("Count", style="cyan")
        
        for risk, count in stats['risk_distribution'].items():
            table.add_row(risk or "unknown", str(count))
        
        console.print(table)


@app.command("export")
def export_data(
    output: str = typer.Option("commands_export.json", "--output", "-o", help="Output file"),
    format: str = typer.Option("json", "--format", "-f", help="Export format (json, csv)")
):
    """Export command history."""
    from storage.command_store import CommandStore
    
    store = CommandStore()
    success = store.export_commands(output, format)
    
    if success:
        console.print(f"[green]Data exported to {output}[/green]")
    else:
        console.print(f"[red]Failed to export data[/red]")


@app.command("clear")
def clear_history(
    days: Optional[int] = typer.Option(None, "--days", "-d", help="Clear commands older than N days"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Clear command history."""
    from storage.command_store import CommandStore
    
    if not confirm:
        if days:
            message = f"Clear commands older than {days} days?"
        else:
            message = "Clear ALL command history?"
        
        if not typer.confirm(message):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
    
    store = CommandStore()
    store.clear_history(days)
    
    if days:
        console.print(f"[green]Cleared commands older than {days} days[/green]")
    else:
        console.print("[green]All command history cleared[/green]")


@app.command("test")
def test_llm():
    """Test LLM connection and functionality."""
    import asyncio
    from services.llm_service import LLMService
    from config.settings import Settings
    
    console.print("[blue]Testing LLM connection...[/blue]")
    
    settings = Settings()
    llm_service = LLMService(settings)
    
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "list files in current directory"}
    ]
    
    try:
        response = asyncio.run(llm_service.generate_response(test_messages))
        console.print("[green]✓ LLM connection successful[/green]")
        console.print(f"Response: {response[:100]}...")
    except Exception as e:
        console.print(f"[red]✗ LLM connection failed: {e}[/red]")
