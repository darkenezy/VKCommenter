import asyncio
import json
from aiohttp import ClientSession


class VKRequest(asyncio.Future):
    def __init__(self, method, kwargs={}):
        super().__init__()
        self.method = method
        self.kwargs = kwargs
        
class VKQueue():
    def __init__(self, tokens, session, futures):
        self.n = 0
        self.token = None
        self.tokens = tokens
        self.futures = futures
        self.session = session
        self.requests_queue = []
        self.delay = 0.33334/len(tokens)
        self.futures.append(asyncio.ensure_future(self.start()))
    
    def request(self, method, **kwargs):
        req = VKRequest(method, kwargs)
        self.requests_queue.append(req)
        return asyncio.wait_for(req, None)

    async def update_token(self):
        await asyncio.sleep(self.delay)
        self.token = self.tokens[(self.n + 1)%len(self.tokens)]
    
    async def start(self):
        while True:
            await self.update_token()
            reqs = []
            for i in range(25):
                if self.requests_queue:
                    reqs.append(self.requests_queue.pop(0))
                else:
                    break
            if reqs:
                self.futures.append(asyncio.ensure_future(self.execute(reqs)))
                
    async def execute(self, reqs):
        code = "return ["
        
        for req in reqs:
            code += "API.{}({}),".format(req.method, json.dumps(req.kwargs, ensure_ascii=False))
        code += "];"
        
        url = "https://api.vk.com/method/execute?access_token={}&v=5.92".format(self.token)
        async with self.session.post(url, data = {"code": code}) as r:
            result = await r.json()
            result = zip(reqs, result["response"])
            for req in result:
                req[0].set_result(req[1])
