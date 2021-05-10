"""
@time: 2020/8/14 4:39 下午
"""
import json

from django.http import HttpResponse

ENABLE_REQUEST_SIGNATURE = False  # 开启签名校检
SIGNATURE_SECRET = 'wrXxDI3FlGO8vqp5Gb3FlWu25idm'  # 私钥
SIGNATURE_ALLOW_TIME_ERROR = 60  # 允许时间误差
SIGNATURE_PASS_URL_NAME = [
]
SIGNATURE_PASS_URL_REGULAR = [
]

SIGNATURE_RESPONSE = 'main.settings.signature_config.signature_backend'


def signature_backend():
    return HttpResponse(json.dumps({'code': -1, 'msg': '请以正确的姿势进入 🤨'}), content_type="application/json")
