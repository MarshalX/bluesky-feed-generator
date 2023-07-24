import typing as t

from atproto import CAR, AtUri, models
from atproto.exceptions import FirehoseError
from atproto.firehose import FirehoseSubscribeReposClient, parse_subscribe_repos_message
from atproto.xrpc_client.models import get_or_create, is_record_type
from atproto.xrpc_client.models.common import XrpcError

from server.logger import logger
from server.database import SubscriptionState

if t.TYPE_CHECKING:
    from atproto.firehose import MessageFrame


def _get_ops_by_type(commit: models.ComAtprotoSyncSubscribeRepos.Commit) -> dict:  # noqa: C901
    operation_by_type = {
        'posts': {'created': [], 'deleted': []},
        'reposts': {'created': [], 'deleted': []},
        'likes': {'created': [], 'deleted': []},
        'follows': {'created': [], 'deleted': []},
    }

    car = CAR.from_bytes(commit.blocks)
    for op in commit.ops:
        uri = AtUri.from_str(f'at://{commit.repo}/{op.path}')

        if op.action == 'update':
            # not supported yet
            continue

        if op.action == 'create':
            if not op.cid:
                continue

            create_info = {'uri': str(uri), 'cid': str(op.cid), 'author': commit.repo}

            record_raw_data = car.blocks.get(op.cid)
            if not record_raw_data:
                continue

            record = get_or_create(record_raw_data, strict=False)
            if uri.collection == models.ids.AppBskyFeedLike and is_record_type(record, models.AppBskyFeedLike):
                operation_by_type['likes']['created'].append({'record': record, **create_info})
            elif uri.collection == models.ids.AppBskyFeedPost and is_record_type(record, models.AppBskyFeedPost):
                operation_by_type['posts']['created'].append({'record': record, **create_info})
            elif uri.collection == models.ids.AppBskyGraphFollow and is_record_type(record, models.AppBskyGraphFollow):
                operation_by_type['follows']['created'].append({'record': record, **create_info})

        if op.action == 'delete':
            if uri.collection == models.ids.AppBskyFeedLike:
                operation_by_type['likes']['deleted'].append({'uri': str(uri)})
            if uri.collection == models.ids.AppBskyFeedPost:
                operation_by_type['posts']['deleted'].append({'uri': str(uri)})
            if uri.collection == models.ids.AppBskyGraphFollow:
                operation_by_type['follows']['deleted'].append({'uri': str(uri)})

    return operation_by_type


def run(name, operations_callback, stream_stop_event=None):
    while True:
        try:
            _run(name, operations_callback, stream_stop_event)
        except FirehoseError as e:
            if e.__context__ and e.__context__.args:
                xrpc_error = e.__context__.args[0]
                if isinstance(xrpc_error, XrpcError) and xrpc_error.error == 'ConsumerTooSlow':
                    logger.warn('Reconnecting to Firehose due to ConsumerTooSlow...')
                    continue

            raise e


def _run(name, operations_callback, stream_stop_event=None):
    state = SubscriptionState.select(SubscriptionState.service == name).first()

    params = None
    if state:
        params = models.ComAtprotoSyncSubscribeRepos.Params(cursor=state.cursor)

    client = FirehoseSubscribeReposClient(params)

    if not state:
        SubscriptionState.create(service=name, cursor=0)

    def on_message_handler(message: 'MessageFrame') -> None:
        # stop on next message if requested
        if stream_stop_event and stream_stop_event.is_set():
            client.stop()
            return

        commit = parse_subscribe_repos_message(message)
        if not isinstance(commit, models.ComAtprotoSyncSubscribeRepos.Commit):
            return

        # update stored state every ~20 events
        if commit.seq % 20 == 0:
            SubscriptionState.update(cursor=commit.seq).where(SubscriptionState.service == name).execute()

        operations_callback(_get_ops_by_type(commit))

    client.start(on_message_handler)
