from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import code
from api_test.common.api_response import JsonResponse
from api_test.common.common import get_availability_project, record_dynamic, check_project_status
from api_test.common.parameter_check import parameter_id_check
from api_test.models import TestCaseGroup, Project
from api_test.serializer import TestCaseGroupSerializer


def parameter_name_check(data):
    if not data['name']:
        return JsonResponse(code=code.CODE_PARAMETER_ERROR,msg='组名不能为空')
    same_name_group=TestCaseGroup.objects.filter(name=data['name'],project=data['project_id'])
    if same_name_group:
        return JsonResponse(code==code.CODE_EXIST_SAME_NAME,msg='存在同名分组')


class AddGroup(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        新增测试用例分组
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=parameter_name_check(data) if isinstance(project,Project) else project
        if result:
            return result
        serializer=TestCaseGroupSerializer(data=data)
        if serializer.is_valid():
            serializer.save(project=project)
        else:
            return JsonResponse(code=code.CODE_Failed)
        record_dynamic(project=project.id, _type='添加', operation_object='用例分组', user=request.user.pk,
                       data='新增用例分组"%s"' % data['name'])
        return JsonResponse(data={
            'group_id':serializer.data.get('id')
        },code=code.CODE_SUCCESS)


class Group(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self,request):
        """
        获取测试用例分组
        :param request:
        :return:
        """
        project=check_project_status(request)
        if not isinstance(project,Project):
            return project
        groups=TestCaseGroup.objects.filter(project=project.id)
        serializer=TestCaseGroupSerializer(groups,many=True)
        return JsonResponse(data=serializer.data,code=code.CODE_SUCCESS)


class DelGroup(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self,request):
        """
        删除测试用例分组
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=parameter_id_check(data) if isinstance(project,Project) else project
        if result:
            return result
        groups=TestCaseGroup.objects.filter(id=data['id'],project=project.id)
        if groups:
            name=groups[0].name
            groups[0].delete()
            record_dynamic(project=project.id, _type='删除', operation_object='测试用例分组', user=request.user.pk,
                           data='删除用例分组 %s' % name)
            return JsonResponse(code=code.CODE_SUCCESS,msg='删除成功')
        return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='用例分组不存在')


class UpdateGroup(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    def post(self,request):
        """
        删除测试用例分组
        :param request:
        :return:
        """
        data=JSONParser().parse(request)
        project=get_availability_project(data,request.user)
        result=parameter_id_check(data) or parameter_name_check(data) if isinstance(project,Project) else project
        if result:
            return result
        try:
            group=TestCaseGroup.objects.get(id=data['id'],project=project.id)
        except ObjectDoesNotExist:
            return JsonResponse(code=code.CODE_OBJECT_NOT_EXIST,msg='用例分组不存在')
        serializer=TestCaseGroupSerializer(data=data)
        if serializer.is_valid():
            serializer.update(instance=group,validated_data=serializer.data)
            record_dynamic(project=project.id, _type='修改', operation_object='测试用例分组', user=request.user.pk,
                           data='修改用例分组 %s' % data['name'])
            return JsonResponse(code=code.CODE_SUCCESS)
        return JsonResponse(code=code.CODE_Failed)
