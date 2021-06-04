# Kubernetes动态准入控制

## 说明

基于Kubernetes 动态准入控制功能，实现针对资源权限控制。可使用的场景：强制命名规范，资源发布控制，审计等。


## 流程图

<div align=center>
    <img src="https://user-images.githubusercontent.com/22042809/120790879-15528e00-c566-11eb-8295-1b5bf151b31d.png" width="70%">
</div>



## 目录结构
<pre>
    ├── README.md                   # 说明文件
    ├── apps                        # 子项目目录
    │   ├── README.md                   - # 项目规范说明文件
    │   └── user                        - # 用户验证模块
    ├── main                        # 项目主目录
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── settings.py             # 主配置文件
    │   ├── urls.py                 # 请求URL主入口
    │   └── wsgi.py
    ├── db.sqlite3                  # 自带数据库（仅开发环境）
    ├── env                         # 不同环境的配置文件
    │   ├── README.md                   - # 配置文件使用说明
    │   └── env                         - # 环境配置文件
    ├── logs                        # 日志
    │   ├── butter-error.log            - # 错误日志
    │   └── butter.log                  - # 运行日志
    ├── manage.py
    ├── reload                      # (uwsgi) 监听该文件变动重启服务
    ├── requirements.txt            # 项目依赖
    ├── static                      # 静态资源文件
    │   ├── css
    │   ├── image
    │   └── js
    └── uwsgi.ini                   # uwsgi配置文件
</pre> 
## 启动项目

* 安装包依赖
  * 进到工程目录 命令行执行: <code>pip3 install -r requirements.txt</code>
* 首次初始化数据库:
  * 进到工程目录 命令行执行: <code>python3 manage migrate</code>
* 复制配置文件:
  * 进到env目录 命令行执行: <code>cp env.example env</code>
* 启动
  * 开发环境
    * 进到工程目录 命令行执行: <code>python3 manage runserver 127.0.0.1:8000</code>
    * 创建管理员用户 命令行执行: <code>python3 manage.py createsuperuser</code>
  * uwsgi
    * 项目目录下执行 <code>uwsgi --ini uwsgi.ini</code>


## 访问项目

* 访问项目
  * 浏览器打开：http://127.0.0.1:8000


## 常见问题

1. `No module named "Crypto"`
```shell script
# 因Python crypto库遗留问题所致，详情参考下方链接
pip uninstall crypto pycryptodome
pip install pycryptodome
```
参考文档：[解释Crypto模块怎么就这么"皮"](https://www.cnblogs.com/fawaikuangtu123/p/9761943.html)

## 版本约定

* 框架版本约定
  * Python 3.8.6
  * Django 3.1.4
  * Celery 4.4.2
  * Django Rest Framework 3.11.0
  
## 相关资料

* 安装Python运行环境
  * https://www.python.org/downloads
* 安装Python包管理工具pip
  * https://www.runoob.com/w3cnote/python-pip-install-usage.html
* 安装Django Web框架
  * https://www.djangoproject.com/download
* 安装开发工具Pycharm
  * https://www.jetbrains.com/pycharm/download/#section=windows
