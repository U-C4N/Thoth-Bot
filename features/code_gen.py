from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
import asyncio
from typing import Optional
import os
from datetime import datetime

from models.ai_manager import AIManager
from utils.logger import setup_logger

console = Console()
logger = setup_logger()

class CodeGenerator:
    def __init__(self, config):
        self.config = config
        self.ai_manager = AIManager(config)

    async def generate_code_with_files(self):
        """Generate code and automatically create necessary files and folders."""
        console.clear()
        console.print(Panel(
            "Code Generation Interface\n" +
            "Describe what you want to create, including:\n" +
            "- Project structure\n" +
            "- File contents\n" +
            "- Dependencies\n" +
            "Type 'exit' to return to main menu",
            title="Code Generation",
            style="bold blue"
        ))

        while True:
            try:
                user_input = Prompt.ask("\n[bold blue]Enter your request[/bold blue]")
                
                if user_input.lower() == "exit":
                    break

                # Show thinking message
                with console.status("[bold green]Generating code structure...[/bold green]"):
                    # Get AI response with file structure and contents
                    response = await self.ai_manager.get_code_response(user_input)
                
                # Display the raw AI response first
                console.print(Panel(
                    Markdown(f"```\n{response}\n```"),
                    title="AI Response",
                    style="cyan"
                ))

                # Ask for confirmation
                if Prompt.ask(
                    "\n[bold yellow]Do you want to create these files and folders?[/bold yellow]",
                    choices=["yes", "no"],
                    default="no"
                ) == "yes":
                    # Parse the response and create files
                    structure = self._parse_file_structure(response)
                    
                    # Generate project name automatically
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = "new_project"
                    project_name = f"{base_name}_{timestamp}"
                    
                    # Create the project directory
                    os.makedirs(project_name, exist_ok=True)
                    console.print(f"[green]Created project directory: {project_name}[/green]")
                    
                    # Create folders
                    for folder in structure['folders']:
                        folder_path = os.path.join(project_name, folder)
                        os.makedirs(folder_path, exist_ok=True)
                        console.print(f"[green]Created folder: {folder_path}[/green]")

                    # Create files
                    for file_info in structure['files']:
                        file_path = os.path.join(project_name, file_info['path'])
                        # Ensure parent directory exists
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        
                        # Skip empty files
                        if not file_info['content'].strip():
                            console.print(f"[yellow]Skipping empty file: {file_path}[/yellow]")
                            continue
                        
                        # Write file content
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(file_info['content'].strip() + '\n')
                        console.print(f"[green]Created file: {file_path}[/green]")

                    console.print(Panel(
                        f"[bold green]Project structure created successfully in '{project_name}' directory![/bold green]",
                        style="green"
                    ))
                
            except Exception as e:
                logger.error(f"Code generation error: {str(e)}")
                console.print(f"[red]Error: {str(e)}[/red]")
                await asyncio.sleep(1)

    def _parse_file_structure(self, ai_response: str) -> dict:
        """Parse AI response to extract folder and file information."""
        structure = {
            'folders': set(),  # Using set to avoid duplicates
            'files': []
        }

        current_file = None
        lines = ai_response.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('FOLDER:'):
                folder_path = line.replace('FOLDER:', '').strip()
                # Add folder and any parent folders
                parts = folder_path.split('/')
                current_path = ""
                for part in parts:
                    if part:
                        current_path = os.path.join(current_path, part)
                        structure['folders'].add(current_path)
                        
            elif line.startswith('FILE:'):
                if current_file:
                    structure['files'].append(current_file)
                file_path = line.replace('FILE:', '').strip()
                current_file = {'path': file_path, 'content': ''}
                # Add the file's directory to folders
                file_dir = os.path.dirname(file_path)
                if file_dir:
                    structure['folders'].add(file_dir)
                
                # Collect content until next FILE: or FOLDER: or end
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith('FILE:') or next_line.startswith('FOLDER:'):
                        i -= 1  # Back up one line to process the marker
                        break
                    current_file['content'] += lines[i] + '\n'
                    i += 1
            i += 1

        if current_file:
            structure['files'].append(current_file)

        # Convert folders set to sorted list
        structure['folders'] = sorted(structure['folders'])
        return structure

    async def generate_code(self):
        """Generate single file code using AI."""
        console.clear()
        console.print(Panel("Code Generation Interface - Type 'exit' to return to main menu", 
                          style="bold blue"))
        
        while True:
            try:
                prompt = await self._get_user_input()
                
                if prompt.lower() == "exit":
                    break
                
                code = await self.ai_manager.generate_code(prompt)
                md = Markdown(f"```python\n{code}\n```")
                console.print(Panel(md, style="green", title="Generated Code"))
                
            except Exception as e:
                logger.error(f"Code generation error: {str(e)}")
                console.print(f"[red]Error: {str(e)}[/red]")
                await asyncio.sleep(1)
    
    async def _get_user_input(self) -> str:
        """Get user input with proper formatting."""
        return Prompt.ask("[bold blue]Enter code generation prompt[/bold blue]")
