## ATProto Feed Generator

> Feed Generators are services that provide custom algorithms to users through the AT Protocol.

Official overview: https://github.com/bluesky-social/feed-generator#overview

Powered by The AT Protocol SDK for Python: https://github.com/MarshalX/atproto

SDK Documentation: https://atproto.blue

### Getting Started

We've set up this simple server with SQLite to store and query data. Feel free to switch this out for whichever database you prefer.

Next, you will need to do two things:
1. Implement indexing logic in `src/data_filter.py`.
2. Implement feed generation logic in `src/algos`.

We've taken care of setting this server up with a did:web. However, you're free to switch this out for did:plc if you like - you may want to if you expect this Feed Generator to be long-standing and possibly migrating domains.

### Publishing your feed

To publish your feed, go to the script at `publish_feed.py` and fill in the variables at the top. Examples are included, and some are optional. To publish your feed generator, simply run `python publish_feed.py`.

To update your feed's display data (name, avatar, description, etc.), just update the relevant variables and re-run the script.

After successfully running the script, you should be able to see your feed from within the app, as well as share it by embedding a link in a post (similar to a quote post).

### Running the Server

Install Python 3.7+, optionally create virtual environment.

Install dependencies:
```shell
pip3 install -r requirements.txt
```

Set `HOSTNAME` env variable (your server's domain):
```shell
export HOSTNAME='example.com'
```

Run development flask server:
```shell
cd src
flask run
```

Run development debug server:
```shell
cd src
python __main__.py
```

**In production, you should use production WSGI server instead! If you want to run server in many workers you should run Data Stream (Firehose) separately!**

Endpoints:
- /.well-known/did.json
- /xrpc/app.bsky.feed.describeFeedGenerator
- /xrpc/app.bsky.feed.getFeedSkeleton

### License

MIT
