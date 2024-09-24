from rich.console import Console
from rich.panel import Panel

console = Console()

class CoderAI:
    def __init__(self, config, api_manager):
        self.config = config
        self.api_manager = api_manager

    async def run(self):
        console.print(Panel("Welcome to Coder AI!", title="Coder AI", expand=False))
        
        # TODO: Implement Coder AI functionality similar to test.txt
        console.print("Coder AI functionality is not yet implemented.")

    async def get_user_input(self, prompt="You: "):
        return await asyncio.get_event_loop().run_in_executor(None, input, prompt)