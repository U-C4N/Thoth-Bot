from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
import asyncio
import aiohttp
import json
from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
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
        
        # Get Serper API key
        self.serper_api_key = config.get("Serper", "api_key")
        
        # Get AI provider and model
        self.provider = config.get("DEFAULT", "ai_provider")
        self.model = config.get(self.provider.title(), "default_model")
        
        # Initialize language model
        self.llm = self._initialize_llm()
        
        # Create search tool
        self.search_tool = Tool(
            name="web_search",
            func=self._search_with_serper,
            description="Search the web using Serper.dev API"
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

    async def _search_with_serper(self, query: str) -> List[Dict]:
        """Perform search using Serper.dev API."""
        if not isinstance(query, str):
            raise ValueError("Search query must be a string")
            
        try:
            url = "https://google.serper.dev/search"
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            payload = json.dumps({"q": query})

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Extract organic results
                        results = []
                        if 'organic' in data:
                            for item in data['organic']:
                                results.append({
                                    'title': item.get('title', ''),
                                    'link': item.get('link', ''),
                                    'snippet': item.get('snippet', ''),
                                    'position': item.get('position', 0)
                                })
                        return results
                    else:
                        logger.error(f"Serper API error: {response.status}")
                        return []
                        
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
        try:
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
                    
                    # Perform direct search first
                    with console.status("[bold green]Searching...[/bold green]"):
                        results = await self._search_with_serper(query)
                    
                    if results:
                        # Store results
                        self.current_results = results
                        
                        # Display direct search results
                        console.print(Panel("Direct Search Results:", style="cyan"))
                        for result in results[:5]:  # Show top 5 results
                            console.print(Panel(
                                f"[bold]{result['title']}[/bold]\n" +
                                f"[blue]{result['link']}[/blue]\n\n" +
                                f"{result['snippet']}",
                                style="green"
                            ))
                    
                    # AI Analysis (optional - user can choose)
                    if Prompt.ask(
                        "\nWould you like an AI analysis of these results?",
                        choices=["y", "n"],
                        default="n"
                    ) == "y":
                        with console.status("[bold green]Analyzing results...[/bold green]"):
                            analysis = await self._analyze_results(results, query)
                        
                        console.print(Panel("AI Analysis:", style="cyan"))
                        console.print(Panel(
                            Markdown(analysis),
                            style="green"
                        ))
                
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}[/red]")
                    await asyncio.sleep(1)
        except KeyboardInterrupt:
            console.print("\nExiting web search...", style="bold yellow")

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

    async def _analyze_results(self, results: List[Dict], query: str) -> str:
        """Analyze search results using AI."""
        # Create a simple researcher agent
        researcher = Agent(
            role='Research Specialist',
            goal='Analyze search results and provide a concise summary',
            backstory="""Expert at analyzing information and providing clear summaries. 
            Only reports facts that are explicitly stated in the search results.""",
            llm=self.llm,
            verbose=True
        )
        
        # Format results for analysis
        formatted_results = "\n\n".join([
            f"Source: {result['title']}\nURL: {result['link']}\nContent: {result['snippet']}"
            for result in results
        ])
        
        # Create analysis task
        task = Task(
            description=f"""Analyze these search results for query: {query}

Search Results:
{formatted_results}

Guidelines:
1. Only include information explicitly stated in the results
2. Do not make assumptions or inferences
3. Cite the source for each piece of information
4. If information conflicts, note the discrepancy
5. Indicate confidence level based on source reliability""",
            expected_output="""A concise summary containing:
            - Verified facts from the search results
            - Source citations
            - Confidence level with explanation""",
            agent=researcher
        )
        
        # Run analysis
        crew = Crew(
            agents=[researcher],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )
        
        return await asyncio.to_thread(crew.kickoff)
