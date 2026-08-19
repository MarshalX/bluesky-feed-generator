#!/usr/bin/env python3
# YOU MUST INSTALL ATPROTO SDK
# pip3 install atproto

import os

from dotenv import load_dotenv
from atproto import Client, models

load_dotenv()

# YOUR bluesky handle
# Ex: user.bsky.social
HANDLE: str = os.environ.get('HANDLE')

# YOUR bluesky password, or preferably an App Password (found in your client settings)
# Ex: abcd-1234-efgh-5678
PASSWORD: str = os.environ.get('PASSWORD')

# The short name of the record to delete. Must match the one used to publish the feed.
# Ex: whats-hot
RECORD_NAME: str = os.environ.get('RECORD_NAME')

# -------------------------------------
# NO NEED TO TOUCH ANYTHING BELOW HERE
# -------------------------------------


def main():
    print(f'You are about to delete the "{RECORD_NAME}" feed generator record of "{HANDLE}".')
    print('Any likes that your feed has will be lost.')
    if input('Type the name of the record to confirm: ').strip() != RECORD_NAME:
        print('Aborting...')
        return

    client = Client()
    client.login(HANDLE, PASSWORD)

    client.com.atproto.repo.delete_record(models.ComAtprotoRepoDeleteRecord.Data(
        repo=client.me.did,
        collection=models.ids.AppBskyFeedGenerator,
        rkey=RECORD_NAME,
    ))

    print('Successfully unpublished!')


if __name__ == '__main__':
    main()
