import asyncio
from rich.console import Console
from rich.panel import Panel
from tavily import TavilyClient

console = Console()

class ArxivAI:
    def __init__(self, config, api_manager):
        self.config = config
        self.api_manager = api_manager
        self.tavily_client = TavilyClient(api_key=self.config.tavily_api_key)

    async def run(self):
        console.print(Panel("Welcome to Arxiv AI!", title="Arxiv AI", expand=False))
        
        while True:
            query = await self.get_user_input("Enter your Arxiv search query (or 'exit' to quit): ")
            
            if query.lower() == "exit":
                break

            results = await self.perform_arxiv_search(query)
            console.print(Panel(results, title="Arxiv Search Results", expand=False))

    async def get_user_input(self, prompt="You: "):
        return await asyncio.get_event_loop().run_in_executor(None, input, prompt)

    async def perform_arxiv_search(self, query):
        try:
            response = await asyncio.to_thread(
                self.tavily_client.search,
                f"site:arxiv.org {query}",
                search_depth="advanced",
                include_answer=True,
                max_results=5
            )
            
            result = f"Summary: {response['answer']}\n\nArxiv Papers:\n"
            for idx, paper in enumerate(response['results'], 1):
                if 'arxiv.org' in paper['url']:
                    result += f"{idx}. Title: {paper['title']}\n"
                    result += f"   URL: {paper['url']}\n"
                    result += f"   Summary: {paper['content'][:200]}...\n\n"
            
            return result
        except Exception as e:
            return f"An error occurred: {str(e)}"