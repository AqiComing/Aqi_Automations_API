from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.parsers import JSONParser

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.models import Project, AutomationResponseJson
from api_test.serializer import ProjectDynamicDeserializer, ProjectSerializer


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


def check_project_status(request):
    """
    检查项目是否存在/可用
    :param request:
    :return:
    """
    project_id = request.GET.get('project_id')
    if not project_id and not project_id.isdecimal():
        return JsonResponse(code=code.CODE_PARAMETER_ERROR)
    try:
        project = Project.objects.get(id=project_id)
    except ObjectDoesNotExist:
        return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST, msg='项目不存在')
    if not project.status:
        return JsonResponse(code=code.CODE_PROJECT_DISABLE)
    return project


def objects_paginator(request,objects):
    """
    将objects填充道页面中，进行分页
    :param request:
    :return:
    """
    try:
        page_size = int(request.GET.get("page_size", 20))
        page = int(request.GET.get("page", 1))
    except(TypeError, ValueError):
        return JsonResponse(code=code.CODE_KEY_ERROR, msg="page and page size must be integer")

    paginator = Paginator(objects, page_size)
    total = paginator.num_pages
    try:
        obm = paginator.page(page)
    except PageNotAnInteger:
        obm = paginator.page(1)
    except EmptyPage:
        obm = paginator.page(paginator.num_pages)
    return{"obm":obm,"page":page,"total":total}


def create_json(api_id,api,data):
    """
    根据json数据生成关联接口
    :param api_id: 接口id
    :param api: 格式化api数据
    :param data: Json数据
    :return:
    """
    if isinstance(data,dict):
        for i in data:
            m=(api+"[\"%s\"]"%i)
            AutomationResponseJson(automation_case_api=api_id,name=i,tier=m,type='json').save()
            create_json(api,m,data[i])
