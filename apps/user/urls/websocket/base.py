"""
@author: liyao
@contact: liyao2598330@126.com
@time: 2021/4/23 11:28 上午
"""
from django.urls import path
from apps.user.consumers import NoticeConsumer
from channels.routing import URLRouter

websocket_routing = URLRouter([
    path('notice/', NoticeConsumer.as_asgi()),
])
