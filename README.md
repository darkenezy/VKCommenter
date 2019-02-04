# CommentBot
Wrapper for VK comment bot

## Usage
### Create a bot instance.<br>
```bot = CommentBot(tokens, session)```

`tokens` - list of VK **user** tokens. Scopes required: `photos,wall,docs`<br>
`session` - asyncio ClientSession object<br>

### Add comment to post
```bot.add_comment(group_id, post_id)```<br>

*Required arguments:*<br>
`group_id` - target group id<br>
`post_id` - target post id<br>
`photo` or `doc` - path to photo or file

*Optional arguments*:
`from_group` - group if. (You must be an owner)<br>
If given the comment would be sent with your group's name
