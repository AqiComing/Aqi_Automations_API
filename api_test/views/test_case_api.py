import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.common.common import objects_paginator, get_availability_project, record_dynamic
from api_test.common.parameter_check import project_status_check
from api_test.models import AutomationTestCase, AutomationCaseApi, Project, APIInfo, AutomationParameter, \
    AutomationParameterRaw, AutomationHead
from api_test.serializer import AutomationCaseApiSerializer, APIInfoSerializer, AutomationCaseApiDesSerializer, \
    AutomationCaseApiListSerializer


def get_test_case(data):
    """
    判断当前id对应的测试用例是否存在，如存在则返回
    :param data:
    :return:
    """
    if not data['case_id'] or not isinstance(data['case_id'],int):
        return JsonResponse(code=code.CODE_PARAMETER_ERROR)
    try:
        test_case=AutomationTestCase.objects.get(id=data['case_id'], project=data['project_id'])
    except ObjectDoesNotExist:
        return JsonResponse(code="999987", msg="测试用例不存在！")
    return test_case


class ApiList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self,request):
        """
        获取用例接口的列表
        :param request:
        :return:
        """
        result = project_status_check(request)
        if result:
            return result
        project_id,case_id=request.GET.get('project_id'),request.GET.get('case_id')
        try:
            AutomationTestCase.objects.get(id=case_id,project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999987",msg="测试用例不存在！")
        objects=AutomationCaseApi.objects.filter(automation_test_case=case_id).order_by('id')
        result = objects_paginator(request, objects)
        serialize = AutomationCaseApiListSerializer(result['obm'], many=True)
        for i in range(len(serialize.data)-1):
            serialize.data[i]['testStatus']=False
        return JsonResponse(data={"data": serialize.data,
                                  "page": result['page'],
                                  "total": result['total']
                                  }, code=code.CODE_SUCCESS)


class AddOldApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        用例绑定已有接口
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        test_case=get_test_case(data)
        if not isinstance(project,Project):
            return project
        elif not isinstance(test_case,AutomationTestCase):
            return test_case

        for api_id in data['api_ids']:
            try:
                api_data=APIInfoSerializer(APIInfo.objects.get(id=api_id,project=project.id)).data
            except ObjectDoesNotExist:
                continue
            with transaction.atomic():
                api_data["automation_test_case_id"]=test_case.pk
                api_serializer=AutomationCaseApiDesSerializer(data=api_data)
                if api_serializer.is_valid():
                    api_serializer.save(automation_test_case=test_case)
                    case_api=api_serializer.data.get('id')
                    if api_data['request_parameter_type']=='from-data':
                        if api_data['request_parameters']:
                            for parameter in api_data['request_parameters']:
                                if parameter['name']:
                                    AutomationParameter(automation_case_api=AutomationCaseApi.objects.get(id=case_api),
                                                        name=parameter["name"],value=parameter['value'],interrelate=False).save()
                        else:
                            if api_data['request_parameter_raw']:
                                AutomationParameterRaw(automation_case_api=AutomationCaseApi.objects.get(id=case_api),
                                                       data=json.loads(api_data['request_parameter_raw']['data'])).save()

                        if api_data.get('headers'):
                            for head in api_data['headers']:
                                if head['name']:
                                    AutomationHead(automation_case_api=AutomationCaseApi.objects.get(id=case_api),
                                                   name=head['name'],value=head['value'],interrelate=False).save()
                        record_dynamic(project=project.id, _type='新增', operation_object='用例接口',
                                       user=request.user.pk, data="用例 %s 新增接口 \" %s \""%(test_case.template_name,
                                                                                         api_serializer.data.get('name')))
        return  JsonResponse(code=code.CODE_SUCCESS)



