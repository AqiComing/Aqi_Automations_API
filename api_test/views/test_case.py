from unittest import TestCase

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.common.common import get_availability_project, record_dynamic, objects_paginator
from api_test.common.parameter_check import project_status_check, parameter_ids_check
from api_test.models import Project, AutomationTestCase, TestCaseGroup
from api_test.serializer import TestCaseDeserializer, TestCaseSerializer


def all_parameter_check(data):
    try:
        if not data['project_id'] or not data['case_name'] or not data['test_case_group_id']:
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
        if not isinstance(data['project_id'],int) or not isinstance(data['test_case_group_id'],int):
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
        same_name_case=AutomationTestCase.objects.filter(case_name=data['case_name'],project=data['project_id'])
        if same_name_case:
            return JsonResponse(code=code.CODE_EXIST_SAME_NAME,msg='存在同名用例名称')
    except KeyError:
        return JsonResponse(code=code.CODE_KEY_ERROR)


class AddCase(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        添加测试用例
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=all_parameter_check(data) if isinstance(project,Project) else project
        if result:
            return result
        with transaction.atomic():
            try:
                serializer = TestCaseDeserializer(data=data)
                if serializer.is_valid():
                    try:
                        group = TestCaseGroup.objects.get(id=data['test_case_group_id'], project=project.id)
                        serializer.save(project=project, test_case_group=group, user=User.objects.get(id=request.user.pk))
                    except KeyError:
                        serializer.save(project=project,user=User.objects.get(id=request.user.pk))
                    record_dynamic(project=project, _type='添加', operation_object='测试用例', user=request.user.pk,
                           data='新增测试用例 %s' % data['case_name'])
                    return JsonResponse(data={'case_id':serializer.data.get('id')},code=code.CODE_SUCCESS)
                return JsonResponse(code=code.CODE_Failed)
            except Exception:
                return JsonResponse(code=code.CODE_Failed)


class CaseList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self,request):
        """
        获取用例列表
        :param request:
        :return:
        """
        result=project_status_check(request)
        if result:
            return result
        project_id, group_id, name = request.GET.get('project_id'), request.GET.get(
            'test_case_group_id'), request.GET.get('name')
        if group_id:
            if not group_id.isdecimal():
                return JsonResponse(code=code.CODE_PARAMETER_ERROR)
            if name:
                objects=AutomationTestCase.objects.filter(project=project_id,case_name__contains=name,test_case_group=group_id).order_by('id')
            else:
                objects=AutomationTestCase.objects.filter(project=project_id,test_case_group=group_id).order_by('id')
        else:
            if name:
                objects = AutomationTestCase.objects.filter(project=project_id, case_name__contains=name).order_by('id')
            else:
                objects = AutomationTestCase.objects.filter(project=project_id).order_by('id')
        result = objects_paginator(request, objects)
        serialize = TestCaseSerializer(result['obm'], many=True)
        return JsonResponse(data={"data": serialize.data,
                                  "page": result['page'],
                                  "total": result['total']
                                  }, code=code.CODE_SUCCESS)


class DelCase(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        删除测试用例
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=parameter_ids_check(data) if isinstance(project,Project) else project
        if result:
            return result
        id_list=Q()
        for id in data['ids']:
            id_list=id_list|Q(id=id)
        case_list=AutomationTestCase.objects.filter(id_list,project=project.id)
        name_list=[]
        for i in case_list:
            name_list.append(str(i.case_name))
        with transaction.atomic():
            case_list.delete()
            record_dynamic(project=project.id,_type='删除',operation_object='测试用例',user=request.user.pk,data="删除测试用例：%s" % name_list)
            return JsonResponse(code=code.CODE_SUCCESS)


class UpdateCase(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        修改用例
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=all_parameter_check(data) if isinstance(project,Project) else project
        if result:
            return result
        try:
            case=AutomationTestCase.objects.get(id=data['id'],project=project.id)
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='测试用例不存在')
        try:
            group=TestCaseGroup.objects.get(id=data['test_case_group_id'],project=project.id)
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='用例分组不存在')
        serializer=TestCaseDeserializer(data=data)
        if serializer.is_valid():
            serializer.update(instance=case,validated_data=data)
            record_dynamic(project=project.id,_type='更新',operation_object='测试用例',user=request.user.pk,data="修改测试用例：%s" % data['case_name'])
            return JsonResponse(code=code.CODE_SUCCESS)
        return JsonResponse(code=code.CODE_Failed)


class UpdateCaseGroup(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        更新用例的分组
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=parameter_ids_check(data) if isinstance(project,Project) else project
        if result:
            return result
        try:
            group=TestCaseGroup.objects.get(id=data['test_case_group_id'],project=project.id)
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='测试用例分组不存在')

        id_list=Q()
        for i in data['ids']:
            id_list=id_list|Q(id=i)
        case_list=AutomationTestCase.objects.filter(id_list,project=project.id)

        case_name=[]
        for j in case_list:
            case_name.append(j.case_name)

        with transaction.atomic():
            case_list.update(test_case_group=group)
            record_dynamic(project=project, _type='修改', operation_object='测试用例', user=request.user.pk,
                           data='修改测试用例分组 %s' % case_name)
            return JsonResponse(code=code.CODE_SUCCESS)


