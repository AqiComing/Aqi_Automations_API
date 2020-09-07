from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from api_test.models import Project, ProjectDynamic, GlobalHost, ReportSenderConfig, ProjectMember, APIGroup, APIHead, \
    APIParameter, APIParameterRaw, APIResponse, APIInfo, TestCaseGroup, AutomationTestCase


class TokenSerializer(serializers.ModelSerializer):
    """
    User info serializer
    """
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    phone = serializers.CharField(source="user.user.phone")
    email = serializers.CharField(source="user.email")
    date_joined = serializers.CharField(source="user.date_joined")

    class Meta:
        model = Token
        fields = ("first_name", "last_name", "phone", "email", "key", "date_joined")


class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name')


class ProjectSerializer(serializers.ModelSerializer):
    """
    Project Serializer
    """
    apiCount = serializers.SerializerMethodField()
    dynamicCount = serializers.SerializerMethodField()
    memberCount = serializers.SerializerMethodField()
    lastUpdateTime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)
    createTime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)
    owner = serializers.CharField(source="owner.first_name")

    class Meta:
        model = Project
        fields = ('id', 'name', 'version', 'type', 'status', 'lastUpdateTime', 'createTime', 'apiCount',
                  'dynamicCount', 'memberCount', 'description', 'owner')

    def get_apiCount(self, obj):
        return obj.api_project.all().count()

    def get_dynamicCount(self, obj):
        return obj.dynamic_project.all().count()

    def get_memberCount(self, obj):
        return obj.member_project.all().count()


class ProjectDeserializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name', 'version', 'type', 'status', 'lastUpdateTime', 'createTime', 'description', 'owner')


class ProjectDynamicDeserializer(serializers.ModelSerializer):
    """
    项目动态信息反序列化
    """

    class Meta:
        model = ProjectDynamic
        fields = ('id', 'project', 'time', 'type', 'operation_object', 'user', 'description')


class ProjectDynamicSerializer(serializers.ModelSerializer):
    """
    项目动态序列化
    """
    operation_user = serializers.CharField(source='user.first_name')
    time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)

    class Meta:
        model = ProjectDynamic
        fields = ('id', 'time', 'type', 'operation_object', 'operation_user', 'description')


class HostSerializer(serializers.ModelSerializer):
    """
    HOST序列化
    """

    class Meta:
        model = GlobalHost
        fields = ('id', 'project_id', 'name', 'host', 'status', 'description')


class ReportSenderConfigSerializer(serializers.ModelSerializer):
    """
    邮件发送人配置序列化
    """
    project = serializers.CharField(source='project.name')

    class Meta:
        model = ReportSenderConfig
        fields = ('id', 'project', 'sender_mailbox', 'user_name', 'mail_token', 'mail_smtp')


class ReportSenderConfigDeserializer(serializers.ModelSerializer):
    """
    邮件发送人配置反序列化
    """

    class Meta:
        model = ReportSenderConfig
        fields = ('id', 'project_id', 'sender_mailbox', 'user_name', 'mail_token', 'mail_smtp')


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    项目成员信息序列化
    """
    user_name=serializers.CharField(source='user.first_name')
    user_phone=serializers.CharField(source='user.user.phone')
    user_email=serializers.CharField(source='user.email')

    class Meta:
        model=ProjectMember
        fields=('id','permission_type','user_name','user_phone','user_email')


class APIGroupSerializer(serializers.ModelSerializer):
    """
    接口分组序列化
    """
    class Meta:
        model=APIGroup
        fields=('id','project_id','name')


class APIHeadSerializer(serializers.ModelSerializer):
    """
    接口请求头序列化
    """
    class Meta:
        model=APIHead
        fields=('id','api','name','value')


class APIParameterSerializer(serializers.ModelSerializer):
    """
    接口请求头序列化
    """
    class Meta:
        model=APIParameter
        fields=('id','api','name','value','_type','required','restrict','description')


class APIParameterRawSerializer(serializers.ModelSerializer):
    """
    接口请求参数源数据序列化
    """
    class Meta:
        model=APIParameterRaw
        fields=('id','api','data')


class APIResponseSerializer(serializers.ModelSerializer):
    """
    接口返回参数序列化
    """
    class Meta:
        model=APIResponse
        fields=('id','api','name','value','_type','required','description')


class APIInfoSerializer(serializers.ModelSerializer):
    """
    接口详细信息序列化
    """
    last_update_time=serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)
    headers=APIHeadSerializer(many=True,read_only=True)
    request_parameters=APIParameterSerializer(many=True,read_only=True)
    response=APIResponseSerializer(many=True,read_only=True)
    request_parameter_raw=APIParameterRawSerializer(many=False,read_only=True)
    update_user=serializers.CharField(source='update_user.first_name')

    class Meta:
        model=APIInfo
        fields=('id','api_group','name','http_type','request_type','api_address','headers',
                'request_parameter_type','request_parameters','request_parameter_raw','status',
                'response','mock_code','data','last_update_time','update_user','description')


class APIInfoDeserializer(serializers.ModelSerializer):
    class Meta:
        model=APIInfo
        fields=('id','project_id','name','http_type','request_type','api_address',
                'request_parameter_type','status','mock_code','data','last_update_time','update_user','description')


class APIInfoListSerializer(serializers.ModelSerializer):
    """
    接口列表序列化
    """
    last_update_time=serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)
    update_user=serializers.CharField(source='update_user.first_name')

    class Meta:
        model=APIInfo
        fields=('id','name','request_type','api_address','mock_status','last_update_time','update_user')


class TestCaseGroupSerializer(serializers.ModelSerializer):
    """
    测试用例分组序列化
    """
    class Meta:
        model=TestCaseGroup
        fields=('id','project_id','name')


class TestCaseSerializer(serializers.ModelSerializer):
    """
    自动化测试用例序列化
    """
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)
    create_user = serializers.CharField(source='user.first_name')

    class Meta:
        model=AutomationTestCase
        fields=('id','test_case_group','case_name','create_user','description','update_time')


class TestCaseDeserializer(serializers.ModelSerializer):
    """
    自动化测试用例反序列化
    """
    class Meta:
        model=AutomationTestCase
        fields = ('id', 'project_id','test_case_group', 'case_name', 'user', 'description', 'update_time')



