from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
import asyncio
from typing import List, Dict, Any
import os
from crewai import Agent, Task, Crew, Process
from tavily import TavilyClient
from langchain.tools import Tool
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from utils.logger import setup_logger
from utils.export_manager import ExportManager

console = Console()
logger = setup_logger()

class WebSearch:
    def __init__(self, config):
        self.config = config
        self.export_manager = ExportManager()
        self.current_results = []
        self.current_query = ""
        
        # Initialize Tavily client
        tavily_api_key = config.get("Tavily", "api_key")
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        
        # Get AI provider and model
        self.provider = config.get("DEFAULT", "ai_provider")
        self.model = config.get(self.provider.title(), "default_model")
        
        # Initialize language model
        self.llm = self._initialize_llm()
        
        # Create search tool
        self.search_tool = Tool(
            name="web_search",
            func=self._search_with_validation,
            description="Search the web for accurate and relevant information"
        )
        
        # Initialize CrewAI agents
        self.agents = self._create_agents()

    def _initialize_llm(self):
        """Initialize the appropriate language model based on config."""
        if self.provider == "groq":
            return ChatGroq(
                groq_api_key=self.config.get("Groq", "api_key"),
                model_name=self.model
            )
        elif self.provider == "openai":
            return ChatOpenAI(
                api_key=self.config.get("OpenAI", "api_key"),
                model_name=self.model
            )
        elif self.provider == "anthropic":
            return ChatAnthropic(
                api_key=self.config.get("Anthropic", "api_key"),
                model_name=self.model
            )
        elif self.provider == "gemini":
            return ChatGoogleGenerativeAI(
                api_key=self.config.get("Gemini", "api_key"),
                model_name=self.model
            )

    def _search_with_validation(self, query: str) -> List[Dict]:
        """Perform search with input validation."""
        if not isinstance(query, str):
            raise ValueError("Search query must be a string")
        try:
            results = self.tavily_client.search(query=query)
            return results.get("results", [])
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []

    def _create_agents(self):
        """Create specialized agents for different search tasks."""
        return {
            "researcher": Agent(
                role='Research Specialist',
                goal='Find and analyze relevant information efficiently',
                backstory="""Expert researcher who finds accurate information quickly and 
                presents it in a clear, organized manner. Focuses on relevance and accuracy.
                Evaluates source credibility and cross-references information.""",
                tools=[self.search_tool],
                llm=self.llm,
                verbose=True
            ),
            
            "synthesizer": Agent(
                role='Information Synthesizer',
                goal='Create concise, accurate summaries with high confidence',
                backstory="""Expert at analyzing and combining information into clear, 
                actionable summaries. Focuses on verification and relevance. 
                Presents information in a structured, easy-to-understand format.""",
                llm=self.llm,
                verbose=True
            )
        }

    async def search(self):
        """Perform web search using CrewAI agents."""
        console.clear()
        console.print(Panel(
            "Web Search Interface - Commands:\n" +
            "/exit - Return to main menu\n" +
            "/export [format] - Export results (txt/md/json)\n" +
            "/help - Show this help message",
            title="Web Search Commands",
            style="bold blue"
        ))
        
        while True:
            try:
                query = await self._get_user_input()
                
                if query.startswith("/"):
                    if await self._handle_command(query):
                        continue
                    break
                
                self.current_query = query
                
                # Create sequential research tasks
                research_task = Task(
                    description=f"""Research query: {query}
                    1. Search for accurate information from reliable sources
                    2. Cross-reference findings across multiple sources
                    3. Rate source reliability (professional > social media)
                    4. Identify key verified information""",
                    expected_output="""Structured research findings with:
                    - Key verified information
                    - Source reliability assessment
                    - Cross-referenced facts""",
                    agent=self.agents["researcher"]
                )

                synthesis_task = Task(
                    description="""Create final summary:
                    1. Combine verified information
                    2. Structure information by importance
                    3. Present clear, concise summary""",
                    expected_output="""Concise summary with:
                    - Key verified findings
                    - Confidence level
                    - Structured presentation""",
                    agent=self.agents["synthesizer"],
                    context=[research_task]
                )

                # Create and run the crew
                crew = Crew(
                    agents=list(self.agents.values()),
                    tasks=[research_task, synthesis_task],
                    verbose=True,
                    process=Process.sequential
                )

                with console.status("[bold green]Researching and analyzing...[/bold green]"):
                    result = await asyncio.to_thread(crew.kickoff)
                
                # Process and store results
                if isinstance(result, str):
                    self.current_results = [{
                        'title': 'Web Search Results',
                        'url': f'Query: {query}',
                        'summary': result
                    }]
                    
                    # Display results
                    console.print(Panel("Search Results:", style="cyan"))
                    console.print(Panel(
                        Markdown(result),
                        style="green"
                    ))
                else:
                    raise ValueError("Invalid result format from crew")
                
            except Exception as e:
                logger.error(f"Web search error: {str(e)}")
                console.print(f"[red]Error: {str(e)}[/red]")
                await asyncio.sleep(1)

    async def _get_user_input(self) -> str:
        """Get user input with proper formatting."""
        return Prompt.ask("[bold blue]Enter search query or command[/bold blue]")
    
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
                    "web",
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
                    title="Web Search Commands",
                    style="bold blue"
                ))
            
            else:
                console.print("[yellow]Unknown command. Type /help for available commands.[/yellow]")
            
            return True
            
        except Exception as e:
            logger.error(f"Command error: {str(e)}")
            console.print(f"[red]Error executing command: {str(e)}[/red]")
            return True
