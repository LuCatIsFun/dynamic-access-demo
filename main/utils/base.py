"""
@time: 2020/7/29 10:49 上午
"""

__all__ = ['BaseUtil', 'PermissionAPIView']

import re
import string
import time
import requests
from datetime import datetime
from random import choice

from django.conf import settings
from rest_framework.request import Request
from rest_framework.views import APIView


class BaseUtil:
    DEFAULT_AVATAR = 'https://s1-fs.pstatp.com/static-resource/v1/b36c64f9-b03d-4d17-a6d9-410e0e9e2d9g'

    @staticmethod
    def get_username_by_id(user_id):
        from apps.user.models import User
        try:
            user_id = int(user_id)
        except:
            return '未知'
        if isinstance(user_id, int) and user_id == 0:
            return '系统'
        user_info = User.objects.filter(id=user_id).first()
        if user_info:
            return user_info.nickname
        else:
            return '未知'

    @staticmethod
    def handle_query_parameter(request: Request, parameter: list, parameter_config: dict = None) -> dict:
        result = dict()
        method = str(request.method).lower()
        if not parameter:  # 空参数直接返回
            return result

        if method in ['get']:  # 获取request原始数据
            data = request.GET
        else:
            data = request.data

        for p in parameter:
            # 参数不存在时跳过
            d = data.get(p)
            if d is None or str(d) in ['', '[]', '{}']:
                continue

            if parameter_config:
                if p in parameter_config:
                    action = parameter_config.get(p)
                    if action not in ['in', 'gt', 'gte', 'lt', 'lte', 'date_range']:
                        raise ValueError('wrong action: %s' % action)
                    if action == 'date_range':
                        d = BaseUtil.try_safe_eval(d)
                        if isinstance(d, list):
                            result['%s__%s' % (p, 'gte')] = d[0]
                            result['%s__%s' % (p, 'lte')] = d[1]
                        else:
                            raise ValueError('date_range value error, must list')

                    else:
                        query = 'contains' if action == 'in' else action
                        result['%s__%s' % (p, query)] = d
                else:
                    result[p] = d
            else:
                result[p] = d
        return result

    @staticmethod
    def get_random_password(length=8, chars=string.ascii_letters + string.digits):
        return ''.join([choice(chars) for i in range(length)])

    @staticmethod
    def get_random_captcha(length=6):
        return ''.join([choice(string.digits) for i in range(length)])

    @staticmethod
    def try_safe_eval(value):
        if isinstance(value, (list, dict, bool)) or value is None:
            return value
        value = str(value)
        if all([value]):
            if value.startswith('[') and value.endswith(']') or \
                    value.startswith('{') and value.endswith('}'):
                value = eval(value.replace('null', 'None'), {'datetime': datetime, 'time': time})

            elif value.lower() in ['true', 'false']:
                return {
                    'true': True,
                    'false': False,
                }.get(value.lower())
        else:
            raise ValueError('value can not be null')

        return value

    @staticmethod
    def get_now():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def distance_now(distance_time):
        now = datetime.now()
        if isinstance(distance_time, str):
            try:
                distance_time = datetime.strptime(distance_time, '%Y-%m-%d %H:%M:%S')
            except:
                raise ValueError('Unresolvable time')

        if not isinstance(distance_time, datetime):
            raise ValueError('Unresolvable time')
        if distance_time > now:
            suffix = '后'
            time_diff = distance_time - now
        else:
            suffix = '前'
            time_diff = now - distance_time

        if time_diff.days > 0:
            return '%s天%s' % (time_diff.days, suffix)
        else:
            if time_diff.seconds >= (60 * 60):
                return '%s小时%s' % (time_diff.seconds // (60 * 60), suffix)
            elif time_diff.seconds >= 60:
                return '%s分钟%s' % (time_diff.seconds // 60, suffix)
            else:
                return '刚刚'

    @staticmethod
    def check_parameter(parameter, kwargs):
        for p in parameter:
            if p not in kwargs.keys():
                return False
        return True

    @staticmethod
    def get_request():
        request = BaseRequest()
        return request

    @staticmethod
    def create_setting(setting_name, vale, note):
        """
        创建新配置
        """
        from .. import models
        setting_info = models.Settings.objects.filter(id=setting_name)
        if setting_info:
            setting_info.update(value=vale, note=note)
        else:
            models.Settings.objects.create(id=setting_name, value=vale,
                                           note=note)
        return True

    @staticmethod
    def update_setting(setting_name, vale):
        """
        根据配置名称更新配置
        """
        from .. import models
        setting_info = models.Settings.objects.filter(id=setting_name)
        if setting_info:
            setting_info.update(value=vale)
        else:
            raise RuntimeError('setting: %s not found' % setting_name)
        return True

    @staticmethod
    def get_setting(setting_name, default_value=None):
        """
        根据配置名称获取配置
        """
        from .. import models
        setting_info = models.Settings.objects.filter(id=setting_name)
        if setting_info:
            value = setting_info.first().value
            return BaseUtil.try_safe_eval(value)
        else:
            if default_value:
                BaseUtil.create_setting(setting_name=setting_name, vale=default_value, note='default create')
                return default_value
            else:
                if not settings.DEBUG:
                    raise RuntimeError('setting: %s not found' % setting_name)

    @staticmethod
    def is_valid_phone(phone):
        # 宽泛方式匹配手机号
        phone_pat = re.compile(r'^1[3-9]\d{9}$')
        try:
            res = re.search(phone_pat, phone)
            if res:
                return True
            else:
                return False
        except Exception as e:
            return False

    @staticmethod
    def is_valid_id_card(id_card):
        ID_CARD_REGEX = r'[1-9][0-9]{14}([0-9]{2}[0-9X])?'
        id_card = str(id_card)
        if not re.match(ID_CARD_REGEX, id_card):
            return False

        items = [int(item) for item in id_card[:-1]]
        factors = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)

        copulas = sum([a * b for a, b in zip(factors, items)])

        ck_codes = ('1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2')

        return ck_codes[copulas % 11].upper() == id_card[-1].upper()

    @staticmethod
    def is_valid_email(email):
        email = str(email)
        for c in ['.', '-', '_']:
            if email.startswith(c):
                return False
        EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,5}$)"
        return not re.match(EMAIL_REGEX, email) is None

    @staticmethod
    def is_valid_bankcard_number(card_num):
        """
        Luhn算法判断银行卡是否有效
        参考资料：https://www.cnblogs.com/cc11001100/p/9357177.html
        生成随机银行卡号：https://ddu1222.github.io/bankcard-validator/bcBuilder.html
        """
        card_num = str(card_num)
        s = 0
        card_num_length = len(card_num)
        for _ in range(1, card_num_length + 1):
            try:
                t = int(card_num[card_num_length - _])
            except ValueError:
                return False
            if _ % 2 == 0:
                t *= 2
                s += t if t < 10 else t % 10 + t // 10
            else:
                s += t
        return s % 10 == 0

    @staticmethod
    def is_valid_passport_number(passport_num):
        """
        https://zh.wikipedia.org/wiki/中华人民共和国护照#个人资料页

        # 2019
        普通护照	外交护照	公务护照	公务普通护照	香港特区护照	      澳门特区护照
        E*	      DE	    SE	     PE	    K、KJ（至2019年）   MA（至2019年）
                                            H#（2019年起）      MB（2019年起）

        普通护照	外交护照	公务护照	公务普通护照	香港特区护照	澳门特区护照
        G	    D	    S	      P	         H	            M

        星号（*）处为一个字母或数字，最初启用的为数字0-9，目前已全部使用完毕并改用字母，从A开始按顺序分配（I、O除外）；井号（#）处为一个字母或数字，启用的为数字2-9[来源请求]，然后从A开始按顺序分配（I、O除外）
        """
        passport_num = str(passport_num)
        PASSPORT_REGEX = r'(^[EeKkGgDdSsPpHhMm]\d{8}$)|(^(([Ee][a-zA-Z])|([DdSsPp][Ee])|' \
                         r'([Kk][Jj])|([Mm][Aa])|([Mm][Bb])|(1[45]))\d{7}$)'
        return not re.match(PASSPORT_REGEX, passport_num) is None

    @staticmethod
    def is_valid_taiwan_compatriot_permit(taiwan_id):
        """
        台湾居民来往大陆通行证
        规则： 新版8位或18位数字， 旧版10位数字 + 英文字母
        样本： 12345678 或 1234567890B
        """
        taiwan_id = str(taiwan_id)
        TAIWAN_REGEX = r'^\d{8}|^[a-zA-Z0-9]{10}|^\d{18}$'

        return not re.match(TAIWAN_REGEX, taiwan_id) is None

    @staticmethod
    def extract_url_by_string(string_content):
        url_regular = re.compile(r"(https|http)?:\/\/(([0-9]{1,3}\.){3}[0-9]{1,3}|([0-9a-zA-Z_!~*'()-]+\.)*([0-9a-zA-Z]"
                                 r"[0-9a-zA-Z-]{0,61})?[0-9a-zA-Z]\.[0-9a-zA-Z]{2,6})(:[0-9a-zA-Z]{1,4})?"
                                 r"((\/[0-9a-zA-Z_!~*().;?:@&=+$,%#-]*)+)?")
        result = url_regular.search(string_content)
        if result:
            if result.group(0) in string_content:
                return result.group(0).strip()
            else:
                return None
        else:
            return None

    @staticmethod
    def sort_item(data: list) -> list:
        """传入列表，根据parent确立父子级关系，根据sort关键字排序"""
        data = list(data)
        # 首先获取父级为None的菜单为根菜单
        parent_tree = []
        for item in data:
            if not item['parent'] and item not in parent_tree:
                parent_tree.append(item)
        # 根菜单排序
        parent_tree = sorted(parent_tree, key=lambda x: x['sort'])

        def has_children(parent_id: str) -> bool:
            """判断传入id是否存在子节点"""
            for _item in data:
                if _item['parent'] == parent_id:
                    return True
            return False

        def get_children(parent_id: str) -> list:
            """获取对应id的子节点"""
            result = []
            for _item in data:
                if _item['parent'] == parent_id:
                    result.append(_item)
            return result

        def handle_parent(parent: list) -> list:
            """递归处理传入节点列表，获取子节点"""
            result = []
            for p in parent:
                if has_children(p['id']):
                    p['children'] = handle_parent(get_children(p['id']))
                result.append(p)
            return sorted(result, key=lambda x: x['sort'])  # 对子节点进行排序

        return handle_parent(parent=parent_tree)

    @staticmethod
    def filter_item(data: list, filter_data: list) -> list:

        def is_keep(item_data: dict) -> bool:
            """检查自身或自身的子节点是否有符合条件"""
            if item_data['id'] in filter_data:
                return True

            if 'children' in item_data:
                for children_item in item_data['children']:
                    if is_keep(children_item):
                        return True
            return False

        def handle_filter(_data: list) -> list:
            """递归所有元素，符合筛选条件的打上_keep=True"""
            for d in _data:
                d['_keep'] = is_keep(d)
                if 'children' in d:
                    d['children'] = handle_filter(d['children'])
            return _data

        def generate_result(_data):
            """将符合结果的数据生成至新的list中"""
            response = []

            for d in _data:
                if 'children' in d:
                    d['children'] = generate_result(d['children'])
                if d['_keep']:
                    del d['_keep']
                    response.append(d)

            return response

        return generate_result(handle_filter(data))


