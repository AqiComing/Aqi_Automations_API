from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from api_test.models import Project, ProjectDynamic, GlobalHost


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
        return 0


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
        model=GlobalHost
        fields=('id','project_id','name','host','status','description')
