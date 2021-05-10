"""
@author: liyao
@contact: liyao2598330@126.com
@time: 2020/12/29 下午3:07
"""
from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    page_size = 10  # 表示每页的默认显示数量
    page_size_query_param = 'pageSize'  # 表示url中每页数量参数
    page_query_param = 'pageCurrent'  # 表示url中的页码参数
    max_page_size = 100
