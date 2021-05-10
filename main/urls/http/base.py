"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import re_path, include
from main import views

from main.utils import http_403_handle
from main.utils import http_404_handle
from main.utils import http_500_handle


urlpatterns = [
    re_path('^api/v1/user/', include('apps.user.urls.http.base'), name='user_api'),
    re_path('^api/v1/system/', include('apps.user.urls.http.system'), name='system_api'),
    # re_path('^api/v1/example/', include('apps.example.urls'), name='example_api'),

    re_path('^health$', views.health, name='health_check'),
    re_path('^api/demo/$', views.Demo.as_view(), name='Demo')
]


handler403 = http_403_handle
handler404 = http_404_handle
handler500 = http_500_handle
