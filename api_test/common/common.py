from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.parsers import JSONParser

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.models import Project
from api_test.serializer import ProjectDynamicDeserializer


def record_dynamic(project,_type,operation_object,user,data):
    """
    记录项目动态
    """
    time=datetime.now()
    dynamic_serializer=ProjectDynamicDeserializer(
        data={
            "time":time,
            "project":project,
            "type":_type,
            "operation_object":operation_object,
            "user":user,
            "description":data
        }
    )
    if dynamic_serializer.is_valid():
        dynamic_serializer.save()


def get_availability_project(data,user):
    """
    检查项目是否存在/可用/用户是否有权限
    :param request:
    :return: 项目如果可用返回项目，否则返回错误code
    """
    try:
        project = Project.objects.get(id=data['project_id'])
        if not user.is_superuser and project.owner.is_superuser:
            return JsonResponse(code.CODE_NO_PERMISSION_ERROR, msg='用户无操作权限')
        if not project.status:
            return JsonResponse(code=code.CODE_PROJECT_DISABLE, msg='项目禁用')
    except ObjectDoesNotExist:
        return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST, msg='项目不存在')
    return project
