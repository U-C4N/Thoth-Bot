from rich.console import Console
from rich.prompt import Prompt, FloatPrompt, IntPrompt
from rich.panel import Panel
from rich.table import Table
import asyncio

from utils.logger import setup_logger
from models.model_config import ModelConfigManager, ModelConfig

console = Console()
logger = setup_logger()

class SettingsManager:
    def __init__(self, config):
        self.config = config
        self.model_config = ModelConfigManager(config)

    async def manage_settings(self):
        """Manage application settings."""
        console.clear()
        while True:
            try:
                self._display_settings_menu()
                choice = Prompt.ask(
                    "Select an option", 
                    choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "b"]
                )
                
                if choice == "1":
                    await self._manage_openai_settings()
                elif choice == "2":
                    await self._manage_anthropic_settings()
                elif choice == "3":
                    await self._manage_groq_settings()
                elif choice == "4":
                    await self._manage_gemini_settings()
                elif choice == "5":
                    await self._manage_arxiv_settings()
                elif choice == "6":
                    await self._manage_logging_settings()
                elif choice == "7":
                    await self._manage_default_provider()
                elif choice == "8":
                    await self._view_current_settings()
                elif choice == "9":
                    await self._manage_model_configs()
                elif choice.lower() == "b":
                    break
                    
            except Exception as e:
                logger.error(f"Settings management error: {str(e)}")
                console.print(f"[red]Error: {str(e)}[/red]")
                await asyncio.sleep(1)

    def _display_settings_menu(self):
        """Display the settings menu."""
        menu_table = Table(show_header=False, box=None)
        menu_table.add_column("Option", style="cyan")
        menu_table.add_column("Description", style="white")
        
        menu_items = [
            ("1", "OpenAI Settings"),
            ("2", "Anthropic Settings"),
            ("3", "Groq Settings"),
            ("4", "Gemini Settings"),
            ("5", "arXiv Settings"),
            ("6", "Logging Settings"),
            ("7", "Default AI Provider"),
            ("8", "View Current Settings"),
            ("9", "Model Configurations"),
            ("b", "Back to Main Menu")
        ]
        
        for option, description in menu_items:
            menu_table.add_row(f"[{option}]", description)
        
        console.print(Panel(menu_table, title="Settings Menu", border_style="cyan"))

    async def _manage_openai_settings(self):
        """Manage OpenAI-specific settings."""
        api_key = Prompt.ask("Enter OpenAI API Key", 
                           default=self.config.get("OpenAI", "api_key"))
        model = Prompt.ask("Enter Default Model", 
                         default=self.config.get("OpenAI", "default_model"))
        
        self.config.set("OpenAI", "api_key", api_key)
        self.config.set("OpenAI", "default_model", model)
        console.print("[green]OpenAI settings updated successfully![/green]")
        await asyncio.sleep(1)

    async def _manage_anthropic_settings(self):
        """Manage Anthropic-specific settings."""
        api_key = Prompt.ask("Enter Anthropic API Key", 
                           default=self.config.get("Anthropic", "api_key"))
        model = Prompt.ask("Enter Default Model", 
                         default=self.config.get("Anthropic", "default_model"))
        
        self.config.set("Anthropic", "api_key", api_key)
        self.config.set("Anthropic", "default_model", model)
        console.print("[green]Anthropic settings updated successfully![/green]")
        await asyncio.sleep(1)

    async def _manage_groq_settings(self):
        """Manage Groq-specific settings."""
        api_key = Prompt.ask("Enter Groq API Key", 
                           default=self.config.get("Groq", "api_key"))
        model = Prompt.ask("Enter Default Model", 
                         default=self.config.get("Groq", "default_model"))
        
        self.config.set("Groq", "api_key", api_key)
        self.config.set("Groq", "default_model", model)
        console.print("[green]Groq settings updated successfully![/green]")
        await asyncio.sleep(1)

    async def _manage_gemini_settings(self):
        """Manage Gemini-specific settings."""
        api_key = Prompt.ask("Enter Gemini API Key", 
                           default=self.config.get("Gemini", "api_key"))
        model = Prompt.ask("Enter Default Model", 
                         default=self.config.get("Gemini", "default_model"))
        
        self.config.set("Gemini", "api_key", api_key)
        self.config.set("Gemini", "default_model", model)
        console.print("[green]Gemini settings updated successfully![/green]")
        await asyncio.sleep(1)

    async def _manage_arxiv_settings(self):
        """Manage arXiv-specific settings."""
        results = Prompt.ask("Enter Results Per Page", 
                           default=self.config.get("ArXiv", "results_per_page"))
        
        self.config.set("ArXiv", "results_per_page", results)
        console.print("[green]arXiv settings updated successfully![/green]")
        await asyncio.sleep(1)

    async def _manage_logging_settings(self):
        """Manage logging settings."""
        log_level = Prompt.ask("Enter Log Level (INFO/DEBUG/WARNING/ERROR)", 
                             default=self.config.get("DEFAULT", "log_level"))
        log_file = Prompt.ask("Enter Log File Path", 
                            default=self.config.get("DEFAULT", "log_file"))
        
        self.config.set("DEFAULT", "log_level", log_level)
        self.config.set("DEFAULT", "log_file", log_file)
        console.print("[green]Logging settings updated successfully![/green]")
        await asyncio.sleep(1)

    async def _manage_default_provider(self):
        """Manage default AI provider."""
        providers = ["openai", "anthropic", "groq", "gemini"]
        current = self.config.get("DEFAULT", "ai_provider")
        provider = Prompt.ask(
            "Select Default AI Provider",
            choices=providers,
            default=current
        )
        
        self.config.set("DEFAULT", "ai_provider", provider)
        console.print("[green]Default AI provider updated successfully![/green]")
        await asyncio.sleep(1)

    async def _view_current_settings(self):
        """View all current settings."""
        sections = ["DEFAULT", "OpenAI", "Anthropic", "Groq", "Gemini", "ArXiv"]
        settings_table = Table(title="Current Settings")
        settings_table.add_column("Section", style="cyan")
        settings_table.add_column("Setting", style="green")
        settings_table.add_column("Value", style="yellow")
        
        for section in sections:
            settings = self.config.get_section(section)
            for key, value in settings.items():
                # Mask API keys
                if "api_key" in key.lower():
                    value = "*" * len(value)
                settings_table.add_row(section, key, value)
        
        # Add model configurations
        for provider in ["openai", "anthropic", "groq", "gemini"]:
            models = self.model_config.get_available_models(provider)
            for model_name in models[provider]:
                try:
                    config = self.model_config.get_model_config(provider, model_name)
                    settings_table.add_row(
                        f"Models.{provider}",
                        model_name,
                        f"max_tokens={config.max_tokens}, temp={config.temperature}"
                    )
                except ValueError:
                    continue
        
        console.print(settings_table)
        await asyncio.sleep(3)

    async def _manage_model_configs(self):
        """Manage AI model configurations."""
        while True:
            console.clear()
            console.print(Panel("Model Configuration Management", style="cyan"))
            
            # Display available models
            table = Table(title="Available Models")
            table.add_column("Provider", style="cyan")
            table.add_column("Model", style="green")
            
            models = self.model_config.get_available_models()
            for provider, model_list in models.items():
                for model in model_list:
                    table.add_row(provider, model)
            
            console.print(table)
            
            # Get user input
            provider = Prompt.ask(
                "Enter provider (or 'b' to go back)",
                choices=list(models.keys()) + ['b']
            )
            
            if provider.lower() == 'b':
                break
                
            model_name = Prompt.ask(
                "Enter model name",
                choices=models[provider]
            )
            
            # Get current config
            try:
                current_config = self.model_config.get_model_config(provider, model_name)
            except ValueError:
                current_config = ModelConfig(
                    name=model_name,
                    provider=provider
                )
            
            # Get new configuration
            max_tokens = IntPrompt.ask(
                "Enter max tokens (optional)",
                default=str(current_config.max_tokens or '')
            )
            temperature = FloatPrompt.ask(
                "Enter temperature (0.0-1.0)",
                default=str(current_config.temperature)
            )
            top_p = FloatPrompt.ask(
                "Enter top_p (0.0-1.0)",
                default=str(current_config.top_p)
            )
            presence_penalty = FloatPrompt.ask(
                "Enter presence penalty (-2.0-2.0)",
                default=str(current_config.presence_penalty)
            )
            frequency_penalty = FloatPrompt.ask(
                "Enter frequency penalty (-2.0-2.0)",
                default=str(current_config.frequency_penalty)
            )
            context_window = IntPrompt.ask(
                "Enter context window size (optional)",
                default=str(current_config.context_window or '')
            )
            
            # Create and save new configuration
            new_config = ModelConfig(
                name=model_name,
                provider=provider,
                max_tokens=max_tokens if max_tokens else None,
                temperature=temperature,
                top_p=top_p,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                context_window=context_window if context_window else None
            )
            
            self.model_config.set_model_config(new_config)
            console.print(f"[green]Configuration for {provider}/{model_name} updated successfully![/green]")
            await asyncio.sleep(1)
