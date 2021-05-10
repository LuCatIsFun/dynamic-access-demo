"""
@author: liyao
@contact: liyao2598330@126.com
@time: 2021/4/23 11:21 上午
"""
from channels.routing import URLRouter
from django.urls import re_path

from apps.user.urls.websocket import base as user_base

websocket_urlpatterns = URLRouter([
    re_path('^ws/v1/$', URLRouter([
        re_path('^user/$', user_base.websocket_routing),
    ])),
])
