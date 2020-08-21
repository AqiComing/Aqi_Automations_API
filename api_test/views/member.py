from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.common.common import get_availability_project, record_dynamic, objects_paginator
from api_test.models import Project, ReportSenderConfig, ProjectMember
from api_test.serializer import ReportSenderConfigDeserializer, ReportSenderConfigSerializer, ProjectMemberSerializer


def all_parameter_check(data):
    """
    校验参数
    :param data:
    :return:
    """
    try:
        if not isinstance(data['project_id'],int):
            return JsonResponse(code=code.CODE_PARAMETER_ERROR,msg='项目id错误')
        if not data['sender_mailbox'] or not data['user_name'] or not data['mail_token'] or not data['mail_smtp']:
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
    except KeyError:
        return JsonResponse(code=code.CODE_KEY_ERROR)


class ProjectMemberList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self,request):
        """
        获取成员列表
        :param request:
        :return:
        """
        result=objects_paginator(request,model=ProjectMember,_order_by='id')
        if isinstance(result,JsonResponse):
            return result
        serialize=ProjectMemberSerializer(result['obm'],many=True)
        return JsonResponse(data={"data":serialize.data,
                                  "page":result['page'],
                                  "total":result['total']
                                  },code=code.CODE_SUCCESS)


class GetEmail(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self,request):
        """
        获取邮箱配置
        :param request:
        :return:
        """
        project_id=request.GET.get("project_id")
        if not project_id or not project_id.isdecimal():
            return JsonResponse(code=code.CODE_PARAMETER_ERROR)
        try:
            project=Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='项目不存在')
        if not project.status:
            return JsonResponse(code=code.CODE_PROJECT_DISABLE,msg='项目不可用')
        try:
            object=ReportSenderConfig.objects.get(project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_SUCCESS)
        data=ReportSenderConfigSerializer(object).data
        return JsonResponse(code=code.CODE_SUCCESS,data=data)


class EmailConfig(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=all_parameter_check(data) if isinstance(project,Project) else project
        if result:
            return result
        serialize=ReportSenderConfigDeserializer(data=data)
        if serialize.is_valid():
            try:
                object=ReportSenderConfig.objects.get(project=data['project_id'])
                serialize.update(instance=object,validated_data=data)
            except ObjectDoesNotExist:
                serialize.save(project=project)
            record_dynamic(project=data["project_id"],_type='添加', operation_object='邮箱', user=request.user.pk, data= '添加邮箱配置')
            return JsonResponse(code=code.CODE_SUCCESS)
        return JsonResponse(code=code.CODE_Failed)



