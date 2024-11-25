import asyncio
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.style import Style
from rich.text import Text
from rich import box
from typing import List

from utils.config_manager import ConfigManager
from utils.logger import setup_logger
from utils.rich_components import create_header, create_menu
from features.chat import ChatInterface
from features.code_gen import CodeGenerator
from features.arxiv_search import ArxivSearch
from features.settings import SettingsManager

console = Console()
logger = setup_logger()

class AIAssistant:
    def __init__(self):
        self.config = ConfigManager()
        self.chat = ChatInterface(self.config)
        self.code_gen = CodeGenerator(self.config)
        self.arxiv = ArxivSearch(self.config)
        self.settings = SettingsManager(self.config)
        self.running = True

    async def main_menu(self):
        while self.running:
            try:
                console.clear()
                header = create_header("AI Assistant")
                menu = create_menu([])  # Empty plugin list
                
                console.print(header)
                console.print(menu)

                choices = ["1", "2", "3", "4", "5", "q"]

                try:
                    choice = Prompt.ask("Select an option", choices=choices)
                except KeyboardInterrupt:
                    console.print("\nExiting to main menu...", style="bold yellow")
                    continue
                
                if choice == "1":
                    await self.chat.start_chat()
                elif choice == "2":
                    await self.code_gen.generate_code_with_files()
                elif choice == "3":
                    pass
                elif choice == "4":
                    await self.arxiv.search()
                elif choice == "5":
                    await self.settings.manage_settings()
                elif choice.lower() == "q":
                    self.running = False
                    console.print("Goodbye!", style="bold blue")
                    break

            except KeyboardInterrupt:
                console.print("\nExiting program...", style="bold yellow")
                self.running = False
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                await asyncio.sleep(2)

async def main():
    assistant = AIAssistant()
    await assistant.main_menu()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\nExiting gracefully...", style="bold yellow")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        console.print(f"[red]Fatal error: {str(e)}[/red]")
