import datetime
import hashlib
import json

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from main.utils import BaseUtil


class User(AbstractUser):
    """继承自带user类，增加拓展字段"""
    USER_ROLE_CHOICES = (
        ('user', u'普通用户'),
        ('admin', u'管理员'),
    )
    mobile = models.CharField(max_length=30, blank=True, verbose_name='电话')
    role_id = models.CharField(max_length=30, verbose_name='用户角色ID', blank=True, null=True)
    department_id = models.CharField(max_length=30, verbose_name='用户部门ID', blank=True, null=True)
    avatar = models.CharField(max_length=500, verbose_name='头像地址')
    nickname = models.CharField(max_length=30, default='未设置昵称', verbose_name='昵称')
    token = models.CharField(max_length=64, blank=True, null=True, verbose_name='认证token')
    expired_date_time = models.DateTimeField(default=timezone.now, verbose_name="失效时间")
    dead_date_time = models.DateTimeField(default=timezone.now, verbose_name="最长可用时间")

    TOKEN_EXPIRED_TIME = 7

    @staticmethod
    def generate_token():
        now = str(datetime.datetime.now())
        md5 = hashlib.md5()
        md5.update(bytes(now + settings.SECRET_KEY, encoding='utf-8'))
        return md5.hexdigest()

    def create_token(self):
        """
            删除现有token，重新创建新token
        """
        self.token = None
        token, expired_date_time = self.flush_token()
        return token, expired_date_time

    def flush_token(self):
        """
            刷新token，token最大可用时间无法超过最长可用时间，如果不存在则创建新token
        """
        token_expired_time = settings.TOKEN_EXPIRED_TIME if hasattr(settings, 'TOKEN_EXPIRED_TIME') \
            else self.TOKEN_EXPIRED_TIME

        if self.token:
            expired_date_time = datetime.datetime.now() + datetime.timedelta(days=token_expired_time)

            if self.expired_date_time >= self.dead_date_time:
                self.token = None
            elif expired_date_time >= self.dead_date_time:
                self.expired_date_time = self.dead_date_time
            else:
                self.expired_date_time = expired_date_time

            token = self.token
        else:
            token = self.generate_token()
            now = datetime.datetime.now()
            self.token = token
            self.expired_date_time = now + datetime.timedelta(days=token_expired_time)
            self.dead_date_time = now + datetime.timedelta(days=30)

        self.save()
        return token, self.expired_date_time

    @property
    def menu(self) -> list:
        """根据角色获取用户菜单"""

        # 用户需要基础路由dashboard，否则登录后无组件可以跳转。
        # 判断用户是否自定义了dashboard，没有则插入默认首页
        def has_dashboard(_menu):
            for m in _menu:
                if m['path'] == '/dashboard':
                    return True
            return False

        role_info = Role.objects.filter(id=self.role_id).first()
        result = []
        if role_info:
            data = [json.loads(i[0]) for i in MenuRoleRelation.objects.filter(role_id=self.role_id).values_list('data')]
            result = BaseUtil.sort_item(data=data)

        # 超级管理员插入额外拓展菜单
        if self.is_superuser:
            result.extend(Menu.superuser_menu())

        # 判断处理dashboard
        if result:
            if not has_dashboard(result):
                result.insert(0, Menu.base_dashboard_menu())
            menu = result
        else:
            menu = Menu.base_menu()
        return menu

    @property
    def permission(self) -> list:
        if self.role_id:
            permission_info = PermissionCodeRoleRelation.objects.filter(role_id=self.role_id).values_list('code')
            return [p[0] for p in permission_info] if permission_info else []
        else:
            return []

    @property
    def role(self) -> dict:
        if self.role_id:
            role_info = Role.objects.filter(id=self.role_id).first()
            if role_info:
                return {
                    'roleName': role_info.name,
                    'value': role_info.key
                }
        return {}

    @property
    def role_name(self):
        """用户角色名称"""
        if self.role_id:
            role_info = Role.objects.filter(id=self.role_id).first()
            if role_info:
                return role_info.name

        return None

    class Meta:
        default_permissions = ()
        verbose_name = '用户'
        verbose_name_plural = '用户管理'


