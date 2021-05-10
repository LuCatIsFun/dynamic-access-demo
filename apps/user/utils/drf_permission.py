"""
@time: 2020/8/14 2:48 下午
"""

__all__ = ['AdminOrHigherPermission', 'SuperUserPermission']

from rest_framework import permissions


def check_permission(allow_role, request):
    if request.user.is_superuser:
        return True
    elif hasattr(request.user, 'role') and request.user.role in allow_role:
        return True
    else:
        return False


class CodePermission(permissions.BasePermission):
    REQUEST_METHOD_MAP = {
        'list': 'GET',
        'create': 'POST',
        'destroy': 'DELETE',
        'retrieve': 'GET',
        'put': 'PUT',
        'get': 'GET',
        'post': 'POST',
        'patch': 'PATCH'
    }

    def check_permission_format(self, permission_code, permission_code_by_action, view):
        """检查配置的权限是否合法，不满足格式要求会抛异常"""
        module_path = "{}.{}".format(view.__module__, view.__class__.__name__)
        if permission_code and permission_code is not None and not isinstance(permission_code, (int, list)):
            raise TypeError(
                '<%s> permission_code type was not int or list' % module_path
            )
        else:
            if isinstance(permission_code, list):
                for action_code in permission_code:
                    if not isinstance(action_code, int):
                        raise TypeError(
                            '<%s> permission_code list value "%s" type was not int' % (module_path, action_code)
                        )
        if permission_code_by_action and permission_code_by_action is not None:
            """"""
            if not isinstance(permission_code_by_action, dict):
                raise TypeError(
                    '<%s> permission_code_by_action type was not dict' % module_path
                )
            for action in permission_code_by_action:
                if str(action).lower() not in self.REQUEST_METHOD_MAP:
                    raise TypeError(
                        '<%s> permission_code_by_action: action "%s" not support, allow:[%s]' % (
                            module_path, action, ",".join(self.REQUEST_METHOD_MAP.keys())
                        )
                    )
                if not hasattr(view, action):
                    raise AttributeError(
                        '<%s> permission_code_by_action: action "%s" is undefined' % (
                            module_path, action
                        )
                    )
                if not isinstance(permission_code_by_action.get(action, None), (int, list)):
                    raise TypeError(
                        '<%s> permission_code_by_action: "%s" code type was not int or list' % (module_path, action)
                    )
                else:
                    if isinstance(action_list := permission_code_by_action.get(action, None), list):
                        for action_code in action_list:
                            if not isinstance(action_code, int):
                                raise TypeError(
                                    '<%s> permission_code_by_action: "%s" code list value "%s" type was not int' % (
                                        module_path, action, action_code
                                    )
                                )

    def get_permission(self, view) -> tuple:
        """获取配置的权限"""
        return getattr(view, 'permission_code') if hasattr(view, 'permission_code') else None, \
               getattr(view, 'permission_code_by_action') if hasattr(view, 'permission_code_by_action') else None

    def is_require_permission(self, view) -> bool:
        """检查类是否需要权限访问"""
        permission_code, permission_code_by_action = self.get_permission(view)

        if permission_code or permission_code_by_action:
            return True
        return False

    @staticmethod
    def query_permission(role_id, code) -> bool:
        """查询权限code，True为满足所有，False为任一不满足。None视为不需要权限，返回True"""
        if isinstance(code, int):
            code = [code]
        elif role_id is None:
            return True

        from apps.user.models import PermissionCodeRoleRelation
        for c in code:
            if isinstance(c, list):
                if not CodePermission.query_permission(role_id=role_id, code=c):
                    return False
                continue
            if PermissionCodeRoleRelation.objects.filter(role_id=role_id, code=c).count() == 0:
                return False
        return True

    def has_permission(self, request, view):
        if self.is_require_permission(view):
            if not request.user.role_id:
                return False

            permission_code, permission_code_by_action = self.get_permission(view)
            self.check_permission_format(permission_code, permission_code_by_action, view)
            if permission_code_by_action and isinstance(permission_code_by_action, dict):
                permission_action = list(
                    set(permission_code_by_action.keys()) &
                    set([r for r in self.REQUEST_METHOD_MAP if self.REQUEST_METHOD_MAP[r] == request.method])
                )
                permission_action_code = [permission_code_by_action[k] for k in permission_code_by_action if
                                          k in permission_action and permission_code_by_action[k]]
            else:
                permission_action_code = []
            return self.query_permission(role_id=request.user.role_id, code=permission_code) & self.query_permission(
                role_id=request.user.role_id, code=permission_action_code
            )
        else:
            return True


class AdminOrHigherPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return check_permission(['admin'], request)


class SuperUserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser
