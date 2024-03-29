import json

import aiohttp

from .queue import VKQueue


class VKCommenter:
    def __init__(self, tokens):
        self._queue = VKQueue(tokens)
        self._session = None
		
        self._cache = {}

    async def _upload_doc(self, path, group_id):
        if ("doc", path) in self._cache:
            return self._cache[("doc", path)]
        
        upload_data = await self._queue.request("docs.getWallUploadServer")
        
        upload_url = upload_data["upload_url"]

        post_request = self._session.post(
            upload_url, data={"file": open(path, "rb")}
        )

        async with post_request as resp:
            response = json.loads(await resp.text())

        doc = await self._queue.request("docs.save", file=response["file"])

        doc_id = "doc{}_{}".format(doc["doc"]["owner_id"], doc["doc"]["id"])
        self._cache[("doc", path)] = doc_id
 
        return doc_id

    async def _upload_image(self, path, group_id):
        if ("image", path) in self._cache:
            return self._cache[("image", path)]
        
        upload_data = await self._queue.request("photos.getWallUploadServer",
                                                group_id=group_id)

        upload_url = upload_data["upload_url"]

        post_request = self._session.post(
            upload_url, data={"photo": open(path, "rb")}
        )

        async with post_request as resp:
            response = json.loads(await resp.text())

        photo = await self._queue.request(
            "photos.saveWallPhoto",
            server=response["server"],
            photo=response["photo"],
            hash=response["hash"],
            group_id=group_id
        )

        photo_id = "photo{}_{}_{}".format(
            photo[0]["owner_id"], photo[0]["id"], photo[0]["access_key"]
        )
        self._cache[("image", path)] = photo_id
		
        return photo_id

    # Public API -------------------------------------------------------------

    async def start(self):
        self._queue.start()

    async def create_comment(self, group_id, post_id, text=None, image=None,
                          doc=None, from_group=None, reply_to_comment=None):

        if image and doc:
            raise ValueError("Only either image or doc should be present")

        if not image and not doc and not text:
            raise ValueError("Text, doc or image should be present")

        if not self._session:
            self._session = aiohttp.ClientSession()

        if image:
            attach = await self._upload_image(image, group_id)

        elif doc:
            attach = await self._upload_doc(doc, group_id)

        else:
            attach = None

        kwargs = {
            "owner_id": -group_id,
            "post_id": post_id
        }

        if attach:
            kwargs["attachments"] = attach

        if text:
            kwargs["message"] = text

        if reply_to_comment:
            kwargs["reply_to_comment"] = reply_to_comment

        if from_group:
            kwargs["from_group"] = from_group

        await self._queue.request("wall.createComment", **kwargs)

    async def dispose(self):
        await self._queue.dispose()

        if self._session:
            await self._session.close()
