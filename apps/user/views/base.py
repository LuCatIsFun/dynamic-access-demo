from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.http import is_safe_url

from main.utils import PermissionAPIView

from apps.user.models import User
from apps.user.throttling import LoginAnonRateThrottle


class Login(PermissionAPIView):
    # 登录接口不走认证token
    authentication_classes = []
    throttle_classes = (LoginAnonRateThrottle,)

    def post(self, request):
        # 账户密码登录
        username = request.data.get('username')
        password = request.data.get('password')
        if not all([username, password]):
            return request.response.error(message="用户名或密码错误")

        user_info = authenticate(request, username=username, password=password)
        if user_info:
            auth_login(request, user_info, backend='django.contrib.auth.backends.ModelBackend')
        else:
            user_info = User.objects.filter(username=username).first()

            if user_info:
                if not user_info.is_active:
                    return request.response.error(message='糟糕，登录失败，用户已被冻结')
            return request.response.error(message='用户名或密码错误')

        response = dict()

        response['userId'] = user_info.id
        response['token'], response['token_expired'] = user_info.create_token()
        response['username'] = user_info.nickname
        response['nickname'] = user_info.nickname
        response['roles'] = []
        return request.response.success(result=response)


class Logout(PermissionAPIView):
    authentication_classes = []

    # noinspection PyMethodMayBeStatic
    def get(self, request, next_page=None, redirect_field_name=REDIRECT_FIELD_NAME):
        """
        Logs out the user and displays 'You are logged out' message.
        """
        auth_logout(request)
        if next_page is not None:
            next_page = resolve_url(next_page)

        if (redirect_field_name in request.POST or
                redirect_field_name in request.GET):
            next_page = request.POST.get(redirect_field_name,
                                         request.GET.get(redirect_field_name))
            # Security check -- don't allow redirection to a different host.
            if not is_safe_url(url=next_page, allowed_hosts=request.get_host()):
                next_page = request.path

        if next_page:
            # Redirect to this page until the session has been cleared.
            return HttpResponseRedirect(next_page)

        return HttpResponseRedirect('/')


class UserProfile(PermissionAPIView):

    def get(self, request, user_id):
        user = request.user
        assert user.id != user_id, 403
        role_info = user.role_id
        return request.response.success(result={
            'nickname': user.nickname,
            'roles': [],
            'userId': user.id,
            'username': user.username
        })


class UserPermission(PermissionAPIView):

    def get(self, request, user_id):
        user = request.user
        assert user.id != user_id, 403
        return request.response.success(result=user.permission)


class UserMenu(PermissionAPIView):

    def get(self, request, user_id):
        user = request.user
        assert user.id != user_id, 403
        return request.response.success(result=user.menu)
