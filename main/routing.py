"""
@author: liyao
@contact: liyao2598330@126.com
@time: 2021/4/23 11:06 上午
"""
from apps.user.utils.authentication import TokenAuthMiddlewareStack
from channels.routing import URLRouter
from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
# from main.urls.websocket import base
from apps.user.urls.websocket import base
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': TokenAuthMiddlewareStack(
        base.websocket_routing
    ),
})
