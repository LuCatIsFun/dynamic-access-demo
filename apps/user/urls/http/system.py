"""echidna URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path

from apps.user.views import system as views

urlpatterns = [
    re_path('^departments/$', views.DepartmentManage.as_view(), name='DepartmentManage'),
    re_path('^department/(?P<department_id>[a-zA-z0-9]{22})/$', views.DepartmentDetail.as_view(), name='DepartmentDetail'),
    re_path('^menus/$', views.MenuManage.as_view(), name='MenuManage'),
    re_path('^menu/(?P<menu_id>[a-zA-z0-9]{22})/$', views.MenuDetail.as_view(),
            name='MenuDetail'),
    re_path('^roles/$', views.RoleManage.as_view(), name='RoleManage'),
    re_path('^role/(?P<role_id>[a-zA-z0-9]{22})/$', views.RoleDetail.as_view(),
            name='RoleDetail'),
    re_path('^accounts/$', views.AccountManage.as_view(), name='AccountManage'),
    re_path('^account/(?P<user_id>[0-9]*)/$', views.AccountDetail.as_view(),
            name='AccountDetail'),
    re_path('^permission/codes/$', views.PermissionCodeManage.as_view(), name='PermissionCodeManage'),
    re_path('^permission/code/(?P<permission_code_id>[a-zA-z0-9]{22})/$', views.PermissionCodeDetail.as_view(),
                name='PermissionCodeDetail'),
    re_path('^permission/code_relations/$', views.PermissionCodeRoleRelationManage.as_view(), name='PermissionCodeRoleRelationManage'),
]
