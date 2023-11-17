from datetime import datetime

import peewee


db = peewee.SqliteDatabase('feed_database.db')
db_version = 2


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Post(BaseModel):
    uri = peewee.CharField(index=True)
    cid = peewee.CharField()
    reply_parent = peewee.CharField(null=True, default=None)
    reply_root = peewee.CharField(null=True, default=None)
    indexed_at = peewee.DateTimeField(default=datetime.now)


class SubscriptionState(BaseModel):
    service = peewee.CharField(unique=True)
    cursor = peewee.IntegerField()

class DbMetadata(BaseModel):
    version = peewee.IntegerField()


if db.is_closed():
    db.connect()
    db.create_tables([Post, SubscriptionState, DbMetadata])

    # DB migration
    current_version = 1 if DbMetadata.select().count() == 0 else DbMetadata.select().first().version
    
    if current_version != db_version:
        with db.atomic():    
            # V2
            # Drop cursors stored from the old bsky.social PDS
            if current_version == 1:
                SubscriptionState.delete().execute()
            
            # Update version in DB
            if DbMetadata.select().count() == 0:
                DbMetadata.insert({DbMetadata.version:db_version}).execute()
            else:
                DbMetadata.update({DbMetadata.version:db_version}).execute()