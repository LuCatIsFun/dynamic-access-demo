"""
@time: 2020/7/28 5:09 下午
"""

__all__ = ['http_403_handle', 'http_404_handle', 'http_500_handle', 'drf_exception_handler']


# django rest framework 自定义异常信息
from rest_framework.exceptions import ValidationError


def drf_exception_handler(exc, context):
    from rest_framework.views import exception_handler

    response = exception_handler(exc, context)

    if response is not None:
        from main.utils import HttpResponseMessage

        if isinstance(exc, ValidationError):    # serializers验证错误取第一条异常
            message = exc.detail[next(iter(exc.detail))][0]
        else:
            message = HttpResponseMessage.get_message(response.status_code)['message']

        response.data = {
            'code': -1,
            'message': message
        }
        return response
    return None


# SEO 不返回错误的HTTP状态码
def http_403_handle(request, exception):
    return request.response(response_code=403)


def http_404_handle(request, exception):
    return request.response(response_code=404)


def http_500_handle(exception):
    from main.utils import CommonReturn

    response = CommonReturn()
    return response(response_code=500)
