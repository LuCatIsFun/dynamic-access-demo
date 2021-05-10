"""
@author: liyao
@contact: liyao2598330@126.com
@software: pycharm
@time: 2020/3/30 11:41 下午
@desc:
"""

import datetime
import functools
import json

from django.http import HttpResponse


# Json 无法解析 datetime 类型的数据，构建 DateEncoder 类解决 datetime 解析问题
class DateEncoder(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")

        else:
            return json.JSONEncoder.default(self, obj)


# 利用偏函数重写 dumps 方法，使其支持解析 datetime 类型
json.dumps = functools.partial(json.dumps, cls=DateEncoder)


"""
@author: liyao
@contact: liyao2598330@126.com
@time: 2020/8/14 12:02 下午
"""

__all__ = ['HttpResponseMessage', 'CommonReturn']


class HttpResponseMessage:
    """
        根据不同的http状态码，设置统一的默认返回信息
        https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status

        >>> from main.utils import HttpResponseMessage
        >>> hrm = HttpResponseMessage()
        >>> hrm(200)
        {'msg': 'ok'}
        >>> hrm.get_message(200)
        {'msg': 'ok'}
    """

    http_default = '服务可能发生了一点点小问题，程序员哥哥正在加班处理..'
    http_status_code = [200, 201, 400, 401, 403, 404, 405, 429, 500]

    http_200 = 'success'
    http_201 = '资源创建成功'

    http_400 = '糟糕，缺少必要的参数或参数格式异常'
    http_401 = '糟糕，登陆信息失效或异常，请重新登陆后在尝试'
    http_403 = '糟糕，您没有权限访问此资源'
    http_404 = '您请求的资源不存在'
    http_405 = '不支持此方式请求，请以正确的姿势进入'
    http_429 = '请求过快，请降低访问频率'

    http_500 = '处理异常，服务器可能抽风了'

    @classmethod
    def __call__(cls, code: int, *args, **kwargs) -> dict:
        """
            根据http状态码返回默认信息和表情
        :param code: http_status_code
        :return: eg. {'msg': 'ok', 'mood': '(ノ￣ω￣)ノ'}
        """
        return cls.get_message(code)

    @classmethod
    def get_message(cls, code: int) -> dict:
        """
            根据http状态码返回默认信息和表情
        :param code: http_status_code
        :return: eg. {'msg': 'ok', 'mood': '(ノ￣ω￣)ノ'}
        """
        assert isinstance(code, int) and 200 <= code < 600, 'code Must be a standard HTTP status code'
        message = getattr(cls, 'http_%s' % code) if hasattr(cls, 'http_%s' % code) else cls.http_default
        return {
            'message': message,
        }


class CommonReturn(object):
    """
        公共返回函数，封装了一个django HttpResponse 对象，自动把传入的参数转为json
    """
    # 业务返回码
    success_code = 0
    failed_code = -1

    # 默认http状态返回码
    http_response_default_code = 200
    http_response_success_code = 200
    http_response_failed_code = 200

    http_response_message = HttpResponseMessage()

    @classmethod
    def __call__(cls, *args, **kwargs):
        """
        :param response_code:
        :param kwargs:
        :return:
        """
        if 'code' in kwargs:
            return cls.return_data(args, kwargs, code=kwargs['code'])
        return cls.return_data(args, kwargs)

    @staticmethod
    def handle_data_type(args: (list, dict), kwargs: dict) -> None:
        assert 'code' not in kwargs.keys() or 'code' in kwargs.keys() and \
               isinstance(kwargs['code'], int), kwargs['code']
        assert not args or isinstance(args[0], (list, dict, str)), args

    @classmethod
    def success(cls, *args: (dict, list), **kwargs) -> HttpResponse:
        """
            Success message return format

            if args exist，the parameters in kwargs will be overridden

            >>> response = CommonReturn()
            >>> response.success(message="hello world")
            '<HttpResponse status_code=200, "application/json">'
            >>> response.success(message="hello world").getvalue()
            'b\'{"code": 0, "msg": "hello world"}\''

        :param response_code: set http response code
        :return:
        """
        cls.handle_data_type(args, kwargs)

        code = kwargs['code'] if 'code' in kwargs.keys() else cls.success_code
        kwargs['response_code'] = kwargs['response_code'] if 'response_code' in kwargs.keys() else \
            cls.http_response_success_code
        return cls.return_data(args, kwargs, code=code)

    @classmethod
    def error(cls, *args: (dict, list), **kwargs) -> HttpResponse:
        """
            Failure message return format

            if args exist，the parameters in kwargs will be overridden

            >>> response = CommonReturn()
            >>> response.error(message="have some error")
            '<HttpResponse status_code=500, "application/json">'
            >>> response.error(message="have some error").getvalue()
            'b\'{"code": -1, "msg": "have some error"}\''

        :param response_code: set http response code
        :return:
        """
        cls.handle_data_type(args, kwargs)

        code = kwargs['code'] if 'code' in kwargs.keys() else cls.failed_code
        kwargs['response_code'] = kwargs['response_code'] if 'response_code' in kwargs.keys() else \
            cls.http_response_failed_code
        return cls.return_data(args, kwargs, code=code)

    @classmethod
    def return_data(cls, args: tuple, kwargs: dict, code: int = None):
        response = {}
        response_code = cls.http_response_default_code
        for k in kwargs.keys():
            if k == 'response_code':
                assert isinstance(kwargs[k], int), kwargs[k]
                response_code = kwargs[k]

                http_response_message = cls.http_response_message(code=response_code)
                for key in ['message']:
                    if key not in kwargs.keys():
                        response[key] = http_response_message[key]

            else:
                response[k] = kwargs[k]

        if args:
            response = args[0]

        if isinstance(response, dict):
            if not code and response_code != 200:
                response['code'] = cls.failed_code
            else:
                response['code'] = code if isinstance(code, int) else cls.success_code

            try:
                return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json",
                                    status=response_code)
            except UnicodeEncodeError:
                return HttpResponse(json.dumps(response), content_type="application/json",
                                    status=response_code)
        else:
            return HttpResponse(response, status=response_code)

