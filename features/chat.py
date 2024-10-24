from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
import asyncio
from typing import Optional
import os

from models.ai_manager import AIManager
from utils.logger import setup_logger
from utils.session_manager import SessionManager
from utils.export_manager import ExportManager

console = Console()
logger = setup_logger()

class ChatInterface:
    def __init__(self, config):
        self.config = config
        self.ai_manager = AIManager(config)
        self.conversation_history = []
        self.session_manager = SessionManager()
        self.export_manager = ExportManager()

    async def start_chat(self):
        """Start an interactive chat session with the AI."""
        console.clear()
        console.print(Panel(
            "Chat Interface - Commands:\n" +
            "/exit - Return to main menu\n" +
            "/save [name] - Save current session\n" +
            "/load - Load a previous session\n" +
            "/list - List available sessions\n" +
            "/export [format] - Export current session (txt/md/json)\n" +
            "/clear - Clear current session\n" +
            "/help - Show this help message",
            title="Chat Commands",
            style="bold blue"
        ))
        
        while True:
            try:
                user_input = await self._get_user_input()
                
                if user_input.startswith("/"):
                    if await self._handle_command(user_input):
                        continue
                    break
                
                # Add user message to history
                self.conversation_history.append({"role": "user", "content": user_input})
                
                # Get AI response
                response = await self.ai_manager.get_chat_response(
                    self.conversation_history
                )
                
                # Add AI response to history
                self.conversation_history.append({"role": "assistant", "content": response})
                
                # Display response
                md = Markdown(response)
                console.print(Panel(md, style="green", title="AI Response"))
                
            except Exception as e:
                logger.error(f"Chat error: {str(e)}")
                console.print(f"[red]Error: {str(e)}[/red]")
                await asyncio.sleep(1)
    
    async def _get_user_input(self) -> str:
        """Get user input with proper formatting."""
        return Prompt.ask("[bold blue]You[/bold blue]")
    
    async def _handle_command(self, command: str) -> bool:
        """Handle chat commands. Returns False if should exit chat."""
        try:
            cmd_parts = command.split()
            cmd = cmd_parts[0].lower()
            
            if cmd == "/exit":
                return False
            
            elif cmd == "/save":
                name = cmd_parts[1] if len(cmd_parts) > 1 else None
                filename = self.session_manager.save_session(self.conversation_history, name)
                console.print(f"[green]Session saved as: {filename}[/green]")
            
            elif cmd == "/load":
                self.session_manager.display_sessions()
                filename = Prompt.ask("Enter session filename to load")
                self.conversation_history = self.session_manager.load_session(filename)
                console.print("[green]Session loaded successfully![/green]")
                
                # Display last few messages for context
                console.print("\n[yellow]Recent messages from loaded session:[/yellow]")
                last_messages = self.conversation_history[-3:]  # Show last 3 messages
                for msg in last_messages:
                    role_style = "blue" if msg["role"] == "user" else "green"
                    console.print(f"[{role_style}]{msg['role'].title()}:[/{role_style}]")
                    console.print(Markdown(msg["content"]))
                    console.print()
            
            elif cmd == "/list":
                self.session_manager.display_sessions()
            
            elif cmd == "/export":
                if not self.conversation_history:
                    console.print("[yellow]No messages to export in current session[/yellow]")
                    return True
                
                export_format = "md"
                if len(cmd_parts) > 1 and cmd_parts[1] in ["txt", "md", "json"]:
                    export_format = cmd_parts[1]
                
                # Use the new ExportManager for better formatted exports
                filename = self.export_manager.export_conversation(
                    self.conversation_history,
                    export_format=export_format,
                    name="chat"
                )
                console.print(f"[green]Session exported to: {filename}[/green]")
            
            elif cmd == "/clear":
                if Prompt.ask("Are you sure you want to clear the current session?", choices=["y", "n"]) == "y":
                    self.conversation_history = []
                    console.print("[green]Session cleared![/green]")
            
            elif cmd == "/help":
                console.print(Panel(
                    "Available Commands:\n" +
                    "/exit - Return to main menu\n" +
                    "/save [name] - Save current session\n" +
                    "/load - Load a previous session\n" +
                    "/list - List available sessions\n" +
                    "/export [format] - Export current session (txt/md/json)\n" +
                    "/clear - Clear current session\n" +
                    "/help - Show this help message",
                    title="Chat Commands",
                    style="bold blue"
                ))
            
            else:
                console.print("[yellow]Unknown command. Type /help for available commands.[/yellow]")
            
            return True
            
        except Exception as e:
            logger.error(f"Command error: {str(e)}")
            console.print(f"[red]Error executing command: {str(e)}[/red]")
            return True
