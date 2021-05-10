"""
@author: liyao
@contact: liyao2598330@126.com
@time: 2021/4/20 12:51 下午
"""
import django_filters
from apps.user.models import Department
from apps.user.models import PermissionCode
from apps.user.models import PermissionCodeRoleRelation
from apps.user.models import Menu
from apps.user.models import Role
from apps.user.models import User
from django.db.models import Q


class DepartmentFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    status = django_filters.NumberFilter(field_name='status')

    class Meta:
        model = Department
        fields = ('name', 'status')


class MenuFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    status = django_filters.NumberFilter(field_name='status')

    class Meta:
        model = Menu
        fields = ('name', 'status')


class RoleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    status = django_filters.NumberFilter(field_name='status')

    class Meta:
        model = Role
        fields = ('name', 'status')


class PermissionCodeFilter(django_filters.FilterSet):
    note = django_filters.CharFilter(field_name='note', lookup_expr='icontains')
    code = django_filters.NumberFilter(field_name='code')

    class Meta:
        model = PermissionCode
        fields = ('note', 'code')


class PermissionCodeRoleRelationFilter(django_filters.FilterSet):
    roleId = django_filters.CharFilter(field_name='role_id')
    code = django_filters.NumberFilter(field_name='code')
    permissionCodeId = django_filters.CharFilter(field_name='permission_code_id')

    class Meta:
        model = PermissionCodeRoleRelation
        fields = ('roleId', 'code', 'permissionCodeId')


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')
    nickname = django_filters.CharFilter(field_name='nickname', lookup_expr='icontains')
    user_id = django_filters.CharFilter(field_name='id', lookup_expr='icontains')
    department_id = django_filters.CharFilter(field_name='department_id', method="department_recursive_query")

    def department_recursive_query(self, queryset, name, value):
        """部门ID递归查询，如查询技术部，则实际递归查询技术部下所有子部门"""
        department_list = []
        query = Q(department_id=value)

        def handle_department(department_id):
            if department_id not in department_list and department_id != value:
                department_list.append(department_id)

            department_info = Department.objects.filter(parent=department_id)
            if department_info:
                for dept in department_info:
                    handle_department(dept.id)

        handle_department(value)
        for q in department_list:
            query = query | Q(department_id=q)
        return queryset.filter(query)

    class Meta:
        model = User
        fields = ('username', 'nickname', 'user_id')