class BaseRequest(BaseUtil):

    def __init__(self):
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        request = requests.Session()
        request.mount("https://", adapter)
        request.mount("http://", adapter)
        self.request = request

    @staticmethod
    def handle_request_params(data):
        if 'self' in data:
            del data['self']
        return data

    def get(self, url, params=None, data=None, headers=None, cookies=None, files=None,
            auth=None, timeout=None, allow_redirects=True, proxies=None,
            hooks=None, stream=None, verify=None, cert=None, json=None):
        return self.request.get(**self.handle_request_params(locals()))

    def post(self, url, params=None, data=None, headers=None, cookies=None, files=None,
             auth=None, timeout=None, allow_redirects=True, proxies=None,
             hooks=None, stream=None, verify=None, cert=None, json=None):
        return self.request.post(**self.handle_request_params(locals()))

    def delete(self, url, params=None, data=None, headers=None, cookies=None, files=None,
               auth=None, timeout=None, allow_redirects=True, proxies=None,
               hooks=None, stream=None, verify=None, cert=None, json=None):
        return self.request.delete(**self.handle_request_params(locals()))

    def put(self, url, params=None, data=None, headers=None, cookies=None, files=None,
            auth=None, timeout=None, allow_redirects=True, proxies=None,
            hooks=None, stream=None, verify=None, cert=None, json=None):
        return self.request.put(**self.handle_request_params(locals()))

    def patch(self, url, params=None, data=None, headers=None, cookies=None, files=None,
              auth=None, timeout=None, allow_redirects=True, proxies=None,
              hooks=None, stream=None, verify=None, cert=None, json=None):
        return self.request.patch(**self.handle_request_params(locals()))


class PermissionAPIView(APIView):
    subclass = []
    permission_code = []
    permission_code_by_action = {}

    permission_meta = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclass.append(cls)

    @staticmethod
    def get_register_permission_code():
        code_map = {}
        for cls in PermissionAPIView.subclass:
            if isinstance(cls.permission_code, int):
                if cls.permission_code not in code_map:
                    code_map[cls.permission_code] = []

            if isinstance(cls.permission_code, list):
                code_map = {
                    **code_map,
                    **{
                        code: [] for code in cls.permission_code
                        if code not in code_map and isinstance(code, int)
                    }
                }
        for cls in PermissionAPIView.subclass:
            if cls.permission_meta and isinstance(cls.permission_meta, dict):
                for key in cls.permission_meta:
                    if isinstance(key, int):
                        if key in code_map and key not in code_map[key]:
                            code_map[key].append(cls.permission_meta[key])