class Role(models.Model):
    """角色"""
    STATUS = (
        (1, '启用'),
        (2, '停用')
    )
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=100, verbose_name="名称")
    status = models.IntegerField(choices=STATUS, verbose_name="状态")
    key = models.CharField(max_length=100, verbose_name="角色Key")
    remark = models.CharField(max_length=200, verbose_name="备注")
    create_date_time = models.DateTimeField(default=timezone.now)

    @property
    def menu(self):
        return [i[0] for i in set(MenuRoleRelation.objects.filter(role_id=self.id).values_list('menu_id'))]

    class Meta:
        default_permissions = ()
        verbose_name = '角色'

    def delete(self, using=None, keep_parents=False):
        MenuRoleRelation.objects.filter(role_id=self.id).delete()
        User.objects.filter(role_id=self.id).update(role_id=None)
        return super().delete()


class Menu(models.Model):
    """系统菜单"""
    STATUS = (
        (1, '启用'),
        (2, '停用')
    )
    LINK_TYPE = (
        (1, '内嵌'),
        (2, '外链')
    )
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=100, verbose_name="名称")
    i18n = models.CharField(max_length=100, verbose_name="国际化地址", null=True, blank=True)
    path = models.CharField(max_length=100, verbose_name="路径")
    status = models.IntegerField(choices=STATUS, verbose_name="状态")
    sort = models.IntegerField(verbose_name="菜单排序")
    keepalive = models.IntegerField(verbose_name="开启缓存")
    component_name = models.CharField(max_length=100, verbose_name="组件名称", null=True, blank=True)
    component_path = models.CharField(default="LAYOUT", max_length=200, verbose_name="组件地址", null=True, blank=True)
    icon = models.CharField(max_length=100, verbose_name="图标", null=True, blank=True)
    redirect = models.CharField(max_length=100, verbose_name="重定向", null=True, blank=True)
    is_link = models.IntegerField(verbose_name="外链", null=True, blank=True)
    link_type = models.IntegerField(verbose_name="外链类型", choices=LINK_TYPE, null=True, blank=True)
    show = models.IntegerField(verbose_name="是否显示", null=True, blank=True)
    type = models.IntegerField(verbose_name="组件类型")
    permission = models.CharField(max_length=100, verbose_name="权限标识", null=True, blank=True)
    parent = models.CharField(max_length=30, verbose_name="菜单父级", null=True, blank=True)

    create_date_time = models.DateTimeField(default=timezone.now)

    class Meta:
        default_permissions = ()
        verbose_name = '菜单'
        verbose_name_plural = '菜单管理'

    @staticmethod
    def tree(filter_data: list = None):  # filter_data 指定搜索结果的ID，不在此列表中的数据会从树形中剔除
        """以树形获取当前部门"""
        from apps.user.serializer import MenuSerializer

        data = BaseUtil.sort_item(
            data=MenuSerializer(Menu.objects.all(), many=True).data
        )

        if isinstance(filter_data, list):
            data = BaseUtil.filter_item(data, filter_data)

        return data

    def recursive_delete(self):
        """递归删除自己及所有子节点"""

        def handle_delete(parent_id):
            response = []
            instance = Menu.objects.filter(parent=parent_id)

            if instance.count() > 0:
                for item in instance:
                    response.extend(handle_delete(item.id))

            response.append(parent_id)
            return list(set(response))

        for menu_id in handle_delete(self.id):
            MenuRoleRelation.objects.filter(menu_id=menu_id).delete()
            Menu.objects.filter(id=menu_id).delete()

        return True

    @property
    def meta(self):
        return {
            'title': self.i18n if self.i18n else self.name,
            'icon': self.icon,
            'frameSrc': self.path if self.is_link and self.link_type == 1 else None,
            'ignoreKeepAlive': self.keepalive == 2
        }

    @property
    def component(self):
        self.type = int(self.type)
        if self.is_link:
            return 'IFRAME'
        else:
            if self.type == 1:
                return 'LAYOUT'
            else:
                return self.component_path

    @property
    def dict(self):
        """将model转化为前端需要的dict格式"""
        if self.show:
            component_name = self.component_name if self.component_name else self.name
            result = dict(path=('/' + self.component_name) if self.is_link == 1 and self.link_type == 1 else self.path,
                          component=self.component, name=component_name, meta=self.meta,
                          parent=self.parent, sort=self.sort, id=self.id)
            if self.type == 1 and self.redirect:
                result['redirect'] = self.redirect
        else:
            result = None

        return result

    @property
    def json(self):
        """将model转化为前端需要的json格式"""
        return json.dumps(self.dict)

    @staticmethod
    def base_menu():
        """没有任何权限用户的菜单"""
        return [
            {
                "path": "/dashboard",
                "name": "Welcome",
                "component": "/dashboard/blank/index",
                "meta": {
                    "title": "routes.dashboard.dashboard",
                    "affix": True,
                    "icon": "bx:bx-home"
                }
            }
        ]

    @staticmethod
    def superuser_menu():
        """默认写死的管理员权限，需要与前端对应，否则初始用户无菜单可操作"""
        return [
            {
                "path": "/system",
                "name": "System",
                "component": "LAYOUT",
                "redirect": "/system/account",
                "meta": {
                    "icon": "carbon:user-role",
                    "title": "routes.system.moduleName"
                },
                "children": [
                    {
                        "path": "account",
                        "name": "Account",
                        "component": "/sys/system/account/index",
                        "meta": {
                            "title": "routes.system.account",
                        },
                    },
                    {
                        "path": "role",
                        "name": "Role",
                        "component": "/sys/system/role/index",
                        "meta": {
                            "title": "routes.system.role"
                        }
                    },
                    {
                        "path": "menu",
                        "name": "Menu",
                        "component": "/sys/system/menu/index",
                        "meta": {
                            "title": "routes.system.menu"
                        }
                    },
                    {
                        "path": "dept",
                        "name": "Dept",
                        "component": "/sys/system/dept/index",
                        "meta": {
                            "title": "routes.system.dept"
                        }
                    }
                ]
            }
        ]

    @staticmethod
    def base_dashboard_menu():
        """基础用户仪表盘"""
        return {
            "path": "/dashboard",
            "name": "Welcome",
            "component": "/dashboard/workbench/index",
            "meta": {
                "title": "routes.dashboard.workbench",
                "affix": True,
                "icon": "bx:bx-home"
            }
        }


