"""
@time: 2020/12/22 下午3:58
"""
from rest_framework import generics
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from apps.user import serializer
from apps.user import models as UserModels
from apps.user import filters as UserFilters
from apps.user.utils.drf_permission import SuperUserPermission


class DepartmentManage(generics.ListCreateAPIView):
    permission_classes = [SuperUserPermission]
    queryset = UserModels.Department.objects.all().order_by("-create_date_time")
    serializer_class = serializer.DepartmentSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_class = UserFilters.DepartmentFilter

    def get(self, request, *args, **kwargs):
        response = self.list(request, *args, **kwargs)
        filter_data = [i['id'] for i in response.data['results']]
        return request.response.success(
            result=UserModels.Department.tree(filter_data)      # 支持搜索树形
        )

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return request.response.success(
            result={'detail': '创建成功'}
        )


class DepartmentDetail(APIView):
    permission_classes = [SuperUserPermission]

    def put(self, request, department_id):
        instance = serializer.DepartmentSerializer(
            instance=get_object_or_404(UserModels.Department, pk=department_id),
            data=request.data
        )
        instance.is_valid(raise_exception=True)
        instance.save()
        return request.response.success(
            result={'detail': '更新部门成功'}
        )

    def delete(self, request, department_id):
        instance = get_object_or_404(UserModels.Department, pk=department_id)
        instance.recursive_delete()
        return request.response.success(
            result={'detail': '删除部门成功'}
        )


class MenuManage(generics.ListCreateAPIView):
    permission_classes = [SuperUserPermission]
    queryset = UserModels.Menu.objects.all().order_by("-create_date_time")
    serializer_class = serializer.MenuSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_class = UserFilters.MenuFilter

    def get(self, request, *args, **kwargs):
        response = self.list(request, *args, **kwargs)
        filter_data = [i['id'] for i in response.data['results']]
        return request.response.success(
            result=UserModels.Menu.tree(filter_data)      # 支持搜索树形
        )

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return request.response.success(
            result={'detail': '创建成功'}
        )


class RoleManage(generics.ListCreateAPIView):
    permission_classes = [SuperUserPermission]
    queryset = UserModels.Role.objects.all().order_by("-create_date_time")
    serializer_class = serializer.RoleSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_class = UserFilters.RoleFilter

    def get(self, request, *args, **kwargs):
        return request.response.success(
            result=self.list(request, *args, **kwargs).data['results']
        )

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return request.response.success(
            result={'detail': '创建成功'}
        )


class AccountManage(generics.ListCreateAPIView):
    permission_classes = [SuperUserPermission]
    queryset = UserModels.User.objects.all().order_by("-date_joined")
    serializer_class = serializer.UserSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_class = UserFilters.UserFilter

    def get(self, request, *args, **kwargs):
        return request.response.success(
            result=self.list(request, *args, **kwargs).data['results']
        )

    def post(self, request, *args, **kwargs):
        instance = self.get_serializer(data=request.data)
        instance.is_valid(raise_exception=True)
        instance.save()
        return request.response.success(
            result={'detail': '创建成功'}
        )


class AccountDetail(APIView):
    permission_classes = [SuperUserPermission]

    def put(self, request, user_id):
        instance = serializer.UserSerializer(
            instance=get_object_or_404(UserModels.User, pk=user_id),
            data=request.data,
            context={'request': request}
        )
        instance.is_valid(raise_exception=True)
        instance.save()
        return request.response.success(
            result={'detail': '更新用户成功'}
        )

    def delete(self, request, user_id):
        instance = get_object_or_404(UserModels.User, pk=user_id)
        assert user_id != str(request.user.id), '你不能删除你自己 (￣.￣)'
        instance.delete()
        return request.response.success(
            result={'detail': '删除用户成功'}
        )


class RoleDetail(APIView):
    permission_classes = [SuperUserPermission]

    def put(self, request, role_id):
        instance = serializer.RoleSerializer(
            instance=get_object_or_404(UserModels.Role, pk=role_id),
            data=request.data,
            context={'request': request}
        )
        instance.is_valid(raise_exception=True)
        instance.save()
        return request.response.success(
            result={'detail': '更新角色成功'}
        )

    def delete(self, request, role_id):
        instance = get_object_or_404(UserModels.Role, pk=role_id)
        instance.delete()
        return request.response.success(
            result={'detail': '删除角色成功'}
        )


class MenuDetail(APIView):
    permission_classes = [SuperUserPermission]

    def put(self, request, menu_id):
        instance = serializer.MenuSerializer(
            instance=get_object_or_404(UserModels.Menu, pk=menu_id),
            data=request.data
        )
        instance.is_valid(raise_exception=True)
        instance.save()
        return request.response.success(
            result={'detail': '更新菜单成功'}
        )

    def delete(self, request, menu_id):
        instance = get_object_or_404(UserModels.Menu, pk=menu_id)
        instance.recursive_delete()
        return request.response.success(
            result={'detail': '删除菜单成功'}
        )


class PermissionCodeManage(generics.ListCreateAPIView):
    permission_classes = [SuperUserPermission]
    queryset = UserModels.PermissionCode.objects.all().order_by("-create_date_time")
    serializer_class = serializer.PermissionCodeSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_class = UserFilters.PermissionCodeFilter

    def post(self, request, *args, **kwargs):
        instance = self.get_serializer(data=request.data)
        instance.is_valid(raise_exception=True)
        instance.save()
        return request.response.success(
            result={'detail': '创建成功'}
        )


class PermissionCodeDetail(APIView):
    permission_classes = [SuperUserPermission]

    def put(self, request, permission_code_id):
        instance = serializer.PermissionCodeSerializer(
            instance=get_object_or_404(UserModels.PermissionCode, pk=permission_code_id),
            data=request.data
        )
        instance.is_valid(raise_exception=True)
        instance.save()
        return request.response.success(
            result={'detail': '更新权限成功'}
        )

    def delete(self, request, permission_code_id):
        instance = get_object_or_404(UserModels.PermissionCode, pk=permission_code_id)
        instance.delete()
        return request.response.success(
            result={'detail': '删除权限成功'}
        )


class PermissionCodeRoleRelationManage(generics.ListCreateAPIView):
    permission_classes = [SuperUserPermission]
    queryset = UserModels.PermissionCodeRoleRelation.objects.all().order_by("-code")
    serializer_class = serializer.PermissionCodeRoleRelationSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_class = UserFilters.PermissionCodeRoleRelationFilter

    def get(self, request, *args, **kwargs):
        return request.response.success(
            result=self.list(request, *args, **kwargs).data['results']
        )
