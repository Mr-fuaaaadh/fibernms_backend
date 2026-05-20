from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

from saas.accounts.models import User


@database_sync_to_async
def get_user_from_token(token: str):
    try:
        payload = AccessToken(token)
        return User.objects.get(id=payload['user_id'], is_active=True)
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_params = parse_qs(scope.get('query_string', b'').decode())
        token = (query_params.get('token') or [None])[0]
        if token:
            scope['user'] = await get_user_from_token(token)
        return await super().__call__(scope, receive, send)
