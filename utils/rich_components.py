from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from typing import List

console = Console()

def create_header(title: str) -> Panel:
    """Create a stylized header panel."""
    return Panel(
        Text(title, justify="center", style="bold blue"),
        border_style="blue",
        padding=(1, 2)
    )

def create_menu(plugins: List[str] = None) -> Panel:
    """Create the main menu panel."""
    menu_table = Table(show_header=False, show_edge=False, box=None)
    menu_table.add_column("Option", style="cyan")
    menu_table.add_column("Description", style="white")
    
    menu_items = [
        ("1", "Chat with AI"),
        ("2", "Generate Code"),
        ("3", "Web Search"),
        ("4", "ArXiv Search"),
        ("5", "Settings"),
        ("6", "Help"),
        ("q", "Quit")
    ]
    
    # Add plugin options
    if plugins:
        for i, plugin in enumerate(plugins, start=7):
            menu_items.append((str(i), f"Plugin: {plugin}"))
    
    for option, description in menu_items:
        menu_table.add_row(f"[{option}]", description)
    
    return Panel(
        menu_table,
        title="Main Menu",
        border_style="cyan",
        padding=(1, 2)
    )

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
