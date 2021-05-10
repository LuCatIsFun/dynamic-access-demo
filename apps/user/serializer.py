"""
@author: liyao
@contact: liyao2598330@126.com
@time: 2021/3/26 下午1:17
"""
from shortuuid import uuid
from rest_framework import serializers
from django.db.models import Q
from django.utils.translation import ugettext as _

from apps.user.models import Department
from apps.user.models import Menu
from apps.user.models import User
from apps.user.models import Role
from apps.user.models import MenuRoleRelation
from apps.user.models import PermissionCodeRoleRelation
from apps.user.models import PermissionCode


class DepartmentSerializer(serializers.ModelSerializer):
    create_date_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    id = serializers.CharField(read_only=True)
    status = serializers.CharField(
        error_messages={
            'required': _('部门状态不能为空')
        })
    name = serializers.CharField(
        error_messages={
            'required': _('部门名称不能为空')
        })

    class Meta:
        model = Department
        fields = "__all__"

    def create(self, validated_data):
        assert not Department.objects.filter(name=validated_data.get('name')), '部门名称已存在'
        return Department.objects.create(id=uuid(), **validated_data)

    def update(self, instance, validated_data):
        # instance.name = validated_data.get('name')
        # instance.remark = validated_data.get('remark')
        # instance.status = validated_data.get('status')
        # instance.sort = validated_data.get('sort')
        # instance.parent = validated_data.get('parent')
        # instance.save()
        for d in validated_data:
            if hasattr(instance, d):
                setattr(instance, d, validated_data.get(d))
        instance.save()
        return instance


class PermissionCodeSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    create_date_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    role_id = serializers.CharField(default=None, write_only=True, error_messages={'required': '角色ID不能为空'})
    code = serializers.IntegerField(min_value=1001, error_messages={'min_value': '权限值1~1000为保留值'})

    class Meta:
        model = PermissionCode
        fields = "__all__"

    def create(self, validated_data):
        code, role_id, note = validated_data.get('code'), validated_data.get('role_id'), validated_data.get('note')
        assert not PermissionCode.objects.filter(code=code), '权限值已存在'
        permission_code_id = uuid()
        PermissionCodeRoleRelation.objects.create(
            id=uuid(), role_id=role_id, permission_code_id=permission_code_id, code=code,
            note=note
        )
        return PermissionCode.objects.create(id=permission_code_id, code=code, note=note)

    def update(self, instance, validated_data):
        for d in validated_data:
            if hasattr(instance, d):
                setattr(instance, d, validated_data.get(d))
        instance.save()
        PermissionCodeRoleRelation.objects.filter(permission_code_id=instance.id).update(
            code=validated_data.get('code'), note=validated_data.get('note')
        )
        return instance


class PermissionCodeRoleRelationSerializer(serializers.ModelSerializer):
    create_date_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = PermissionCodeRoleRelation
        fields = "__all__"


class MenuSerializer(serializers.ModelSerializer):
    create_date_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    id = serializers.CharField(read_only=True)

    # 前端需要字符串格式的
    status = serializers.CharField()
    is_link = serializers.CharField()
    type = serializers.CharField()
    show = serializers.CharField()
    keepalive = serializers.CharField()
    link_type = serializers.CharField()

    class Meta:
        model = Menu
        fields = "__all__"

    def create(self, validated_data):
        return Menu.objects.create(id=uuid(), **validated_data)

    def update(self, instance, validated_data):
        for d in validated_data:
            if hasattr(instance, d):
                setattr(instance, d, validated_data.get(d))
        instance.save()
        MenuRoleRelation.objects.filter(menu_id=instance.id).update(data=instance.json)
        return instance


class RoleSerializer(serializers.ModelSerializer):
    create_date_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    id = serializers.CharField(read_only=True)
    menu = serializers.JSONField(read_only=True)
    status = serializers.CharField()

    class Meta:
        model = Role
        fields = "__all__"

    def create(self, validated_data):
        role_id = uuid()
        assert Role.objects.filter(name=validated_data.get('name')).count() == 0, '角色名称已存在'
        assert Role.objects.filter(key=validated_data.get('key')).count() == 0, '角色值已存在'
        self.handle_menu_change(role_id=role_id, is_update=False)
        return Role.objects.create(id=role_id, **validated_data)

    def update(self, instance, validated_data):
        for d in validated_data:
            setattr(instance, d, validated_data.get(d))
        instance.save()
        self.handle_menu_change(is_update=True, role_id=instance.id)
        return instance

    def handle_menu_change(self, role_id: str, is_update: bool, ):
        """更新创建角色时，处理菜单变化"""
        menus = self.context.get('request').data.get('menu')
        assert not menus or isinstance(menus, list), 400

        if is_update:  # 删除现有菜单
            MenuRoleRelation.objects.filter(role_id=role_id).delete()

        menu_list = []

        def handle_menu(_menu_id):
            """因为树形只能返回最后选中的节点，非全选状态下，无法返回选中节点的父节点，这里要兼容递归查询一下"""
            menu_info = Menu.objects.get(id=_menu_id)

            if _menu_id not in menu_list:  # 防止重复处理
                menu_list.append(_menu_id)
                MenuRoleRelation.objects.create(id=uuid(), role_id=role_id, menu_id=_menu_id, data=menu_info.json)

            if menu_info.parent:
                handle_menu(menu_info.parent)

        if menus:
            for menu_id in menus:
                handle_menu(menu_id)
        return True


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    id = serializers.CharField(read_only=True)
    role_name = serializers.CharField(read_only=True)
    role_id = serializers.CharField(default=None, allow_null=True)
    department_id = serializers.CharField(default=None, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'date_joined', 'department_id', 'role_name', 'role_id', 'nickname', 'email')

    def create(self, validated_data):
        # 预检查
        assert not User.objects.filter(username=validated_data.get('username')), '用户名已存在'

        instance = User.objects.create_user(**validated_data)

        # 处理额外的更新
        return self.handle_user_change(instance=instance, is_update=False)

    def update(self, instance, validated_data):
        """更新用户逻辑"""
        # 预检查
        assert not validated_data.get('username') or not User.objects.filter(
            ~Q(id=instance.id) & Q(username=validated_data.get('username'))
        ), '用户名已存在'
        # 保存更新基础信息
        for d in validated_data:
            setattr(instance, d, validated_data.get(d))
        instance.save()     # 注意 instance的保存顺序，可能会导致保存互相覆盖

        # 处理额外的更新
        return self.handle_user_change(instance=instance, is_update=True)

    def handle_user_change(self, instance, is_update: bool):
        request = self.context.get('request')
        assert request, 500  # 'UserSerializer：更新用户需要在context中增加request参数'

        password = request.data.get('password')

        # 1.判断是否需要更新密码
        assert is_update or password, '新用户密码不能为空哦'
        if password:
            instance.set_password(password)
            instance.token = None
            instance.save()
        return instance
