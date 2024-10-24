from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
import asyncio
from typing import List, Dict, Any
import os

from utils.logger import setup_logger
from utils.export_manager import ExportManager

console = Console()
logger = setup_logger()

class ArxivSearch:
    def __init__(self, config):
        self.config = config
        self.export_manager = ExportManager()
        self.results_per_page = int(config.get("ArXiv", "results_per_page", fallback="10"))
        self.current_results = []
        self.current_query = ""

    async def search(self):
        """Search arXiv papers."""
        console.clear()
        console.print(Panel(
            "arXiv Search Interface - Commands:\n" +
            "/exit - Return to main menu\n" +
            "/export [format] - Export results (txt/md/json)\n" +
            "/help - Show this help message",
            title="arXiv Search Commands",
            style="bold blue"
        ))
        
        while True:
            try:
                # Get search query
                query = await self._get_user_input()
                
                if query.startswith("/"):
                    if await self._handle_command(query):
                        continue
                    break
                
                self.current_query = query
                
                # For now, use placeholder results
                self.current_results = [
                    {
                        "title": "Sample Paper 1",
                        "authors": ["Author A", "Author B"],
                        "abstract": "This is a sample paper abstract.",
                        "url": "https://arxiv.org/abs/sample.1234"
                    }
                ]
                
                # Display results
                console.print(Panel("Search Results:", style="cyan"))
                for result in self.current_results:
                    console.print(Panel(
                        f"[bold]{result['title']}[/bold]\n" +
                        f"Authors: {', '.join(result['authors'])}\n" +
                        f"URL: {result['url']}\n\n" +
                        f"Abstract: {result['abstract']}",
                        style="green"
                    ))
                
            except Exception as e:
                logger.error(f"arXiv search error: {str(e)}")
                console.print(f"[red]Error: {str(e)}[/red]")
                await asyncio.sleep(1)
    
    async def _get_user_input(self) -> str:
        """Get user input with proper formatting."""
        return Prompt.ask("[bold blue]Enter arXiv search query or command[/bold blue]")
    
    async def _handle_command(self, command: str) -> bool:
        """Handle search commands. Returns False if should exit search."""
        try:
            cmd_parts = command.split()
            cmd = cmd_parts[0].lower()
            
            if cmd == "/exit":
                return False
            
            elif cmd == "/export":
                if not self.current_results:
                    console.print("[yellow]No results to export[/yellow]")
                    return True
                
                export_format = "md"
                if len(cmd_parts) > 1 and cmd_parts[1] in ["txt", "md", "json"]:
                    export_format = cmd_parts[1]
                
                filename = self.export_manager.export_search_results(
                    self.current_results,
                    "arxiv",
                    self.current_query,
                    export_format
                )
                console.print(f"[green]Results exported to: {filename}[/green]")
            
            elif cmd == "/help":
                console.print(Panel(
                    "Available Commands:\n" +
                    "/exit - Return to main menu\n" +
                    "/export [format] - Export results (txt/md/json)\n" +
                    "/help - Show this help message",
                    title="arXiv Search Commands",
                    style="bold blue"
                ))
            
            else:
                console.print("[yellow]Unknown command. Type /help for available commands.[/yellow]")
            
            return True
            
        except Exception as e:
            logger.error(f"Command error: {str(e)}")
            console.print(f"[red]Error executing command: {str(e)}[/red]")
            return True
