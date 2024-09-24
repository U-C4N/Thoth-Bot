import asyncio
from rich.console import Console
from rich.panel import Panel
from tavily import TavilyClient

console = Console()

class SearchAI:
    def __init__(self, config, api_manager):
        self.config = config
        self.api_manager = api_manager
        self.tavily_client = TavilyClient(api_key=self.config.tavily_api_key)
        self.search_depth = None

    async def run(self):
        console.print(Panel("Welcome to Search AI!", title="Search AI", expand=False))
        
        self.search_depth = await self.select_search_depth()
        console.print(f"Selected search depth: {self.search_depth}")

        while True:
            query = await self.get_user_input("Enter your search query (or 'exit' to quit): ")
            
            if query.lower() == "exit":
                break

            results = await self.perform_search(query)
            console.print(Panel(results, title="Search Results", expand=False))

    async def get_user_input(self, prompt="You: "):
        return await asyncio.get_event_loop().run_in_executor(None, input, prompt)

    async def select_search_depth(self):
        console.print("Available search depths:")
        console.print("1. Basic")
        console.print("2. Advanced")
        while True:
            choice = await self.get_user_input("Select a search depth (1-2): ")
            if choice == '1':
                return "basic"
            elif choice == '2':
                return "advanced"
            else:
                console.print("Invalid choice. Please try again.", style="bold red")

    async def perform_search(self, query):
        try:
            response = await asyncio.to_thread(
                self.tavily_client.search,
                query,
                search_depth=self.search_depth,
                include_answer=True,
                max_results=5
            )
            
            result = f"Answer: {response['answer']}\n\nSources:\n"
            for idx, source in enumerate(response['results'], 1):
                result += f"{idx}. {source['title']}\n   URL: {source['url']}\n   Content: {source['content'][:200]}...\n\n"
            
            return result
        except Exception as e:
            return f"An error occurred: {str(e)}"