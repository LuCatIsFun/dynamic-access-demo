"""
@time: 2020/8/14 2:54 下午
"""
from datetime import datetime
from urllib.parse import parse_qs
from django.core.cache import cache
from django.db import close_old_connections
from channels.auth import AuthMiddlewareStack
from rest_framework import authentication
from django.contrib.auth.models import AnonymousUser

from main import exception

from channels.db import database_sync_to_async

__all__ = ['TokenAuthMiddlewareStack', 'TokenAuthMiddleware']


def handle_token(request):
    """
    获取request对象中的认证信息。读取顺序如下，获取到值则忽略后面步骤

        1，header中获取 'Authorization'
        2，post请求：rest封装的data对象获取 'token'
        3. get, post请求参数中，获取 'token'关键字
        4. cookie中，获取'token'关键字

    未获取到时抛出未认证异常
    """
    # 尝试获取header头部的token
    if request.META.get("HTTP_AUTHORIZATION"):
        token = request.META.get("HTTP_AUTHORIZATION")
    # 尝试获取 drf 中的token
    elif request.data.get('token'):
        token = request.data.get('token')
    else:
        # 尝试获取django请求参数中的token
        token = None
        for method in ['GET', 'POST']:
            if hasattr(request, method):
                token = getattr(request, method).get('token')
                if token:
                    break
        # 尝试获取cookie中的token
        if not all([token]):
            for cookie_name in ['token']:
                if request.COOKIES.get(cookie_name):
                    token = request.COOKIES.get(cookie_name)
                    break

    if not all([token]):
        raise exception.MiddlewareAuthenticationException(message='未认证的请求')
    return token


class TokenAuthentication(authentication.BaseAuthentication):
    """
        基于Token的自定义身份认证
    """

    def authenticate(self, request):
        from apps.user import models

        token = handle_token(request)

        # 根据token获取用户信息
        user_info = models.User.objects.filter(token=token).first()

        if not user_info:
            # 增加临时token
            temporary_token_info = cache.get('user_temporary_token_%s' % token)
            if isinstance(temporary_token_info, int):
                user_info = models.User.objects.filter(id=temporary_token_info).first()
                if not user_info.is_active:
                    raise exception.MiddlewareAuthenticationException(message='用户已被冻结')

                return user_info, token
            raise exception.MiddlewareAuthenticationException(message='认证信息不存在，请重新登录')
        else:
            if datetime.now() < user_info.expired_date_time:

                if not user_info.is_active:
                    raise exception.MiddlewareAuthenticationException(message='用户已被冻结')

                return user_info, token
            else:
                raise exception.MiddlewareAuthenticationException(message='认证失效，请重新登录')


@database_sync_to_async
def get_user(token):
    from apps.user import models
    user_info = models.User.objects.filter(token=token).first()
    if user_info:
        return user_info
    else:
        return AnonymousUser


class TokenAuthMiddleware:
    """channel WebSocket自定义认证"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        close_old_connections()
        if token := parse_qs(scope["query_string"].decode("utf8")).get('token', []):
            scope['user'] = await get_user(token[0])
            return await self.app(scope, receive, send)
        else:
            return AnonymousUser


def TokenAuthMiddlewareStack(app):
    return TokenAuthMiddleware(AuthMiddlewareStack(app))
