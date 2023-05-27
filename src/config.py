import os

SERVICE_DID = os.environ.get('SERVICE_DID', None)
HOSTNAME = os.environ.get('HOSTNAME', None)

WHATS_ALF_NAME = 'whats-alf'
WHATS_ALF_URI = f'at://{SERVICE_DID}/app.bsky.feed.generator/{WHATS_ALF_NAME}'

if SERVICE_DID is None or HOSTNAME is None:
    raise RuntimeError('You should set environment variables first. Required variables: SERVICE_DID, HOSTNAME.')
