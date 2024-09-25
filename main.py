import os
import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from modules.chat_ai import ChatAI
from modules.coder_ai import CoderAI
from modules.search_ai import SearchAI
from modules.arxiv_ai import ArxivAI
from utils.config import Config
from utils.api_manager import APIManager

console = Console()

class ThotBot:
    def __init__(self):
        load_dotenv()
        self.config = Config()
        self.api_manager = APIManager()
        self.chat_ai = ChatAI(self.config, self.api_manager)
        self.coder_ai = CoderAI(self.config, self.api_manager)
        self.search_ai = SearchAI(self.config, self.api_manager)
        self.arxiv_ai = ArxivAI(self.config, self.api_manager)

    async def run(self):
        console.print(Panel("Welcome to Thot Bot!", title="Thot Bot", expand=False))
        
        try:
            while True:
                choice = await self.get_user_choice()
                
                if choice == "1":
                    await self.chat_ai.run()
                elif choice == "2":
                    await self.coder_ai.run()
                elif choice == "3":
                    await self.search_ai.run()
                elif choice == "4":
                    await self.arxiv_ai.run()
                elif choice.lower() == "exit":
                    break
                else:
                    console.print("Invalid choice. Please try again.", style="bold red")
        finally:
            await self.api_manager.close()

        console.print(Panel("Thank you for using Thot Bot!", title="Goodbye", expand=False))

    async def get_user_choice(self):
        console.print("\nPlease select an option:")
        console.print("1. Chat AI")
        console.print("2. Coder AI")
        console.print("3. Search AI")
        console.print("4. Arxiv AI")
        console.print("Type 'exit' to quit")
        return await asyncio.get_event_loop().run_in_executor(None, input, "Your choice: ")

if __name__ == "__main__":
    bot = ThotBot()
    asyncio.run(bot.run())