"""
@time: 2020/7/30 4:42 下午
"""

import logging
import secrets
import time
import uuid

from django.http.response import Http404
from django.utils.deprecation import MiddlewareMixin

from main.exception import BaseException

from main.utils import CommonReturn

logger = logging.getLogger(__name__)
common_return = CommonReturn()


class RegisterMiddleware(MiddlewareMixin):

    @staticmethod
    def process_request(request):
        request.process_time_start = time.process_time()
        request.response_time_start = time.perf_counter()
        request.request_id = 'r_%s' % secrets.token_urlsafe(20)
        request.response = common_return

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        pass

    @staticmethod
    def process_response(request, response):
        response.setdefault('process_time', "%.2fms" % ((time.process_time() - request.process_time_start) * 100))
        response.setdefault('response_time', "%.2fms" % ((time.perf_counter() - request.response_time_start) * 100))
        response.setdefault('r_id', request.request_id)
        return response

    def process_exception(self, request, exception):
        import traceback
        error_detail = traceback.format_exc()
        error_id = uuid.uuid5(uuid.NAMESPACE_DNS, error_detail)

        # 404异常直接返回
        if isinstance(exception, Http404):
            raise exception

        # assert异常
        elif isinstance(exception, AssertionError):
            # 判断是否有错误详情，没有则按http 500错误信息返回
            detail = exception.args[0] \
                if exception.args else common_return.http_response_message.get_message(500)['message']
            # (简写) int类型判断是否为可用的http返回码，如果是则返回对应http错误信息
            if isinstance(detail, int) and detail in common_return.http_response_message.http_status_code:
                return request.response(
                    response_code=detail,
                    message=common_return.http_response_message.get_message(detail)['message']
                )
            else:
                return request.response.error(message=detail)

        elif isinstance(exception, BaseException):
            if exception.console_log:
                logger.error('error Id:{error_id}\ndetail:{detail}'.format(error_id=error_id, detail=error_detail))
            return request.response(message=exception.message, response_code=exception.response_code, code=exception.code)
        else:
            logger.error('error Id:{error_id}\ndetail:{detail}'.format(error_id=error_id, detail=error_detail))
            return request.response.error(message='糟糕，服务器处理异常，您可凭借此ID：%s 咨询管理员' % error_id)
