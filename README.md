
# VKCommenter

Asynchronous system for creating comment to posts in vkontakte's groups.

## Usage

- Create commenter and pass your tokens to it. Tokens should be users and
    have following scopes: `photos,wall,docs`.

```py
from vkcommenter import VKCommenter

tokens = ["token1", "token2", "token3"]

commenter = VKCommenter(tokens)
```

- Start commenter (asynchronously)

```py

async def programm():
    await commenter.start()

```

- Create comments with VKCommenter's method `create_comment`

```py
commenter.create_comment(
    group_id, post_id, text=None, image=None,
    doc=None, from_group=None, reply_to_comment=None
)
```

Arguments:

- `group_id` - target group id
- `post_id` - target post id
- `text` - text for comment
- `image`, `doc` - path to photo or file to attach to comment
- `reply_to_comment` - if comment is reply to other comment
- `from_group` - group id (if you want to create comment as a group)

- Gracefully stop commenter

```py

async def programm():
    await commenter.dispose()

```

# Authors

- Michael Krukov (@michaelkrukov)
- Daniel Korotkov (@darkenezy)
