
#!/usr/bin/env python3
"""
Real-Time LLM-Enhanced CLI Assistant
Main entry point for the CLI application
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.table import Table
from typing import Optional, List
import asyncio
from pathlib import Path

from cli.commands import app as commands_app
from core.context import ContextManager
from core.parser import IntentParser
from core.safety import SafetyValidator
from services.llm_service import LLMService
from storage.command_store import CommandStore
from config.settings import Settings

# Initialize Rich console for enhanced output
console = Console()

# Main Typer app
app = typer.Typer(
    name="rllm",
    help="Real-Time LLM-Enhanced CLI Assistant - Translate natural language to shell commands",
    add_completion=False,
    rich_markup_mode="rich"
)

# Add sub-commands
app.add_typer(commands_app, name="cmd")

# Global state
settings = Settings()
context_manager = ContextManager()
command_store = CommandStore()
llm_service = LLMService(settings)
intent_parser = IntentParser(llm_service)
safety_validator = SafetyValidator()


@app.command()
def ask(
    query: str = typer.Argument(..., help="Natural language description of what you want to do"),
    execute: bool = typer.Option(False, "--execute", "-x", help="Execute the command immediately"),
    explain: bool = typer.Option(True, "--explain/--no-explain", help="Show explanation"),
    context: bool = typer.Option(True, "--context/--no-context", help="Use conversation context"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show command without executing")
):
    """Ask the assistant to generate a shell command from natural language."""
    
    console.print(f"[bold blue]Processing:[/bold blue] {query}")
    
    try:
        # Get context if enabled
        session_context = context_manager.get_context() if context else None
        
        # Parse intent and generate command
        result = asyncio.run(intent_parser.parse(query, session_context))
        
        if not result:
            console.print("[red]Failed to generate command[/red]")
            raise typer.Exit(1)
        
        # Display command with syntax highlighting
        syntax = Syntax(result.command, "bash", theme="monokai", line_numbers=False)
        console.print(Panel(syntax, title="Generated Command", border_style="green"))
        
        # Show explanation if requested
        if explain and result.explanation:
            console.print(f"[bold yellow]Explanation:[/bold yellow] {result.explanation}")
        
        # Safety validation
        risk_assessment = safety_validator.validate(result.command)
        
        if risk_assessment.risk_level in ["high", "critical"]:
            console.print(f"[bold red]⚠️  Risk Level: {risk_assessment.risk_level.upper()}[/bold red]")
            for warning in risk_assessment.warnings:
                console.print(f"[yellow]• {warning}[/yellow]")
        
        # Show alternatives if available
        if result.alternatives:
            table = Table(title="Alternative Commands")
            table.add_column("Command", style="cyan")
            table.add_column("Description", style="green")
            
            for alt in result.alternatives[:3]:  # Show top 3 alternatives
                table.add_row(alt, "Alternative approach")
            
            console.print(table)
        
        # Execution logic
        should_execute = False
        
        if dry_run:
            console.print("[yellow]Dry run mode - command not executed[/yellow]")
        elif execute or Confirm.ask("Execute this command?", default=False):
            should_execute = True
        
        if should_execute:
            # Final safety check for high-risk commands
            if risk_assessment.risk_level == "critical":
                if not Confirm.ask("[bold red]This is a CRITICAL risk command. Are you absolutely sure?[/bold red]", default=False):
                    console.print("[yellow]Command execution cancelled[/yellow]")
                    return
            
            # Execute command
            console.print("[bold green]Executing...[/bold green]")
            success = asyncio.run(_execute_command(result.command))
            
            if success:
                # Store successful command
                command_store.store_command(
                    command=result.command,
                    query=query,
                    explanation=result.explanation,
                    risk_level=risk_assessment.risk_level
                )
                
                # Update context
                context_manager.add_interaction(query, result.command)
        
        # Store in history regardless of execution
        context_manager.add_to_history(query, result.command, executed=should_execute)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def interactive():
    """Start interactive mode for continuous conversation."""
    
    console.print(Panel(
        "[bold green]Real-Time LLM CLI Assistant[/bold green]\n"
        "Type your requests in natural language.\n"
        "Commands: 'exit', 'history', 'context', 'help'",
        title="Interactive Mode"
    ))
    
    while True:
        try:
            query = Prompt.ask("\n[bold blue]rllm>[/bold blue]", default="")
            
            if not query or query.lower() in ['exit', 'quit']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif query.lower() == 'history':
                _show_history()
                continue
            elif query.lower() == 'context':
                _show_context()
                continue
            elif query.lower() == 'help':
                _show_help()
                continue
            
            # Process the query
            ctx = typer.Context(ask)
            ctx.invoke(ask, query=query, execute=False, explain=True, context=True, dry_run=False)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@app.command()
def history(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of recent commands to show"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search in command history")
):
    """Show command history."""
    commands = command_store.get_history(limit=limit, search=search)
    
    if not commands:
        console.print("[yellow]No commands in history[/yellow]")
        return
    
    table = Table(title="Command History")
    table.add_column("ID", style="cyan", width=6)
    table.add_column("Query", style="green")
    table.add_column("Command", style="yellow")
    table.add_column("Risk", style="red")
    table.add_column("Time", style="blue")
    
    for cmd in commands:
        table.add_row(
            str(cmd.id),
            cmd.query[:50] + "..." if len(cmd.query) > 50 else cmd.query,
            cmd.command[:60] + "..." if len(cmd.command) > 60 else cmd.command,
            cmd.risk_level or "low",
            cmd.timestamp.strftime("%H:%M:%S")
        )
    
    console.print(table)


@app.command()
def export_script(
    output: str = typer.Option("script.sh", "--output", "-o", help="Output script file"),
    last: int = typer.Option(5, "--last", "-l", help="Number of recent commands to include")
):
    """Export recent commands as a shell script."""
    commands = command_store.get_history(limit=last)
    
    if not commands:
        console.print("[yellow]No commands to export[/yellow]")
        return
    
    script_content = ["#!/bin/bash", "# Generated by RLLM CLI Assistant", ""]
    
    for cmd in reversed(commands):  # Reverse to get chronological order
        script_content.append(f"# {cmd.query}")
        script_content.append(cmd.command)
        script_content.append("")
    
    Path(output).write_text("\n".join(script_content))
    console.print(f"[green]Script exported to {output}[/green]")


async def _execute_command(command: str) -> bool:
    """Execute a shell command and display output."""
    import subprocess
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            console.print("[green]Output:[/green]")
            console.print(result.stdout)
        
        if result.stderr:
            console.print("[red]Error:[/red]")
            console.print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        console.print("[red]Command timed out[/red]")
        return False
    except Exception as e:
        console.print(f"[red]Execution error: {e}[/red]")
        return False


def _show_history():
    """Show recent command history."""
    history_data = context_manager.get_history(limit=5)
    
    if not history_data:
        console.print("[yellow]No history available[/yellow]")
        return
    
    table = Table(title="Recent History")
    table.add_column("Query", style="green")
    table.add_column("Command", style="yellow")
    table.add_column("Status", style="blue")
    
    for item in history_data:
        status = "✓ Executed" if item.get('executed') else "○ Generated"
        table.add_row(item['query'], item['command'], status)
    
    console.print(table)


def _show_context():
    """Show current conversation context."""
    context = context_manager.get_context()
    
    if not context:
        console.print("[yellow]No context available[/yellow]")
        return
    
    console.print(Panel(
        f"Working Directory: {context.get('current_directory', 'Unknown')}\n"
        f"Previous Commands: {len(context.get('previous_commands', []))}\n"
        f"OS: {context.get('os_info', 'Unknown')}",
        title="Current Context"
    ))


def _show_help():
    """Show interactive mode help."""
    console.print(Panel(
        "[bold]Available Commands:[/bold]\n"
        "• Just type what you want to do in natural language\n"
        "• 'history' - Show recent commands\n"
        "• 'context' - Show current context\n"
        "• 'exit' or 'quit' - Exit interactive mode\n"
        "• 'help' - Show this help message",
        title="Help"
    ))


if __name__ == "__main__":
    app()
