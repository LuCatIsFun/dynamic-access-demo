"""
@time: 2020/8/14 1:51 下午
"""

import json


class BaseException(Exception):
    """
        Error handling
    """

    code = -1

    response_code = 500

    console_log = False

    def __init__(self, message: str):
        super(BaseException, self).__init__()
        self._msg = message

    @property
    def message(self):
        return self._msg

    def __str__(self):
        return "{message}".format(message=json.dumps(self.message, ensure_ascii=False))


class MiddlewareAuthenticationException(BaseException):
    response_code = 401
    code = -1
