from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.db import models

PROJECT_TYPE = (('Web', 'Web'), ('App', 'App'))
HTTP_CHOICE=(
    ('HTTP','HTTP'),
    ('HTTPS','HTTPS')
)
REQUEST_TYPE_CHOICE=(
    ('POST','POST'),
    ('GET','GET'),
    ('PUT','PUT'),
    ('DELETE','DELETE')
)
REQUEST_PARAMETER_TYPE_CHOICE=(
    ('form-data','表单(form-data)'),
    ('raw','源数据（raw）'),
    ('Restful','Restful')
)
HTTP_CODE_CHOICE=(
    ('0','0'),
    ('200','200'),
    ('302','302'),
    ('400','400'),
    ('404','404'),
    ('500','500'),
    ('502','502'),
)

EXAMINE_TYPE_CHOICE=(
    ('no_check','不校验'),
    ('only_check_status','校验http状态'),
    ('json','JSON校验'),
    ('entirely_check','完全校验'),
    ('regular_check','正则校验')
)

PARAMETER_TYPE_CHOICE=(('Int','Int'),('String','String'))

RESULT_CHOICE=(
    ('PASS','成功'),
    ('FAIL','失败')
)

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


class APIInfo(models.Model):
    """
    接口信息
    """
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='api_project', verbose_name='所属项目')
    api_group = models.ForeignKey(APIGroup, blank=True, null=True, related_name='api_group', on_delete=models.SET_NULL,
                                  verbose_name='所属分组')
    name=models.CharField(max_length=50,verbose_name="接口名称")
    http_type=models.CharField(max_length=50,default='HTTP',verbose_name='http/https',choices=HTTP_CHOICE)
    request_type=models.CharField(max_length=50,verbose_name='请求方式',choices=REQUEST_TYPE_CHOICE)
    api_address=models.CharField(max_length=1024,verbose_name='接口地址')
    request_parameter_type=models.CharField(max_length=50,verbose_name='请求参数格式',choices=REQUEST_PARAMETER_TYPE_CHOICE)
    status=models.BooleanField(default=True,verbose_name='状态')
    mock_status=models.BooleanField(default=False,verbose_name='mock状态')
    mock_code=models.CharField(max_length=50,blank=True,null=True,verbose_name='Http状态',choices=HTTP_CODE_CHOICE)
    data=models.TextField(blank=True,null=True,verbose_name='Mock内容')
    last_update_time=models.DateTimeField(auto_now=True,verbose_name='最近更新')
    update_user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,max_length=50,verbose_name='更新人',related_name='api_update_user')
    description=models.CharField(max_length=1024,blank=True,null=True,verbose_name='描述')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '接口'
        verbose_name_plural = '接口管理'


class APIHead(models.Model):
    """
    接口请求头
    """
    id=models.AutoField(primary_key=True)
    api=models.ForeignKey(APIInfo,on_delete=models.CASCADE,verbose_name='所属接口',related_name='headers')
    name=models.CharField(max_length=1024,verbose_name='消息头')
    value=models.CharField(max_length=1024,blank=True,null=True,verbose_name='请求值')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '请求头'
        verbose_name_plural = '请求头管理'


class APIParameter(models.Model):
    id=models.AutoField(primary_key=True)
    api=models.ForeignKey(APIInfo,on_delete=models.CASCADE,verbose_name='所属接口',related_name='request_parameters')
    name=models.CharField(max_length=1024,verbose_name='参数名')
    _type=models.CharField(default='String',max_length=1024,verbose_name='参数类型',choices=PARAMETER_TYPE_CHOICE)
    value=models.CharField(max_length=1024,blank=True,null=True,verbose_name='参数值')
    required=models.BooleanField(default=True,verbose_name='是否必填')
    restrict=models.CharField(max_length=1024,blank=True,null=True,verbose_name='输入限制')
    description=models.CharField(max_length=1024,blank=True,null=True,verbose_name='描述')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '请求参数'
        verbose_name_plural = '请求参数管理'


