from django.db import models
from django.utils import timezone


# 配置
class Settings(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    value = models.TextField()
    note = models.CharField(max_length=300)
    create_date_time = models.DateTimeField(default=timezone.now)

    class Meta:
        default_permissions = ()
        ordering = ['-create_date_time']
