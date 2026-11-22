import threading
import typing as t
from collections import OrderedDict

from atproto import DidInMemoryCache, IdResolver, verify_jwt
from atproto.exceptions import AtProtocolError
from flask import Request

from server import config

if t.TYPE_CHECKING:
    from atproto_core.did_doc import DidDocument
    from atproto_identity.cache.models import CachedDidResult

_CACHE_MAX_ENTRIES = 10_000


class _BoundedDidCache(DidInMemoryCache):
    """In-memory DID cache with LRU eviction."""

    def __init__(self, max_entries: int, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self._cache: OrderedDict = OrderedDict()
        self._max_entries = max_entries
        self._lock = threading.Lock()

    def set(self, did: str, document: 'DidDocument') -> None:
        with self._lock:
            super().set(did, document)
            self._cache.move_to_end(did)
            while len(self._cache) > self._max_entries:
                self._cache.popitem(last=False)

    def get(self, did: str) -> t.Optional['CachedDidResult']:
        with self._lock:
            if did in self._cache:
                self._cache.move_to_end(did)
            return super().get(did)

    def delete(self, did: str) -> None:
        with self._lock:
            self._cache.pop(did, None)

    def clear(self) -> None:
        with self._lock:
            super().clear()


_CACHE = _BoundedDidCache(_CACHE_MAX_ENTRIES)
_ID_RESOLVER = IdResolver(cache=_CACHE)

_AUTHORIZATION_HEADER_NAME = 'Authorization'
_AUTHORIZATION_HEADER_VALUE_PREFIX = 'Bearer '


class AuthorizationError(Exception):
    ...


def _parse_request_nsid(request: 'Request') -> str:
    """Extract the NSID of the called XRPC method from the request path (``/xrpc/<nsid>``)."""
    return request.path.rsplit('/', 1)[-1]


def validate_auth(request: 'Request') -> str:
    """Validate authorization header.

    Args:
        request: The request to validate.

    Returns:
        :obj:`str`: Requester DID.

    Raises:
        :obj:`AuthorizationError`: If the authorization header is invalid.
    """
    auth_header = request.headers.get(_AUTHORIZATION_HEADER_NAME)
    if not auth_header:
        raise AuthorizationError('Authorization header is missing')

    if not auth_header.startswith(_AUTHORIZATION_HEADER_VALUE_PREFIX):
        raise AuthorizationError('Invalid authorization header')

    jwt = auth_header[len(_AUTHORIZATION_HEADER_VALUE_PREFIX) :].strip()

    try:
        # "own_did" binds the token to this service by checking the "aud" claim.
        payload = verify_jwt(jwt, _ID_RESOLVER.did.resolve_atproto_key, own_did=config.SERVICE_DID)
    except AtProtocolError as e:
        raise AuthorizationError(f'Invalid token: {e}') from e

    # The "lxm" claim binds the token to a single XRPC method
    nsid = _parse_request_nsid(request)
    if getattr(payload, 'lxm', None) != nsid:
        raise AuthorizationError(f'Token is not bound to the "{nsid}" method')

    return payload.iss
