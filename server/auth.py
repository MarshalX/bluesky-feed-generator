from atproto import DidInMemoryCache, IdResolver, verify_jwt
from atproto.exceptions import TokenInvalidSignatureError
from flask import Request


_CACHE = DidInMemoryCache()
_ID_RESOLVER = IdResolver(cache=_CACHE)

_AUTHORIZATION_HEADER_NAME = 'Authorization'
_AUTHORIZATION_HEADER_VALUE_PREFIX = 'Bearer '


class AuthorizationError(Exception):
    ...


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
        return verify_jwt(jwt, _ID_RESOLVER.did.resolve_atproto_key).iss
    except TokenInvalidSignatureError as e:
        raise AuthorizationError('Invalid signature') from e
