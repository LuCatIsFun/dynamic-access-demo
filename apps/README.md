# 项目目录

## 规范
* 创建项目规范
    * 所有项目必须在 apps 目录下
    * 项目名必须为小写(userauth),不可以为UserAuth或USERAUTH


* 项目规范细则
    * 头部规范

    Py2模块文件的头部包含有 utf-8 编码声明(如果模块中使用了非 ASCII 编码的字符, 建议进行声明), 以及标准的文档字符串。
    ```
    # -*- coding: utf-8 -*-
    ```
    * 命名约定
        * 类名称：采用骆驼拼写法(CamelCase), 但如果首字母是缩略词则保持大写不变(HTTPWriter, 而不是 HttpWriter)
        * 变量名：小写_以及_下划线(lowercase_with_underscores)。
        * 方法与函数名：小写_以及_下划线(lowercase_with_underscores)。
        * 常量：大写_以及_下划线(UPPERCASE_WITH_UNDERSCORES)。
        * 预编译的正则表达式：name_re。 例如 `html_re = r"(?<=<h1>).+?(?=<h1>)"`
        * 命名要有寓意, 不使用拼音, 不使用无意义简单字母命名 (循环中计数例外 for i in)
        * 命名缩写要谨慎, 尽量是大家认可的缩写
    * 参数命名约定
        * 实例方法：self 为第一个参数。
    * 公共函数
      每个项目常用的的公共函数存放在该项目下的`commons.py`中,方便其他模块调用。
    * 注释约定
    ```python
    def user_info(user_id: int) -> None:
        """
            根据用户ID获取用户信息.

        :param user_id: 用户ID
        :return_type: dict
        :return: 返回用户身份的字典信息
        """
    ```


## 创建项目

1. `mkdir apps/you_project_name`    创建项目文件夹
2. `python manage.py startapp you_project_name apps/you_project_name`   创建项目骨架
