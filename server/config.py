import os

from dotenv import load_dotenv

load_dotenv()

SERVICE_DID = os.environ.get('SERVICE_DID', None)
HOSTNAME = os.environ.get('HOSTNAME', None)

if HOSTNAME is None:
    raise RuntimeError('You should set "HOSTNAME" environment variable first.')

if SERVICE_DID is None:
    SERVICE_DID = f'did:web:{HOSTNAME}'


FEED_URI = os.environ.get('FEED_URI')
if FEED_URI is None:
    raise RuntimeError('Publish your feed first (run publish_feed.py) to obtain Feed URI. '
                       'Set this URI to "FEED_URI" environment variable.')