class PermissionCode(models.Model):
    """权限代码"""
    id = models.CharField(max_length=30, primary_key=True)
    code = models.IntegerField(verbose_name="权限码")
    note = models.CharField(max_length=100, verbose_name="权限码说明")
    create_date_time = models.DateTimeField(default=timezone.now)

    class Meta:
        default_permissions = ()
        verbose_name = '权限代码'

    def delete(self, using=None, keep_parents=False):
        PermissionCodeRoleRelation.objects.filter(permission_code_id=self.id).delete()
        return super().delete()


class PermissionCodeRoleRelation(models.Model):
    """菜单关系表"""
    id = models.CharField(max_length=30, primary_key=True)
    role_id = models.CharField(max_length=30, verbose_name="角色ID")
    permission_code_id = models.CharField(max_length=30, verbose_name="权限代码ID")
    code = models.IntegerField(verbose_name="权限码")
    note = models.CharField(max_length=100, verbose_name="权限码说明")

    class Meta:
        default_permissions = ()


class MenuRoleRelation(models.Model):
    """菜单关系表"""
    id = models.CharField(max_length=30, primary_key=True)
    role_id = models.CharField(max_length=30, verbose_name="角色ID")
    menu_id = models.CharField(max_length=30, verbose_name="菜单ID")
    data = models.JSONField(verbose_name="菜单数据")

    class Meta:
        default_permissions = ()


class Department(models.Model):
    """部门"""
    STATUS = (
        (1, '启用'),
        (2, '停用')
    )
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=100, verbose_name="名称")
    remark = models.CharField(max_length=200, verbose_name="备注")
    status = models.IntegerField(verbose_name="状态", choices=STATUS)
    sort = models.IntegerField(verbose_name="部门排序")
    parent = models.CharField(max_length=30, verbose_name="部门父级", null=True, blank=True)
    create_date_time = models.DateTimeField(default=timezone.now)

    @staticmethod
    def tree(filter_data: list = None):  # filter_data 指定搜索结果的ID，不在此列表中的数据会从树形中剔除
        """以树形获取当前部门"""
        from apps.user.serializer import DepartmentSerializer

        data = BaseUtil.sort_item(
            data=DepartmentSerializer(Department.objects.all(), many=True).data
        )

        if isinstance(filter_data, list):
            data = BaseUtil.filter_item(data, filter_data)

        return data

    def recursive_delete(self):
        """递归删除自己及所有子节点"""

        def handle_delete(parent_id):
            response = []
            instance = Department.objects.filter(parent=parent_id)

            if instance.count() > 0:
                for item in instance:
                    response.extend(handle_delete(item.id))

            response.append(parent_id)
            return list(set(response))

        for department_id in handle_delete(self.id):
            Department.objects.filter(id=department_id).delete()

        return True

    def delete(self, using=None, keep_parents=False):
        User.objects.filter(department_id=self.id).update(department_id=None)
        return super(self).delete()

    class Meta:
        default_permissions = ()
        verbose_name = '部门'
        verbose_name_plural = '部门管理'