class APIParameterRaw(models.Model):
    id=models.AutoField(primary_key=True)
    api=models.OneToOneField(APIInfo,on_delete=models.CASCADE,verbose_name='所属接口',related_name='request_parameter_raw')
    data=models.TextField(blank=True,null=True,verbose_name='内容')

    class Meta:
        verbose_name='请求参数Raw'


class APIResponse(models.Model):
    id=models.AutoField(primary_key=True)
    api=models.ForeignKey(APIInfo,on_delete=models.CASCADE,verbose_name='所属接口',related_name='response')
    name=models.CharField(max_length=1024,verbose_name='参数名')
    _type=models.CharField(default='String',max_length=1024,verbose_name='参数类型',choices=PARAMETER_TYPE_CHOICE)
    value=models.CharField(max_length=1024,blank=True,null=True,verbose_name='参数值')
    required=models.BooleanField(default=True,verbose_name='是否必含')
    description=models.CharField(max_length=1024,blank=True,null=True,verbose_name='描述')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '返回参数'
        verbose_name_plural = '返回参数管理'


class TestCaseGroup(models.Model):
    id=models.AutoField(primary_key=True)
    project=models.ForeignKey(Project,on_delete=models.CASCADE,verbose_name='项目')
    name=models.CharField(max_length=50,verbose_name='测试用例分组')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name="测试用例分组"
        verbose_name_plural="测试用例分组管理"


class AutomationTestCase(models.Model):
    """
    自动化测试用例
    """
    id=models.AutoField(primary_key=True)
    project=models.ForeignKey(Project,on_delete=models.CASCADE,verbose_name='所属项目')
    test_case_group = models.ForeignKey(TestCaseGroup, blank=True, null=True, on_delete=models.SET_NULL,
                                        verbose_name='所属用例分组', related_name='test_case_group')
    case_name=models.CharField(max_length=50,verbose_name='用例名称')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='创建人',
                             related_name='create_user')
    description=models.CharField(max_length=1024,blank=True,null=True,verbose_name='描述')
    update_time=models.DateTimeField(auto_now=True,verbose_name='更新时间')

    def __unicode__(self):
        return self.case_name

    def __str__(self):
        return self.case_name

    class Meta:
        verbose_name='自动化测试用例'
        verbose_name_plural='自动测试用'


class AutomationCaseApi(models.Model):
    """
    用例执行接口
    """
    id=models.AutoField(primary_key=True)
    automation_test_case=models.ForeignKey(AutomationTestCase,on_delete=models.CASCADE,verbose_name='用例',related_name='api')

    name=models.CharField(max_length=50,verbose_name='接口名称')
    http_type=models.CharField(max_length=50,default='HTTP',verbose_name='HTTP/HTTPS',choices=HTTP_CHOICE)
    request_type=models.CharField(max_length=50,verbose_name='请求方式',choices=REQUEST_TYPE_CHOICE)
    api_address=models.CharField(max_length=1024,verbose_name='接口地址')
    request_parameter_type=models.CharField(max_length=50,verbose_name='参数请求格式',choices=REQUEST_PARAMETER_TYPE_CHOICE)
    format_raw=models.BooleanField(default=False,verbose_name='是否转换位源数据')
    examine_type=models.CharField(default='no_check',max_length=50,verbose_name='校验方式',choices=EXAMINE_TYPE_CHOICE)
    http_code=models.CharField(max_length=50,blank=True,null=True,verbose_name='HTTP状态',choices=HTTP_CODE_CHOICE)
    response_data=models.TextField(blank=True,null=True,verbose_name='返回内容')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name='用例接口'
        verbose_name_plural='用例接口管理'


