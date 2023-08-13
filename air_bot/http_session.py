import aiohttp


class HttpSessionMaker:
    def __init__(self):
        # aiohttp.ClientSession() wants to be called inside a coroutine
        self._session: aiohttp.ClientSession | None = None

    def __call__(self):
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session:
            await self._session.close()
