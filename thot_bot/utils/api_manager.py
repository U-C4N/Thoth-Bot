import aiohttp

class APIManager:
    def __init__(self):
        self.session = None

    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def groq_request(self, endpoint, data):
        # TODO: Implement Groq API request
        pass

    async def tavily_request(self, endpoint, data):
        # TODO: Implement Tavily API request
        pass