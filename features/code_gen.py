from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress
from rich.table import Table
from rich import box
import asyncio
from typing import Optional, Dict, List
import os
import json
from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from utils.logger import setup_logger

console = Console()
logger = setup_logger()

class CodeGenerator:
    def __init__(self, config):
        try:
            self.config = config
            self.gemini_key = config.get("Gemini", "api_key")
            self.model_name = config.get("Gemini", "default_model", fallback="gemini-exp-1121")
            
            # Configure Gemini
            genai.configure(api_key=self.gemini_key)
            
            # Set generation config
            self.generation_config = GenerationConfig(
                temperature=0.7,
                top_p=1,
                top_k=1,
                max_output_tokens=8192,
            )
            
            # Initialize model
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config
            )
            
            # Start a chat
            self.chat = self.model.start_chat(history=[])
            
            logger.info(f"Successfully initialized Gemini model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error initializing CodeGenerator: {str(e)}")
            raise

    async def generate_code_with_files(self):
        """Generate code with automatic file and folder creation."""
        console.clear()
        console.print(Panel(
            "🚀 Code Generation Interface\n\n" +
            "I'll help you create and improve your project.\n" +
            "Type 'exit' to return to main menu",
            title="Code Generator",
            border_style="bright_blue"
        ))
        
        while True:
            try:
                # Get project description
                project_desc = await self._get_user_input()
                
                if project_desc.lower() == "exit":
                    break
                
                # Create project directory
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                project_dir = f"generated_project_{timestamp}"
                os.makedirs(project_dir, exist_ok=True)
                
                with Progress() as progress:
                    task1 = progress.add_task("[cyan]Planning project structure...", total=100)
                    task2 = progress.add_task("[green]Generating code...", total=100)
                    task3 = progress.add_task("[yellow]Reviewing and optimizing...", total=100)
                    
                    # Generate project structure
                    progress.update(task1, advance=50)
                    
                    structure_prompt = f"""Create a complete Python project structure for: {project_desc}
                    
                    Requirements:
                    1. Create all necessary files and directories
                    2. Include proper documentation
                    3. Follow Python best practices
                    4. Include error handling
                    5. Add unit tests
                    6. Create requirements.txt
                    7. Add a detailed README.md
                    
                    Format your response as a JSON object with this structure:
                    {{
                        "files": [
                            {{
                                "path": "relative/path/to/file",
                                "content": "file content"
                            }}
                        ],
                        "dependencies": ["package1", "package2"]
                    }}
                    
                    Rules:
                    1. Use forward slashes in paths
                    2. Include complete file contents
                    3. Add all necessary imports
                    4. Follow PEP 8 style guide
                    5. Add proper error handling
                    6. Include docstrings and comments"""
                    
                    response = await self._get_gemini_response(structure_prompt)
                    progress.update(task1, advance=50)
                    progress.update(task2, advance=30)
                    
                    try:
                        # Clean and parse JSON response
                        cleaned_response = response.replace("```json", "").replace("```", "").strip()
                        start_idx = cleaned_response.find("{")
                        end_idx = cleaned_response.rfind("}") + 1
                        if start_idx == -1 or end_idx <= 0:
                            raise ValueError("No valid JSON object found in response")
                        cleaned_response = cleaned_response[start_idx:end_idx]
                        
                        # Parse project structure
                        project_structure = json.loads(cleaned_response)
                        
                        # Validate project structure
                        if not isinstance(project_structure, dict):
                            raise ValueError("Invalid project structure format")
                        if "files" not in project_structure:
                            raise ValueError("No files specified in project structure")
                        if not isinstance(project_structure["files"], list):
                            raise ValueError("Files must be a list")
                        
                        # Create files
                        created_files = []
                        for file_info in project_structure.get("files", []):
                            if not isinstance(file_info, dict) or "path" not in file_info or "content" not in file_info:
                                logger.warning(f"Skipping invalid file info: {file_info}")
                                continue
                                
                            file_path = os.path.join(project_dir, file_info["path"])
                            try:
                                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.write(file_info["content"])
                                created_files.append(file_info["path"])
                            except Exception as e:
                                logger.error(f"Error creating file {file_path}: {str(e)}")
                                raise
                        
                        progress.update(task2, advance=40)
                        
                        # Create requirements.txt
                        if project_structure.get("dependencies"):
                            if not isinstance(project_structure["dependencies"], list):
                                raise ValueError("Dependencies must be a list")
                                
                            requirements_path = os.path.join(project_dir, "requirements.txt")
                            try:
                                with open(requirements_path, "w", encoding="utf-8") as f:
                                    for dep in project_structure["dependencies"]:
                                        if isinstance(dep, str):
                                            f.write(f"{dep}\n")
                                created_files.append("requirements.txt")
                            except Exception as e:
                                logger.error(f"Error creating requirements.txt: {str(e)}")
                                raise
                        
                        progress.update(task2, advance=30)
                        
                        # Review code
                        if created_files:
                            review_prompt = f"""Review the following Python project and suggest improvements:

                            Project Description: {project_desc}

                            Files:
                            {chr(10).join(f'=== {path} ===\n{open(os.path.join(project_dir, path)).read()}\n' for path in created_files)}

                            Provide specific suggestions for:
                            1. Code quality
                            2. Performance
                            3. Security
                            4. Best practices
                            5. Error handling"""

                            review_response = await self._get_gemini_response(review_prompt)
                            progress.update(task3, advance=100)
                            
                            # Show success message and created files
                            console.print("\n[bold green]✨ Project created successfully![/bold green]")
                            console.print(f"[cyan]Project directory: {project_dir}[/cyan]\n")
                            
                            table = Table(title="Created Files", box=box.ROUNDED)
                            table.add_column("File", style="cyan")
                            table.add_column("Status", style="green")
                            
                            for file_path in created_files:
                                table.add_row(file_path, "✓ Created")
                            
                            console.print(table)
                            
                            # Show review
                            console.print("\n[bold cyan]Code Review:[/bold cyan]")
                            console.print(Panel(Markdown(review_response), title="Suggestions", border_style="yellow"))
                        else:
                            raise ValueError("No files were created")
                        
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON response: {str(e)}")
                    except Exception as e:
                        raise Exception(f"Error creating project: {str(e)}")
                
            except Exception as e:
                logger.error(f"Code generation error: {str(e)}")
                console.print(f"[red]Error: {str(e)}[/red]")
                await asyncio.sleep(1)
    
    async def _get_gemini_response(self, prompt: str) -> str:
        """Get response from Gemini model."""
        try:
            # Add safety check for model
            if not hasattr(self, 'chat') or not self.chat:
                self.chat = self.model.start_chat(history=[])
            
            # Send message and get response
            response = self.chat.send_message(prompt)
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini")
                
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    async def _get_user_input(self) -> str:
        """Get user input with proper formatting."""
        return Prompt.ask("\n[bold blue]What would you like me to create?[/bold blue]")
