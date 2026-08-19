from datetime import datetime, timezone

import peewee

db = peewee.SqliteDatabase('feed_database.db')


def _utc_now() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(tzinfo=None, microsecond=now.microsecond // 1000 * 1000)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Post(BaseModel):
    uri = peewee.CharField(index=True)
    cid = peewee.CharField()
    reply_parent = peewee.CharField(null=True, default=None)
    reply_root = peewee.CharField(null=True, default=None)
    indexed_at = peewee.DateTimeField(default=_utc_now)


class SubscriptionState(BaseModel):
    service = peewee.CharField(unique=True)
    cursor = peewee.BigIntegerField()


if db.is_closed():
    db.connect()
    db.create_tables([Post, SubscriptionState])
