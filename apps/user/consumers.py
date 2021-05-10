"""
@author: liyao
@contact: liyao2598330@126.com
@time: 2021/4/23 11:32 上午
"""

from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser
import json


class NoticeConsumer(WebsocketConsumer):
    def connect(self):
        if not isinstance(self.scope.get('user'), AnonymousUser):
            self.accept()
        else:
            self.close(code=1008)

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        self.send(text_data=json.dumps({
            'message': text_data
        }))
