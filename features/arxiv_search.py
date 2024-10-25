import arxiv
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
import asyncio
from typing import List, Dict, Any
import os
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

class ArxivSearch:
    def __init__(self, config):
        self.config = config
        self.export_manager = ExportManager()
        self.results_per_page = int(config.get("ArXiv", "results_per_page", fallback="10"))
        self.current_results = []
        self.current_query = ""
        
        # Initialize arxiv client
        self.client = arxiv.Client(
            page_size=self.results_per_page,
            delay_seconds=3.0,
            num_retries=3
        )
        
        # Get AI provider and model
        self.provider = config.get("DEFAULT", "ai_provider")
        self.model = config.get(self.provider.title(), "default_model")
        
        # Initialize language model
        self.llm = self._initialize_llm()

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

    async def _search_arxiv(self, query: str) -> List[Dict]:
        """Search arxiv papers using the API."""
        try:
            # Create search query
            search = arxiv.Search(
                query=query,
                max_results=self.results_per_page,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            # Execute search synchronously in a thread pool
            def do_search():
                return list(self.client.results(search))

            # Run in thread pool
            papers = await asyncio.to_thread(do_search)
            
            # Format results
            results = []
            for paper in papers:
                results.append({
                    'title': paper.title,
                    'authors': [author.name for author in paper.authors],
                    'abstract': paper.summary,
                    'url': paper.entry_id,
                    'pdf_url': paper.pdf_url,
                    'published': paper.published.strftime("%Y-%m-%d"),
                    'categories': paper.categories,
                    'comment': paper.comment,
                    'journal_ref': paper.journal_ref,
                    'doi': paper.doi
                })
            return results

        except Exception as e:
            logger.error(f"arXiv search error: {str(e)}")
            return []

    async def search(self):
        try:
            console.clear()
            console.print(Panel(
                "arXiv Search Interface - Commands:\n" +
                "/exit - Return to main menu\n" +
                "/export [format] - Export results (txt/md/json)\n" +
                "/filter [category] - Filter by category\n" +
                "/sort [criterion] - Sort results\n" + 
                "/help - Show this help message",
                title="arXiv Search Commands",
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
                    
                    # Search papers
                    with console.status("[bold green]Searching arXiv...[/bold green]"):
                        results = await self._search_arxiv(query)
                    
                    if results:
                        self.current_results = results
                        
                        # Display results list
                        console.print("\n[bold cyan]Search Results:[/bold cyan]")
                        for i, result in enumerate(results, 1):
                            console.print(f"[{i}] {result['title']}")
                        
                        # Ask for paper selection
                        if len(results) > 0:
                            selection = Prompt.ask(
                                "\nSelect a paper to view details (1-{})".format(len(results)),
                                default="1"
                            )
                            try:
                                idx = int(selection) - 1
                                if 0 <= idx < len(results):
                                    selected = results[idx]
                                    # Display detailed view of selected paper
                                    console.print(Panel(
                                        f"[bold]{selected['title']}[/bold]\n\n" +
                                        f"Authors: {', '.join(selected['authors'])}\n" +
                                        f"Published: {selected['published']}\n" +
                                        f"Categories: {', '.join(selected['categories'])}\n" +
                                        f"URL: [blue]{selected['url']}[/blue]\n" +
                                        f"PDF: [blue]{selected['pdf_url']}[/blue]\n\n" +
                                        f"Abstract:\n{selected['abstract']}",
                                        title=f"Paper Details [{selection}/{len(results)}]",
                                        style="green"
                                    ))
                                else:
                                    console.print("[red]Invalid selection[/red]")
                            except ValueError:
                                console.print("[red]Invalid input[/red]")
                        
                        # Optional AI analysis
                        if Prompt.ask(
                            "\nWould you like an AI analysis of these papers?",
                            choices=["y", "n"],
                            default="n"
                        ) == "y":
                            with console.status("[bold green]Analyzing papers...[/bold green]"):
                                analysis = await self._analyze_papers(results, query)
                            
                            console.print(Panel("AI Analysis:", style="cyan"))
                            console.print(Panel(
                                Markdown(analysis),
                                style="green"
                            ))
                    else:
                        console.print("[yellow]No papers found.[/yellow]")
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}[/red]")
                    await asyncio.sleep(1)
        except KeyboardInterrupt:
            console.print("\nExiting arXiv search...", style="bold yellow")

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

    async def _analyze_papers(self, papers: List[Dict], query: str) -> str:
        """Analyze papers using AI."""
        # Create a simple researcher agent
        researcher = Agent(
            role='Research Specialist',
            goal='Analyze academic papers and provide a concise summary',
            backstory="""Expert at analyzing academic papers and providing clear summaries. 
            Focuses on key findings, methodologies, and contributions.""",
            llm=self.llm,
            verbose=True
        )
        
        # Format papers for analysis
        formatted_papers = "\n\n".join([
            f"Title: {paper['title']}\nAuthors: {', '.join(paper['authors'])}\nAbstract: {paper['abstract']}"
            for paper in papers
        ])
        
        # Create analysis task
        task = Task(
            description=f"""Analyze these papers for query: {query}

Papers:
{formatted_papers}

Guidelines:
1. Identify key themes and findings
2. Highlight important methodologies
3. Note significant contributions
4. Suggest potential applications
5. Identify research trends""",
            expected_output="""A concise summary containing:
            - Key themes and findings
            - Important methodologies
            - Significant contributions
            - Potential applications
            - Research trends""",
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
