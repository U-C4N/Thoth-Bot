from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from typing import List
from rich import box

console = Console()

def create_header(title: str) -> Panel:
    """Create a header panel."""
    return Panel(title, style="bold blue")

def create_menu(plugins: list = None) -> Panel:
    """Create the main menu panel."""
    table = Table(box=box.ROUNDED, show_header=False, show_edge=False)
    table.add_column("Option", style="cyan")
    table.add_column("Description", style="green")
    
    # Add main menu options
    table.add_row("1", "Chat with AI")
    table.add_row("2", "Generate Code")
    table.add_row("3", "Web Search")
    table.add_row("4", "ArXiv Search")
    table.add_row("5", "Settings")
    table.add_row("q", "Quit")
    
    return Panel(table, title="Main Menu", border_style="blue")

def create_error_panel(message: str) -> Panel:
    """Create an error message panel."""
    return Panel(
        Text(message, style="red"),
        title="Error",
        border_style="red",
        padding=(1, 2)
    )

def create_success_panel(message: str) -> Panel:
    """Create a success message panel."""
    return Panel(
        Text(message, style="green"),
        title="Success",
        border_style="green",
        padding=(1, 2)
    )
