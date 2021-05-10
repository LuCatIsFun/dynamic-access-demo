# Generated by Django 3.2 on 2021-04-25 14:41

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='名称')),
                ('remark', models.CharField(max_length=200, verbose_name='备注')),
                ('status', models.IntegerField(choices=[(1, '启用'), (2, '停用')], verbose_name='状态')),
                ('sort', models.IntegerField(verbose_name='部门排序')),
                ('parent', models.CharField(blank=True, max_length=30, null=True, verbose_name='部门父级')),
                ('create_date_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': '部门',
                'verbose_name_plural': '部门管理',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='名称')),
                ('i18n', models.CharField(blank=True, max_length=100, null=True, verbose_name='国际化地址')),
                ('path', models.CharField(max_length=100, verbose_name='路径')),
                ('status', models.IntegerField(choices=[(1, '启用'), (2, '停用')], verbose_name='状态')),
                ('sort', models.IntegerField(verbose_name='菜单排序')),
                ('keepalive', models.IntegerField(verbose_name='开启缓存')),
                ('component_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='组件名称')),
                ('component_path', models.CharField(blank=True, default='LAYOUT', max_length=200, null=True, verbose_name='组件地址')),
                ('icon', models.CharField(blank=True, max_length=100, null=True, verbose_name='图标')),
                ('redirect', models.CharField(blank=True, max_length=100, null=True, verbose_name='重定向')),
                ('is_link', models.IntegerField(blank=True, null=True, verbose_name='外链')),
                ('link_type', models.IntegerField(blank=True, choices=[(1, '内嵌'), (2, '外链')], null=True, verbose_name='外链类型')),
                ('show', models.IntegerField(blank=True, null=True, verbose_name='是否显示')),
                ('type', models.IntegerField(verbose_name='组件类型')),
                ('permission', models.CharField(blank=True, max_length=100, null=True, verbose_name='权限标识')),
                ('parent', models.CharField(blank=True, max_length=30, null=True, verbose_name='菜单父级')),
                ('create_date_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': '菜单',
                'verbose_name_plural': '菜单管理',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='MenuRoleRelation',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('role_id', models.CharField(max_length=30, verbose_name='角色ID')),
                ('menu_id', models.CharField(max_length=30, verbose_name='菜单ID')),
                ('data', models.JSONField(verbose_name='菜单数据')),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='PermissionCode',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('code', models.IntegerField(verbose_name='权限码')),
                ('note', models.CharField(max_length=100, verbose_name='权限码说明')),
                ('create_date_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': '权限代码',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='PermissionCodeRoleRelation',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('role_id', models.CharField(max_length=30, verbose_name='角色ID')),
                ('permission_code_id', models.CharField(max_length=30, verbose_name='权限代码ID')),
                ('code', models.IntegerField(verbose_name='权限码')),
                ('note', models.CharField(max_length=100, verbose_name='权限码说明')),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='名称')),
                ('status', models.IntegerField(choices=[(1, '启用'), (2, '停用')], verbose_name='状态')),
                ('key', models.CharField(max_length=100, verbose_name='角色Key')),
                ('remark', models.CharField(max_length=200, verbose_name='备注')),
                ('create_date_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': '角色',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('mobile', models.CharField(blank=True, max_length=30, verbose_name='电话')),
                ('role_id', models.CharField(blank=True, max_length=30, null=True, verbose_name='用户角色ID')),
                ('department_id', models.CharField(blank=True, max_length=30, null=True, verbose_name='用户部门ID')),
                ('avatar', models.CharField(max_length=500, verbose_name='头像地址')),
                ('nickname', models.CharField(default='未设置昵称', max_length=30, verbose_name='昵称')),
                ('token', models.CharField(blank=True, max_length=64, null=True, verbose_name='认证token')),
                ('expired_date_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='失效时间')),
                ('dead_date_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最长可用时间')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户管理',
                'default_permissions': (),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]