"""Command-line interface for SSH Tools MCP."""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from .client import SSHClient

app = typer.Typer(help="SSH Tools for MCP servers")
console = Console()

@app.command()
def connect(
    hostname: str = typer.Argument(..., help="Remote host to connect to"),
    username: str = typer.Argument(..., help="Username to authenticate as"),
    port: int = typer.Option(22, help="SSH port"),
    password: Optional[str] = typer.Option(None, help="Password for authentication"),
    key_file: Optional[str] = typer.Option(None, help="Path to private key file"),
    command: Optional[str] = typer.Option(None, help="Command to execute")
):
    """Connect to a remote host and optionally execute a command."""
    try:
        with SSHClient(hostname, username, port) as client:
            client.connect(password=password, key_filename=key_file)
            
            if command:
                result = client.execute_command(command)
                
                if result["return_code"] == 0:
                    if result["stdout"]:
                        console.print(result["stdout"])
                else:
                    console.print(f"[red]Error:[/red] {result['stderr']}")
                    raise typer.Exit(1)
            else:
                console.print(f"[green]Successfully connected to {hostname}[/green]")
                
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

def main():
    """Main entry point for the CLI."""
    app()