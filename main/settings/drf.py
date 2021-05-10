"""
@time: 2020/7/31 12:30 下午
"""

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'main.utils.handlers.drf_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.user.utils.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ],
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '3/second',
        'user': '10/second'
    },
    "UNAUTHENTICATED_TOKEN": None,  # 匿名，request.auth = None
    "DEFAULT_PARSER_CLASSES": [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'apps.user.utils.drf_permission.CodePermission',
    ],
    'DEFAULT_PAGINATION_CLASS': 'main.utils.pagination.Pagination',  # LimitOffsetPagination 分页风格
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',)
}
