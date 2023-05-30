from datetime import datetime
from typing import Optional

from server import config
from server.database import Post

uri = config.WHATS_ALF_URI


def handler(cursor: Optional[str], limit: int) -> dict:
    posts = Post.select().order_by(Post.indexed_at.desc()).order_by(Post.cid.desc()).limit(limit)

    if cursor:
        cursor_parts = cursor.split('::')
        if len(cursor_parts) != 2:
            raise ValueError('Malformed cursor')

        indexed_at, cid = cursor_parts
        indexed_at = datetime.fromtimestamp(int(indexed_at) / 1000)
        posts = posts.where(Post.indexed_at <= indexed_at).where(Post.cid < cid)

    feed = [{'post': post.uri} for post in posts]

    cursor = None
    last_post = posts[-1] if posts else None
    if last_post:
        cursor = f'{int(last_post.indexed_at.timestamp() * 1000)}::{last_post.cid}'

    return {
        'cursor': cursor,
        'feed': feed
    }
