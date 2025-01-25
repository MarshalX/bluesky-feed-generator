#!/usr/bin/env python3
# YOU MUST INSTALL ATPROTO SDK
# pip3 install atproto

import os

from dotenv import load_dotenv
from atproto import Client, models

load_dotenv()

def _get_bool_env_var(value: str) -> bool:
    # Helper function to convert string to bool

    if value is None:
        return False

    normalized_value = value.strip().lower()
    if normalized_value in {'1', 'true', 't', 'yes', 'y'}:
        return True

    return False


# YOUR bluesky handle
# Ex: user.bsky.social
HANDLE: str = os.environ.get('HANDLE')

# YOUR bluesky password, or preferably an App Password (found in your client settings)
# Ex: abcd-1234-efgh-5678
PASSWORD: str = os.environ.get('PASSWORD')

# The hostname of the server where feed server will be hosted
# Ex: feed.bsky.dev
HOSTNAME: str = os.environ.get('HOSTNAME')

# A short name for the record that will show in urls
# Lowercase with no spaces.
# Ex: whats-hot
RECORD_NAME: str = os.environ.get('RECORD_NAME')

# A display name for your feed
# Ex: What's Hot
DISPLAY_NAME: str = os.environ.get('DISPLAY_NAME')

# (Optional) A description of your feed
# Ex: Top trending content from the whole network
DESCRIPTION: str = os.environ.get('DESCRIPTION')

# (Optional) The path to an image to be used as your feed's avatar
# Ex: ./path/to/avatar.jpeg
AVATAR_PATH: str = os.environ.get('AVATAR_PATH')

# (Optional). Only use this if you want a service did different from did:web
SERVICE_DID: str = os.environ.get('SERVICE_DID')

# (Optional). If your feed accepts interactions from clients
ACCEPTS_INTERACTIONS: bool = _get_bool_env_var(os.environ.get('ACCEPTS_INTERACTIONS'))

# (Optional). If your feed is a video feed
IS_VIDEO_FEED: bool = _get_bool_env_var(os.environ.get('IS_VIDEO_FEED'))

# -------------------------------------
# NO NEED TO TOUCH ANYTHING BELOW HERE
# -------------------------------------


def main():
    client = Client()
    client.login(HANDLE, PASSWORD)

    feed_did = SERVICE_DID
    if not feed_did:
        feed_did = f'did:web:{HOSTNAME}'

    avatar_blob = None
    if AVATAR_PATH:
        with open(AVATAR_PATH, 'rb') as f:
            avatar_data = f.read()
            avatar_blob = client.upload_blob(avatar_data).blob

    response = client.com.atproto.repo.put_record(models.ComAtprotoRepoPutRecord.Data(
        repo=client.me.did,
        collection=models.ids.AppBskyFeedGenerator,
        rkey=RECORD_NAME,
        record=models.AppBskyFeedGenerator.Record(
            did=feed_did,
            display_name=DISPLAY_NAME,
            accepts_interactions=ACCEPTS_INTERACTIONS,
            description=DESCRIPTION,
            avatar=avatar_blob,
            content_mode='app.bsky.feed.defs#contentModeVideo' if IS_VIDEO_FEED else None,
            created_at=client.get_current_time_iso(),
        )
    ))

    print('Successfully published!')
    print('Feed URI (put in "FEED_URI" env var):', response.uri)


if __name__ == '__main__':
    main()