class AutomationHead(models.Model):
    """
    用例接口请求头
    """
    id=models.AutoField(primary_key=True)
    automation_case_api = models.ForeignKey(AutomationCaseApi, related_name='header', on_delete=models.CASCADE,
                                            verbose_name='接口')
    name=models.CharField(max_length=1024,verbose_name='参数名')
    value=models.CharField(max_length=1024,verbose_name='内容',blank=True,null=True)
    interrelate=models.BooleanField(default=False,verbose_name='是否关联')

    def __unicode__(self):
        return self.value

    class Meta:
        verbose_name='请求头'
        verbose_name_plural='请求头管理'


class AutomationParameter(models.Model):
    """
    请求参数
    """
    id=models.AutoField(primary_key=True)
    automation_case_api = models.ForeignKey(AutomationCaseApi, related_name='parameter_list', on_delete=models.CASCADE,
                                            verbose_name='接口')
    name=models.CharField(max_length=1024,verbose_name='参数名')
    value=models.CharField(max_length=1024,verbose_name='内容',blank=True,null=True)
    interrelate=models.BooleanField(default=False,verbose_name='是否关联')

    def __unicode__(self):
        return self.value

    class Meta:
        verbose_name='接口参数'
        verbose_name_plural='接口参数管理'


class AutomationParameterRaw(models.Model):
    """
    请求的源数据参数
    """
    id=models.AutoField(primary_key=True)
    automation_case_api = models.OneToOneField(AutomationCaseApi, related_name='parameter_raw', on_delete=models.CASCADE,
                                            verbose_name='接口')
    data=models.TextField(verbose_name="请求参数源数据",blank=True,null=True)

    class Meta:
        verbose_name="请求参数源数据"
        verbose_name_plural="请求参数源数据管理"


class AutomationResponseJson(models.Model):
    """
    返回json参数
    """
    id=models.AutoField(primary_key=True)
    automation_case_api = models.ForeignKey(AutomationCaseApi, related_name='response', on_delete=models.CASCADE,
                                            verbose_name='接口')
    name=models.CharField(max_length=1024,verbose_name='JSON参数',blank=True,null=True)
    tier=models.CharField(max_length=1024,verbose_name='层级关系',blank=True,null=True)
    type=models.CharField(max_length=1024,verbose_name='关联类型',default='json',choices=(('json','json'),('Regular','Regular')))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name='结果JSON参数'
        verbose_name_plural='结果JSON参数管理'


class AutomationTestResult(models.Model):
    """
    手动执行结果
    """
    id=models.AutoField(primary_key=True)
    automation_case_api = models.ForeignKey(AutomationCaseApi, on_delete=models.CASCADE,verbose_name='接口'
                                            ,related_name='test_result')
    url=models.CharField(max_length=1024,verbose_name="请求地址")
    request_type=models.CharField(max_length=50,verbose_name="请求方式",choices=REQUEST_TYPE_CHOICE)
    host=models.CharField(max_length=1024,verbose_name="host",null=True,blank=True)
    header=models.CharField(max_length=1024,verbose_name="请求头",null=True,blank=True)
    parameter=models.TextField(blank=True,null=True,verbose_name="请求参数")
    status_code=models.CharField(max_length=50,verbose_name="期望HTTP状态",blank=True,null=True,choices=HTTP_CODE_CHOICE)
    examine_type=models.CharField(max_length=1024,verbose_name="匹配规则")
    data=models.TextField(blank=True,null=True,verbose_name="规则内容")
    result=models.CharField(max_length=50,verbose_name="测试结果",choices=RESULT_CHOICE)
    http_status=models.CharField(max_length=50,verbose_name='http状态',blank=True,null=True,choices=HTTP_CODE_CHOICE)
    response_data=models.TextField(blank=True,null=True,verbose_name='实际返回内容')
    test_time=models.DateTimeField(auto_now_add=True,verbose_name='测试时间')

    def __unicode__(self):
        return self.http_status

    class Meta:
        verbose_name="手动测试结果"
        verbose_name_plural="手动测试结果管理"
