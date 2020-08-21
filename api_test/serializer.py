from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from api_test.models import Project, ProjectDynamic, GlobalHost, ReportSenderConfig, ProjectMember


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
        return 0

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
