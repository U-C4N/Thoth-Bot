import asyncio
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout

from utils.config_manager import ConfigManager
from utils.logger import setup_logger
from utils.rich_components import create_header, create_menu
from features.chat import ChatInterface
from features.code_gen import CodeGenerator
from features.web_search import WebSearch
from features.arxiv_search import ArxivSearch
from features.settings import SettingsManager
from plugins import PluginManager

console = Console()
logger = setup_logger()

class AIAssistant:
    def __init__(self):
        self.config = ConfigManager()
        self.plugin_manager = PluginManager(self.config)
        self.chat = ChatInterface(self.config)
        self.code_gen = CodeGenerator(self.config)
        self.web_search = WebSearch(self.config)
        self.arxiv = ArxivSearch(self.config)
        self.settings = SettingsManager(self.config)
        self.running = True

    async def initialize(self):
        """Initialize the assistant and discover plugins."""
        await self.plugin_manager.discover_plugins()
        logger.info(f"Loaded plugins: {self.plugin_manager.list_plugins()}")

    async def main_menu(self):
        while self.running:
            try:
                console.clear()
                header = create_header("AI Assistant")
                menu = create_menu(self.plugin_manager.list_plugins())
                
                console.print(header)
                console.print(menu)

                # Add plugin options to choices
                choices = ["1", "2", "3", "4", "5", "6", "q"]
                plugin_choices = [str(i) for i in range(7, 7 + len(self.plugin_manager.list_plugins()))]
                choices.extend(plugin_choices)

                choice = Prompt.ask("Select an option", choices=choices)
                
                if choice == "1":
                    await self.chat.start_chat()
                elif choice == "2":
                    await self.code_gen.generate_code_with_files()
                elif choice == "3":
                    await self.web_search.search()
                elif choice == "4":
                    await self.arxiv.search()
                elif choice == "5":
                    await self.settings.manage_settings()
                elif choice == "6":
                    console.clear()
                    console.print(Panel("Help and Documentation", style="bold green"))
                elif choice in plugin_choices:
                    # Execute plugin
                    plugin_index = int(choice) - 7
                    plugin_name = self.plugin_manager.list_plugins()[plugin_index]
                    plugin = self.plugin_manager.get_plugin(plugin_name)
                    if plugin:
                        try:
                            # Get plugin parameters
                            if plugin_name == "CalculatorPlugin":
                                operation = Prompt.ask(
                                    "Enter operation", 
                                    choices=["add", "subtract", "multiply", "divide"]
                                )
                                numbers = []
                                while True:
                                    num = Prompt.ask("Enter number (or 'done' to finish)")
                                    if num.lower() == 'done':
                                        break
                                    try:
                                        numbers.append(float(num))
                                    except ValueError:
                                        console.print("[red]Invalid number, try again[/red]")
                                        continue
                                
                                if numbers:
                                    result = await plugin.execute(operation, *numbers)
                                else:
                                    result = {"status": "error", "message": "No numbers provided"}
                            else:
                                result = await plugin.execute()
                                
                            if isinstance(result, dict) and result.get("status") == "error":
                                console.print(Panel(
                                    f"[red]Error: {result.get('message', 'Unknown error')}[/red]",
                                    title=f"Plugin: {plugin_name}"
                                ))
                            else:
                                console.print(Panel(
                                    str(result), 
                                    title=f"Plugin: {plugin_name}",
                                    style="green"
                                ))
                            await asyncio.sleep(2)
                        except Exception as e:
                            console.print(f"[red]Plugin error: {str(e)}[/red]")
                            await asyncio.sleep(2)
                elif choice.lower() == "q":
                    self.running = False
                    console.print("Goodbye!", style="bold blue")
                    break

            except Exception as e:
                logger.error(f"Main menu error: {str(e)}")
                console.print(f"[red]Error: {str(e)}[/red]")
                await asyncio.sleep(2)

async def main():
    assistant = AIAssistant()
    await assistant.initialize()
    await assistant.main_menu()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\nExiting gracefully...", style="bold yellow")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        console.print(f"[red]Fatal error: {str(e)}[/red]")
