import asyncio
import json

import aiohttp


class VKRequest(asyncio.Future):
    def __init__(self, method, kwargs={}):
        super().__init__()
        self.method = method
        self.kwargs = kwargs


class VKQueue:
    def __init__(self, tokens):
        if len(tokens) < 1:
            raise ValueError("You didn't provided tokens")

        self._tokens = list(tokens)
        self._current_token = 0

        self._delay = 0.34 / len(self._tokens)

        self._running = False

        self._requests_queue = []

        self._tasks = []
        self._session = None

    async def _loop(self):
        while self._running:

            await asyncio.sleep(self._delay)

            self._current_token += 1

            token = self._tokens[self._current_token  % len(self._tokens)]

            requests = []

            for _ in range(25):
                if self._requests_queue:
                    requests.append(self._requests_queue.pop(0))

                else:
                    break

            if requests:
                self._tasks.append(
                    asyncio.ensure_future(self._execute(token, requests))
                )

    async def _execute(self, token, requests):
        if not self._session:
            self._session = aiohttp.ClientSession()

        code = "return ["

        for request in requests:
            code += "API.{}({}),".format(
                request.method, json.dumps(request.kwargs, ensure_ascii=False)
            )

        code += "];"

        url = "https://api.vk.com/method/execute?access_token={}&v=5.92" \
                    .format(token)

        async with self._session.post(url, data={"code": code}) as response:
            result = await response.json()

        for req, result in zip(requests, result["response"]):
            req.set_result(result)

    # Public API -------------------------------------------------------------

    def start(self):
        self._running = True

        self._tasks.append(
            asyncio.ensure_future(self._loop())
        )

    def request(self, method, **kwargs):
        req = VKRequest(method, kwargs)

        self._requests_queue.append(req)

        return asyncio.wait_for(req, None)

    async def dispose(self):
        self._running = False

        await asyncio.gather(*self._tasks)

        if self._session:
            await self._session.close()
