from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


# python ../../manage.py makemigrations 生成迁移文件
# python ../../manage.py migrate 数据库迁移
class User(AbstractUser):  # django自带的用户模型类，需要添加手机号为验证字段
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name="邮箱验证状态")

    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
