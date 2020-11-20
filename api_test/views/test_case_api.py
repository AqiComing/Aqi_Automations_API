import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.common.common import objects_paginator, get_availability_project, record_dynamic, create_json
from api_test.common.parameter_check import project_status_check
from api_test.models import AutomationTestCase, AutomationCaseApi, Project, APIInfo, AutomationParameter, \
    AutomationParameterRaw, AutomationHead, AutomationResponseJson
from api_test.serializer import AutomationCaseApiSerializer, APIInfoSerializer, AutomationCaseApiDesSerializer, \
    AutomationCaseApiListSerializer, AutomationHeadSerializer, AutomationParameterSerializer, \
    AutomationParameterRawSerializer


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

def all_parameter_check(data):
    """
    检查所有参数
    :param data:
    :return:
    """
    try:
        if not data['project_id'] or not data['automation_test_case_id'] or not data['name'] or not data['http_type'] \
            or not data['request_type'] or not data['api_address'] or not data['request_parameter_type'] \
            or not data['examine_type']:
            return JsonResponse(code=code.CODE_PARAMETER_ERROR,msg='必需参数值未空')
        if not isinstance(data['project_id'],int) or not isinstance(data['automation_test_case_id'],int):
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
        if data['http_type'] not in ('HTTP', "HTTPS") or data['request_type'] not in (
            'POST', 'GET', 'PUT', 'DELETE') or data['request_parameter_type'] not in ['form-data', 'raw', 'Restful']:
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
    except KeyError:
        return JsonResponse(code=code.CODE_KEY_ERROR)


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
                                   user=request.user.pk, data="用例 %s 新增接口 \" %s \"" % (test_case.case_name,
                                                                                       api_serializer.data.get('name')))
                else:
                    return JsonResponse(code=code.CODE_Failed)
        return JsonResponse(code=code.CODE_SUCCESS)


class CaseAPIInfo(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self,request):
        """
        获取接口详情
        :param request:
        :return:
        """
        result = project_status_check(request)
        if result:
            return result
        project_id, case_id,api_id = request.GET.get('project_id'), request.GET.get('case_id'),request.GET.get('api_id')
        try:
            AutomationTestCase.objects.get(id=case_id,project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999987",msg="测试用例不存在！")
        try:
            case_api=AutomationCaseApi.objects.get(id=api_id,automation_test_case=case_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999987",msg="用例接口不存在！")
        data=AutomationCaseApiSerializer(case_api).data
        try:
            name=AutomationResponseJson.objects.get(automation_case_api=api_id,type="Regular")
            data['RegularParam']=name.name
        except ObjectDoesNotExist:
            pass
        return JsonResponse(code=code.CODE_SUCCESS,data=data)


class DelAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        删除用例的api接口
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        test_case=get_test_case(data)
        if not isinstance(project, Project):
            return project
        if not isinstance(test_case, AutomationTestCase):
            return test_case
        for api_id in data['ids']:
            case_api=AutomationCaseApi.objects.filter(id=api_id,automation_test_case=test_case.id)
            if len(case_api)!=0:
                name=case_api[0].name
                case_api.delete()
                record_dynamic(project=project.id,_type="删除", operation_object="用例接口",user=request.user.pk,
                               data="删除用例\"%s\"的接口\"%s\""%(test_case.case_name,name))
        return JsonResponse(code=code.CODE_SUCCESS)


class AddNewAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        用例新增接口
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        test_case=get_test_case(data)
        result = all_parameter_check(data) if isinstance(project,Project) else project
        all_parameter_check(data)
        if result:
            return result
        if not isinstance(test_case,AutomationTestCase):
            return test_case
        api=AutomationCaseApi.objects.filter(name=data['name'],automation_test_case=test_case.id)
        if len(api):
            return JsonResponse(code=code.CODE_EXIST_SAME_NAME)
        with transaction.atomic():
            serializer=AutomationCaseApiSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                new_api_id=serializer.data.get("id")
                new_api=AutomationCaseApi.objects.get(new_api_id)
                if len(data.get('headDict')):
                    for head in data['headDict']:
                        if head['name']:
                            head['automation_case_api_id']=new_api_id
                            head_serializer=AutomationHeadSerializer(data=head)
                            if head_serializer.is_valid():
                                head_serializer.save()
                if data["request_parameter_type"]=='form-data':
                    if len(data.get("request_list")):
                        for parameter in data["request_list"]:
                            parameter["automation_case_api_id"]=new_api_id
                            parameter_serializer=AutomationParameterSerializer(data=parameter)
                            if parameter_serializer.is_valid():
                                parameter_serializer.save()
                else:
                    # if len(data.get["request_list"]):
                    #     AutomationParameterRaw(automation_case_api=new_api,data=data["request_list"]).save()
                    if len(data.get('request_list')):
                        data["automation_case_api_id"]=new_api_id
                        parameter_serializer=AutomationParameterRawSerializer(data=data)
                        if parameter_serializer.is_valid():
                            parameter_serializer.save()
                if data.get("examine_type")=="json":
                    try:
                        response=eval(data['response_data'].replace('true',"True").replace("false","False").replace("null","None"))
                        api="<response[JSON][%s]>"% new_api_id
                        create_json(new_api,api,response)
                    except KeyError:
                        return JsonResponse(code=code.CODE_Failed)
                    except AttributeError:
                        return JsonResponse(code="999998",msg="校验内容不能为空")
                elif data.get("examine_type")=="Regular_check":
                    if data.get("RegularParam"):
                        AutomationResponseJson(automation_case_api=new_api,name=data["RegularParam"],
                                               tier='<response[Regular][%s]["%s"]>'%(new_api_id,data['response_data']),
                                               type="Regular").save()
                    return JsonResponse(data={"api_id":new_api_id},code=code.CODE_SUCCESS)
                return JsonResponse(code=code.CODE_Failed)




