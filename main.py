from vk_queue import *


async def session_init():
    return ClientSession()


class CommentBot():
    def __init__(self, tokens, session):
        self.futures = []
        self.session = session
        self.queue = VKQueue(tokens, session, self.futures)
        
    async def add_comment(self, group_id, post_id, photo=None, doc=None, from_group=0):
        if photo:
            attach = await self.upload_photo(photo, group_id)
        elif doc:
            attach = await self.upload_doc(doc, group_id)
        else:
            print('No attachment given')
            return
            
        x = await self.queue.request('wall.createComment',
                                     owner_id=-group_id,
                                     post_id=post_id,
                                     attachments=attach,
                                     from_group=from_group)
        
    async def upload_doc(self, path, group_id):
        server = (await self.queue.request('docs.getWallUploadServer'))['upload_url']
        async with self.session.post(server, data={'file': open(path, 'rb')}) as r:
            resp = json.loads(await r.text())

        doc = await self.queue.request('docs.save', file=resp['file'])
        
        return "doc{}_{}".format(doc['doc']['owner_id'], doc['doc']['id'])
    
    async def upload_photo(self, path, group_id):
        server = (await self.queue.request('photos.getWallUploadServer', group_id=group_id))['upload_url']
        async with self.session.post(server, data={'photo': open(path, 'rb')}) as r:
            resp = json.loads(await r.text())

        photo = await self.queue.request('photos.saveWallPhoto',
                                         server=resp['server'],
                                         photo=resp['photo'],
                                         hash=resp['hash'],
                                         group_id=group_id)
        
        return "photo{}_{}_{}".format(photo[0]['owner_id'], photo[0]['id'], photo[0]['access_key'])

            
tokens = ['TOKEN1',
          'TOKEN2',
          'TOKEN3']

loop = asyncio.get_event_loop()
session = loop.run_until_complete(session_init())

bot = CommentBot(tokens, session)

if __name__ == "__main__":
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(*bot.futures)
    finally:
        loop.close()
    


















        
