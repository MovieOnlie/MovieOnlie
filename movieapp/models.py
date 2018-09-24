from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class MyUser(AbstractUser):
    phone = models.CharField(
        max_length=13,
        verbose_name='手机号',
        unique=True
    )
    icon = models.ImageField(upload_to='icons',
                             null=True)

#类别
class Category(models.Model):
    name = models.CharField(max_length=30,
                            verbose_name="类别名称")
    content = models.TextField(verbose_name="类别介绍")
    likes = models.ImageField(verbose_name="点赞数")

    def __str__(self):
        return self.name

#类别下的视频信息
class Page(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name="视频名称")
    icon = models.URLField(null=True,verbose_name="视频预览图")
    url = models.URLField(verbose_name="视频链接")
    views = models.ImageField(verbose_name="浏览数")
    category = models.ForeignKey('Category',verbose_name="所属类别")
    def __str__(self):
        return self.name