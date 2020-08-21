from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.db import models

PROJECT_TYPE = (('Web', 'Web'), ('App', 'App'))

"""
@receiver(post_save,sender=**)
当创建用户时，同步创建token
"""


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class UserProfile(models.Model):
    """
    扩展现有用户的功能
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='user', related_name='user')
    phone = models.CharField(max_length=11, default='None', blank=True, verbose_name='phone number')
    openId = models.CharField(max_length=50, default=0, verbose_name='唯一标识')
    unionId = models.CharField(max_length=50, default=0, verbose_name='企业唯一标识')

    def __unicode__(self):
        return self.user.username

    def __str__(self):
        return self.phone


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='Project name')
    version = models.CharField(max_length=50, verbose_name='Project version')
    type = models.CharField(max_length=50, verbose_name='Project Type', choices=PROJECT_TYPE)
    description = models.CharField(max_length=512, blank=True, null=True, verbose_name='Project description')
    status = models.BooleanField(default=True, verbose_name='Project status')
    lastUpdateTime = models.DateTimeField(auto_now=True, verbose_name='Last update time')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='Create time')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=50, verbose_name='owner')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = "Project"


class ProjectDynamic(models.Model):
    """
    项目动态
    """
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, related_name='dynamic_project', on_delete=models.CASCADE, verbose_name='所属项目')
    time = models.DateTimeField(max_length=128, verbose_name='操作时间')
    type = models.CharField(max_length=50, verbose_name='操作类型')
    operation_object = models.CharField(max_length=50, verbose_name='操作对象')
    user = models.ForeignKey(User, blank=True, null=True, related_name='user_name', on_delete=models.SET_NULL,
                             verbose_name='操作人')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')

    def __unicode__(self):
        return self.type

    class Meta:
        verbose_name = '项目动态'
        verbose_name_plural = '项目动态'


class GlobalHost(models.Model):
    """
    Host域名
    """
    id = models.AutoField(primary_key=True)
    # on_delete 级联删除
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目')
    name = models.CharField(max_length=50, verbose_name='名称')
    host = models.CharField(max_length=256, verbose_name='host地址')
    description = models.CharField(max_length=256, verbose_name='描述')
    status = models.BooleanField(default=True, verbose_name='状态')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'HOST'
        verbose_name_plural = 'Host管理'


class ReportSenderConfig(models.Model):
    id=models.AutoField(primary_key=True)
    project=models.ForeignKey(Project,on_delete=models.CASCADE,verbose_name='项目')
    sender_mailbox=models.EmailField(max_length=1024,blank=True,null=True,verbose_name='发件人邮箱')
    user_name=models.CharField(max_length=50,blank=True,null=True,verbose_name='用户名')
    mail_token=models.CharField(max_length=1024,blank=True,null=True,verbose_name='邮箱口令')
    mail_smtp=models.CharField(max_length=1024,blank=True,null=True,verbose_name='邮箱服务器')

    def __unicode__(self):
        return self.sender_mailbox

    class Meta:
        verbose_name='邮件发送配置'
        verbose_name_plural='邮件发送配置'


class ProjectMember(models.Model):
    """"
    项目成员
    """
    CHOICES={
        ('超级管理员','超级管理员'),
        ('开发人员', '开发人员'),
        ('测试人员', '测试人员'),
    }
    id=models.AutoField(primary_key=True)
    permission_type=models.CharField(max_length=50,verbose_name='权限角色',choices=CHOICES)
    project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='member_project',verbose_name='所属项目')
    user=models.ForeignKey(User,related_name='member_user',on_delete=models.CASCADE,verbose_name='用户')

    def __unicode__(self):
        return self.permission_type

    def __str__(self):
        return self.permission_type

    class Meta:
        verbose_name='项目成员'
        verbose_name_plural='项目成员'


class APIGroup(models.Model):
    """
    接口一级分组
    """
    id=models.AutoField(primary_key=True)
    project=models.ForeignKey(Project,on_delete=models.CASCADE,verbose_name='项目')
    name=models.CharField(max_length=50,verbose_name='接口一级分组')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name='接口一级分组'
        verbose_name_plural='接口一级分组'
